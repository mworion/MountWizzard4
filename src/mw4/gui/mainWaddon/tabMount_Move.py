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
# Licence APL2.0
#
###########################################################
from functools import partial
from mw4.gui.mainWaddon.slewInterface import SlewInterface
from mw4.gui.utilities.toolsQtWidget import changeStyleDynamic, clickable, sleepAndEvents
from mw4.mountcontrol.convert import (
    convertDecToAngle,
    convertRaToAngle,
    formatDstrToText,
    formatHstrToText,
    valueToAngle,
)
from PySide6.QtWidgets import QInputDialog, QLineEdit
from skyfield.api import Angle


class MountMove:
    """ """

    def __init__(self, mainW):
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.slewInterface = SlewInterface(self)

        self.slewSpeeds = {
            "max": {
                "button": self.ui.slewSpeedMax,
                "func": self.app.mount.setting.setSlewSpeedMax,
            },
            "high": {
                "button": self.ui.slewSpeedHigh,
                "func": self.app.mount.setting.setSlewSpeedHigh,
            },
            "med": {
                "button": self.ui.slewSpeedMed,
                "func": self.app.mount.setting.setSlewSpeedMed,
            },
            "low": {
                "button": self.ui.slewSpeedLow,
                "func": self.app.mount.setting.setSlewSpeedLow,
            },
        }

        self.setupMoveClassic = {
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

        self.setupMoveAltAz = {
            "N": {"button": self.ui.moveNorthAltAz, "coord": [1, 0]},
            "NE": {"button": self.ui.moveNorthEastAltAz, "coord": [1, 1]},
            "E": {"button": self.ui.moveEastAltAz, "coord": [0, 1]},
            "SE": {"button": self.ui.moveSouthEastAltAz, "coord": [-1, 1]},
            "S": {"button": self.ui.moveSouthAltAz, "coord": [-1, 0]},
            "SW": {"button": self.ui.moveSouthWestAltAz, "coord": [-1, -1]},
            "W": {"button": self.ui.moveWestAltAz, "coord": [-1, 0]},
            "NW": {"button": self.ui.moveNorthWestAltAz, "coord": [1, -1]},
        }

        self.setupStepsizes = {
            "Stepsize 0.25°": 0.25,
            "Stepsize 0.5°": 0.5,
            "Stepsize 1.0°": 1,
            "Stepsize 2.0°": 2,
            "Stepsize 5.0°": 5,
            "Stepsize 10°": 10,
            "Stepsize 20°": 20,
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
        self.app.mount.signals.slewed.connect(self.moveAltAzDefault)
        self.app.gameDirection.connect(self.moveAltAzGameController)
        self.app.game_sR.connect(self.moveClassicGameController)
        self.setupGuiMount()

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("mainW", {})
        self.ui.slewSpeedMax.setChecked(config.get("slewSpeedMax", False))
        self.ui.slewSpeedHigh.setChecked(config.get("slewSpeedHigh", False))
        self.ui.slewSpeedMed.setChecked(config.get("slewSpeedMed", False))
        self.ui.slewSpeedLow.setChecked(config.get("slewSpeedLow", True))
        self.ui.moveDuration.setCurrentIndex(config.get("moveDuration", 0))
        self.ui.moveStepSizeAltAz.setCurrentIndex(config.get("moveStepSizeAltAz", 0))

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["slewSpeedMax"] = self.ui.slewSpeedMax.isChecked()
        config["slewSpeedHigh"] = self.ui.slewSpeedHigh.isChecked()
        config["slewSpeedMed"] = self.ui.slewSpeedMed.isChecked()
        config["slewSpeedLow"] = self.ui.slewSpeedLow.isChecked()
        config["moveDuration"] = self.ui.moveDuration.currentIndex()
        config["moveStepSizeAltAz"] = self.ui.moveStepSizeAltAz.currentIndex()

    def setupGuiMount(self) -> None:
        """ """
        for direction in self.setupMoveClassic:
            self.setupMoveClassic[direction]["button"].clicked.connect(
                partial(self.moveClassic, direction)
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
        """ """
        for uiR in self.setupMoveClassic:
            changeStyleDynamic(self.setupMoveClassic[uiR]["button"], "run", False)
        self.app.mount.obsSite.stopMoveAll()

    def countDuration(self, duration: int) -> None:
        """ """
        for t in range(duration * 10, -1, -1):
            self.ui.stopMoveAll.setText(f"{t / 10:.1f}s")
            sleepAndEvents(100)
        self.ui.stopMoveAll.setText("STOP")

    def moveDuration(self) -> None:
        """ """
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

    def moveClassicGameController(self, decVal: int, raVal: int) -> None:
        """ """
        dirRa = 0
        dirDec = 0
        if raVal < 64:
            dirRa = 1
        elif raVal > 192:
            dirRa = -1
        if decVal < 64:
            dirDec = -1
        elif decVal > 192:
            dirDec = 1

        direction = [dirRa, dirDec]
        if direction == [0, 0]:
            self.stopMoveAll()
        else:
            self.moveClassic(direction)

    def moveClassic(self, direction: str) -> None:
        """ """
        uiList = self.setupMoveClassic
        for key in uiList:
            changeStyleDynamic(uiList[key]["button"], "run", False)

        changeStyleDynamic(uiList[direction]["button"], "run", True)

        coord = uiList[direction]["coord"]
        if coord[0] == 1:
            self.app.mount.obsSite.moveNorth()
        elif coord[0] == -1:
            self.app.mount.obsSite.moveSouth()
        elif coord[0] == 0:
            self.app.mount.obsSite.stopMoveNorth()
            self.app.mount.obsSite.stopMoveSouth()

        if coord[1] == 1:
            self.app.mount.obsSite.moveEast()
        elif coord[1] == -1:
            self.app.mount.obsSite.moveWest()
        elif coord[1] == 0:
            self.app.mount.obsSite.stopMoveEast()
            self.app.mount.obsSite.stopMoveWest()

        self.moveDuration()

    def setSlewSpeed(self, speed):
        """ """
        self.slewSpeeds[speed]["func"]()

    def moveAltAzDefault(self) -> None:
        """ """
        for key in self.setupMoveAltAz:
            changeStyleDynamic(self.setupMoveAltAz[key]["button"], "run", False)

    def moveAltAzGameController(self, value: int) -> None:
        """ """
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
        """ """
        uiList = self.setupMoveAltAz
        changeStyleDynamic(uiList[direction]["button"], "run", True)

        key = list(self.setupStepsizes)[self.ui.moveStepSizeAltAz.currentIndex()]
        step = self.setupStepsizes[key]

        coord = self.setupMoveAltAz[direction]["coord"]
        targetAlt = self.targetAlt = Angle(degrees=self.targetAlt.degrees + coord[0] * step)
        targetAz = self.targetAz = Angle(
            degrees=(self.targetAz.degrees + coord[1] * step) % 360
        )
        self.slewInterface.slewTargetAltAz(targetAlt, targetAz)

    def checkRaDecInputs(self) -> None:
        """ """
        canSlew = self.app.mount.obsSite.setTargetRaDec(self.targetRa, self.targetDec)
        self.ui.moveRaDecAbsolute.setEnabled(canSlew)

    def setRA(self) -> None:
        """ """
        dlg = QInputDialog()
        value, ok = dlg.getText(
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
        """ """
        dlg = QInputDialog()
        value, ok = dlg.getText(
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
        """ """
        canSlew = self.app.mount.obsSite.setTargetAltAz(self.targetAlt, self.targetAz)
        self.ui.moveAltAzAbsolute.setEnabled(canSlew)

    def setAlt(self) -> None:
        """ """
        alt = self.ui.moveCoordinateAlt.text()
        self.targetAlt = valueToAngle(alt, preference="degrees")
        self.checkAltAzInputs()

    def setAz(self) -> None:
        """ """
        az = self.ui.moveCoordinateAz.text()
        self.targetAz = valueToAngle(az, preference="degrees")
        self.checkAltAzInputs()

    def moveAltAzAbsolute(self) -> None:
        """ """
        self.slewInterface.slewTargetAltAz(self.targetAlt, self.targetAz)

    def moveRaDecAbsolute(self) -> None:
        """ """
        self.slewInterface.slewTargetRaDec(self.targetRa, self.targetDec)
