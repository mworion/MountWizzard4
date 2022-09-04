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

# local imports
from base.driverDataClass import Signals


class DirectWeather:
    """
    """

    __all__ = ['DirectWeather']
    log = logging.getLogger(__name__)

    def __init__(self, app=None):

        self.app = app
        self.signals = Signals()

        # minimum set for driver package built in
        self.framework = ''
        self.run = {
            'directWeather': self
        }
        self.deviceName = ''
        self.data = {}
        self.defaultConfig = {
            'framework': '',
            'frameworks': {
                'directWeather': {
                    'deviceName': 'On Mount'
                }
            }
        }
        self.running = False
        self.enabled = False
        self.app.mount.signals.settingDone.connect(self.updateData)

    def startCommunication(self):
        """
        startCommunication enables the cyclic polling in framework driver
        :return: success
        """
        self.enabled = True
        self.app.deviceStat['directWeather'] = False
        return True

    def stopCommunication(self):
        """
        :return:
        """
        self.enabled = False
        self.running = False
        self.app.deviceStat['directWeather'] = None
        self.data.clear()
        self.signals.deviceDisconnected.emit('DirectWeather')
        return True

    def updateData(self, sett):
        """
        :param sett:
        :return:
        """
        if not self.enabled:
            return False

        value1 = sett.weatherTemperature
        value2 = sett.weatherPressure
        value3 = sett.weatherHumidity
        value4 = sett.weatherDewPoint
        value5 = sett.weatherAge
        isValid = None not in [value1, value2, value3, value4, value5]

        if not isValid and self.running:
            self.signals.deviceDisconnected.emit('DirectWeather')
            self.running = False
        elif isValid and not self.running:
            self.signals.deviceConnected.emit('DirectWeather')
            self.running = True

        self.app.deviceStat['directWeather'] = isValid
        self.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = value1
        self.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = value2
        self.data['WEATHER_PARAMETERS.WEATHER_DEWPOINT'] = value3
        self.data['WEATHER_PARAMETERS.WEATHER_HUMIDITY'] = value4
        self.data['WEATHER_PARAMETERS.WEATHER_AGE'] = value5
        return True
