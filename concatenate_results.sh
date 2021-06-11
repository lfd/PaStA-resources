#!/bin/bash

# PaStA - Patch Stack Analysis
#
# Copyright (c) OTH Regensburg, 2021
#
# Author:
#   Ralf Ramsauer <ralf.ramsauer@oth-regensburg.de>
#
# This work is licensed under the terms of the GNU GPL, version 2.  See
# the COPYING file in the top-level directory.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.

CHAR=characteristics.csv
REL=releases.csv

echo "project,id,from,time,type,version,list,list.matches_patch,ignored,committer,committer.correct,committer.xcorrect" > $CHAR
echo "project,release,date" > $REL

projects="qemu xen u-boot linux"
for p in $projects; do
	tail -n +2 $p/resources/releases.csv | sed -e "s/\(.*\)/${p},\1/" >> $REL
	tail -n +2 $p/resources/characteristics.csv | sed -e "s/\(.*\)/${p},\1/" >> $CHAR
done
