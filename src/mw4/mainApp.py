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
import logging
import sys
from importlib.metadata import version
from mw4.base.bootstrap import MwGlob
from mw4.base.deviceRegistry import DeviceRegistry
from mw4.base.loggerMW import setCustomLoggingLevel
from mw4.base.timerManager import CyclicTimerManager
from mw4.gui.mainWindow.mainWindow import MainWindow
from mw4.logic.buildData.buildpoints import BuildPoint
from mw4.logic.buildData.hipparcos import Hipparcos
from mw4.logic.profiles.profile import loadProfileStart
from mw4.mountcontrol.mount import MountDevice
from PySide6.QtCore import QObject, QThreadPool, Signal
from PySide6.QtWidgets import QApplication
from queue import Queue
from skyfield.api import wgs84
from skyfield.toposlib import GeographicPosition


class MountWizzard4(QObject):
    __version__ = version("mountwizzard4")
    log = logging.getLogger("MW4")

    # --- UI signals ---
    material = Signal(object, object)
    msg = Signal(object, object, object, object)
    tabsMovable = Signal(object)
    colorChange = Signal()
    playSound = Signal(object)
    showImage = Signal(object)
    showAnalyse = Signal(object)
    # --- Hemisphere / build point signals ---
    redrawHemisphere = Signal()
    redrawHorizon = Signal()
    updatePointMarker = Signal()
    drawBuildPoints = Signal()
    buildPointsChanged = Signal()
    drawHorizonPoints = Signal()
    # --- Device signals ---
    operationRunning = Signal(object)
    updateDomeSettings = Signal()
    hostChanged = Signal()
    remoteCommand = Signal(object)
    # --- Mount signals ---
    virtualStop = Signal()
    mountOff = Signal()
    mountOn = Signal()
    refreshModel = Signal()
    refreshName = Signal()
    # --- Satellite signals ---
    sendSatelliteData = Signal(object, object)
    updateSatellite = Signal(object, object)
    showSatellite = Signal(object, object, object, object, object)
    # --- Gamepad signals ---
    gameABXY = Signal(object)
    gamePMH = Signal(object)
    gameDirection = Signal(object)
    gameSL = Signal(object, object)
    gameSR = Signal(object, object)
    # --- Cyclic update signals (emitted by CyclicTimerManager) ---
    update0_1s = Signal()
    update1s = Signal()
    update3s = Signal()
    update10s = Signal()
    update30s = Signal()
    update3m = Signal()
    update30m = Signal()
    # --- Startup signals (emitted once by CyclicTimerManager) ---
    start3s = Signal()
    # --- Thread pool configuration ---
    MAX_THREAD_COUNT: int = 30  # allows concurrent device polling + model workers

    def __init__(
        self,
        mwGlob: MwGlob,
        application: QApplication,
        test: int = 0,
    ) -> None:
        super().__init__()
        """Set up global references, thread pool, flags, and profile."""
        self.mwGlob = mwGlob
        self.application = application
        self.threadPool = QThreadPool()
        self.threadPool.setMaxThreadCount(self.MAX_THREAD_COUNT)
        self.expireData: bool = False
        self.onlineMode: bool = False
        self.statusOperationRunning: int = 0
        self.messageQueue: Queue = Queue()
        self.config = loadProfileStart(self.mwGlob["configDir"])
        """Push initial lifecycle messages into the message queue."""
        profile = self.config.get("profileName", "-")
        workDir = self.mwGlob["workDir"]
        self.messageQueue.put((1, "System", "Lifecycle", "MountWizzard4 started..."))
        self.messageQueue.put((1, "System", "Workdir", f"[{workDir}]"))
        self.messageQueue.put((1, "System", "Profile", f"[{profile}]"))
        """Create the mount device and load ephemeris data."""
        self.mount = MountDevice(self, verbose=True)
        self.dReg: DeviceRegistry = DeviceRegistry(self)
        topo = self.initConfig()
        self.mount.obsSite.location = topo
        self.buildPoint = BuildPoint(self)
        self.hipparcos = Hipparcos(self)
        self.ephemeris = self.mount.obsSite.loader("de440_mw4.bsp")
        """Create, configure, and show the main window."""
        self.mainW = MainWindow(self)
        self.mainW.initConfig()
        self.mainW.showWindow()
        """Set up the cyclic timer manager and start the mount timers."""
        self.mount.startMountTimers()
        self.timerMgr = CyclicTimerManager(app=self, parent=self)
        self.timerMgr.start()
        """Wire up application-level signal connections."""
        self.application.aboutToQuit.connect(self.aboutToQuit)
        self.operationRunning.connect(self.storeStatusOperationRunning)

        if test:
            self.update10s.connect(self.quit)
        if len(sys.argv) > 1:
            self.messageQueue.put((1, "System", "Arguments", sys.argv[1]))

    def initConfig(self) -> GeographicPosition:
        setCustomLoggingLevel(self, self.config.get("loglevel", "DEBUG"))
        lat = self.config.get("topoLat", 51.47)
        lon = self.config.get("topoLon", 0)
        elev = self.config.get("topoElev", 46)
        topo = wgs84.latlon(longitude_degrees=lon, latitude_degrees=lat, elevation_m=elev)
        return topo

    def storeConfig(self) -> None:
        self.config["loglevel"] = logging.getLevelName(self.log.level)
        location = self.dReg.drivers["mount"]["class"].obsSite.location
        if location is not None:
            self.config["topoLat"] = float(location.latitude.degrees)
            self.config["topoLon"] = float(location.longitude.degrees)
            self.config["topoElev"] = float(location.elevation.m)

    def storeStatusOperationRunning(self, status: int) -> None:
        self.statusOperationRunning = status

    def aboutToQuit(self) -> None:
        self.timerMgr.stop()
        self.mount.stopAllMountTimers()

    def quit(self) -> None:
        self.dReg.drivers["mount"]["stat"] = False
        self.aboutToQuit()
        self.messageQueue.put((1, "System", "Lifecycle", "MountWizzard4 manual stopped"))
        self.application.quit()
