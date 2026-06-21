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
from functools import partial
from mw4.mountcontrol.convert import valueToFloat
from typing import Any


class SettPark:
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.parkTexts: list = []
        self.parkAlt: list = []
        self.parkAz: list = []
        self.parkSaveButtons: list = []

        for i in range(10):
            self.parkSaveButtons.append(getattr(self.ui, f"parkSave{i:1d}"))
            self.parkTexts.append(getattr(self.ui, f"parkText{i:1d}"))
            self.parkAlt.append(getattr(self.ui, f"parkAlt{i:1d}"))
            self.parkAz.append(getattr(self.ui, f"parkAz{i:1d}"))

    def initConfig(self) -> None:
        config = self.app.config.get("SettingPark", {})
        for i in range(10):
            self.parkTexts[i].setText(config.get(f"ParkText{i:1d}"))
            self.parkAlt[i].setValue(valueToFloat(config.get(f"ParkAlt{i:1d}", 0)))
            self.parkAz[i].setValue(valueToFloat(config.get(f"ParkAz{i:1d}", 0)))
        for i in range(10):
            self.parkTexts[i].textChanged.connect(self.storeConfig)
            self.parkSaveButtons[i].clicked.connect(partial(self.saveActualPosition, i))
        self.app.parkChanged.emit()

    def storeConfig(self) -> None:
        self.app.config["SettingPark"] = {}
        config = self.app.config["SettingPark"]
        for i in range(10):
            config[f"ParkText{i:1d}"] = self.parkTexts[i].text()
            config[f"ParkAlt{i:1d}"] = self.parkAlt[i].value()
            config[f"ParkAz{i:1d}"] = self.parkAz[i].value()
        self.app.parkChanged.emit()

    def setupIcons(self) -> None:
        for i in range(10):
            self.parentW.wIcon(getattr(self.ui, f"parkSave{i:1d}"), "download")

    def saveActualPosition(self, index: int) -> None:
        obs = self.app.dReg["mount"].obsSite
        self.parkAlt[index].setValue(obs.Alt.degrees)
        self.parkAz[index].setValue(obs.Az.degrees)
        self.storeConfig()
