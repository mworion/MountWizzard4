#!/bin/bash
cd $(dirname "$0")

#
# Installer for osx
# (c) 2020 mworion
#

echo
echo ---------------------------------------------
echo
echo "    M   M  W   W   W    4"
echo "   MM  MM  W  WW  W    4"
echo "  M M M M  W W W W    4  4"
echo " M  MM  M  WW  WW    444444"
echo "M   M   M  W   W       4"
echo
echo ---------------------------------------------
echo install script version 0.2
echo ---------------------------------------------
echo

echo
echo ---------------------------------------------
echo checking installed python version
echo ---------------------------------------------
echo

# starting a new install log
python3 --version > install.log

# changing to the actual directory as working directory

# get version of python3 installation
T=$(python3 --version)

# check which valid version is installed
if [[ $T == *"3.8"* ]]; then
  P_VER="python3.8"

elif [[ $T == *"3.7"* ]]; then
  P_VER="python3.7"

elif [[ $T == *"3.6"* ]]; then
  P_VER="python3.6"
fi

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
echo ---------------------------------------------
echo updating pip installer
echo ---------------------------------------------
echo

python3 -m pip install --upgrade pip --user >> install.log

echo
echo ---------------------------------------------
echo installing $P_VER in virtual environ
echo ---------------------------------------------
echo

COMMAND="python3 -m venv venv >> install.log"
eval ${COMMAND}

# check if virtualenv is available
if [ ! -f ./venv/bin/activate ]; then
  echo
  echo ---------------------------------------------
  echo no valid virtual environment installed
  echo please check the install.log for errors
  echo ---------------------------------------------
  echo

  exit
fi

echo
echo ---------------------------------------------
echo installing mountwizzard4 - takes some time
echo ---------------------------------------------
echo

source ./venv/bin/activate >> install.log
python -m pip install pip --upgrade >> install.log
python -m pip install setuptools --upgrade >> install.log
python -m pip install wheel --upgrade >> install.log
pip install mountwizzard4.tar.gz >> install.log
deactivate

echo
echo ---------------------------------------------
echo installed mountwizzard4 successfully
echo for details see install.log
echo ---------------------------------------------
echo

echo MountWizzard4 successfully installed >> install.log