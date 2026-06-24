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
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.qtHelpers import svg2pixmap
from typing import Any


class Mount(TabAddon):
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.app.dReg["hidController"].signals.hidABXY.connect(self.changeParkHid)
        self.app.dReg["hidController"].signals.hidABXY.connect(self.stopHid)
        self.app.dReg["hidController"].signals.hidABXY.connect(self.changeTrackingHid)
        self.app.dReg["hidController"].signals.hidABXY.connect(self.flipMountHid)
        self.app.dReg["hidController"].signals.deviceConnected.connect(self.setHidIcons)
        self.app.dReg["hidController"].signals.deviceDisconnected.connect(self.setHidIcons)
        self.app.hidModeChanged.connect(self.setHidIcons)
        self.ui.flipMount.clicked.connect(self.flipMount)
        self.ui.tracking.clicked.connect(self.changeTracking)
        self.ui.setLunarTracking.clicked.connect(self.setLunarTracking)
        self.ui.setSiderealTracking.clicked.connect(self.setSiderealTracking)
        self.ui.setSolarTracking.clicked.connect(self.setSolarTracking)
        self.ui.park.clicked.connect(self.changePark)
        self.ui.stop.clicked.connect(self.stop)

    def initConfig(self) -> None:
        config = self.app.config.get("WindowMain", {})
        self.ui.coordsJ2000.setChecked(config.get("coordsJ2000", False))
        self.ui.coordsJNow.setChecked(config.get("coordsJNow", False))
        self.setHidIcons()

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["coordsJ2000"] = self.ui.coordsJ2000.isChecked()
        config["coordsJNow"] = self.ui.coordsJNow.isChecked()

    def setHidIcon(self, ui: Any, status: int = 0) -> None:
        colors = [self.mainW.M_PRIM2, self.mainW.M_TER, self.mainW.M_GREEN]
        color = colors[status]
        pixmap = svg2pixmap("assets/icon/controller.svg", color).scaled(16, 16)
        ui.setPixmap(pixmap)

    def setHidIcons(self) -> None:
        base = {
            self.ui.controller1: self.app.dReg["hidController"].instance.config.moveAltAz,
            self.ui.controller2: self.app.dReg["hidController"].instance.config.moveRaDec,
            self.ui.controller3: self.app.dReg["hidController"].instance.config.tracking,
            self.ui.controller4: self.app.dReg["hidController"].instance.config.parkStop,
            self.ui.controller5: self.app.dReg["hidController"].instance.config.dome,
        }
        connected = self.app.dReg["hidController"].stat
        for ui, statFlag in base.items():
            if connected and statFlag:
                status = 2
            elif connected and not statFlag:
                status = 1
            else:
                status = 0
            self.setHidIcon(ui, status)

    def changeTrackingHid(self, value: bytes) -> None:
        if value == 0b00000100:
            self.changeTracking()

    def changeTracking(self) -> None:
        obs = self.app.dReg["mount"].obsSite
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

    def changeParkHid(self, value: bytes) -> None:
        if value == 0b00000001:
            self.changePark()

    def changePark(self) -> None:
        obs = self.app.dReg["mount"].obsSite
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
        if self.app.dReg["mount"].setting.setLunarTracking():
            self.msg.emit(0, "Mount", "Command", "Tracking set to Lunar")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot set tracking to Lunar")

    def setSiderealTracking(self) -> None:
        if self.app.dReg["mount"].setting.setSiderealTracking():
            self.msg.emit(0, "Mount", "Command", "Tracking set to Sidereal")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot set tracking to Sidereal")

    def setSolarTracking(self) -> None:
        if self.app.dReg["mount"].setting.setSolarTracking():
            self.msg.emit(0, "Mount", "Command", "Tracking set to Solar")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot set tracking to Solar")

    def flipMountHid(self, value: bytes) -> None:
        if value == 0b00000010:
            self.flipMount()

    def flipMount(self) -> None:
        if self.app.dReg["mount"].obsSite.flip():
            self.msg.emit(0, "Mount", "Command", "Mount flipped")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot flip mount")

    def stopHid(self, value: bytes) -> None:
        if value == 0b00001000:
            self.stop()

    def stop(self) -> None:
        if self.app.dReg["mount"].obsSite.stop():
            self.msg.emit(0, "Mount", "Command", "Mount stopped")
        else:
            self.msg.emit(2, "Mount", "Command", "Cannot stop mount")
