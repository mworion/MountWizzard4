# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from importlib.metadata import version
from mw4.base.appSignals import AppSignals
from mw4.base.audioManager import AudioManager
from mw4.base.bootstrap import MwGlob
from mw4.base.loggerMW import setCustomLoggingLevel
from mw4.base.timeManager import TimeManager
from mw4.deviceRegistry import DeviceRegistry
from mw4.gui.mainWindow.mainWindow import MainWindow
from mw4.logic.controllers.model.buildpoints import BuildPoint
from mw4.logic.controllers.model.hipparcos import Hipparcos
from mw4.logic.profiles.profile import loadProfileStart
from PySide6.QtCore import QObject, QThreadPool
from PySide6.QtWidgets import QApplication
from queue import Queue
from skyfield.api import wgs84


class MountWizzard4(QObject):
    __version__ = version("mountwizzard4")
    log = logging.getLogger("MW4")

    MAX_THREAD_COUNT: int = 30  # allows concurrent device polling + model workers

    def __init__(
        self,
        mwGlob: MwGlob,
        application: QApplication,
        test: int = 0,
        arguments: str = "",
    ) -> None:
        super().__init__()
        # Set up global references, thread pool, flags, and profile.
        self.mwGlob = mwGlob
        self.application = application
        self.threadPool = QThreadPool()
        self.threadPool.setMaxThreadCount(self.MAX_THREAD_COUNT)
        self.expireData: bool = False
        self.isOnline: bool = False
        self.statusOperationRunning: int = 0
        self.messageQueue: Queue = Queue()
        self.signals = AppSignals()
        self.signals.ui.msg.connect(self.writeMessageQueue)
        self.config = loadProfileStart(self.mwGlob["configDir"])
        # Push initial lifecycle messages into the message queue.
        profile = self.config.get("profileName", "-")
        workDir = self.mwGlob["workDir"]
        self.signals.ui.msg.emit(1, "System", "Lifecycle", "MountWizzard4 started...")
        self.signals.ui.msg.emit(1, "System", "Workdir", f"{workDir}")
        self.signals.ui.msg.emit(1, "System", "Profile", f"{profile}")
        if arguments:
            self.signals.ui.msg.emit(1, "System", "Arguments", f"{arguments}")
        self.timeMgr = TimeManager(app=self)
        self.dReg: DeviceRegistry = DeviceRegistry(self)
        self.dReg.addDevices()
        self.audioMgr = AudioManager(app=self)
        self.initConfig()
        self.buildPoint = BuildPoint(self)
        self.hipparcos = Hipparcos(self)
        self.ephemeris = self.dReg.mount.obsSite.loader("de440_mw4.bsp")
        self.mainW = MainWindow(self)
        self.mainW.initConfig()
        self.mainW.showWindow()
        self.dReg.startDevices()
        self.timeMgr.start()
        self.signals.ui.operationRunning.connect(self.storeStatusOperationRunning)

        if test:
            self.timeMgr.update10s.connect(self.mainW.close)

    def initConfig(self) -> None:
        self.log.debug("Initializing configuration main application")
        self.dReg.initConfig()
        cfgSetting = self.config.get("SettingUpdate", {})
        # the settings tab owns the log level (loglevelInfo / Debug / Trace)
        if cfgSetting.get("loglevelInfo", False):
            level = "INFO"
        elif cfgSetting.get("loglevelTrace", False):
            level = "TRACE"
        else:
            level = "DEBUG"
        setCustomLoggingLevel(self, level)
        self.isOnline = cfgSetting.get("isOnline", False)
        lat = self.config.get("topoLat", 51.47)
        lon = self.config.get("topoLon", 0)
        elev = self.config.get("topoElev", 46)
        topo = wgs84.latlon(longitude_degrees=lon, latitude_degrees=lat, elevation_m=elev)
        self.dReg.mount.obsSite.location = topo
        self.timeMgr.unitTimeUTC = self.config.get("unitTimeUTC", True)

    def storeConfig(self) -> None:
        self.log.debug("Storing configuration main application")
        # the log level is stored by the settings tab; remove the old key
        self.config.pop("loglevel", None)
        self.dReg.storeConfig()
        location = self.dReg.mount.location
        if location is not None:
            self.config["topoLat"] = float(location.latitude.degrees)
            self.config["topoLon"] = float(location.longitude.degrees)
            self.config["topoElev"] = float(location.elevation.m)
        self.config["unitTimeUTC"] = self.timeMgr.unitTimeUTC

    def storeStatusOperationRunning(self, status: int) -> None:
        self.statusOperationRunning = status

    def writeMessageQueue(self, prio: int, source: str, mType: str, message: str) -> None:
        self.log.debug("Message window : %s - %s - %s", source, mType, message)
        self.messageQueue.put((prio, source, mType, message))
