#!/bin/bash
cd $(dirname "$0")

#
# Installer for debian astroberry 2.0.4
# (c) 2021 mworion
#

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
echo
echo "    █████╗ ███████╗████████╗██████╗  ██████╗ "
echo "   ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗"
echo "   ███████║███████╗   ██║   ██████╔╝██║   ██║"
echo "   ██╔══██║╚════██║   ██║   ██╔══██╗██║   ██║"
echo "   ██║  ██║███████║   ██║   ██║  ██║╚██████╔╝"
echo "   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ "
echo "                                             "
echo "   ██████╗ ███████╗██████╗ ██████╗ ██╗   ██╗ "
echo "   ██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗ ██╔╝ "
echo "   ██████╔╝█████╗  ██████╔╝██████╔╝ ╚████╔╝  "
echo "   ██╔══██╗██╔══╝  ██╔══██╗██╔══██╗  ╚██╔╝   "
echo "   ██████╔╝███████╗██║  ██║██║  ██║   ██║    "
echo "   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    "
echo
echo install script version 2.2 astroberry
echo --------------------------------------------------------

echo install script version 2.2 astroberry > install.log 2>&1

echo
echo --------------------------------------------------------
echo installing pyqt5 packages on system
echo --------------------------------------------------------

sudo apt-get install python3-pyqt5 >> install.log 2>&1

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
  exit
fi

echo installing wheel >> install.log 2>&1
python3 -m pip install pip --upgrade >> install.log 2>&1

echo
echo --------------------------------------------------------
echo update tools
echo --------------------------------------------------------

echo checking system packages, should be no mw4 in >> install.log  2>&1
python3 -m pip list >> install.log 2>&1

python3 -m pip install pip --upgrade >> install.log 2>&1
python3 -m pip install setuptools --upgrade >> install.log 2>&1
python3 -m pip install wheel --upgrade >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installing mountwizzard4
echo --------------------------------------------------------

python3 -m pip install mountwizzard4 >> install.log 2>&1

echo
echo --------------------------------------------------------
echo installed mountwizzard4 successfully
echo for details see install.log
echo --------------------------------------------------------

echo MountWizzard4 successfully installed >> install.log 2>&1


