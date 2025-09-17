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
from functools import partial

# external packages
from PySide6.QtWidgets import QInputDialog, QLineEdit
from PySide6.QtCore import QObject

# local import
from gui.utilities.toolsQtWidget import sleepAndEvents
from mountcontrol.convert import convertRaToAngle, convertDecToAngle
from mountcontrol.convert import formatHstrToText, formatDstrToText
from mountcontrol.convert import valueToFloat
from gui.utilities.slewInterface import SlewInterface
from gui.utilities.toolsQtWidget import changeStyleDynamic, clickable


class MountMove(QObject, SlewInterface):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

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

        self.targetAlt = None
        self.targetAz = None
        self.slewSpeedSelected = None
        self.ui.stopMoveAll.clicked.connect(self.stopMoveAll)
        self.ui.moveAltAzAbsolute.clicked.connect(self.moveAltAzAbsolute)
        self.ui.moveRaDecAbsolute.clicked.connect(self.moveRaDecAbsolute)
        clickable(self.ui.moveCoordinateRa).connect(self.setRA)
        self.ui.moveCoordinateRa.textEdited.connect(self.setRA)
        self.ui.moveCoordinateRa.returnPressed.connect(self.setRA)
        clickable(self.ui.moveCoordinateDec).connect(self.setDEC)
        self.ui.moveCoordinateDec.textEdited.connect(self.setDEC)
        self.ui.moveCoordinateDec.returnPressed.connect(self.setDEC)
        self.app.mount.signals.slewed.connect(self.moveAltAzDefault)
        self.app.gameDirection.connect(self.moveAltAzGameController)
        self.app.game_sR.connect(self.moveClassicGameController)
        self.setupGuiMount()

    def initConfig(self):
        """ """
        config = self.app.config.get("mainW", {})
        self.ui.slewSpeedMax.setChecked(config.get("slewSpeedMax", True))
        self.ui.slewSpeedHigh.setChecked(config.get("slewSpeedHigh", False))
        self.ui.slewSpeedMed.setChecked(config.get("slewSpeedMed", False))
        self.ui.slewSpeedLow.setChecked(config.get("slewSpeedLow", False))
        self.ui.moveDuration.setCurrentIndex(config.get("moveDuration", 0))
        self.ui.moveStepSizeAltAz.setCurrentIndex(config.get("moveStepSizeAltAz", 0))

    def storeConfig(self):
        """ """
        config = self.app.config["mainW"]
        config["slewSpeedMax"] = self.ui.slewSpeedMax.isChecked()
        config["slewSpeedHigh"] = self.ui.slewSpeedHigh.isChecked()
        config["slewSpeedMed"] = self.ui.slewSpeedMed.isChecked()
        config["slewSpeedLow"] = self.ui.slewSpeedLow.isChecked()
        config["moveDuration"] = self.ui.moveDuration.currentIndex()
        config["moveStepSizeAltAz"] = self.ui.moveStepSizeAltAz.currentIndex()

    def setupGuiMount(self):
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

    def stopMoveAll(self):
        """ """
        for uiR in self.setupMoveClassic:
            changeStyleDynamic(self.setupMoveClassic[uiR]["button"], "running", False)
        self.app.mount.obsSite.stopMoveAll()

    def countDuration(self, duration):
        """ """
        for t in range(duration * 10, -1, -1):
            self.ui.stopMoveAll.setText(f"{t / 10:.1f}s")
            sleepAndEvents(100)
        self.ui.stopMoveAll.setText("STOP")

    def moveDuration(self):
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
            return False
        self.stopMoveAll()
        return True

    def moveClassicGameController(self, decVal, raVal):
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

    def moveClassic(self, direction):
        """ """
        uiList = self.setupMoveClassic
        for key in uiList:
            changeStyleDynamic(uiList[key]["button"], "running", False)

        changeStyleDynamic(uiList[direction]["button"], "running", True)

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

    def moveAltAzDefault(self):
        """
        :return:
        """
        self.targetAlt = None
        self.targetAz = None
        for key in self.setupMoveAltAz:
            changeStyleDynamic(self.setupMoveAltAz[key]["button"], "running", False)
        return True

    def moveAltAzGameController(self, value):
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
            return False
        self.moveAltAz(direction)
        return True

    def moveAltAz(self, direction):
        """ """
        alt = self.app.mount.obsSite.Alt
        az = self.app.mount.obsSite.Az
        if alt is None or az is None:
            return False

        uiList = self.setupMoveAltAz
        changeStyleDynamic(uiList[direction]["button"], "running", True)

        key = list(self.setupStepsizes)[self.ui.moveStepSizeAltAz.currentIndex()]
        step = self.setupStepsizes[key]

        coord = self.setupMoveAltAz[direction]["coord"]
        if self.targetAlt is None or self.targetAz is None:
            targetAlt = self.targetAlt = alt.degrees + coord[0] * step
            targetAz = self.targetAz = az.degrees + coord[1] * step
        else:
            targetAlt = self.targetAlt = self.targetAlt + coord[0] * step
            targetAz = self.targetAz = self.targetAz + coord[1] * step

        targetAz = targetAz % 360
        suc = self.slewTargetAltAz(targetAlt, targetAz)
        return suc

    def setRA(self):
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
            return False

        value = convertRaToAngle(value)
        if value is None:
            self.ui.moveCoordinateRaFloat.setText("")
            return False

        text = formatHstrToText(value)
        self.ui.moveCoordinateRa.setText(text)
        self.ui.moveCoordinateRaFloat.setText(f"{value.hours:2.4f}")
        return True

    def setDEC(self):
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
            return False

        value = convertDecToAngle(value)
        if value is None:
            self.ui.moveCoordinateDecFloat.setText("")
            return False

        text = formatDstrToText(value)
        self.ui.moveCoordinateDec.setText(text)
        self.ui.moveCoordinateDecFloat.setText(f"{value.degrees:2.4f}")
        return True

    def moveAltAzAbsolute(self):
        """ """
        alt = self.ui.moveCoordinateAlt.text()
        alt = valueToFloat(alt)
        if alt is None:
            return False

        az = self.ui.moveCoordinateAz.text()
        az = valueToFloat(az)
        if az is None:
            return False

        az = (az + 360) % 360
        suc = self.slewTargetAltAz(alt, az)
        return suc

    def moveRaDecAbsolute(self):
        """ """
        value = self.ui.moveCoordinateRa.text()
        ra = convertRaToAngle(value)
        if ra is None:
            return False

        value = self.ui.moveCoordinateDec.text()
        dec = convertDecToAngle(value)
        if dec is None:
            return False

        suc = self.slewTargetRaDec(ra, dec)
        return suc
