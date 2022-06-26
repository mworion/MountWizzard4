############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
import platform
from packaging.utils import Version

excludedPlatforms = ['armv7l', 'aarch64']
isAvailable = platform.machine() not in excludedPlatforms
isAnalyse = False
isWindows = platform.system() == 'Windows'
isLinux = platform.system() == 'Linux'
isMac = platform.system() == 'Darwin'


def checkAutomation():
    verResult = Version('3.8.2') <= Version(platform.python_version())
    winResult = platform.system() == 'Windows'
    result = verResult and winResult
    return result
