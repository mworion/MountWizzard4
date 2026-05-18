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
from mw4.base.ascomClass import AscomClass
from typing import Any


class SensorWeatherAscom(AscomClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def pollData(self) -> None:
        self.getAndStoreDeviceProp("temperature", "WEATHER_PARAMETERS.WEATHER_TEMPERATURE")
        self.getAndStoreDeviceProp("pressure", "WEATHER_PARAMETERS.WEATHER_PRESSURE")
        self.getAndStoreDeviceProp("dewpoint", "WEATHER_PARAMETERS.WEATHER_DEWPOINT")
        self.getAndStoreDeviceProp("humidity", "WEATHER_PARAMETERS.WEATHER_HUMIDITY")
        self.getAndStoreDeviceProp("cloudcover", "WEATHER_PARAMETERS.CloudCover")
        self.getAndStoreDeviceProp("rainrate", "WEATHER_PARAMETERS.RainVol")
        self.getAndStoreDeviceProp("skyquality", "SKY_QUALITY.SKY_BRIGHTNESS")
