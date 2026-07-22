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
from enum import Enum
from functools import partial
from mw4.base.threadUtils import mainThreadSleep
from mw4.gui.mainWaddon.slewInterface import SlewInterface
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.nativeQt.qtInputDialog import MWInputDialog
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, clickable
from mw4.mountcontrol.convert import (
    convertDecToAngle,
    convertRaToAngle,
    formatDstrToText,
    formatHstrToText,
    valueToAngle,
)
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget
from skyfield.api import Angle
from typing import Any


class StepSize(Enum):
    """Enum for Alt/Az movement step sizes."""

    Step025 = (0.25, "Stepsize 0.25°")
    Step05 = (0.5, "Stepsize 0.5°")
    Step10 = (1.0, "Stepsize 1.0°")
    Step20 = (2.0, "Stepsize 2.0°")
    Step50 = (5.0, "Stepsize 5.0°")
    Step100 = (10.0, "Stepsize 10°")
    Step200 = (20.0, "Stepsize 20°")

    @property
    def valueDegrees(self) -> float:
        """Get the step size value in degrees."""
        return self.value[0]

    @property
    def displayText(self) -> str:
        """Get the display text for the step size."""
        return self.value[1]


class MountMove(TabAddon):
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.slewInterface = SlewInterface(self)
        self.oldDirection: str = "STOP"
        self.durationTimer: QTimer | None = None
        self.countdownRemaining: int = 0

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

        self.setButtons: dict[str, dict[str, Any]] = {
            "N": {
                "buttonRaDec": self.ui.moveNorth,
                "buttonAltAz": self.ui.moveNorthAltAz,
                "coord": [1, 0],
            },
            "NE": {
                "buttonRaDec": self.ui.moveNorthEast,
                "buttonAltAz": self.ui.moveNorthEastAltAz,
                "coord": [1, 1],
            },
            "E": {
                "buttonRaDec": self.ui.moveEast,
                "buttonAltAz": self.ui.moveEastAltAz,
                "coord": [0, 1],
            },
            "SE": {
                "buttonRaDec": self.ui.moveSouthEast,
                "buttonAltAz": self.ui.moveSouthEastAltAz,
                "coord": [-1, 1],
            },
            "S": {
                "buttonRaDec": self.ui.moveSouth,
                "buttonAltAz": self.ui.moveSouthAltAz,
                "coord": [-1, 0],
            },
            "SW": {
                "buttonRaDec": self.ui.moveSouthWest,
                "buttonAltAz": self.ui.moveSouthWestAltAz,
                "coord": [-1, -1],
            },
            "W": {
                "buttonRaDec": self.ui.moveWest,
                "buttonAltAz": self.ui.moveWestAltAz,
                "coord": [0, -1],
            },
            "NW": {
                "buttonRaDec": self.ui.moveNorthWest,
                "buttonAltAz": self.ui.moveNorthWestAltAz,
                "coord": [1, -1],
            },
            "STOP": {
                "buttonRaDec": self.ui.stopMoveAll,
                "buttonAltAz": self.ui.stopMoveAll,
                "coord": [0, 0],
            },
        }

        # Build reverse-lookup dictionary for direction vectors
        self.directionByVector: dict[tuple[int, int], str] = {}
        for k, v in self.setButtons.items():
            coord_tuple = (v["coord"][0], v["coord"][1])
            self.directionByVector[coord_tuple] = k

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
        for d in self.setButtons:
            self.setButtons[d]["buttonRaDec"].clicked.connect(partial(self.moveRaDec, d))
            self.setButtons[d]["buttonAltAz"].clicked.connect(partial(self.moveAltAz, d))
        for s in self.slewSpeeds:
            self.slewSpeeds[s]["button"].clicked.connect(partial(self.setSlewSpeed, s))
        self.ui.moveStepSizeAltAz.clear()
        for step_size in StepSize:
            self.ui.moveStepSizeAltAz.addItem(step_size.displayText)

    def stopMoveAll(self) -> None:
        self.app.dReg["mount"].obsSite.stopMoveAll()
        mainThreadSleep(250)
        for key in self.setButtons:
            changeStyleDynamic(self.setButtons[key]["buttonRaDec"], "run", "false")
            changeStyleDynamic(self.setButtons[key]["buttonAltAz"], "run", "false")

    def startDurationTimer(self) -> None:
        """Start a timer for the move duration countdown."""
        if self.durationTimer is not None:
            self.durationTimer.stop()
        self.durationTimer = QTimer()
        self.durationTimer.setInterval(100)
        self.durationTimer.timeout.connect(self.onDurationTick)
        self.countdownRemaining = 10 * self.ui.moveDuration.currentIndex()
        self.durationTimer.start()

    def onDurationTick(self) -> None:
        """Handle duration timer tick."""
        if self.countdownRemaining > 0:
            self.ui.stopMoveAll.setText(f"{self.countdownRemaining / 10:.1f}s")
            self.countdownRemaining -= 1
        else:
            if self.durationTimer is not None:
                self.durationTimer.stop()
            self.ui.stopMoveAll.setText("STOP")
            self.stopMoveAll()

    def moveDuration(self) -> None:
        if self.ui.moveDuration.currentIndex() == 0:
            return
        self.startDurationTimer()

    def convertDirection(self, directionVector: list[int]) -> str:
        """Convert a direction vector to a direction string."""
        return self.directionByVector.get(tuple(directionVector), "STOP")  # type: ignore

    def moveRaDec(self, direction: str) -> None:
        uiList = self.setButtons
        for key in uiList:
            changeStyleDynamic(uiList[key]["buttonRaDec"], "run", "false")
            changeStyleDynamic(uiList[direction]["buttonRaDec"], "run", "true")
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
        if direction != self.oldDirection:
            self.moveRaDec(direction)
            self.oldDirection = direction

    def setSlewSpeed(self, speed: str) -> None:
        self.slewSpeeds[speed]["func"]()

    def moveAltAzDefault(self) -> None:
        for key in self.setButtons:
            changeStyleDynamic(self.setButtons[key]["buttonAltAz"], "run", "false")

    def moveAltAz(self, direction: str) -> None:
        changeStyleDynamic(self.setButtons[direction]["buttonAltAz"], "run", "true")
        stepSizeText = self.ui.moveStepSizeAltAz.currentText()
        step = next(s.valueDegrees for s in StepSize if s.displayText == stepSizeText)
        coord = self.setButtons[direction]["coord"]
        obs = self.app.dReg["mount"].obsSite
        targetAlt = Angle(degrees=obs.Alt.degrees + coord[0] * step)
        targetAz = Angle(degrees=(obs.Az.degrees + coord[1] * step) % 360)
        self.slewInterface.slewTargetAltAz(targetAlt, targetAz)

    def moveAltAzHid(self, value: int) -> None:
        if value == 0b00000000:
            direction = "N"
        elif value == 0b00000010:
            direction = "E"
        elif value == 0b00000100:
            direction = "S"
        elif value == 0b00000110:
            direction = "W"
        else:
            return
        self.moveAltAz(direction)

    def checkRaDecInputs(self) -> None:
        canSlew = self.app.dReg["mount"].obsSite.setTargetRaDec(self.targetRa, self.targetDec)
        self.ui.moveRaDecAbsolute.setEnabled(canSlew)

    def setRA(self) -> None:
        value, ok = MWInputDialog.getText(
            self.mainW,
            "Set telescope RA",
            "Format: <dd[H] mm ss.s> in hours or <[+]d.d> in degrees",
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
