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
from PySide6.QtCore import QObject, Signal


class Signals(QObject):
    """ """

    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(str)
    deviceDisconnected = Signal(str)
    exposed = Signal(object)
    downloaded = Signal(object)
    saved = Signal(object)
    azimuth = Signal(object)
    slewed = Signal(object)
    message = Signal(object)
    version = Signal(int)
    result = Signal(object)
