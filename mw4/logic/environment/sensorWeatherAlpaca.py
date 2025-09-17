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
from base.alpacaClass import AlpacaClass


class SensorWeatherAlpaca(AlpacaClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.data = parent.data

    def workerPollData(self) -> None:
        """ """
        if not self.deviceConnected:
            return

        self.getAndStoreAlpacaProperty("temperature", "WEATHER_PARAMETERS.WEATHER_TEMPERATURE")
        self.getAndStoreAlpacaProperty("pressure", "WEATHER_PARAMETERS.WEATHER_PRESSURE")
        self.getAndStoreAlpacaProperty("dewpoint", "WEATHER_PARAMETERS.WEATHER_DEWPOINT")
        self.getAndStoreAlpacaProperty("humidity", "WEATHER_PARAMETERS.WEATHER_HUMIDITY")
        self.getAndStoreAlpacaProperty("cloudcover", "WEATHER_PARAMETERS.CloudCover")
        self.getAndStoreAlpacaProperty("rainrate", "WEATHER_PARAMETERS.RainVol")
        self.getAndStoreAlpacaProperty("skyquality", "SKY_QUALITY.SKY_BRIGHTNESS")
