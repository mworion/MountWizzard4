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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
import logging
from pathlib import Path


class SensorWeatherBoltwood:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, parent):
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.signals = parent.signals
        self.filePath: str = ""
        self.deviceConnected: bool = False
        self.defaultConfig = {
            "deviceName": "Boltwood II",
            "filePath": "",
        }
        self.app.update3s.connect(self.pollBoltwoodData)

    def startCommunication(self) -> None:
        """ """
        self.deviceConnected = True

    def stopCommunication(self) -> None:
        """ """
        self.data.clear()
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit("SeeingWeather")

    @staticmethod
    def convert_knots2kmh(knots: float) -> float:
        """ """
        return knots * 1.852

    @staticmethod
    def convert_mph2kmh(mph: float) -> float:
        """ """
        return mph * 1.609344

    @staticmethod
    def convertFtoC(tempF: float) -> float:
        """ """
        return (tempF - 32) * 5.0 / 9.0

    def parseAndWriteBoltwoodData(self, rawData: str) -> bool:
        """
            · File write date
            · File write time
            · Temperature scale (Celsius or Fahrenheit)
            ·Wind speed scale (Mph or Knots)
            ·Sky Temperature
            ·Ambient Temperature
            ·Sensor Temperature
            ·Wind Speed
            ·Humidity
            ·Dew Point
            ·Dew Heater Percentage
            ·Rain Flag
            ·Wet Flag
            ·Elapsed time since last file write
            ·Elapsed days since last write
            ·Cloud/Clear flag (1=Clear,2=Light Clouds,3=Very Cloudy)
            ·Wind Limit flag (1=Calm,2=Windy,3=Very Windy)
            ·Rain flag (1=Dry,2=Damp,3=Rain)
            ·Darkness flag (1=Dark,2=Dim,3=Daylight)
            · Roof Close flag
            · Alert flag (0=No Alert,1=Alert)
        """
        dataParts = rawData.split()
        if len(dataParts) != 21:
            self.log.warning("Boltwood data invalid")
            return False

        if dataParts[2] == "F":
            skyTemp = self.convertFtoC(float(dataParts[4]))
            ambientTemp = self.convertFtoC(float(dataParts[5]))
            dewPoint = self.convertFtoC(float(dataParts[9]))
        else:
            skyTemp = float(dataParts[4])
            ambientTemp = float(dataParts[5])
            dewPoint = float(dataParts[9])

        if dataParts[3] == "K":
            windSpeed = self.convert_knots2kmh(float(dataParts[7]))
        else:
            windSpeed = self.convert_mph2kmh(float(dataParts[7]))

        self.data["SKY_QUALITY.SKY_BRIGHTNESS"] = skyTemp
        self.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = ambientTemp
        self.data["WEATHER_PARAMETERS.WEATHER_HUMIDITY"] = float(dataParts[8])
        self.data["WEATHER_PARAMETERS.WEATHER_DEWPOINT"] = dewPoint
        self.data["WEATHER_PARAMETERS.WIND_SPEED"] = windSpeed
        return True

    def processBoltwoodData(self, filePath: Path) -> bool:
        """ """
        if not filePath.is_file():
            self.log.warning("Boltwood file path invalid")
            return False
        with filePath.open("r") as file:
            rawData = file.readline()
        return self.parseAndWriteBoltwoodData(rawData)

    def pollBoltwoodData(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        filePath = Path(self.filePath)
        if not self.processBoltwoodData(filePath):
            self.stopCommunication()
            return
        self.signals.deviceConnected.emit("BoltwoodWeather")

