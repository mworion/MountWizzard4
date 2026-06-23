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
from collections.abc import Callable
from functools import partial
from mw4.base.threadUtils import mainThreadSleep
from mw4.gui.mainWaddon.slewInterface import SlewInterface
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, clickable
from mw4.gui.utilities.qtInputDialog import MWInputDialog
from mw4.mountcontrol.convert import (
    convertDecToAngle,
    convertRaToAngle,
    formatDstrToText,
    formatHstrToText,
    valueToAngle,
)
from PySide6.QtWidgets import QLineEdit
from pytestqt.qtbot import QWidget
from skyfield.api import Angle
from typing import Any


class MountMove(TabAddon):
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.slewInterface = SlewInterface(self)

        self.slewSpeeds: dict[str, dict[str, QWidget | Callable]] = {
            "max": {
                "button": self.ui.slewSpeedMax,
                "func": self.app.dReg["mount"].setting.setSlewSpeedMax,
            },
            "high": {
                "button": self.ui.slewSpeedHigh,
                "func": self.app.dReg["mount"].setting.setSlewSpeedHigh,
            },
            "med": {
                "button": self.ui.slewSpeedMed,
                "func": self.app.dReg["mount"].setting.setSlewSpeedMed,
            },
            "low": {
                "button": self.ui.slewSpeedLow,
                "func": self.app.dReg["mount"].setting.setSlewSpeedLow,
            },
        }

        self.setupMoveClassic: dict[str, dict[str, Any]] = {
            "N": {"button": self.ui.moveNorth, "coord": [1, 0]},
            "NE": {"button": self.ui.moveNorthEast, "coord": [1, 1]},
            "E": {"button": self.ui.moveEast, "coord": [0, 1]},
            "SE": {"button": self.ui.moveSouthEast, "coord": [-1, 1]},
            "S": {"button": self.ui.moveSouth, "coord": [-1, 0]},
            "SW": {"button": self.ui.moveSouthWest, "coord": [-1, -1]},
            "W": {"button": self.ui.moveWest, "coord": [0, -1]},
            "NW": {"button": self.ui.moveNorthWest, "coord": [1, -1]},
            "STOP": {"button": self.ui.stopMoveAll, "coord": [0, 0]},
        }

        self.setupMoveAltAz: dict[str, dict[str, Any]] = {
            "N": {"button": self.ui.moveNorthAltAz, "coord": [1, 0]},
            "NE": {"button": self.ui.moveNorthEastAltAz, "coord": [1, 1]},
            "E": {"button": self.ui.moveEastAltAz, "coord": [0, 1]},
            "SE": {"button": self.ui.moveSouthEastAltAz, "coord": [-1, 1]},
            "S": {"button": self.ui.moveSouthAltAz, "coord": [-1, 0]},
            "SW": {"button": self.ui.moveSouthWestAltAz, "coord": [-1, -1]},
            "W": {"button": self.ui.moveWestAltAz, "coord": [-1, 0]},
            "NW": {"button": self.ui.moveNorthWestAltAz, "coord": [1, -1]},
        }

        self.setupStepsizes: dict[str, float] = {
            "Stepsize 0.25°": 0.25,
            "Stepsize 0.5°": 0.5,
            "Stepsize 1.0°": 1.0,
            "Stepsize 2.0°": 2.0,
            "Stepsize 5.0°": 5.0,
            "Stepsize 10°": 10.0,
            "Stepsize 20°": 20.0,
        }
        self.targetAlt: Angle = Angle(degrees=0)
        self.targetAz: Angle = Angle(degrees=0)
        self.targetRa: Angle = Angle(hours=0)
        self.targetDec: Angle = Angle(degrees=0)
        self.ui.stopMoveAll.clicked.connect(self.stopMoveAll)
        self.ui.moveAltAzAbsolute.clicked.connect(self.moveAltAzAbsolute)
        self.ui.moveRaDecAbsolute.clicked.connect(self.moveRaDecAbsolute)
        clickable(self.ui.moveCoordinateRa).connect(self.setRA)
        clickable(self.ui.moveCoordinateDec).connect(self.setDEC)
        self.ui.moveCoordinateAlt.textEdited.connect(self.setAlt)
        self.ui.moveCoordinateAz.textEdited.connect(self.setAz)
        self.app.dReg["mount"].signals.slewed.connect(self.moveAltAzDefault)
        self.app.dReg["hidController"].signals.hidDirection.connect(self.moveAltAzHid)
        self.app.dReg["hidController"].signals.hidSR.connect(self.moveRaDecHid)
        self.setupGuiMount()

    def initConfig(self) -> None:
        config = self.app.config.get("WindowMain", {})
        self.ui.slewSpeedMax.setChecked(config.get("slewSpeedMax", False))
        self.ui.slewSpeedHigh.setChecked(config.get("slewSpeedHigh", False))
        self.ui.slewSpeedMed.setChecked(config.get("slewSpeedMed", False))
        self.ui.slewSpeedLow.setChecked(config.get("slewSpeedLow", True))
        self.ui.moveDuration.setCurrentIndex(config.get("moveDuration", 0))
        self.ui.moveStepSizeAltAz.setCurrentIndex(config.get("moveStepSizeAltAz", 0))

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["slewSpeedMax"] = self.ui.slewSpeedMax.isChecked()
        config["slewSpeedHigh"] = self.ui.slewSpeedHigh.isChecked()
        config["slewSpeedMed"] = self.ui.slewSpeedMed.isChecked()
        config["slewSpeedLow"] = self.ui.slewSpeedLow.isChecked()
        config["moveDuration"] = self.ui.moveDuration.currentIndex()
        config["moveStepSizeAltAz"] = self.ui.moveStepSizeAltAz.currentIndex()

    def setupGuiMount(self) -> None:
        for direction in self.setupMoveClassic:
            self.setupMoveClassic[direction]["button"].clicked.connect(
                partial(self.moveRaDec, direction)
            )

        for direction in self.setupMoveAltAz:
            self.setupMoveAltAz[direction]["button"].clicked.connect(
                partial(self.moveAltAz, direction)
            )

        for speed in self.slewSpeeds:
            self.slewSpeeds[speed]["button"].clicked.connect(partial(self.setSlewSpeed, speed))

        self.ui.moveStepSizeAltAz.clear()
        for text in self.setupStepsizes:
            self.ui.moveStepSizeAltAz.addItem(text)

    def stopMoveAll(self) -> None:
        self.app.dReg["mount"].obsSite.stopMoveAll()
        mainThreadSleep(250)
        for uiR in self.setupMoveClassic:
            changeStyleDynamic(self.setupMoveClassic[uiR]["button"], "run", False)

    def countDuration(self, duration: int) -> None:
        for t in range(duration * 10, -1, -1):
            self.ui.stopMoveAll.setText(f"{t / 10:.1f}s")
            mainThreadSleep(100)
        self.ui.stopMoveAll.setText("STOP")

    def moveDuration(self) -> None:
        if self.ui.moveDuration.currentIndex() == 1:
            self.countDuration(10)
        elif self.ui.moveDuration.currentIndex() == 2:
            self.countDuration(5)
        elif self.ui.moveDuration.currentIndex() == 3:
            self.countDuration(2)
        elif self.ui.moveDuration.currentIndex() == 4:
            self.countDuration(1)
        else:
            return
        self.stopMoveAll()

    def convertDirection(self, directionVector: list[int]) -> str:
        for direction in self.setupMoveClassic:
            if self.setupMoveClassic[direction]["coord"] == directionVector:
                return direction
        return "STOP"

    def moveRaDecHid(self, decVal: int, raVal: int) -> None:
        dirRa = 0
        dirDec = 0
        if raVal < 108:
            dirRa = 1
        elif raVal > 152:
            dirRa = -1
        if decVal < 108:
            dirDec = -1
        elif decVal > 152:
            dirDec = 1

        directionVector = [dirRa, dirDec]
        direction = self.convertDirection(directionVector)
        self.moveRaDec(direction)

    def moveRaDec(self, direction: str) -> None:
        uiList = self.setupMoveClassic
        for key in uiList:
            changeStyleDynamic(uiList[key]["button"], "run", False)
        changeStyleDynamic(uiList[direction]["button"], "run", True)

        coord = uiList[direction]["coord"]
        if coord == [0, 0]:
            self.stopMoveAll()

        if coord[0] == 1:
            self.app.dReg["mount"].obsSite.moveNorth()
        elif coord[0] == -1:
            self.app.dReg["mount"].obsSite.moveSouth()
        elif coord[0] == 0:
            self.app.dReg["mount"].obsSite.stopMoveNorth()
            self.app.dReg["mount"].obsSite.stopMoveSouth()

        if coord[1] == 1:
            self.app.dReg["mount"].obsSite.moveEast()
        elif coord[1] == -1:
            self.app.dReg["mount"].obsSite.moveWest()
        elif coord[1] == 0:
            self.app.dReg["mount"].obsSite.stopMoveEast()
            self.app.dReg["mount"].obsSite.stopMoveWest()

        self.moveDuration()

    def setSlewSpeed(self, speed):
        self.slewSpeeds[speed]["func"]()

    def moveAltAzDefault(self) -> None:
        for key in self.setupMoveAltAz:
            changeStyleDynamic(self.setupMoveAltAz[key]["button"], "run", False)

    def moveAltAzHid(self, value: int) -> None:
        if value == 0b00000000:
            direction = "N"
        elif value == 0b00000010:
            direction = "E"
        elif value == 0b00000100:
            direction = "W"
        elif value == 0b00000110:
            direction = "S"
        else:
            return
        self.moveAltAz(direction)

    def moveAltAz(self, direction: str) -> None:
        changeStyleDynamic(self.setupMoveAltAz[direction]["button"], "run", True)
        step = self.setupStepsizes[self.ui.moveStepSizeAltAz.currentText()]
        coord = self.setupMoveAltAz[direction]["coord"]
        obs = self.app.dReg["mount"].obsSite
        targetAlt = Angle(degrees=obs.Alt.degrees + coord[0] * step)
        targetAz = Angle(degrees=(obs.Az.degrees + coord[1] * step) % 360)
        self.slewInterface.slewTargetAltAz(targetAlt, targetAz)

    def checkRaDecInputs(self) -> None:
        canSlew = self.app.dReg["mount"].obsSite.setTargetRaDec(self.targetRa, self.targetDec)
        self.ui.moveRaDecAbsolute.setEnabled(canSlew)

    def setRA(self) -> None:
        value, ok = MWInputDialog.getText(
            self.mainW,
            "Set telescope RA",
            "Format: <dd[H] mm ss.s> in hours or <[+]d.d> in degrees",
            QLineEdit.EchoMode.Normal,
            self.ui.moveCoordinateRa.text(),
        )
        if not ok:
            return
        valueFormat = convertRaToAngle(value)
        text = formatHstrToText(valueFormat)
        self.ui.moveCoordinateRa.setText(text)
        self.ui.moveCoordinateRaFloat.setText(f"{valueFormat.hours:2.4f}")
        self.checkRaDecInputs()

    def setDEC(self) -> None:
        value, ok = MWInputDialog.getText(
            self.mainW,
            "Set telescope DEC",
            "Format: <dd[Deg] mm ss.s> or <[+]d.d> in degrees",
            QLineEdit.EchoMode.Normal,
            self.ui.moveCoordinateDec.text(),
        )
        if not ok:
            return
        valueFormat = convertDecToAngle(value)
        text = formatDstrToText(valueFormat)
        self.ui.moveCoordinateDec.setText(text)
        self.ui.moveCoordinateDecFloat.setText(f"{valueFormat.degrees:2.4f}")
        self.checkRaDecInputs()

    def checkAltAzInputs(self) -> None:
        canSlew = self.app.dReg["mount"].obsSite.setTargetAltAz(self.targetAlt, self.targetAz)
        self.ui.moveAltAzAbsolute.setEnabled(canSlew)

    def setAlt(self) -> None:
        alt = self.ui.moveCoordinateAlt.text()
        self.targetAlt = valueToAngle(alt, preference="degrees")
        self.checkAltAzInputs()

    def setAz(self) -> None:
        az = self.ui.moveCoordinateAz.text()
        self.targetAz = valueToAngle(az, preference="degrees")
        self.checkAltAzInputs()

    def moveAltAzAbsolute(self) -> None:
        self.slewInterface.slewTargetAltAz(self.targetAlt, self.targetAz)

    def moveRaDecAbsolute(self) -> None:
        self.slewInterface.slewTargetRaDec(self.targetRa, self.targetDec)
