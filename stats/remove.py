#!/usr/bin/env python3

from pypasta import *
clustering = Clustering.from_file('./resources/buildroot/resources/patch-groups')
with open('./resources/buildroot/resources/git-commit-bots', 'r') as f:
    message_ids = f.read().splitlines()

for message_id in message_ids:
    if message_id in clustering:
        clustering.remove_element(message_id)

clustering.to_file('patch-groups-without-bots')
