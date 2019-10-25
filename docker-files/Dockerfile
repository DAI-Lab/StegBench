FROM debian:stretch-20170907

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

#!/bin/bash

set -e

# Download
RUN wget -O /usr/bin/jsteg https://github.com/lukechampine/jsteg/releases/download/v0.1.0/jsteg-linux-amd64
RUN chmod +x /usr/bin/jsteg

RUN wget -O /usr/bin/slink https://github.com/lukechampine/jsteg/releases/download/v0.2.0/slink-linux-amd64
RUN chmod +x /usr/bin/slink

RUN ??

[CMD]