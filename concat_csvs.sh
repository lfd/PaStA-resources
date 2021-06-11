#!/bin/bash

CHAR=characteristics.csv
REL=releases.csv

echo "project,id,from,time,type,version,list,list.matches_patch,ignored,committer,committer.correct,committer.xcorrect" > $CHAR
echo "project,release,date" > $REL

projects="qemu xen u-boot linux"
for p in $projects; do
	tail -n +2 $p/resources/releases.csv | sed -e "s/\(.*\)/${p},\1/" >> $REL
	tail -n +2 $p/resources/characteristics.csv | sed -e "s/\(.*\)/${p},\1/" >> $CHAR
done
