#!/bin/bash
cd $(dirname "$0")

#
# run script for debian astroberry 2.0.4
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
echo run script version 2.2 astroberry
echo --------------------------------------------------------

echo run script version 2.2 astroberry >> run.log 2>&1

export QT_SCALE_FACTOR=1 >> run.log 2>&1
export QT_FONT_DPI=96 >> run.log 2>&1
export LC_ALL=C >> run.log 2>&1

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

startCommand="python3 $HOME/.local/lib/$P_VER/site-packages/mw4/loader.py"
$($startCommand) >> run.log 2>&1