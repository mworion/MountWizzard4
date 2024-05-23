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

# external packages

# local imports
from base.alpacaClass import AlpacaClass


class SensorWeatherAlpaca(AlpacaClass):
    """
    """
    __all__ = ['SensorWeatherAlpaca']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals
        self.data = data

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.getAndStoreAlpacaProperty('temperature',
                                       'WEATHER_PARAMETERS.WEATHER_TEMPERATURE')
        self.getAndStoreAlpacaProperty('pressure',
                                       'WEATHER_PARAMETERS.WEATHER_PRESSURE')
        self.getAndStoreAlpacaProperty('dewpoint',
                                       'WEATHER_PARAMETERS.WEATHER_DEWPOINT')
        self.getAndStoreAlpacaProperty('humidity',
                                       'WEATHER_PARAMETERS.WEATHER_HUMIDITY')
        self.getAndStoreAlpacaProperty('cloudcover',
                                       'WEATHER_PARAMETERS.CloudCover')
        self.getAndStoreAlpacaProperty('rainrate',
                                       'WEATHER_PARAMETERS.RainVol')
        self.getAndStoreAlpacaProperty('skyquality',
                                       'SKY_QUALITY.SKY_BRIGHTNESS')
        return True
