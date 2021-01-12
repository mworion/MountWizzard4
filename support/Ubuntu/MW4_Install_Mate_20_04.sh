#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu Mate 20.04 for aarch64 (RPi4)
# (c) 2021 mworion
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
echo install script version 0.4
echo install for aarch64 and ubuntu 20.04
echo ---------------------------------------------
echo install script version 0.4 > install.log 2>&1
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
echo installing application - takes some time
echo ---------------------------------------------
echo

echo
echo ---------------------------------------------
echo start virtualenv and update tools
echo ---------------------------------------------
echo

source ./venv/bin/activate venv >> install.log 2>&1
pip install pip --upgrade >> install.log 2>&1
pip install setuptools --upgrade >> install.log 2>&1
pip install wheel --upgrade >> install.log 2>&1

echo
echo ---------------------------------------------
echo installing precompiled packages
echo ---------------------------------------------
echo

WHL="https://github.com/mworion/mountwizzard4/raw/master/support/wheels/ubuntu20.04"
ARCH="_aarch64.whl"

if [ "${P_VER:0:9}" == "python3.9" ]; then
  pip install "${WHL}"/numpy-1.19.3-cp39-cp39-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/kiwisolver-1.3.1-cp39-cp39-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/pyerfa-1.7.1.1-cp39-cp39-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/Pillow-8.1.0-cp39-cp39-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/matplotlib-3.3.3-cp39-cp39-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/astropy-4.2-cp39-cp39-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/pybase64-1.1.1-cp39-cp39-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/scipy-1.5.4-cp39-cp39-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/sep-1.1.1-cp39-cp39-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/sgp4-2.15-cp39-cp39-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/PyQt5_sip-12.8.1-cp39-cp39-linux"${ARCH}" >> install.log 2>&1

elif [ "${P_VER:0:9}" == "python3.8" ]; then
  pip install "${WHL}"/numpy-1.19.3-cp38-cp38-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/kiwisolver-1.3.1-cp38-cp38-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/pyerfa-1.7.1.1-cp38-cp38-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/Pillow-8.1.0-cp38-cp38-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/matplotlib-3.3.3-cp38-cp38-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/astropy-4.2-cp38-cp38-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/pybase64-1.1.1-cp38-cp38-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/scipy-1.5.4-cp38-cp38-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/sep-1.1.1-cp38-cp38-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/sgp4-2.15-cp38-cp38-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/PyQt5_sip-12.8.1-cp38-cp38-linux"${ARCH}" >> install.log 2>&1

elif [ "${P_VER:0:9}" == "python3.7" ]; then
  pip install "${WHL}"/numpy-1.19.3-cp37-cp37-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/kiwisolver-1.3.1-cp37-cp37-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/pyerfa-1.7.1.1-cp37-cp37-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/Pillow-8.1.0-cp37-cp37-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/matplotlib-3.3.3-cp37-cp37-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/astropy-4.2-cp37-cp37-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/pybase64-1.1.1-cp37-cp37-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/scipy-1.5.4-cp37-cp37-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/sep-1.1.1-cp37-cp37-linux"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/sgp4-2.15-cp37-cp37-manylinux2014"${ARCH}" >> install.log 2>&1
  pip install "${WHL}"/PyQt5_sip-12.8.1-cp37-cp37-linux"${ARCH}" >> install.log 2>&1
fi

pip install "${WHL}"/PyQt5-5.15.2-cp36.cp37.cp38.cp39-abi3-manylinux2014"${ARCH}" >> install.log 2>&1

echo
echo ---------------------------------------------
echo installing mountwizzard4
echo ---------------------------------------------
echo

pip install mountwizzard4 >> install.log 2>&1

echo
echo ---------------------------------------------
echo installed mountwizzard4 successfully
echo for details see install.log
echo ---------------------------------------------
echo

echo MountWizzard4 successfully installed >> install.log 2>&1


