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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
import PyQt5
# local imports
from mw4.telescope.telescopeIndi import TelescopeIndi


class TelescopeSignals(PyQt5.QtCore.QObject):
    """
    The TelescopeSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['TelescopeSignals']

    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal(object)
    deviceConnected = PyQt5.QtCore.pyqtSignal(object)
    deviceDisconnected = PyQt5.QtCore.pyqtSignal(object)


class Telescope:

    __all__ = ['Telescope',
               ]

    logger = logging.getLogger(__name__)

    def __init__(self, app):

        self.app = app
        self.threadPool = app.threadPool
        self.signals = TelescopeSignals()

        self.data = {}
        self.framework = None
        self.run = {
            'indi': TelescopeIndi(self.app, self.signals, self.data),
        }
        self.name = ''

        self.host = ('localhost', 7624)

        # signalling from subclasses to main
        self.run['indi'].client.signals.serverConnected.connect(self.serverConnected)
        self.run['indi'].client.signals.serverDisconnected.connect(self.serverDisconnected)
        self.run['indi'].client.signals.deviceConnected.connect(self.deviceConnected)
        self.run['indi'].client.signals.deviceDisconnected.connect(self.deviceDisconnected)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        if self.framework in self.run.keys():
            self.run[self.framework].host = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        if self.framework in self.run.keys():
            self.run[self.framework].name = value

    # wee need to collect dispatch all signals from the different frameworks
    def deviceConnected(self, deviceName):
        self.signals.deviceConnected.emit(deviceName)

    def deviceDisconnected(self, deviceName):
        self.signals.deviceDisconnected.emit(deviceName)

    def serverConnected(self):
        self.signals.serverConnected.emit()

    def serverDisconnected(self, deviceList):
        self.signals.serverDisconnected.emit(deviceList)

    def startCommunication(self):
        """

        """

        if self.framework in self.run.keys():
            suc = self.run[self.framework].startCommunication()
            return suc
        else:
            return False

    def stopCommunication(self):
        """

        """

        if self.framework in self.run.keys():
            suc = self.run[self.framework].stopCommunication()
            return suc
        else:
            return False
