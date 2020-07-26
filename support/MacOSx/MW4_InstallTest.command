#########################
# Installer for OSx
# (c) 2020 mworion
#########################

#!/bin/zsh

# starting a new install log
python3 --version > install.log

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

# updating pip3
echo ""
echo "----------------------------------------"
echo "Updating pip installer"

python3 -m pip install --upgrade pip >> install.log

# now starting to install all things
echo ""
echo "----------------------------------------"
echo "Installing $P_VER in virtual environ "

# check if virtualenv needs to be installed
if ! type "virtualenv" > /dev/null; then
  echo "Need to install virtualenv first "

  pip3 install virtualenv >> install.log

fi

# running the virtual environment installation
COMMAND="virtualenv venv -p $P_VER >> install.log"
eval ${COMMAND}

# check if virtualenv is available
if [ ! -f ./venv/bin/activate ]; then
  echo ""
  echo "----------------------------------------"
  echo "No valid virtual environment installed"
  echo "Please check the install.log for errors"
  echo "----------------------------------------"
  echo ""
  exit

fi

# now enable the virtual environment
source ./venv/bin/activate >> install.log

#  install mountwizzard4
echo "Installing mountwizzard4 - take a minute"

pip install mountwizzard4.tar.gz >> install.log

# closing virtual environment
deactivate

echo ""
echo "Installed mountwizzard4 successfully"
echo "For details see install.log"
echo "----------------------------------------"
echo ""