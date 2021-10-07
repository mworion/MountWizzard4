#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu 18.04 for aarch64
# (c) 2021 mworion
#

echo --------------------------------------------------------
echo
echo "         ███╗   ███╗██╗    ██╗██╗  ██╗"
echo "         ████╗ ████║██║    ██║██║  ██║"
echo "         ██╔████╔██║██║ █╗ ██║███████║"
echo "         ██║╚██╔╝██║██║███╗██║╚════██║"
echo "         ██║ ╚═╝ ██║╚███╔███╔╝     ██║"
echo "         ╚═╝     ╚═╝ ╚══╝╚══╝      ╚═╝"
echo
echo --------------------------------------------------------
echo install script version 2.1 aarch64
echo --------------------------------------------------------

echo install script version 2.1 aarch64 > install.log 2>&1

echo
echo --------------------------------------------------------
echo checking installed python version
echo --------------------------------------------------------


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

echo variable P_VER has value of $P_VER >> install.log 2>&1

if [ "${P_VER:0:6}" == "python" ]; then
  echo
  echo --------------------------------------------------------
  echo python version ok
  echo --------------------------------------------------------
else
  echo
  echo --------------------------------------------------------
  echo no valid python version installed
  echo --------------------------------------------------------
  exit
fi

echo installing wheel >> install.log 2>&1
python3 -m pip install pip --upgrade >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installing $P_VER in virtual environ
echo --------------------------------------------------------

echo Installing $P_VER in virtual environ >> install.log 2>&1

{
python3 -m venv venv >> install.log 2>&1
} || {
  echo
  echo --------------------------------------------------------
  echo no valid virtual environment installed
  echo please check the install.log for errors
  echo install virtualenv with
  echo sudo apt-get install python3-virtualenv
  echo --------------------------------------------------------
  
  echo no valid virtual environment installed >> install.log 2>&1
  exit
}

echo
echo --------------------------------------------------------
echo installing application - takes some time
echo --------------------------------------------------------

echo
echo --------------------------------------------------------
echo start virtualenv and update tools
echo --------------------------------------------------------

source venv/bin/activate >> install.log 2>&1
pip install pip --upgrade >> install.log 2>&1
pip install setuptools --upgrade >> install.log 2>&1
pip install wheel --upgrade >> install.log 2>&1

GITHUB="https://github.com/mworion/MountWizzard4/tree/master/support"
UBUNTU="/2.0/wheels/ubuntu18.04"

echo
echo --------------------------------------------------------
echo installing precompiled packages
echo --------------------------------------------------------

pip install numpy==1.21.2 --find-links "${GITHUB}${UBUNTU}" >> install.log 2>&1
pip install pyerfa==2.0.0 --find-links "${GITHUB}${UBUNTU}" >> install.log 2>&1
pip install sgp4==2.20 --find-links "${GITHUB}${UBUNTU}" >> install.log 2>&1
pip install sep==1.2.0 --find-links "${GITHUB}${UBUNTU}" >> install.log 2>&1
pip install PyQt5-sip==12.8.1 --find-links "${GITHUB}${UBUNTU}" >> install.log 2>&1
pip install PyQt5==5.15.4 --find-links "${GITHUB}${UBUNTU}" >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installing mountwizzard4
echo --------------------------------------------------------

pip install mountwizzard4 >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installed mountwizzard4 successfully
echo for details see install.log
echo --------------------------------------------------------

echo MountWizzard4 successfully installed >> install.log 2>&1


