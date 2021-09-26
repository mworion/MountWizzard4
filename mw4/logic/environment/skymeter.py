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
# standard libraries
import logging
import platform

# external packages
from PyQt5.QtCore import pyqtSignal, QObject

# local imports
from logic.environment.skymeterIndi import SkymeterIndi
from logic.environment.skymeterAlpaca import SkymeterAlpaca
if platform.system() == 'Windows':
    from logic.environment.skymeterAscom import SkymeterAscom


class SkymeterSignals(QObject):
    """
    """

    __all__ = ['SkymeterSignals']

    serverConnected = pyqtSignal()
    serverDisconnected = pyqtSignal(object)
    deviceConnected = pyqtSignal(str)
    deviceDisconnected = pyqtSignal(str)


class Skymeter:
    """
    """

    __all__ = ['Skymeter']
    log = logging.getLogger(__name__)

    def __init__(self, app):
        self.app = app
        self.threadPool = app.threadPool
        self.signals = SkymeterSignals()
        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': SkymeterIndi(self.app, self.signals, self.data),
            'alpaca': SkymeterAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == 'Windows':
            self.run['ascom'] = SkymeterAscom(self.app, self.signals, self.data)
            ascomSignals = self.run['ascom'].ascomSignals
            ascomSignals.serverConnected.connect(self.signals.serverConnected)
            ascomSignals.serverDisconnected.connect(self.signals.serverDisconnected)
            ascomSignals.deviceConnected.connect(self.signals.deviceConnected)
            ascomSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        for fw in self.run:
            self.defaultConfig['frameworks'].update(self.run[fw].defaultConfig)

        alpacaSignals = self.run['alpaca'].alpacaSignals
        alpacaSignals.serverConnected.connect(self.signals.serverConnected)
        alpacaSignals.serverDisconnected.connect(self.signals.serverDisconnected)
        alpacaSignals.deviceConnected.connect(self.signals.deviceConnected)
        alpacaSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        indiSignals = self.run['indi'].client.signals
        indiSignals.serverConnected.connect(self.signals.serverConnected)
        indiSignals.serverDisconnected.connect(self.signals.serverDisconnected)
        indiSignals.deviceConnected.connect(self.signals.deviceConnected)
        indiSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].startCommunication(loadConfig=loadConfig)
        return suc

    def stopCommunication(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].stopCommunication()
        return suc
