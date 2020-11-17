#!/bin/bash
cd $(dirname "$0")

#
# run script for Ubuntu
# (c) 2020 mworion
#

echo
echo ---------------------------------------------
echo Checking installed python version
echo ---------------------------------------------
echo

echo Checking environment and start script > run.log

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

if [ ! -f ./venv/bin/activate ]; then
  echo
  echo ---------------------------------------------
  echo No valid virtual environment installed
  echo Please run MW4_Install.command first
  echo ---------------------------------------------
  echo
  exit
fi

source ./venv/bin/activate >> run.log
COMMAND="python ./venv/lib/$P_VER/site-packages/mw4/loader.py >> run.log"
eval ${COMMAND}
deactivate
