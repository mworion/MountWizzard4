#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu Mate
# (c) 2020 mworion
#

# starting a new install log
echo .
echo ---------------------------------------------
echo Checking installed python version
echo ---------------------------------------------
echo .

echo checking environment and start script

T=`python3 --version`
P_VER=""

if [ "${T:0:10}" == "Python 3.8" ]; then
  P_VER="python3.8"
elif [ "${T:0:10}" == "Python 3.7" ]; then
  P_VER="python3.7"
elif [ "${T:0:10}" == "Python 3.6" ]; then
  P_VER="python3.6"
fi

echo variable P_VER has value of $P_VER

if [ "${P_VER:0:6}" == "python" ]; then
  echo .
  echo ---------------------------------------------
  echo Python version ok
  echo ---------------------------------------------
  echo .

else
  echo .
  echo ---------------------------------------------
  echo No valid python version installed
  echo ---------------------------------------------
  echo .
  exit

fi

echo .
echo installing wheel
python3 -m pip install pip --upgrade

echo .
echo ---------------------------------------------
echo Installing $P_VER in virtual environ
echo ---------------------------------------------
echo .

echo .
echo Installing $P_VER in virtual environ

{
virtualenv venv
} || {
  echo .
  echo ---------------------------------------------
  echo No valid virtual environment installed
  echo Please check the install.log for errors
  echo install virtualenv with
  echo sudo apt-get install python3-virtualenv
  echo ---------------------------------------------
  echo .
  exit
}

echo .
echo ---------------------------------------------
echo Installing mountwizzard4 - takes some time
echo ---------------------------------------------
echo .

echo .

source ./venv/bin/activate
pip install pip --upgrade
pip install setuptools --upgrade
pip install wheel --upgrade
pip install numpy==1.19.4
pip install astropy==4.0.3
pip install matplotlib==3.3.2
pip install photutils==1.0.1
pip install mountwizzard4


echo .
echo ---------------------------------------------
echo Installed mountwizzard4 successfully
echo For details see install.log
echo ---------------------------------------------
echo .

echo MountWizzard4 successfully installed


