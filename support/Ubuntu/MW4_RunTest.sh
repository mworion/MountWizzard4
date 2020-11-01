#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu / Ubuntu Mate
# (c) 2020 mworion
#

# starting a new install log
echo .
echo ---------------------------------------------
echo Checking installed python version
echo ---------------------------------------------
echo .

echo Checking environment and start script > install.log

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

export QT_SCALE_FACTOR=1
export QT_FONT_DPI=96

source ./venv/bin/activate

startCommand="python ./venv/lib/$P_VER/site-packages/mw4/loader.py test"
$($startCommand)
deactivate
