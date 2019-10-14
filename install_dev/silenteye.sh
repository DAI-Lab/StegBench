#!/bin/bash

set -e

# Download

wget -O /usr/bin/silenteye.deb https://sourceforge.net/projects/silenteye/files/Application/0.4/silenteye-0.4.0-i386.deb/download
chmod +x /usr/bin/silenteye.deb

##NEED TO BE FIGURED OUT

# dpkg --configure -a
# apt install -f 
# apt-get update
# apt-get install -y libqtgui4
# apt-get install -y libqca2
# # apt-get install -y libqtmultimediakit1
# sudo dpkg -i /usr/bin/silenteye.deb

# set -e

# apt-get install -y g++ libfontconfig1-dev libfreetype6-dev libx11-dev libxcursor-dev libxext-dev libxfixes-dev libxft-dev libxi-dev libxrandr-dev libxrender-dev libssl-dev

# wget http://download.qt.io/official_releases/qt/4.8/4.8.7/qt-everywhere-opensource-src-4.8.7.tar.gz
# tar -zxvf qt-everywhere-opensource-src-4.8.7.tar.gz
# cd qt-everywhere-opensource-src-4.8.7
# ./configure -release -nomake examples -nomake demos -no-qt3support -no-scripttools -no-opengl -no-webkit -no-phonon -no-sql-sqlite -gtkstyle -opensource -prefix /usr/local/Qt-4.8.7-release
# make
# make install

# cd ..
# rm qt-everywhere-opensource-src-4.8.7.tar.gz
# rm qt-everywhere-opensource-src-4

# wget http://delta.affinix.com/download/qca/2.0/qca-2.0.3.tar.bz2
# bunzip2 qca-2.0.3.tar.bz2 && tar -xvf qca-2.0.3.tar
# cd qca-2.0.3
# patch src/botantools/botan/botan/secmem.h fix_build_gcc4.7.diff
# ./configure --qtdir=/usr/local/Qt-4.8.7-release/
# make
# make install

# cd ..
# rm qca-2.0.3



# wget http://delta.affinix.com/download/qca/2.0/plugins/qca-ossl-2.0.0-beta3.tar.bz2
# bunzip2 qca-ossl-2.0.0-beta3.tar.bz2 && tar -xvf qca-ossl-2.0.0-beta3.tar
# cd qca-ossl-2.0.0-beta3
# patch qca-ossl.cpp < detect_ssl2_available.diff
# patch qca-ossl.cpp < detect_md2_available.diff
# ./configure --qtdir=/usr/local/Qt-4.8.7-release/
# make
# make install
