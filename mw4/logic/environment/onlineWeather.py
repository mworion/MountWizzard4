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
import logging
import json
import os
from pathlib import Path

# external packages
import numpy as np
import requests

# local imports
from base.tpool import Worker
from base.signalsDevices import Signals


class OnlineWeather:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.location = app.mount.obsSite.location

        # minimum set for driver package built in
        self.framework = ""
        self.run = {"onlineWeather": self}
        self.deviceName = ""
        self.data = {}
        self.worker: Worker = None
        self.defaultConfig = {
            "framework": "",
            "frameworks": {
                "onlineWeather": {
                    "deviceName": "OnlineWeather",
                    "apiKey": "",
                    "hostaddress": "api.openweathermap.org",
                }
            },
        }
        self.running = False
        self.enabled = False
        self.hostaddress = ""
        self.apiKey = ""
        self._online = False
        self.app.update10s.connect(self.pollOpenWeatherMapData)

    @property
    def online(self) -> bool:
        return self._online

    @online.setter
    def online(self, value: bool) -> None:
        self._online = value
        self.pollOpenWeatherMapData()

    def startCommunication(self) -> None:
        """ """
        self.enabled = True
        self.pollOpenWeatherMapData()

    def stopCommunication(self) -> None:
        """ """
        self.enabled = False
        self.running = False
        self.data.clear()
        self.signals.deviceDisconnected.emit("OnlineWeather")

    @staticmethod
    def getDewPoint(tempAir: float, relativeHumidity: float) -> float:
        """
        Compute the dew point in degrees Celsius

        :param tempAir: current ambient temperature in degrees Celsius
        :param relativeHumidity: relative humidity in %
        :return: the dew point in degrees Celsius
        """
        if tempAir < -40 or tempAir > 80:
            return 0
        if relativeHumidity < 0 or relativeHumidity > 100:
            return 0

        A = 17.27
        B = 237.7
        alpha = ((A * tempAir) / (B + tempAir)) + np.log(relativeHumidity / 100.0)
        dewPoint = (B * alpha) / (A - alpha)
        return dewPoint

    def processOpenWeatherMapData(self) -> bool:
        """ """
        dataFile = self.app.mwGlob["dataDir"] / "openweathermap.data"
        if not os.path.isfile(dataFile):
            self.log.info(f"{dataFile} not available")
            return False

        try:
            with open(dataFile, "r") as f:
                data = json.load(f)
        except Exception as e:
            self.log.warning(f"Cannot load data file, error: {e}")
            return False

        if "main" in data:
            val = data["main"].get("temp", 273.15) - 273.15
            self.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = val
            val = data["main"].get("pressure", 0)
            self.data["WEATHER_PARAMETERS.WEATHER_PRESSURE"] = val
            val = data["main"].get("humidity", 0)
            self.data["WEATHER_PARAMETERS.WEATHER_HUMIDITY"] = val
            val = self.getDewPoint(
                self.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"],
                self.data["WEATHER_PARAMETERS.WEATHER_HUMIDITY"],
            )
            self.data["WEATHER_PARAMETERS.WEATHER_DEWPOINT"] = val

        else:
            return False

        if "clouds" in data:
            self.data["WEATHER_PARAMETERS.CloudCover"] = data["clouds"].get("all", 0)

        if "wind" in data:
            self.data["WEATHER_PARAMETERS.WindSpeed"] = data["wind"].get("speed", 0)
            self.data["WEATHER_PARAMETERS.WindDir"] = data["wind"].get("deg", 0)

        if "rain" in data:
            self.data["WEATHER_PARAMETERS.RainVol"] = data["rain"].get("3h", 0)
        else:
            self.data["WEATHER_PARAMETERS.RainVol"] = 0
        return True

    def workerGetOpenWeatherMapData(self, url: Path) -> None:
        """ """
        try:
            data = requests.get(url, timeout=30)
        except Exception as e:
            self.log.critical(f"[{url}] general exception: [{e}]")
            return

        if data.status_code != 200:
            self.log.warning(f"[{url}] status is not 200")
            return

        with open(self.app.mwGlob["dataDir"] / "openweathermap.data", "w+") as f:
            json.dump(data.json(), f, indent=4)
            self.log.trace(data.json())

    def sendStatus(self, status: bool) -> None:
        """ """
        if not status and self.running:
            self.signals.deviceDisconnected.emit("OnlineWeather")
        elif status and not self.running:
            self.signals.deviceConnected.emit("OnlineWeather")

    def getOpenWeatherMapData(self, url: Path) -> None:
        """ """
        self.worker = Worker(self.workerGetOpenWeatherMapData, url)
        self.worker.signals.finished.connect(self.processOpenWeatherMapData)
        self.worker.signals.result.connect(self.sendStatus)
        self.threadPool.start(self.worker)

    def loadingFileNeeded(self, fileName: Path, hours: float) -> bool:
        """ """
        filePath = self.app.mwGlob["dataDir"] / fileName
        if not os.path.isfile(filePath):
            return True

        ageData = self.app.mount.obsSite.loader.days_old(fileName)
        return ageData > hours / 24

    def pollOpenWeatherMapData(self) -> None:
        """ """
        if not self.enabled:
            return
        if not self.apiKey:
            return

        if not self.online and self.running:
            self.signals.deviceDisconnected.emit("OnlineWeather")
            self.running = False
            return
        elif self.online and not self.running:
            self.signals.deviceConnected.emit("OnlineWeather")
            self.running = True

        if not self.loadingFileNeeded("openweathermap.data", 1):
            self.processOpenWeatherMapData()
            return

        lat = self.location.latitude.degrees
        lon = self.location.longitude.degrees

        webSite = f"http://{self.hostaddress}/data/2.5/weather"
        url = f"{webSite}?lat={lat:1.2f}&lon={lon:1.2f}"
        self.getOpenWeatherMapData(url=url + f"&APPID={self.apiKey}")
        self.log.debug(f"{url}")
