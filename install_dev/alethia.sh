#!/bin/bash

set -e

git clone https://github.com/daniellerch/aletheia.git /tmp/alethia
cd /tmp/alethia
sudo pip3 install -r requirements.txt 
sudo apt-get install -y octave octave-image octave-signal
sudo apt-get install -y liboctave-dev imagemagick

cd external/jpeg_toolbox
make
cd ..

cd maxSRM
make
cd ..
cd .. 
cd ..

mv aletheia /opt/

#NEED TO FIGURE OUT HOW TO COMPLETELY INSTALL IT
#MIGHT NEED TO MAKE A FORK OF ALETHIA FOR OUR PURPOSES