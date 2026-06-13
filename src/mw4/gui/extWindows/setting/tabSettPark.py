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
from mw4.mountcontrol.convert import valueToFloat
from skyfield.api import Angle
from typing import Any


class SettPark:
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui

        self.posButtons = {}
        self.posTexts = {}
        self.posAlt = {}
        self.posAz = {}
        self.posSaveButtons = {}

        for i in range(0, 10):
            # Use getattr() instead of eval() to safely resolve UI widget names. (SEC-2)
            # self.posButtons[i] = getattr(self.ui, f"posButton{i:1d}")
            self.posSaveButtons[i] = getattr(self.ui, f"posSave{i:1d}")

            self.posTexts[i] = getattr(self.ui, f"posText{i:1d}")
            self.posAlt[i] = getattr(self.ui, f"posAlt{i:1d}")
            self.posAz[i] = getattr(self.ui, f"posAz{i:1d}")

        for index in self.posTexts:
            self.posTexts[index].editingFinished.connect(self.updateParkPosButtonText)
        # for index in self.posButtons:
        #    self.posButtons[index].clicked.connect(partial(self.slewToParkPos, index))
        # for index in self.posSaveButtons:
        #    self.posButtons[index].clicked.connect(partial(self.saveActualPosition, index))

    def initConfig(self) -> None:
        config = self.app.config.get("SettingPark", {})
        for index in self.posTexts:
            keyConfig = f"posText{index:1d}"
            self.posTexts[index].setText(config.get(keyConfig, f"Park Pos {index:1d}"))
        for index in self.posAlt:
            keyConfig = f"posAlt{index:1d}"
            val = valueToFloat(config.get(keyConfig))
            if val:
                self.posAlt[index].setValue(val)
        for index in self.posAz:
            keyConfig = f"posAz{index:1d}"
            val = valueToFloat(config.get(keyConfig))
            if val:
                self.posAz[index].setValue(val)
        self.updateParkPosButtonText()
        self.parentW.app.mainW.ui.parkMountAfterSlew.setChecked(
            config.get("parkMountAfterSlew", False)
        )

    def storeConfig(self) -> None:
        self.app.config["SettingPark"] = {}
        config = self.app.config["SettingPark"]
        for index in self.posTexts:
            keyConfig = f"posText{index:1d}"
            config[keyConfig] = self.posTexts[index].text()
        for index in self.posAlt:
            keyConfig = f"posAlt{index:1d}"
            config[keyConfig] = self.posAlt[index].value()
        for index in self.posAz:
            keyConfig = f"posAz{index:1d}"
            config[keyConfig] = self.posAz[index].value()
        config["parkMountAfterSlew"] = self.parentW.app.mainW.ui.parkMountAfterSlew.isChecked()

    def setupIcons(self) -> None:
        self.parentW.wIcon(self.ui.posSave0, "download")
        self.parentW.wIcon(self.ui.posSave1, "download")
        self.parentW.wIcon(self.ui.posSave2, "download")
        self.parentW.wIcon(self.ui.posSave3, "download")
        self.parentW.wIcon(self.ui.posSave4, "download")
        self.parentW.wIcon(self.ui.posSave5, "download")
        self.parentW.wIcon(self.ui.posSave6, "download")
        self.parentW.wIcon(self.ui.posSave7, "download")
        self.parentW.wIcon(self.ui.posSave8, "download")
        self.parentW.wIcon(self.ui.posSave9, "download")

    def updateParkPosButtonText(self) -> None:
        for index in self.posButtons:
            text = self.posTexts[index].text()
            self.posButtons[index].setText(text)
            self.posButtons[index].setEnabled(text.strip() != "")

    def parkAtPos(self) -> None:
        self.app.dReg["mount"].signals.slewed.disconnect(self.parkAtPos)
        if not self.app.dReg["mount"].obsSite.parkOnActualPosition():
            self.msg.emit(2, "Mount", "Command", "Cannot park at current position")

    def slewToParkPos(self, index: int) -> None:
        altValue = self.posAlt[index].value()
        azValue = self.posAz[index].value()
        posTextValue = self.posTexts[index].text()

        if not self.app.dReg["mount"].obsSite.setTargetAltAz(
            alt=Angle(degrees=altValue), az=Angle(degrees=azValue)
        ):
            self.msg.emit(2, "Mount", "Command error", f"Cannot slew to [{posTextValue}]")
            return

        if not self.app.dReg["mount"].obsSite.startSlewing(slewType="notrack"):
            self.msg.emit(2, "Mount", "Command error", f"Cannot slew to [{posTextValue}]")
            return

        self.msg.emit(0, "Mount", "Command", f"Slew to [{posTextValue}]")
        if not self.ui.parkMountAfterSlew.isChecked():
            return

        self.app.dReg["mount"].signals.slewed.connect(self.parkAtPos)

    def saveActualPosition(self, index: int) -> None:
        obs = self.app.dReg["mount"].obsSite
        self.posAlt[index].setValue(obs.Alt.degrees)
        self.posAz[index].setValue(obs.Az.degrees)
