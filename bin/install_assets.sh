mkdir utils
cd utils

git clone https://github.com/DominicBreuker/stego-toolkit.git
cd stego-toolkit
bash bin/build.sh

cd ..
git clone https://github.com/daniellerch/aletheia
cd aletheia
pip3 install -r requirements.txt 
pip3 install scipy==1.1.0
pip3 install tensorflow==1.10.0
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

pip install steganogan

git clone git@github.com:DAI-Lab/StegDetect.git
cd StegDetect
make install

cd ..

git clone https://github.com/b3dk7/StegExpose.git
