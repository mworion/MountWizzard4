#!/bin/bash
cd $(dirname "$0")

#
# Installer for Ubuntu / Ubuntu Mate
# (c) 2021 mworion
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
echo update script version 2.1 astroberry
echo --------------------------------------------------------

echo update script version 2.1 astroberry > update.log 2>&1

echo
echo --------------------------------------------------------
echo checking installed python version
echo --------------------------------------------------------


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
  echo --------------------------------------------------------
  echo python version ok: ${P_VER}
  echo --------------------------------------------------------
else
  echo
  echo --------------------------------------------------------
  echo no valid python version installed
  echo --------------------------------------------------------

  echo no valid python version installed >> update.log 2>&1
  exit
fi

echo
echo --------------------------------------------------------
echo updating MW4 to newest official release
echo --------------------------------------------------------

python3 -m pip install mountwizzard4 --upgrade --no-cache-dir >> update.log 2>&1

echo
echo --------------------------------------------------------
echo updated mountwizzard4 successfully
echo for details see update.log
echo --------------------------------------------------------
