#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu / Ubuntu Mate
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
echo update script version 0.2
echo ---------------------------------------------
echo

echo
echo ---------------------------------------------
echo checking installed python version
echo ---------------------------------------------
echo

echo Checking environment and start script > update.log

T=`python3 --version`
P_VER=""

if [ "${T:0:10}" == "Python 3.8" ]; then
  P_VER="python3.8"
elif [ "${T:0:10}" == "Python 3.7" ]; then
  P_VER="python3.7"
elif [ "${T:0:10}" == "Python 3.6" ]; then
  P_VER="python3.6"
fi

echo variable P_VER has value of $P_VER >> update.log

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
echo updating MW4 to newest official release
echo ---------------------------------------------
echo

source ./venv/bin/activate
pip install mountwizzard4 --upgrade --no-cache-dir >> update.log
deactivate

echo
echo ----------------------------------------
echo updated mountwizzard4 successfully
echo for details see update.log
echo ----------------------------------------
echo