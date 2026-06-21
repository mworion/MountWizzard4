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
import json
import logging
import numpy as np
import requests
from dataclasses import dataclass, field
from mw4.base.tpool import Worker
from pathlib import Path
from collections.abc import Any


@dataclass
class DeviceConfigOnlineWeather:
    deviceName: str = field(default="OnlineWeather")
    hostAddress: str | None = field(default="")
    apiKey: str = field(default="")


class SensorWeatherOnline:
    DEVICE_TYPE = "observingconditions"
    log = logging.getLogger("MW4")

    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.app = parent.app
        self.data: dict[str, Any] = parent.data
        self.config = DeviceConfigOnlineWeather()
        self.signals = parent.signals
        self.location: Any = None
        self.threadPool = parent.app.threadPool
        self.worker: Worker | None = None
        self.running: bool = False
        self.status: bool = False

    def startCommunication(self) -> None:
        self.location = self.app.dReg["mount"].obsSite.location
        self.pollOpenWeatherMapData()
        self.app.update3s.connect(self.pollOpenWeatherMapData)

    def stopCommunication(self) -> None:
        self.running = False
        self.data.clear()
        self.signals.deviceDisconnected.emit(self.config.deviceName)
        self.app.update3m.disconnect(self.pollOpenWeatherMapData)

    @staticmethod
    def getDewPoint(tempAir: float, relativeHumidity: float) -> float:
        if tempAir < -40 or tempAir > 80:
            return 0
        if relativeHumidity < 0 or relativeHumidity > 100:
            return 0

        A = 17.27
        B = 237.7
        alpha = ((A * tempAir) / (B + tempAir)) + np.log(relativeHumidity / 100.0)
        dewPoint = (B * alpha) / (A - alpha)
        return dewPoint

    def processOpenWeatherMapData(self) -> None:
        dataFile = self.app.mwGlob["dataDir"] / "openweathermap.data"
        if not dataFile.is_file():
            self.log.info(f"{dataFile} not available")
            return

        with open(dataFile) as f:
            try:
                data = json.load(f)
            except Exception as e:
                self.log.warning(f"Cannot load data file, error: {e}")
                return

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

        if "clouds" in data:
            self.data["WEATHER_PARAMETERS.CloudCover"] = data["clouds"].get("all", 0)

        if "wind" in data:
            self.data["WEATHER_PARAMETERS.WindSpeed"] = data["wind"].get("speed", 0)
            self.data["WEATHER_PARAMETERS.WindDir"] = data["wind"].get("deg", 0)

        if "rain" in data:
            self.data["WEATHER_PARAMETERS.RainVol"] = data["rain"].get("3h", 0)
        else:
            self.data["WEATHER_PARAMETERS.RainVol"] = 0

    def workerGetOpenWeatherMapData(self, url: Path) -> bool:
        try:
            data = requests.get(str(url), timeout=30)
            self.log.debug(f"Weather url: [{url}] response code: [{data.status_code}]")
        except Exception as e:
            self.log.critical(f"[{url}] general exception: [{e}]")
            return False
        if data.status_code != 200:
            self.log.warning(f"[{url}] status is not 200")
            return False
        self.log.debug(f"Data: [{data}]")
        with open(self.app.mwGlob["dataDir"] / "openweathermap.data", "w+") as f:
            json.dump(data.json(), f, indent=4)
        return True

    def sendStatus(self, status: bool) -> None:
        if not status and self.running:
            self.signals.deviceDisconnected.emit(self.config.deviceName)
            self.running = False
        elif status and not self.running:
            self.signals.deviceConnected.emit(self.config.deviceName)
            self.running = True
        if self.status:
            self.processOpenWeatherMapData()

    def loadingFileNeeded(self, fileName: Path, hours: float) -> bool:
        filePath = self.app.mwGlob["dataDir"] / fileName
        if not filePath.is_file():
            return True
        ageData = self.app.dReg["mount"].obsSite.loader.days_old(fileName)
        return ageData > hours / 24

    def getOpenWeatherMapData(self, url: Path) -> None:
        if not self.loadingFileNeeded("openweathermap.data", 1):
            self.processOpenWeatherMapData()
            self.sendStatus(True)
            return
        self.worker = Worker(self.workerGetOpenWeatherMapData, url)
        self.worker.signals.result.connect(self.sendStatus)
        self.threadPool.start(self.worker)

    def pollOpenWeatherMapData(self) -> None:
        if not self.config.apiKey or not self.app.isOnline:
            self.sendStatus(False)
            return

        lat = self.location.latitude.degrees
        lon = self.location.longitude.degrees

        webSite = f"http://{self.config.hostAddress}/data/2.5/weather"
        url = Path(f"{webSite}?lat={lat:1.2f}&lon={lon:1.2f}")
        self.getOpenWeatherMapData(url=url + f"&APPID={self.config.apiKey}")
