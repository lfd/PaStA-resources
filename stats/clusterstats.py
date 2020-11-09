#!/usr/bin/env python3

import sys

from pypasta import *

if len(sys.argv) != 2:
    print("%s project" % sys.argv[0])
    quit(-1)

project = sys.argv[1]

c = Clustering.from_file('./resources/%s/resources/patch-groups' % project)

downstream = c.get_downstream()
upstream = c.get_upstream()

mail_clusters = [(d, u) for d, u in c.iter_split() if len(d) != 0]
mail_clusters_upstream = [(d, u) for d, u in mail_clusters if len(u) != 0]
mail_clusters_not_upstream = [(d, u) for d, u in mail_clusters if len(u) == 0]

hashes_assigned = [len(u) for _, u in mail_clusters]

def mcu(num, foo=False):
    if foo:
        no_clusters = len([d for d, u in mail_clusters_upstream if len(u) >= num])
    else:
        no_clusters = len([d for d, u in mail_clusters_upstream if len(u) == num])

    return num, no_clusters, 100 * no_clusters / len(mail_clusters_upstream)

def mcd(num, foo=False):
    if foo:
        no_clusters = len([d for d, u in mail_clusters if len(d) >= num])
    else:
        no_clusters = len([d for d, u in mail_clusters if len(d) == num])

    return num, no_clusters, 100 * no_clusters / len(mail_clusters)



print('           Total mails with patches: %7u' % len(downstream))
print('                      Total commits: %7u' % len(upstream))
print('                      Mail clusters: %7u' % len(mail_clusters))
print()
print('Total number of unassigned clusters: %7u' % len(mail_clusters_not_upstream))
print('Total number of   assigned clusters: %7u' % len(mail_clusters_upstream))
print()
print('Total number of unassigned messages: %7u' % sum([len(d) for d, _ in mail_clusters_not_upstream]))
print('Total number of   assigned messages: %7u' % sum([len(d) for d, _ in mail_clusters_upstream]))
print()
print('Percentage of commit hashes in clusters: %.2f%% (aka. commit coverage)' % (100 * sum(hashes_assigned) / len(upstream)))
print('     Percentage of clusters with hashes: %.2f%%' % (100 * len(mail_clusters_upstream) / len(mail_clusters)))
print()

for i in range(1, 5):
    print('Mail clusters with   %u commit hashes:       %8u (%5.2f%%)' % mcu(i))
print('Mail clusters with >=%u commit hashes:       %8u (%5.2f%%)' % mcu(5, True))

print()

for i in range(1, 5):
    print('     Mail clusters with   %u messages:       %8u (%5.2f%%)' % mcd(i))
print('     Mail clusters with >=%u messages:       %8u (%5.2f%%)' % mcd(5, True))


#print('\n'.join([list(u)[0] for d, u in mail_clusters_upstream if len(u) >= 2]))
