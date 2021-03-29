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
from PyQt5.QtCore import QObject, pyqtSignal

# local imports
from logic.cover.coverIndi import CoverIndi
from logic.cover.coverAlpaca import CoverAlpaca
if platform.system() == 'Windows':
    from logic.cover.coverAscom import CoverAscom


class CoverSignals(QObject):
    """
    The FlipFlatSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['CoverSignals']

    serverConnected = pyqtSignal()
    serverDisconnected = pyqtSignal(object)
    deviceConnected = pyqtSignal(str)
    deviceDisconnected = pyqtSignal(str)


class Cover:

    __all__ = ['Cover',
               ]

    log = logging.getLogger(__name__)

    def __init__(self, app):

        self.app = app
        self.threadPool = app.threadPool
        self.signals = CoverSignals()

        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': CoverIndi(self.app, self.signals, self.data),
            'alpaca': CoverAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == 'Windows':
            self.run['ascom'] = CoverAscom(self.app, self.signals, self.data)
            ascomSignals = self.run['ascom'].ascomSignals
            ascomSignals.serverConnected.connect(self.signals.serverConnected)
            ascomSignals.serverDisconnected.connect(self.signals.serverDisconnected)
            ascomSignals.deviceConnected.connect(self.signals.deviceConnected)
            ascomSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        for fw in self.run:
            self.defaultConfig['frameworks'].update(self.run[fw].defaultConfig)

        # signalling from subclasses to main
        alpacaSignals = self.run['alpaca'].client.signals
        alpacaSignals.serverConnected.connect(self.signals.serverConnected)
        alpacaSignals.serverDisconnected.connect(self.signals.serverDisconnected)
        alpacaSignals.deviceConnected.connect(self.signals.deviceConnected)
        alpacaSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        # signalling from subclasses to main
        indiSignals = self.run['indi'].client.signals
        indiSignals.serverConnected.connect(self.signals.serverConnected)
        indiSignals.serverDisconnected.connect(self.signals.serverDisconnected)
        indiSignals.deviceConnected.connect(self.signals.deviceConnected)
        indiSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return:
        """
        if self.framework not in self.run.keys():
            return False
        suc = self.run[self.framework].startCommunication(loadConfig=loadConfig)
        return suc

    def stopCommunication(self):
        """
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].stopCommunication()
        return suc

    def closeCover(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].closeCover()
        return suc

    def openCover(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].openCover()
        return suc

    def haltCover(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].haltCover()
        return suc

    def lightOn(self):
        """
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].lightOn()
        return suc

    def lightOff(self):
        """
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].lightOff()
        return suc

    def lightIntensity(self, value):
        """
        :param value:
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].lightIntensity(value)
        return suc
