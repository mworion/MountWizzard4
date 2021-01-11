#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu Mate
# (c) 2020 mworion
#

echo
echo ---------------------------------------------
echo
echo " ███╗   ███╗ ██╗    ██╗ ██╗  ██╗"
echo " ████╗ ████║ ██║    ██║ ██║  ██║"
echo " ██╔████╔██║ ██║ █╗ ██║ ███████║"
echo " ██║╚██╔╝██║ ██║███╗██║ ╚════██║"
echo " ██║ ╚═╝ ██║ ╚███╔███╔╝      ██║"
echo " ╚═╝     ╚═╝  ╚══╝╚══╝       ╚═╝"
echo
echo ---------------------------------------------
echo install script version 0.3
echo ---------------------------------------------
echo install script version 0.3 > install.log 2>&1
echo

echo
echo ---------------------------------------------
echo checking installed python version
echo ---------------------------------------------
echo

echo checking environment and start script >> install.log 2>&1

T=`python3 --version`
P_VER=""

if [ "${T:0:10}" == "Python 3.9" ]; then
  P_VER="python3.9"
elif [ "${T:0:10}" == "Python 3.8" ]; then
  P_VER="python3.8"
elif [ "${T:0:10}" == "Python 3.7" ]; then
  P_VER="python3.7"
fi

echo variable P_VER has value of $P_VER

if [ "${P_VER:0:6}" == "python" ]; then
  echo
  echo ---------------------------------------------
  echo python version ok
  echo ---------------------------------------------
  echo
else
  echo
  echo ---------------------------------------------
  echo no valid python version installed
  echo ---------------------------------------------
  echo
  exit
fi

echo
echo installing wheel >> install.log 2>&1
python3 -m pip install pip --upgrade >> install.log 2>&1

echo
echo ---------------------------------------------
echo installing $P_VER in virtual environ
echo ---------------------------------------------
echo

echo Installing $P_VER in virtual environ >> install.log 2>&1

{
virtualenv venv >> install.log 2>&1
} || {
  echo
  echo ---------------------------------------------
  echo no valid virtual environment installed
  echo please check the install.log for errors
  echo install virtualenv with
  echo sudo apt-get install python3-virtualenv
  echo ---------------------------------------------
  echo
  echo no valid virtual environment installed >> install.log 2>&1
  exit
}

echo
echo ---------------------------------------------
echo Installing mountwizzard4 - takes some time
echo ---------------------------------------------
echo

source ./venv/bin/activate venv >> install.log 2>&1
pip install pip --upgrade >> install.log 2>&1
pip install setuptools --upgrade >> install.log 2>&1
pip install wheel --upgrade >> install.log 2>&1
pip install pyerfa-1.7.1.1-cp38-cp38-linux_aarch64.whl >> install.log 2>&1
pip install astropy-4.2-cp38-cp38-linux_aarch64.whl >> install.log 2>&1
pip install matplotlib-3.3.3-cp38-cp38-linux_aarch64.whl >> install.log 2>&1
pip install photutils-1.0.1-cp38-cp38-linux_aarch64.whl >> install.log 2>&1
pip install PyQt5_sip-12.8.1-cp38-cp38-linux_aarch64.whl >> install.log 2>&1
pip install PyQt5-5.15.2-cp35.cp36.cp37.cp38.cp39-abi3-manylinux2014_aarch64.whl >> install.log 2>&1
pip install mountwizzard4 >> install.log 2>&1

echo
echo ---------------------------------------------
echo installed mountwizzard4 successfully
echo for details see install.log
echo ---------------------------------------------
echo

echo MountWizzard4 successfully installed >> install.log 2>&1


