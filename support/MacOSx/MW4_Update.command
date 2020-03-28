#!/bin/zsh

# changing to the actual directory as working directory
cd $(dirname "$0")

# get version of python3 installation
T=$(python3 --version)

# check which valid version is installed
if [[ $T == *"3.8"* ]]; then
  P_VER="python3.8"

elif [[ $T == *"3.7"* ]]; then
  P_VER="python3.7"

elif [[ $T == *"3.6"* ]]; then
  P_VER="python3.6"

else
  echo ""
  echo "----------------------------------------"
  echo "No valid python version installed"
  echo "----------------------------------------"
  echo ""
  exit

fi

# check if virtualenv is available
if [ ! -f ./venv/bin/activate ]; then
  echo ""
  echo "----------------------------------------"
  echo "No valid virtual environment installed"
  echo "Please run MW4_Install.command first"
  echo "----------------------------------------"
  echo ""
  exit

fi

# now enable the virtual environment
source ./venv/bin/activate > /dev/null

# now updating mountwizzard4
pip install mountwizzard4 --upgrade --no-cache-dir > update.log

# closing virtual environment
deactivate

echo ""
echo "Updated mountwizzard4 successfully"
echo "For details see update.log"
echo "----------------------------------------"
echo ""