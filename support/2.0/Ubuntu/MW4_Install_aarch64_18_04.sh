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
echo install script version 2.0 aarch64
echo --------------------------------------------------------

echo install script version 2.0 aarch64 > install.log 2>&1

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
virtualenv venv >> install.log 2>&1
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

source ./venv/bin/activate venv >> install.log 2>&1
pip install pip --upgrade >> install.log 2>&1
pip install setuptools --upgrade >> install.log 2>&1
pip install wheel --upgrade >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installing precompiled packages
echo --------------------------------------------------------

WHL="https://github.com/mworion/mountwizzard4/raw/master/support/wheels/ubuntu18.04"
ARCH="_aarch64.whl"
PY37="-cp37-37m-"
PY38="-cp38-38-"
PY39="-cp39-39-"

if [ "${P_VER:0:9}" == "python3.9" ]; then
  PY=$"{PY39}"
elif [ "${P_VER:0:9}" == "python3.8" ]; then
  PY=$"{PY38}"
elif [ "${P_VER:0:9}" == "python3.7" ]; then
  PY=$"{PY37}"
fi
  
pip install "${WHL}"/pyerfa-2.0.0"${PY}"linux"${ARCH}" >> install.log 2>&1
pip install "${WHL}"/astropy-4.2.1"${PY}"linux"${ARCH}" >> install.log 2>&1
pip install "${WHL}"/sep-1.2.0"${PY}"linux"${ARCH}" >> install.log 2>&1
pip install "${WHL}"/sgp4-2.19"${PY}"manylinux2014"${ARCH}" >> install.log 2>&1
pip install "${WHL}"/PyQt5_sip-12.8.1"${PY}"linux"${ARCH}" >> install.log 2>&1
pip install "${WHL}"/PyQt5-5.15.4-cp36.cp37.cp38.cp39-abi3-manylinux2014"${ARCH}" >> install.log 2>&1

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


