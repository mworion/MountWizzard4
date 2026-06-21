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
from mw4.gui.mainWaddon.tabAddon import TabAddon
from skyfield.api import Angle
from typing import Any


class Park(TabAddon):
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.parkButtons: list = []
        for i in range(10):
            self.parkButtons.append(getattr(self.ui, f"parkButton{i:1d}"))
            self.parkButtons[i].setEnabled(False)
            self.parkButtons[i].clicked.connect(partial(self.slewToPark, i))
        self.app.parkChanged.connect(self.updateParkButtonText)

    def initConfig(self) -> None:
        config = self.app.config.get("MountPark", {})
        self.mainW.ui.parkMountAfterSlew.setChecked(config.get("ParkMountAfterSlew", False))

    def storeConfig(self) -> None:
        self.app.config["MountPark"] = {}
        config = self.app.config["MountPark"]
        config["ParkMountAfterSlew"] = self.mainW.ui.parkMountAfterSlew.isChecked()

    def updateParkButtonText(self) -> None:
        config = self.app.config.get("SettingPark", {})
        for i in range(10):
            text = config.get(f"ParkText{i:1d}")
            self.parkButtons[i].setText(text)
            self.parkButtons[i].setEnabled(bool(text))
            icon = "park" if bool(text) else "question"
            self.mainW.wIcon(self.parkButtons[i], icon)

    def parkAtPos(self) -> None:
        self.app.dReg["mount"].signals.slewed.disconnect(self.parkAtPos)
        if not self.app.dReg["mount"].obsSite.parkOnActualPosition():
            self.msg.emit(2, "Mount", "Command", "Cannot park at current position")

    def slewToPark(self, index: int) -> None:
        config = self.app.config.get("SettingPark", {})
        altValue = Angle(degrees=config.get(f"ParkAlt{index:1d}"))
        azValue = Angle(degrees=config.get(f"ParkAz{index:1d}"))
        parkTextValue = config.get(f"ParkText{index:1d}")
        if not self.app.dReg["mount"].obsSite.setTargetAltAz(altValue, azValue):
            self.msg.emit(2, "Mount", "Command error", f"Cannot slew to [{parkTextValue}]")
            return
        if not self.app.dReg["mount"].obsSite.startSlewing(slewType="notrack"):
            self.msg.emit(2, "Mount", "Command error", f"Cannot slew to [{parkTextValue}]")
            return
        self.msg.emit(0, "Mount", "Command", f"Slew to [{parkTextValue}]")
        if not self.ui.parkMountAfterSlew.isChecked():
            return
        self.app.dReg["mount"].signals.slewed.connect(self.parkAtPos)
