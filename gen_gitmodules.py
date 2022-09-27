#!/usr/bin/env python3

"""
PaStA - Patch Stack Analysis

Copyright (c) OTH Regensburg, 2020

Author:
  Ralf Ramsauer <ralf.ramsauer@oth-regensburg.de>

This work is licensed under the terms of the GNU GPL, version 2.  See
the COPYING file in the top-level directory.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.
"""

import re
import requests

from time import sleep
from collections import defaultdict
from lxml import html

url_lore = 'https://lore.kernel.org/lists.html?o=%d'
url_lore_shards = 'https://lore.kernel.org/%s/_/text/mirror/'
url_github = 'https://raw.githubusercontent.com/lfd/mail-archiver/linux-archives/.gitmodules'

pubin_providers = ['lore.kernel.org', 'github.com']

blacklist = {
    'coda.cs.cmu.edu': {'codalist'},
    'kernelnewbies.org': {'kernelnewbies'},
    'lists.kernelnewbies.org': {'kernelnewbies'},
    'netbsd.org': {'radiotap'},
    'dpdk.org': {'dev'},
    'gitolite.kernel.org': {'transparency-log'},
    'linux.kernel.org': {'keys'},
    'lists.cip-project.org': {'cip-testing', 'cip-testing-results'},
    'cip-testing-results.lists.cip-project.org': {'64575'},
    'lists.linuxfoundation.org': {'linux-kernel-mentees'},
    'lists.lttng.org': {'lttng-dev'},
    'lore.kernel.org': {'linux-firmware', 'signatures'},
    'vger.kernel.org': {'backports', 'fstests', 'linux-trace-users', 'selinux-refpolicy', 'git', 'linux-rt-users'},
}


def get_tree(url):
    code = 0
    retries = 5
    while code != 200:
        resp = requests.get(url)
        code = resp.status_code
        if code != 200:
            print('Crap. sleeping. %s' % url)
            sleep(5)
            retries -= 1
        if retries < 0:
            raise ValueError('Maximum retries reached')

    return html.fromstring(resp.content)


def get_lore():
    ret = defaultdict(dict)
    lists = set()

    for i in range(0, 2):
        tree = get_tree(url_lore % (i * 200))
        this_lists = tree.xpath('/html/body/pre/a/text()')
        lists |= set(this_lists)

    # remove some parsing artefacts
    lists -= {'next (older)', 'all', 'reverse', 'above'}

    for listname in lists:
        url = url_lore_shards % listname
        tree = get_tree(url)

        hoster = tree.xpath('/html/body/form/pre/a/b')
        hoster = hoster[-1].text
        hoster = hoster.split()[0]
        hoster = hoster.split('.', 1)[1]
        print('Working on %s - %s' % (hoster, listname))

        shards = tree.xpath('/html/body/pre/a/@href')
        max_shard = 0
        for shard in shards:
            shard = shard.split('/')[-1]
            if shard.isdigit():
                shard = int(shard)
                if shard > max_shard:
                    max_shard = shard

        ret[hoster][listname] = max_shard

    return ret


def get_github():
    ret = defaultdict(dict)

    matcher = re.compile('\tpath = archives/(.*)')
    project_matcher = re.compile('([^\.]+)\.(.*)\.(\d+)')
    gitmodules = requests.get(url_github).content.decode().split('\n')
    for line in gitmodules:
        match = matcher.match(line)
        if not match:
            continue
        project = match.group(1)
        if project.startswith('ASSORTED'):
            continue

        if project == 'b.a.t.m.a.n.lists.open-mesh.org.0':
            listname = 'b.a.t.m.a.n'
            hoster = 'lists.open-mesh.org'
            shard = 0
        else:
            match = project_matcher.match(project)
            listname, hoster, shard = match.group(1), match.group(2), match.group(3)
        shard = int(shard)

        hoster = ret[hoster]
        if listname not in hoster:
            hoster[listname] = 0
        hoster[listname] = max(shard, hoster[listname])

    return ret


def fill_missing(result, lists, uri_scheme):
    for hoster, lists in lists.items():
        if hoster not in result:
            result[hoster] = dict()
        for list in lists.keys():
            if list not in result[hoster]:
                result[hoster][list] = uri_scheme
    return result


def split_provider(provider_filter, data):
    ret = defaultdict(list)

    for hoster, lists in data.items():
        for listname, provider in lists.items():
            if provider != provider_filter:
                continue

            ret[hoster].append(listname)
    return ret

def generate_submodule(provider, hoster, listname, shard):
    ret = list()
    dst = 'linux/resources/mbox/pubin/%s/%s/%u.git' % (hoster, listname, shard)

    if provider == 'lore.kernel.org':
        url = 'https://lore.kernel.org/%s/%u' % (listname, shard)
    elif provider == 'github.com':
        url = 'https://github.com/linux-mailinglist-archives/%s.%s.%s' % (listname, hoster, shard)

    ret.append('[submodule "%s"]' % dst)
    ret.append('\tpath = %s' % dst)
    ret.append('\turl = %s' % url)
    return ret

data = dict()
data['lore.kernel.org'] = get_lore()
data['github.com'] = get_github()

tmp = dict()
for provider in pubin_providers:
    tmp = fill_missing(tmp, data[provider], provider)

config = str()
for hoster in sorted(tmp.keys()):
    lists = set(tmp[hoster].keys())

    if hoster in blacklist:
        lists -= blacklist[hoster]

    if len(lists) == 0:
        continue

    config += '\n"%s" = [\n' % hoster
    for listname in sorted(lists):
        config += '\t"%s",\n' % listname
    config += ']\n'
    with open('linux-config', 'w') as f:
        f.write(config)


gitmodules = list()
for provider in pubin_providers:
    result = split_provider(provider, tmp)

    gitmodules.append('')
    gitmodules.append('##################################################')
    gitmodules.append('# Linux Public Inboxes hosted by %s' % provider)
    gitmodules.append('##################################################')

    for hoster in sorted(result.keys()):
        listnames = set(result[hoster])
        if hoster in blacklist:
            listnames -= blacklist[hoster]

        if len(listnames) == 0:
            continue

        gitmodules.append('')
        gitmodules.append('## %s' % hoster)
        for listname in sorted(listnames):
            max_shard = data[provider][hoster][listname] + 1
            for shard in range(0, max_shard):
                gitmodules += generate_submodule(provider, hoster, listname, shard)

gitmodules = '\n'.join(gitmodules)
with open('gitmodules', 'w') as f:
    f.write(gitmodules + '\n')
