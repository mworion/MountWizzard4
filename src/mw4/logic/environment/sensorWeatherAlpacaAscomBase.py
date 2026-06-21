############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon
from collections.abc import Any


class SensorWeatherAlpacaAscomBase(AlpacaAscomCommon):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None:
        self.getAndStoreDeviceProp("Temperature", "WEATHER_PARAMETERS.WEATHER_TEMPERATURE")
        self.getAndStoreDeviceProp("Pressure", "WEATHER_PARAMETERS.WEATHER_PRESSURE")
        self.getAndStoreDeviceProp("DewPoint", "WEATHER_PARAMETERS.WEATHER_DEWPOINT")
        self.getAndStoreDeviceProp("Humidity", "WEATHER_PARAMETERS.WEATHER_HUMIDITY")
        self.getAndStoreDeviceProp("CloudCover", "WEATHER_PARAMETERS.CloudCover")
        self.getAndStoreDeviceProp("RainRate", "WEATHER_PARAMETERS.RainVol")
        self.getAndStoreDeviceProp("SkyQuality", "SKY_QUALITY.SKY_BRIGHTNESS")
