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
# standard libraries

# external packages
from PySide6.QtCore import Signal, QObject

# local import


class INDISignals(QObject):
    """
    The INDISignals class offers a list of signals to be used and instantiated
    by the IndiBase class to get signals for indi events.
    """

    __all__ = ["INDISignals"]

    newDevice = Signal(str)
    removeDevice = Signal(str)
    newProperty = Signal(str, str)
    removeProperty = Signal(str, str)

    newBLOB = Signal(str, str)
    newSwitch = Signal(str, str)
    newNumber = Signal(str, str)
    newText = Signal(str, str)
    newLight = Signal(str, str)

    defBLOB = Signal(str, str)
    defSwitch = Signal(str, str)
    defNumber = Signal(str, str)
    defText = Signal(str, str)
    defLight = Signal(str, str)

    newMessage = Signal(str, str)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(str)
    deviceDisconnected = Signal(str)

    serverAlive = Signal(bool)
