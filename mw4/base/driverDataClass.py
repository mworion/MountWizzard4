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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from PySide6.QtCore import Signal, QObject


class Signals(QObject):
    __all__ = ['Signals']

    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(str)
    deviceDisconnected = Signal(str)

    exposed = Signal()
    downloaded = Signal()
    saved = Signal(object)
    exposeReady = Signal()
    azimuth = Signal(object)
    slewFinished = Signal()
    message = Signal(object)
    version = Signal(int)


class RemoteDeviceShutdown(QObject):
    __all__ = ['RemoteDeviceShutdown']
    signalRemoteShutdown = Signal()


class DriverData:
    log = logging.getLogger(__name__)

    def storePropertyToData(self, value, element, elementInv=None):
        """
        :param value:
        :param element:
        :param elementInv:
        :return: reset entry
        """
        removeElement = value is None

        if removeElement and element in self.data:
            del self.data[element]

        if removeElement and elementInv is not None:
            if elementInv in self.data:
                del self.data[elementInv]

        if removeElement:
            return False

        self.data[element] = value

        if elementInv is not None:
            self.data[elementInv] = value

        return True
