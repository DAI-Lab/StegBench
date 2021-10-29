starting_dir=$(pwd)

mkdir utils

cd $starting_dir/utils
git clone https://github.com/DominicBreuker/stego-toolkit.git
cd stego-toolkit
bash bin/build.sh

cd $starting_dir/utils
git clone https://github.com/daniellerch/aletheia
cd aletheia
git checkout v0.1
pip3 install -r requirements.txt
#sudo apt-get install -y octave octave-image octave-signal
#sudo apt-get install -y liboctave-dev imagemagick

cd $starting_dir/utils/aletheia/external/jpeg_toolbox
make

cd $starting_dir/utils/aletheia/external/maxSRM
make

cd $starting_dir/utils/
git clone git@github.com:DAI-Lab/SteganoGAN.git
cd SteganoGAN
make install

cd $starting_dir/utils/
git clone git@github.com:DAI-Lab/StegDetect.git
cd StegDetect
make install

cd $starting_dir/utils/
git clone https://github.com/b3dk7/StegExpose.git
