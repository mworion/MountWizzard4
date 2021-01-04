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

# external packages

# local imports
from base.ascomClass import AscomClass


class SensorWeatherAscom(AscomClass):

    __all__ = ['SensorWeatherAscom',
               ]

    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data

    def getInitialConfig(self):
        """

        :return: true for test purpose
        """

        super().getInitialConfig()

        return True

    def workerPollData(self):
        """

        :return: true for test purpose
        """

        if not self.deviceConnected:
            return False

        self.dataEntry(self.client.temperature, 'WEATHER_PARAMETERS.WEATHER_TEMPERATURE')
        self.dataEntry(self.client.pressure, 'WEATHER_PARAMETERS.WEATHER_PRESSURE')
        self.dataEntry(self.client.dewpoint, 'WEATHER_PARAMETERS.WEATHER_DEWPOINT')
        self.dataEntry(self.client.humidity, 'WEATHER_PARAMETERS.WEATHER_HUMIDITY')

        try:
            val = self.client.skyquality
        except Exception:
            val = 0
        self.dataEntry(val, 'SKY_QUALITY.SKY_BRIGHTNESS')

        try:
            val = self.client.cloudcover
        except Exception:
            val = 0
        self.dataEntry(val, 'cloudCover')

        try:
            val = self.client.rainrate
        except Exception:
            val = 0
        self.dataEntry(val, 'rain')

        try:
            val = self.client.winddirection
        except Exception:
            val = 0
        self.dataEntry(val, 'windDir')

        try:
            val = self.client.windspeed
        except Exception:
            val = 0
        self.dataEntry(val, 'windSpeed')

        return True
