#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu
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
echo Script version 0.2
echo ---------------------------------------------
echo

echo
echo ---------------------------------------------
echo Checking installed python version
echo ---------------------------------------------
echo

echo checking environment and start script > install.log

T=`python3 --version`
P_VER=""

if [ "${T:0:10}" == "Python 3.8" ]; then
  P_VER="python3.8"
elif [ "${T:0:10}" == "Python 3.7" ]; then
  P_VER="python3.7"
elif [ "${T:0:10}" == "Python 3.6" ]; then
  P_VER="python3.6"
fi

echo variable P_VER has value of $P_VER >> install.log

if [ "${P_VER:0:6}" == "python" ]; then
  echo
  echo ---------------------------------------------
  echo Python version ok
  echo ---------------------------------------------
  echo
else
  echo
  echo ---------------------------------------------
  echo No valid python version installed
  echo ---------------------------------------------
  echo

  exit
fi

echo  >> install.log
echo installing wheel >> install.log
python3 -m pip install pip --upgrade >> install.log

echo
echo ---------------------------------------------
echo Installing $P_VER in virtual environ
echo ---------------------------------------------
echo

echo  >> install.log
echo Installing $P_VER in virtual environ >> install.log

{
virtualenv venv >> install.log
} || {
  echo
  echo ---------------------------------------------
  echo No valid virtual environment installed
  echo Please check the install.log for errors
  echo install virtualenv with
  echo sudo apt-get install python3-virtualenv
  echo ---------------------------------------------
  echo
  exit
}

echo
echo ---------------------------------------------
echo Installing mountwizzard4 - takes some time
echo ---------------------------------------------
echo

echo  >> install.log

source ./venv/bin/activate
python -m pip install pip --upgrade >> install.log
python -m pip install setuptools --upgrade >> install.log
python -m pip install wheel --upgrade >> install.log
python -m pip install mountwizzard4.tar.gz >> install.log

echo
echo ---------------------------------------------
echo Installed mountwizzard4 successfully
echo For details see install.log
echo ---------------------------------------------
echo

echo MountWizzard4 successfully installed >> install.log


