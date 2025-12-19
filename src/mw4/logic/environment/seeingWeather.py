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
import json
import logging
import os
import requests
from mw4.base.signalsDevices import Signals
from mw4.base.tpool import Worker
from pathlib import Path
from PySide6.QtCore import Signal


class SeeingWeatherSignals(Signals):
    """ """

    update = Signal()


class SeeingWeather:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool
        self.signals = SeeingWeatherSignals()
        self.location = app.mount.obsSite.location
        self.b = ""
        self.framework = ""
        self.run = {"seeing": self}
        self.deviceName = ""
        self.data = {}
        self.worker: Worker = None
        self.defaultConfig = {
            "framework": "",
            "frameworks": {
                "seeing": {
                    "deviceName": "meteoblue",
                    "apiKey": "free",
                    "hostaddress": "my.meteoblue.com",
                }
            },
        }
        self.running: bool = False
        self.hostaddress: str = ""
        self.apiKey: str = ""

    def startCommunication(self) -> None:
        """ """
        self.app.update3s.connect(self.pollSeeingData)

    def stopCommunication(self) -> None:
        """ """
        self.running = False
        self.data.clear()
        self.signals.deviceDisconnected.emit("SeeingWeather")
        self.app.update3s.disconnect(self.pollSeeingData)

    def processSeeingData(self) -> None:
        """ """
        dataFile = self.app.mwGlob["dataDir"] / "meteoblue.data"
        if not os.path.isfile(dataFile):
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
        """ """
        if not self.app.onlineMode:
            return False
        try:
            data = requests.get(url, timeout=10)
        except Exception as e:
            self.log.critical(f"[{url}] general exception: [{e}]")
            return False

        if data.status_code != 200:
            self.log.warning(f"[{url}] status is {data.status_code}")
            return False

        with open(self.app.mwGlob["dataDir"] / "meteoblue.data", "w+") as f:
            json.dump(data.json(), f, indent=4)
        return True

    def sendStatus(self, status: bool) -> None:
        """ """
        if not status and self.running:
            self.signals.deviceDisconnected.emit("SeeingWeather")
            self.running = False
        elif status and not self.running:
            self.signals.deviceConnected.emit("SeeingWeather")
            self.running = True

    def getSeeingData(self, url: Path) -> None:
        """ """
        if not self.loadingFileNeeded("meteoblue.data", 0.5):
            self.processSeeingData()
            self.sendStatus(True)
            return
        self.worker = Worker(self.workerGetSeeingData, url)
        self.worker.signals.finished.connect(self.processSeeingData)
        self.worker.signals.result.connect(self.sendStatus)
        self.threadPool.start(self.worker)

    def loadingFileNeeded(self, fileName: Path, hours: float) -> bool:
        """ """
        filePath = self.app.mwGlob["dataDir"] / fileName
        if not filePath.is_file():
            return True

        ageData = self.app.mount.obsSite.loader.days_old(fileName)
        return not ageData < hours / 24

    def pollSeeingData(self) -> None:
        """ """
        if not self.apiKey or not self.b:
            return

        lat = self.location.latitude.degrees
        lon = self.location.longitude.degrees

        webSite = f"http://{self.hostaddress}/feed/seeing_json"
        url = f"{webSite}?lat={lat:1.2f}&lon={lon:1.2f}&tz=utc"
        self.getSeeingData(url=url + f"&apikey={self.b}")
        self.log.debug(f"{url}")
