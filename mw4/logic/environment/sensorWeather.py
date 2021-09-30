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
import PyQt5

# local imports
from logic.environment.sensorWeatherIndi import SensorWeatherIndi
from logic.environment.sensorWeatherAlpaca import SensorWeatherAlpaca
if platform.system() == 'Windows':
    from logic.environment.sensorWeatherAscom import SensorWeatherAscom


class SensorWeatherSignals(PyQt5.QtCore.QObject):
    """
    """

    __all__ = ['SensorWeatherSignals']

    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal(object)
    deviceConnected = PyQt5.QtCore.pyqtSignal(str)
    deviceDisconnected = PyQt5.QtCore.pyqtSignal(str)


class SensorWeather:
    """
    """

    __all__ = ['SensorWeather']
    log = logging.getLogger(__name__)

    def __init__(self, app):

        self.app = app
        self.threadPool = app.threadPool
        self.signals = SensorWeatherSignals()
        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': SensorWeatherIndi(self.app, self.signals, self.data),
            'alpaca': SensorWeatherAlpaca(self.app, self.signals, self.data),
        }

        for fw in self.run:
            self.defaultConfig['frameworks'].update(self.run[fw].defaultConfig)

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
