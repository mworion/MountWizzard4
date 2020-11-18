#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu / Ubuntu Mate
# (c) 2020 mworion
#

echo
echo ---------------------------------------------
echo Script version 0.2
echo ---------------------------------------------
echo

echo
echo ---------------------------------------------
echo Checking installed python version
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

echo
echo ---------------------------------------------
echo Updating MW4 to newest official release
echo ---------------------------------------------
echo

source ./venv/bin/activate
pip install mountwizzard4 --upgrade --no-cache-dir >> update.log
deactivate
