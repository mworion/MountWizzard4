#!/bin/bash
cd $(dirname "$0")

#
# installer for Ubuntu
# (c) 2020 mworion
#

echo
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
echo install script version 2.2
echo --------------------------------------------------------

echo install script version 2.2 > install.log 2>&1

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
  echo no valid python version installed >> install.log 2>&1
  exit
fi

echo
echo --------------------------------------------------------
echo updating pip installer
echo --------------------------------------------------------

python3 -m pip install pip --upgrade >> install.log 2>&1

echo
echo --------------------------------------------------------
echo Installing $P_VER in virtual environ
echo --------------------------------------------------------

echo Installing $P_VER in virtual environ >> install.log 2>&1
python3 -m venv venv >> install.log 2>&1

if [ ! -f ./venv/bin/activate ]; then
  echo
  echo ---------------------------------------------
  echo no valid virtual environment installed
  echo please check the install.log for errors
  echo ---------------------------------------------

  echo no valid virtual environment installed >> install.log 2>&1
  exit
fi

echo
echo --------------------------------------------------------
echo installing mountwizzard4 - takes some time
echo --------------------------------------------------------

echo checking system packages, should be no mw4 in >> install.log  2>&1
python -p pip list >> install.log 2>&1

source ./venv/bin/activate venv >> install.log  2>&1
python -m pip install pip --upgrade >> install.log 2>&1
python -m pip install setuptools --upgrade >> install.log 2>&1
python -m pip install wheel --upgrade >> install.log 2>&1
python -m pip install mountwizzard4.tar.gz >> install.log 2>&1

echo checking venv packages, mw4 should be present >> install.log  2>&1
python -p pip list >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installed mountwizzard4 successfully
echo for details see install.log
echo --------------------------------------------------------

echo MountWizzard4 successfully installed >> install.log 2>&1


