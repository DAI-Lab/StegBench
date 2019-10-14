#!/bin/bash

set -e

git clone https://github.com/b3dk7/StegExpose.git /tmp/StegExpose

cp /tmp/StegExpose/StegExpose.jar usr/bin/StegExpose.jar

rm -rf /tmp/StegExpose

chmod +x /usr/bin/StegExpose.jar