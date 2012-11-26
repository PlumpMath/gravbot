wget https://launchpad.net/~panda3d/+archive/ppa/+files/libsquish-dev_1.10-1~precise1_amd64.deb
sudo dpkg -i libsquish-dev_1.10-1~precise1_amd64.deb

sudo apt-get install -y libboost1.48-dev bison git libavcodec-dev libavformat-dev libavutil-dev libfreetype6-dev libopencv-contrib-dev libhighgui-dev libcv-dev libxxf86dga-dev libosmesa6-dev libopenal-dev libgles1-mesa-dev libgles2-mesa-dev libgl1-mesa-dev libgl1-mesa-glx flex

sudo apt-get install mesa-utils mesa-common-dev # not sure if needed

# panda source 
wget https://www.panda3d.org/download/panda3d-1.8.0/panda3d-1.8.0.tar.gz
tar -zxvf panda3d-1.8.0.tar.gz 

# bullet source
wget http://bullet.googlecode.com/files/bullet-2.80-rev2531.zip
unzip bullet-2.80-rev2531.zip 
cd bullet-2.80-rev2531
cmake -DCMAKE_CXX_FLAGS="-fPIC" -DCMAKE_INSTALL_PREFIX=../panda3d-1.8.0/thirdparty/linux-libs-x64/bullet -DINCLUDE_INSTALL_DIR=../panda3d-1.8.0/thirdparty/linux-libs-x64/bullet/include/
make
make install

#librocket doesn't seem to have a direct link so we'll clone :(
git clone https://github.com/lloydw/libRocket.git
cd libRocket/Build
cmake -DCMAKE_INSTALL_PREFIX=../../panda3d-1.8.0/thirdparty/linux-libs-x64/rocket -DBUILD_PYTHON_BINDINGS=on
make
make install

./makepanda/makepanda.py --installer --everything --no-fftw --threads 4 
