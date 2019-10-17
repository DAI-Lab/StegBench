FROM debian:stretch-20170907

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y apt-utils \
                       forensics-all \
                       foremost \
                       binwalk \
                       exiftool \
                       outguess \
                       pngtools \
                       pngcheck \
                       stegosuite \
                       git \
                       hexedit \
                       python3-pip \
                       python-pip \
                       autotools-dev \
                       automake \
                       libevent-dev \
                       bsdmainutils \
                       ffmpeg \
                       crunch \
                       cewl \
                       sonic-visualiser \
                       xxd \
                       atomicparsley && \
    pip3 install python-magic && \
    pip3 install setuptools && \
    pip install tqdm

COPY install /tmp/install
RUN chmod a+x /tmp/install/*.sh && \
    for i in /tmp/install/*.sh;do echo $i && $i;done && \
    rm -rf /tmp/install

COPY install_dev /tmp/install
RUN find /tmp/install -name '*.sh' -exec chmod a+x {} + && \
    for f in $(ls /tmp/install/* | sort );do /bin/sh $f;done && \
    rm -rf /tmp/install
    
COPY . /tmp/stegtest
WORKDIR /tmp/stegtest
RUN sudo pip3 install -e .

WORKDIR /data