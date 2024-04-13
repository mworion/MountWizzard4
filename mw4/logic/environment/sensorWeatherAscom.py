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
from base.ascomClass import AscomClass


class SensorWeatherAscom(AscomClass):

    __all__ = ['SensorWeatherAscom']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        self.getAndStoreAscomProperty('temperature',
                                      'WEATHER_PARAMETERS.WEATHER_TEMPERATURE')
        self.getAndStoreAscomProperty('pressure',
                                      'WEATHER_PARAMETERS.WEATHER_PRESSURE')
        self.getAndStoreAscomProperty('dewpoint',
                                      'WEATHER_PARAMETERS.WEATHER_DEWPOINT')
        self.getAndStoreAscomProperty('humidity',
                                      'WEATHER_PARAMETERS.WEATHER_HUMIDITY')
        self.getAndStoreAscomProperty('cloudcover',
                                      'WEATHER_PARAMETERS.CloudCover')
        self.getAndStoreAscomProperty('rainrate',
                                      'WEATHER_PARAMETERS.RainVol')
        self.getAndStoreAscomProperty('skyquality',
                                      'SKY_QUALITY.SKY_BRIGHTNESS')
        return True
