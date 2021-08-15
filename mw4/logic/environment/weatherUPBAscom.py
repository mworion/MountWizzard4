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


class WeatherUPBAscom(AscomClass):
    """
    """

    __all__ = ['WeatherUPBAscom',
               ]
    CYCLE_POLL_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        self.getAndStoreAscomProperty('temperature', 'WEATHER_PARAMETERS.WEATHER_TEMPERATURE')
        self.getAndStoreAscomProperty('dewpoint', 'WEATHER_PARAMETERS.WEATHER_DEWPOINT')
        self.getAndStoreAscomProperty('humidity', 'WEATHER_PARAMETERS.WEATHER_HUMIDITY')
        return True
