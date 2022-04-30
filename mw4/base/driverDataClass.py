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
# standard libraries
import logging

# external packages
from PyQt5.QtCore import pyqtSignal, QObject


class Signals(QObject):
    __all__ = ['Signals']

    serverConnected = pyqtSignal()
    serverDisconnected = pyqtSignal(object)
    deviceConnected = pyqtSignal(str)
    deviceDisconnected = pyqtSignal(str)

    exposed = pyqtSignal()
    downloaded = pyqtSignal()
    saved = pyqtSignal(object)
    exposeReady = pyqtSignal()
    azimuth = pyqtSignal(object)
    slewFinished = pyqtSignal()
    message = pyqtSignal(object)
    version = pyqtSignal(int)


class RemoteDeviceShutdown(QObject):
    __all__ = ['RemoteDeviceShutdown']
    signalRemoteShutdown = pyqtSignal()


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
