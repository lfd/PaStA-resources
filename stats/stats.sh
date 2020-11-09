#!/usr/bin/bash
prjs=("busybox" "FFmpeg" "flac" "gcc" "git" "jailhouse" "linux" "LLVM" "OpenSSL" "PostgreSQL" "qemu" "u-boot" "wine")
mkdir -p stats
for i in ${prjs[@]}; do
	./clusterstats.py $i > stats/$i.txt
done
