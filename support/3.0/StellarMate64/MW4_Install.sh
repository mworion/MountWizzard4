#!/bin/bash
cd $(dirname "$0")

#
# installer for stellarmate 1.7 for aarch64
# (c) 2021 mworion
#

echo
echo --------------------------------------------------------
echo
echo "             #     # #     # #                           "
echo "             ##   ## #  #  # #    #                      "
echo "             # # # # #  #  # #    #                      "
echo "             #  #  # #  #  # #    #                      "
echo "             #     # #  #  # #######                     "
echo "             #     # #  #  #      #                      "
echo "             #     #  ## ##       #                      "
echo "                                                         "
echo "  #####  ####### ####### #       #          #    ######  "
echo " #     #    #    #       #       #         # #   #     # "
echo " #          #    #       #       #        #   #  #     # "
echo "  #####     #    #####   #       #       #     # ######  "
echo "       #    #    #       #       #       ####### #   #   "
echo " #     #    #    #       #       #       #     # #    #  "
echo "  #####     #    ####### ####### ####### #     # #     # "
echo "                                                         "
echo "          #     #    #    ####### #######                "
echo "          ##   ##   # #      #    #                      "
echo "          # # # #  #   #     #    #                      "
echo "          #  #  # #     #    #    #####                  "
echo "          #     # #######    #    #                      "
echo "          #     # #     #    #    #                      "
echo "          #     # #     #    #    #######                "
echo
echo --------------------------------------------------------
echo install script version 3.0
echo --------------------------------------------------------

echo install script version 3.0 stellarmate 1.7 > install.log 2>&1

echo
echo --------------------------------------------------------
echo installing pyqt5 packages on system
echo --------------------------------------------------------

sudo apt-get install -y python3-pyqt5 >> install.log 2>&1

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
elif [ "${T:0:11}" == "Python 3.10" ]; then
  P_VER="python3.10"
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
python3 -m venv venv >> install.log 2>&1
} || {
  echo
  echo --------------------------------------------------------
  echo no valid virtual environment installed
  echo please check the install.log for errors
  echo install virtualenv with
  echo sudo apt-get install python3-virtualenv
  echo --------------------------------------------------------
  echo
  echo no valid virtual environment installed >> install.log 2>&1
  exit
}

echo
echo --------------------------------------------------------
echo start virtualenv and update tools
echo --------------------------------------------------------

echo checking system packages, should be no mw4 in >> install.log  2>&1
python -p pip list >> install.log 2>&1

source venv/bin/activate >> install.log 2>&1
pip install pip --upgrade >> install.log 2>&1
pip install setuptools --upgrade >> install.log 2>&1
pip install wheel --upgrade >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installing precompiled packages
echo --------------------------------------------------------

GITHUB="https://github.com/mworion/MountWizzard4/blob/master"
WHEELS="/support/wheels/ubuntu20.04"
PRE="${GITHUB}${WHEELS}"
POST="_aarch64.whl?raw=true"

PY37="-cp37-cp37m-"
PY38="-cp38-cp38-"
PY39="-cp39-cp39-"
PY310="-cp310-cp310-"

if [ "${P_VER:0:9}" == "python3.9" ]; then
  PY="${PY39}"
elif [ "${P_VER:0:9}" == "python3.8" ]; then
  PY="${PY38}"
elif [ "${P_VER:0:9}" == "python3.7" ]; then
  PY="${PY37}"
elif [ "${P_VER:0:10}" == "python3.10" ]; then
  PY="${PY310}"
fi

pip install "${PRE}"/sgp4-2.21"${PY}"linux"${POST}" >> install.log 2>&1
pip install "${PRE}"/PyQt5_sip-12.10.1"${PY}"linux"${POST}" >> install.log 2>&1
pip install "${PRE}"/PyQt5-5.15.6-cp37-abi3-manylinux1"${POST}" >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installing mountwizzard4
echo --------------------------------------------------------

pip install mountwizzard4 >> install.log 2>&1

echo checking venv packages, mw4 should be present >> install.log  2>&1
pip list >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installed mountwizzard4 successfully
echo for details see install.log
echo --------------------------------------------------------

echo MountWizzard4 successfully installed >> install.log 2>&1


