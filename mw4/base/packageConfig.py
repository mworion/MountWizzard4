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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
import platform

excludedPlatforms = ['armv7l', 'aarch64']
isAvailable = platform.machine() not in excludedPlatforms
isAnalyse = False
isWindows = platform.system() == 'Windows'
isLinux = platform.system() == 'Linux'
isMac = platform.system() == 'Darwin'
