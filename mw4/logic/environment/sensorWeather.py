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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform

# external packages

# local imports
from base.driverDataClass import Signals
from logic.environment.sensorWeatherIndi import SensorWeatherIndi
from logic.environment.sensorWeatherAlpaca import SensorWeatherAlpaca
if platform.system() == 'Windows':
    from logic.environment.sensorWeatherAscom import SensorWeatherAscom


class SensorWeather:
    """
    """

    __all__ = ['SensorWeather']
    log = logging.getLogger(__name__)

    def __init__(self, app):
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': SensorWeatherIndi(self.app, self.signals, self.data),
            'alpaca': SensorWeatherAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == 'Windows':
            self.run['ascom'] = SensorWeatherAscom(self.app, self.signals, self.data)

        for fw in self.run:
            self.defaultConfig['frameworks'].update({fw: self.run[fw].defaultConfig})

    @property
    def updateRate(self):
        return self.run[self.framework].updateRate

    @updateRate.setter
    def updateRate(self, value):
        value = int(value)
        for fw in self.run:
            self.run[fw].updateRate = value

    @property
    def loadConfig(self):
        return self.run[self.framework].loadConfig

    @loadConfig.setter
    def loadConfig(self, value):
        value = bool(value)
        for fw in self.run:
            self.run[fw].loadConfig = value

    def startCommunication(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].startCommunication()
        return suc

    def stopCommunication(self):
        """
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].stopCommunication()
        return suc
