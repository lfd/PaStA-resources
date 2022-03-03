#!/usr/bin/env bash

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

# Emit data rows (no header) from a potentially split file
tail_split() {
	local base=$1
	if [ -f "$base" ]; then
		tail -n +2 "$base"
	else
		local first=1
		for chunk in $(ls "$base".[0-9][0-9][0-9] 2>/dev/null | sort); do
			if [ $first -eq 1 ]; then
				tail -n +2 "$chunk"
				first=0
			else
				cat "$chunk"
			fi
		done
	fi
}

echo "project,id,from,time,type,version,list,list.matches_patch,ignored,commithash,committer,committer.correct,committer.xcorrect,committer.distance" > $CHAR
echo "project,release,date" > $REL

projects="qemu xen u-boot linux"
for p in $projects; do
	tail -n +2 $p/resources/releases.csv | sed -e "s/\(.*\)/${p},\1/" >> $REL
	tail_split $p/resources/characteristics.csv | sed -e "s/\(.*\)/${p},\1/" >> $CHAR
done
