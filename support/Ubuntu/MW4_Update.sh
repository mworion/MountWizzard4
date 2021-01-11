#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu / Ubuntu Mate
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
echo update script version 0.4
echo ---------------------------------------------
echo update script version 0.4 > update.log 2>&1
echo

if [ ! -f ./venv/bin/activate ]; then
  echo
  echo ----------------------------------------
  echo no valid virtual environment installed
  echo please run MW4_Install.command first
  echo ----------------------------------------
  echo
  exit
fi
echo
echo ---------------------------------------------
echo checking installed python version
echo ---------------------------------------------
echo

echo Checking environment and start script >> update.log 2>&1

T=`python3 --version`
P_VER=""

if [ "${T:0:10}" == "Python 3.9" ]; then
  P_VER="python3.9"
elif [ "${T:0:10}" == "Python 3.8" ]; then
  P_VER="python3.8"
elif [ "${T:0:10}" == "Python 3.7" ]; then
  P_VER="python3.7"
fi

echo variable P_VER has value of $P_VER >> update.log 2>&1

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
  echo no valid python version installed >> update.log 2>&1
  exit
fi

echo
echo ---------------------------------------------
echo updating MW4 to newest official release
echo ---------------------------------------------
echo

source ./venv/bin/activate venv >> update.log 2>&1
pip install mountwizzard4 --upgrade --no-cache-dir >> update.log 2>&1
deactivate >> update.log 2>&1

echo
echo ----------------------------------------
echo updated mountwizzard4 successfully
echo for details see update.log
echo ----------------------------------------
echo