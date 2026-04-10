############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import platform

excludedPlatforms: list[str] = ["armv7l"]
isAvailable: bool = platform.machine() not in excludedPlatforms
isAnalyse: bool = False
isReference: bool = False
isSimulationMount: bool = False
isWindows: bool = platform.system() == "Windows"
isLinux: bool = platform.system() == "Linux"
isMac: bool = platform.system() == "Darwin"
