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
from PySide6.QtCore import Signal
import requests

# local imports
from base.tpool import Worker
from base.signalsDevices import Signals


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

        # minimum set for driver package built in
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
        self.running = False
        self.enabled = False
        self.hostaddress = ""
        self.apiKey = ""
        self._online = False
        self.app.update10m.connect(self.pollSeeingData)

    @property
    def online(self):
        return self._online

    @online.setter
    def online(self, value):
        self._online = value
        self.pollSeeingData()

    def startCommunication(self) -> None:
        """ """
        self.enabled = True
        self.pollSeeingData()

    def stopCommunication(self) -> None:
        """ """
        self.enabled = False
        self.running = False
        self.data.clear()
        self.signals.deviceDisconnected.emit("SeeingWeather")

    def processSeeingData(self) -> bool:
        """ """
        dataFile = self.app.mwGlob["dataDir"] / "meteoblue.data"
        if not os.path.isfile(dataFile):
            self.log.info(f"{dataFile} not available")
            return False

        try:
            with open(dataFile, "r") as f:
                self.data = json.load(f)
        except Exception as e:
            self.log.warning(f"Cannot load data file, error: {e}")
            return False

        self.signals.update.emit()
        return True

    def workerGetSeeingData(self, url: Path) -> None:
        """ """
        try:
            data = requests.get(url, timeout=30)
        except Exception as e:
            self.log.critical(f"[{url}] general exception: [{e}]")
            return

        if data.status_code != 200:
            self.log.warning(f"[{url}] status is {data.status_code}")
            return

        data = data.json()
        self.log.trace(data)

        with open(self.app.mwGlob["dataDir"] / "meteoblue.data", "w+") as f:
            json.dump(data, f, indent=4)

    def sendStatus(self, status: bool) -> None:
        """ """
        if not status and self.running:
            self.signals.deviceDisconnected.emit("SeeingWeather")
        elif status and not self.running:
            self.signals.deviceConnected.emit("SeeingWeather")

    def getSeeingData(self, url: Path) -> None:
        """ """
        self.worker = Worker(self.workerGetSeeingData, url)
        self.worker.signals.finished.connect(self.processSeeingData)
        self.worker.signals.result.connect(self.sendStatus)
        self.threadPool.start(self.worker)

    def loadingFileNeeded(self, fileName: Path, hours: float) -> bool:
        """ """
        filePath = self.app.mwGlob["dataDir"] / fileName
        if not os.path.isfile(filePath):
            return True

        ageData = self.app.mount.obsSite.loader.days_old(fileName)
        if ageData < hours / 24:
            return False
        else:
            return True

    def pollSeeingData(self) -> None:
        """ """
        if not self.enabled:
            return
        if not self.apiKey or not self.b:
            return

        if not self.online and self.running:
            self.signals.deviceDisconnected.emit("SeeingWeather")
            self.running = False
            return
        elif self.online and not self.running:
            self.signals.deviceConnected.emit("SeeingWeather")
            self.running = True

        if not self.loadingFileNeeded("meteoblue.data", 0.5):
            self.processSeeingData()
            return

        lat = self.location.latitude.degrees
        lon = self.location.longitude.degrees

        webSite = f"http://{self.hostaddress}/feed/seeing_json"
        url = f"{webSite}?lat={lat:1.2f}&lon={lon:1.2f}&tz=utc"
        self.getSeeingData(url=url + f"&apikey={self.b}")
        self.log.debug(f"{url}")
