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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class SensorWeatherAscom(AscomClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals

    def workerPollData(self) -> None:
        """ """
        self.getAndStoreAscomProperty("temperature", "WEATHER_PARAMETERS.WEATHER_TEMPERATURE")
        self.getAndStoreAscomProperty("pressure", "WEATHER_PARAMETERS.WEATHER_PRESSURE")
        self.getAndStoreAscomProperty("dewpoint", "WEATHER_PARAMETERS.WEATHER_DEWPOINT")
        self.getAndStoreAscomProperty("humidity", "WEATHER_PARAMETERS.WEATHER_HUMIDITY")
        self.getAndStoreAscomProperty("cloudcover", "WEATHER_PARAMETERS.CloudCover")
        self.getAndStoreAscomProperty("rainrate", "WEATHER_PARAMETERS.RainVol")
        self.getAndStoreAscomProperty("skyquality", "SKY_QUALITY.SKY_BRIGHTNESS")
