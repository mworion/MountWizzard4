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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
import platform

excludedPlatforms = ["armv7l"]
isAvailable = platform.machine() not in excludedPlatforms
isAnalyse = False
isReference = False
isWindows = platform.system() == "Windows"
isLinux = platform.system() == "Linux"
isMac = platform.system() == "Darwin"
isSimulationMount = False
