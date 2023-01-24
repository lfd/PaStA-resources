#!/usr/bin/bash

rm -rf hashes
mkdir hashes

base="v0.14.0-rc0"

cd repo
stable_branches=$(git branch -r | grep 'stable')

git log --pretty=format:%H --no-merges ${base}..origin/master > ../hashes/master

for branch in $stable_branches; do
	b=$(echo $branch | sed -e 's/origin\///')
	git log --pretty=format:%H --no-merges ${base}..${branch} > ../hashes/$b
	echo >> ../hashes/$b
done

cd ../hashes
cat * | sort | uniq > stack-hashes
