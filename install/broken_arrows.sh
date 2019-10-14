#!/bin/bash

set -e

wget -q -O /tmp/broken-arrows.tgz http://bows2.ec-lille.fr/BrokenArrowsV1_1.tgz

mkdir -p /tmp/broken-arrows
tar -xvf /tmp/broken-arrows.tgz -C /tmp/broken-arrows
rm /tmp/broken-arrows.tgz

ls -al /tmp/broken-arrows

cd /tmp/broken-arrows/BrokenArrowsV1_1 && make

cp /tmp/broken-arrows/BrokenArrowsV1_1/embed /usr/bin/ba-embed
chmod +x /usr/bin/ba-embed
cp /tmp/broken-arrows/BrokenArrowsV1_1/detect /usr/bin/ba-detect
chmod +x /usr/bin/ba-detect

rm -rf /tmp/broken-arrows