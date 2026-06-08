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
# License APL2.0
#
###########################################################
from pathlib import Path
from PySide6.QtCore import QObject, Signal


class Signals(QObject):
    deviceConnected = Signal(str, str)
    deviceDisconnected = Signal(str, str)
    exposed = Signal(Path)
    downloaded = Signal(Path)
    saved = Signal(Path)
    azimuth = Signal(object)
    slewed = Signal(str)
    message = Signal(str)
    version = Signal(int)
    result = Signal(object)
