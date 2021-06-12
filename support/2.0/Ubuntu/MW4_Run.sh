#!/bin/bash
cd $(dirname "$0")

#
# run script for osx
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
echo run script version 2.0
echo --------------------------------------------------------

echo run script version 2.0 >> run.log 2>&1
echo

if [ ! -f ./venv/bin/activate ]; then
  echo
  echo --------------------------------------------------------
  echo no valid virtual environment installed
  echo --------------------------------------------------------
  exit
fi

export QT_SCALE_FACTOR=1 >> run.log 2>&1
export QT_FONT_DPI=96 >> run.log 2>&1
source ./venv/bin/activate venv >> run.log 2>&1

echo
echo --------------------------------------------------------
echo checking installed python version
echo --------------------------------------------------------


echo Checking environment and start script >> run.log 2>&1

T=`python3 --version`
P_VER=""

if [ "${T:0:10}" == "Python 3.9" ]; then
  P_VER="python3.9"
elif [ "${T:0:10}" == "Python 3.8" ]; then
  P_VER="python3.8"
elif [ "${T:0:10}" == "Python 3.7" ]; then
  P_VER="python3.7"
fi

echo variable P_VER has value of $P_VER >> run.log 2>&1

if [ "${P_VER:0:6}" == "python" ]; then
  echo
  echo --------------------------------------------------------
  echo python version ok: ${P_VER}
  echo --------------------------------------------------------
else
  echo
  echo --------------------------------------------------------
  echo no valid python version installed
  echo please run MW4_Install.command first
  echo --------------------------------------------------------

  echo no valid python version installed >> run.log 2>&1
  exit
fi

startCommand="python ./venv/lib/$P_VER/site-packages/mw4/loader.py"
$($startCommand)
deactivate >> run.log 2>&1
