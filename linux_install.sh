export AUDIODEV=null
CMAKE_DIR="${TRAVIS_BUILD_DIR}/cmk"
mkdir ${CMAKE_DIR} && cd ${CMAKE_DIR}
wget --no-check-certificate https://github.com/Kitware/CMake/releases/download/v3.17.3/cmake-3.17.3-Linux-x86_64.tar.gz
tar -xvf cmake-3.17.3-Linux-x86_64.tar.gz > /dev/null
mv cmake-3.17.3-Linux-x86_64 cmake-install
PATH=${CMAKE_DIR}/cmake-install:${CMAKE_DIR}/cmake-install/bin:$PATH
cd ${TRAVIS_BUILD_DIR}
sudo apt-get install swig
sudo apt install freeglut3-dev
sudo apt-get install unrar