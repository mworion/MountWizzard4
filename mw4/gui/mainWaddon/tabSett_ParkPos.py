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

# external packages
from functools import partial
from skyfield.api import Angle
from PySide6.QtCore import QObject

# local import
from mountcontrol.convert import valueToFloat


class SettParkPos(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.posButtons = dict()
        self.posTexts = dict()
        self.posAlt = dict()
        self.posAz = dict()
        self.posSaveButtons = dict()

        for i in range(0, 10):
            self.posButtons[i] = eval("self.ui.posButton{0:1d}".format(i))
            self.posSaveButtons[i] = eval("self.ui.posSave{0:1d}".format(i))

            self.posTexts[i] = eval("self.ui.posText{0:1d}".format(i))
            self.posAlt[i] = eval("self.ui.posAlt{0:1d}".format(i))
            self.posAz[i] = eval("self.ui.posAz{0:1d}".format(i))

        for index in self.posTexts:
            self.posTexts[index].editingFinished.connect(self.updateParkPosButtonText)
        for index in self.posButtons:
            self.posButtons[index].clicked.connect(partial(self.slewToParkPos, index))
        for index in self.posSaveButtons:
            self.posButtons[index].clicked.connect(partial(self.saveActualPosition, index))

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
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
        self.ui.parkMountAfterSlew.setChecked(config.get("parkMountAfterSlew", False))

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        for index in self.posTexts:
            keyConfig = f"posText{index:1d}"
            config[keyConfig] = self.posTexts[index].text()
        for index in self.posAlt:
            keyConfig = f"posAlt{index:1d}"
            config[keyConfig] = self.posAlt[index].value()
        for index in self.posAz:
            keyConfig = f"posAz{index:1d}"
            config[keyConfig] = self.posAz[index].value()
        config["parkMountAfterSlew"] = self.ui.parkMountAfterSlew.isChecked()

    def setupIcons(self) -> None:
        """ """
        self.mainW.wIcon(self.ui.posSave0, "download")
        self.mainW.wIcon(self.ui.posSave1, "download")
        self.mainW.wIcon(self.ui.posSave2, "download")
        self.mainW.wIcon(self.ui.posSave3, "download")
        self.mainW.wIcon(self.ui.posSave4, "download")
        self.mainW.wIcon(self.ui.posSave5, "download")
        self.mainW.wIcon(self.ui.posSave6, "download")
        self.mainW.wIcon(self.ui.posSave7, "download")
        self.mainW.wIcon(self.ui.posSave8, "download")
        self.mainW.wIcon(self.ui.posSave9, "download")

    def updateParkPosButtonText(self) -> None:
        """ """
        for index in self.posButtons:
            text = self.posTexts[index].text()
            self.posButtons[index].setText(text)
            self.posButtons[index].setEnabled(text.strip() != "")

    def parkAtPos(self) -> None:
        """ """
        self.app.mount.signals.slewed.disconnect(self.parkAtPos)
        if not self.app.mount.obsSite.parkOnActualPosition():
            self.msg.emit(2, "Mount", "Command", "Cannot park at current position")

    def slewToParkPos(self, index: int) -> None:
        """ """
        altValue = self.posAlt[index].value()
        azValue = self.posAz[index].value()
        posTextValue = self.posTexts[index].text()

        if not self.app.mount.obsSite.setTargetAltAz(
            alt=Angle(degrees=altValue), az=Angle(degrees=azValue)
        ):
            self.msg.emit(2, "Mount", "Command error", f"Cannot slew to [{posTextValue}]")
            return

        if not self.app.mount.obsSite.startSlewing(slewType="notrack"):
            self.msg.emit(2, "Mount", "Command error", f"Cannot slew to [{posTextValue}]")
            return

        self.msg.emit(0, "Mount", "Command", f"Slew to [{posTextValue}]")
        if not self.ui.parkMountAfterSlew.isChecked():
            return

        self.app.mount.signals.slewed.connect(self.parkAtPos)

    def saveActualPosition(self, index: int) -> None:
        """ """
        obs = self.app.mount.obsSite
        if obs.Alt is None or obs.Az is None:
            return
        self.posAlt[index].setValue(obs.Alt.degrees)
        self.posAz[index].setValue(obs.Az.degrees)
