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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
import PyQt5
# local imports
from mw4.base.loggerMW import CustomLogger
from mw4.cover.flipflatIndi import FlipFlatIndi


class FlipFlatSignals(PyQt5.QtCore.QObject):
    """
    The FlipFlatSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['FlipFlatSignals']

    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal(object)
    deviceConnected = PyQt5.QtCore.pyqtSignal(str)
    deviceDisconnected = PyQt5.QtCore.pyqtSignal(str)


class FlipFlat:

    __all__ = ['FlipFlat',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self, app):

        self.app = app
        self.threadPool = app.threadPool
        self.signals = FlipFlatSignals()

        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': FlipFlatIndi(self.app, self.signals, self.data),
        }
        for fw in self.run:
            self.defaultConfig['frameworks'].update(self.run[fw].defaultConfig)

        # signalling from subclasses to main
        self.run['indi'].client.signals.serverConnected.connect(self.signals.serverConnected)
        self.run['indi'].client.signals.serverDisconnected.connect(self.signals.serverDisconnected)
        self.run['indi'].client.signals.deviceConnected.connect(self.signals.deviceConnected)
        self.run['indi'].client.signals.deviceDisconnected.connect(self.signals.deviceDisconnected)

    def startCommunication(self, loadConfig=False):
        """

        """

        if self.framework not in self.run.keys():
            return False
        suc = self.run[self.framework].startCommunication(loadConfig=loadConfig)
        return suc

    def stopCommunication(self):
        """

        """

        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].stopCommunication()
        return suc

    def sendCoverPark(self, park=True):
        """

        :param park:
        :return: success
        """

        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].sendCoverPark(park=park)
        return suc
