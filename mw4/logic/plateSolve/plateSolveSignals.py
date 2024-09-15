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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PySide6.QtCore import QObject, Signal

# local imports


class PlateSolveSignals(QObject):
    """
    """
    __all__ = ['PlateSolveSignals']

    result = Signal(object)
    message = Signal(object)

    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)

