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
from ast import Bytes

# external packages
from PySide6.QtCore import QObject

# local import


class Mount(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()

        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.app.gameABXY.connect(self.changeParkGameController)
        self.app.gameABXY.connect(self.stopGameController)
        self.app.gameABXY.connect(self.changeTrackingGameController)
        self.app.gameABXY.connect(self.flipMountGameController)
        self.ui.flipMount.clicked.connect(self.flipMount)
        self.ui.tracking.clicked.connect(self.changeTracking)
        self.ui.setLunarTracking.clicked.connect(self.setLunarTracking)
        self.ui.setSiderealTracking.clicked.connect(self.setSiderealTracking)
        self.ui.setSolarTracking.clicked.connect(self.setSolarTracking)
        self.ui.park.clicked.connect(self.changePark)
        self.ui.stop.clicked.connect(self.stop)

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("mainW", {})
        self.ui.coordsJ2000.setChecked(config.get("coordsJ2000", False))
        self.ui.coordsJNow.setChecked(config.get("coordsJNow", False))

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["coordsJ2000"] = self.ui.coordsJ2000.isChecked()
        config["coordsJNow"] = self.ui.coordsJNow.isChecked()

    def changeTrackingGameController(self, value: bytes) -> None:
        """ """
        if value == 0b00000100:
            self.changeTracking()

    def changeTracking(self) -> None:
        """ """
        obs = self.app.mount.obsSite
        if obs.status == 0:
            if obs.stopTracking():
                self.msg.emit(0, "Mount", "Command", "Stopped tracking")
            else:
                self.msg.emit(2, "Mount", "Command", "Cannot stop tracking")
        else:
            if obs.startTracking():
                self.msg.emit(0, "Mount", "Command", "Started tracking")
            else:
                self.msg.emit(2, "Mount", "Command", "Cannot start tracking")

    def changeParkGameController(self, value: bytes) -> None:
        """ """
        if value == 0b00000001:
            self.changePark()

    def changePark(self) -> None:
        """ """
        obs = self.app.mount.obsSite
        if obs.status == 5:
            if obs.unpark():
                self.msg.emit(0, "Mount", "Command", "Mount unparked")
            else:
                self.msg.emit(2, "Mount", "Command", "Cannot unpark mount")
        else:
            if obs.park():
                self.msg.emit(0, "Mount", "Command", "Mount parked")
            else:
                self.msg.emit(2, "Mount", "Command", "Cannot park mount")

    def setLunarTracking(self) -> None:
        """ """
        if self.app.mount.setting.setLunarTracking():
            self.msg.emit(0, "Mount", "Command", "Tracking set to Lunar")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot set tracking to Lunar")

    def setSiderealTracking(self) -> None:
        """ """
        if self.app.mount.setting.setSiderealTracking():
            self.msg.emit(0, "Mount", "Command", "Tracking set to Sidereal")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot set tracking to Sidereal")

    def setSolarTracking(self) -> None:
        """ """
        if self.app.mount.setting.setSolarTracking():
            self.msg.emit(0, "Mount", "Command", "Tracking set to Solar")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot set tracking to Solar")

    def flipMountGameController(self, value: Bytes) -> None:
        """ """
        if value == 0b00000010:
            self.flipMount()

    def flipMount(self) -> None:
        """ """
        if self.app.mount.obsSite.flip():
            self.msg.emit(0, "Mount", "Command", "Mount flipped")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot flip mount")

    def stopGameController(self, value: Bytes) -> None:
        """ """
        if value == 0b00001000:
            self.stop()

    def stop(self) -> None:
        """ """
        if self.app.mount.obsSite.stop():
            self.msg.emit(0, "Mount", "Command", "Mount stopped")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot stop mount")
