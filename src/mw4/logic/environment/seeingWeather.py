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
import requests
from dataclasses import dataclass, field
from mw4.base.signalsDevices import Signals
from mw4.base.tpool import Worker
from pathlib import Path
from PySide6.QtCore import Signal
from typing import Any


@dataclass
class DeviceConfigSeeingWeather:
    deviceName: str = field(default="Meteoblue")
    apiKey: str = field(default="free")
    hostAddress: str = field(default="my.meteoblue.com")


class SeeingWeatherSignals(Signals):
    update = Signal()


class SeeingWeather:
    DEVICE_TYPE = "observingconditions"
    log = logging.getLogger("MW4")

    def __init__(self, app: Any = None) -> None:
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool
        self.signals = SeeingWeatherSignals()
        self.location = self.app.dReg["mount"].location
        self.b: str = ""
        self.framework: str = ""
        self.run: dict[str, Any] = {"seeing": self}
        self.data: dict[str, Any] = {}
        self.config = DeviceConfigSeeingWeather()
        self.worker: Worker | None = None
        self.running: bool = False

    def startCommunication(self) -> None:
        self.pollSeeingData()
        self.app.timeMgr.update3s.connect(self.pollSeeingData)

    def stopCommunication(self) -> None:
        self.running = False
        self.data.clear()
        self.signals.deviceDisconnected.emit(self.config.deviceName)
        self.app.timeMgr.update3m.disconnect(self.pollSeeingData)

    def processSeeingData(self) -> None:
        dataFile = self.app.mwGlob["dataDir"] / "meteoblue.data"
        if not dataFile.is_file():
            self.log.info(f"{dataFile} not available")
            return
        with open(dataFile) as f:
            try:
                self.data = json.load(f)
            except Exception as e:
                self.log.warning(f"Cannot load data file, error: {e}")
                return
        self.signals.update.emit()

    def workerGetSeeingData(self, url: Path) -> bool:
        try:
            data = requests.get(str(url), timeout=30)
            self.log.debug(f"Seeing url: [{url}] response code: [{data.status_code}]")
        except Exception as e:
            self.log.critical(f"[{url}] general exception: [{e}]")
            return False
        if data.status_code != 200:
            self.log.warning(f"[{url}] status is not 200")
            return False
        self.log.debug(f"Data: [{data}]")
        with open(self.app.mwGlob["dataDir"] / "meteoblue.data", "w+") as f:
            json.dump(data.json(), f, indent=4)
        return True

    def sendStatus(self, status: bool) -> None:
        if not status and self.running:
            self.signals.deviceDisconnected.emit(self.config.deviceName)
            self.running = False
        elif status and not self.running:
            self.signals.deviceConnected.emit(self.config.deviceName)
            self.running = True
        if status:
            self.processSeeingData()

    def loadingFileNeeded(self, fileName: Path, hours: float) -> bool:
        filePath = self.app.mwGlob["dataDir"] / fileName
        if not filePath.is_file():
            return True
        ageData = self.app.dReg["mount"].obsSite.loader.days_old(fileName)
        return not ageData < hours / 24

    def getSeeingData(self, url: Path) -> None:
        if not self.loadingFileNeeded("meteoblue.data", 0.5):
            self.processSeeingData()
            self.sendStatus(True)
            return
        self.worker = Worker(self.workerGetSeeingData, url)
        self.worker.signals.result.connect(self.sendStatus)
        self.threadPool.start(self.worker)

    def pollSeeingData(self) -> None:
        if not self.config.apiKey or not self.b or not self.app.isOnline:
            self.sendStatus(False)
            return

        lat = self.location.latitude.degrees
        lon = self.location.longitude.degrees

        webSite = f"http://{self.config.hostAddress}/feed/seeing_json"
        url = f"{webSite}?lat={lat:1.2f}&lon={lon:1.2f}&tz=utc"
        self.getSeeingData(url=url + f"&apikey={self.b}")
