#!/bin/bash
cd $(dirname "$0")

#
# run script for osx
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
echo run script version 0.2
echo ---------------------------------------------
echo

if [ ! -f ./venv/bin/activate ]; then
  echo
  echo ----------------------------------------
  echo No valid virtual environment installed
  echo Please run MW4_Install.command first
  echo ----------------------------------------
  echo

  exit
fi

export QT_SCALE_FACTOR=1
export QT_FONT_DPI=96

source ./venv/bin/activate

echo
echo ---------------------------------------------
echo Checking installed python version
echo ---------------------------------------------
echo

echo Checking environment and start script > run.log

T=`python3 --version`
P_VER=""

if [ "${T:0:10}" == "Python 3.8" ]; then
  P_VER="python3.8"
elif [ "${T:0:10}" == "Python 3.7" ]; then
  P_VER="python3.7"
elif [ "${T:0:10}" == "Python 3.6" ]; then
  P_VER="python3.6"
fi

echo variable P_VER has value of $P_VER >> run.log

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
  echo Please run MW4_Install.command first
  echo ---------------------------------------------
  echo

  exit
fi

startCommand="python ./venv/lib/$P_VER/site-packages/mw4/loader.py >> run.log"
$($startCommand)
deactivate
