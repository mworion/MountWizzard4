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


class BoltwoodWeather:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, parent):
        self.parent = parent
        self.app = parent.app
        self.signals = parent.signals

        # minimum set for driver package built in
        self.framework = ""
        self.run: dict = {"boltwood": self}
        self.deviceName: str = ""
        self.data: dict = {}
        self.worker: Worker = None
        self.defaultConfig = {
            "framework": "",
            "frameworks": {
                "boltwood": {
                    "deviceName": "boltwood",
                    "filePath": self.app.mwGlob["dataDir"],
                }
            },
        }
        self.app.update30s.connect(self.pollBoltwoodData)

    def startCommunication(self) -> None:
        """ """
        self.signals.deviceConnected.emit("BoltwoodWeather")
        self.pollBoltwoodData()

    def stopCommunication(self) -> None:
        """ """
        self.data.clear()
        self.signals.deviceDisconnected.emit("SeeingWeather")

    def pollBoltwoodData(self) -> None:
        """ """
        pass