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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform

# external packages
import PyQt5

# local imports
from logic.powerswitch.pegasusUPBIndi import PegasusUPBIndi
from logic.powerswitch.pegasusUPBAscom import PegasusUPBAscom
from logic.powerswitch.pegasusUPBAlpaca import PegasusUPBAlpaca


class PegasusUPBSignals(PyQt5.QtCore.QObject):
    """
    The PegasusUPBSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['PegasusUPBSignals']

    version = PyQt5.QtCore.pyqtSignal(int)

    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal(object)
    deviceConnected = PyQt5.QtCore.pyqtSignal(str)
    deviceDisconnected = PyQt5.QtCore.pyqtSignal(str)


class PegasusUPB:

    __all__ = ['PegasusUPB']

    log = logging.getLogger(__name__)

    def __init__(self, app):

        self.app = app
        self.threadPool = app.threadPool
        self.signals = PegasusUPBSignals()

        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': PegasusUPBIndi(self.app, self.signals, self.data),
            'alpaca': PegasusUPBAlpaca(self.app, self.signals, self.data),
        }
        if platform.system() == 'Windows':
            self.run['ascom'] = PegasusUPBAscom(self.app, self.signals, self.data)
            ascomSignals = self.run['ascom'].ascomSignals
            ascomSignals.serverConnected.connect(self.signals.serverConnected)
            ascomSignals.serverDisconnected.connect(self.signals.serverDisconnected)
            ascomSignals.deviceConnected.connect(self.signals.deviceConnected)
            ascomSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        for fw in self.run:
            self.defaultConfig['frameworks'].update(self.run[fw].defaultConfig)

        alpacaSignals = self.run['alpaca'].client.signals
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
        :return: true for test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].stopCommunication()
        return suc

    def togglePowerPort(self, port=None):
        """
        :param port:
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].togglePowerPort(port=port)
        return suc

    def togglePowerPortBoot(self, port=None):
        """
        :param port:
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].togglePowerPortBoot(port=port)
        return suc

    def toggleHubUSB(self):
        """
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].toggleHubUSB()
        return suc

    def togglePortUSB(self, port=None):
        """
        :param port:
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].togglePortUSB(port=port)
        return suc

    def toggleAutoDew(self):
        """
        :return: true fot test purpose
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].toggleAutoDew()
        return suc

    def sendDew(self, port='', value=None):
        """
        :param port:
        :param value:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].sendDew(port=port, value=value)
        return suc

    def sendAdjustableOutput(self, value=None):
        """
        :param value:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].sendAdjustableOutput(value=value)
        return suc

    def reboot(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].reboot()
        return suc
