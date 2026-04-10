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
import logging
import sys
from importlib.metadata import version
from mw4.base.loggerMW import setCustomLoggingLevel
from mw4.base.timerManager import CyclicTimerManager
from mw4.gui.mainWindow.mainWindow import MainWindow
from mw4.logic.buildData.buildpoints import DataPoint
from mw4.logic.buildData.hipparcos import Hipparcos
from mw4.logic.camera.camera import Camera
from mw4.logic.cover.cover import Cover
from mw4.logic.dome.dome import Dome
from mw4.logic.environment.directWeather import DirectWeather
from mw4.logic.environment.seeingWeather import SeeingWeather
from mw4.logic.environment.sensorWeather import SensorWeather
from mw4.logic.filter.filter import Filter
from mw4.logic.focuser.focuser import Focuser
from mw4.logic.measure.measure import MeasureData
from mw4.logic.plateSolve.plateSolve import PlateSolve
from mw4.logic.powerswitch.kmRelay import KMRelay
from mw4.logic.powerswitch.pegasusUPB import PegasusUPB
from mw4.logic.profiles.profile import loadProfileStart
from mw4.logic.remote.remote import Remote
from mw4.logic.telescope.telescope import Telescope
from mw4.mountcontrol.mount import MountDevice
from PySide6.QtCore import QObject, QThreadPool, Signal
from PySide6.QtWidgets import QApplication
from queue import Queue
from skyfield.api import wgs84
from skyfield.toposlib import Topos
from typing import Any


class MountWizzard4(QObject):
    """Main application object for MountWizzard4."""

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
    game_sL = Signal(object, object)
    game_sR = Signal(object, object)

    # --- Cyclic update signals (emitted by CyclicTimerManager) ---
    update0_1s = Signal()
    update1s = Signal()
    update3s = Signal()
    update10s = Signal()
    update30s = Signal()
    update60s = Signal()
    update3m = Signal()
    update10m = Signal()
    update30m = Signal()
    update1h = Signal()

    # --- Startup signals (emitted once by CyclicTimerManager) ---
    start1s = Signal()
    start3s = Signal()
    start5s = Signal()
    start10s = Signal()
    start30s = Signal()

    messageQueue = Queue()

    def __init__(
        self,
        mwGlob: dict[str, Any],
        application: QApplication,
        test: int = 0,
    ) -> None:
        super().__init__()
        self._initCore(mwGlob, application)
        self._initMount()
        self._initDevices()
        self._initGui()
        self._initTimers()
        self._connectSignals(test)

    # ------------------------------------------------------------------
    # Initialisation phases
    # ------------------------------------------------------------------

    def _initCore(
        self, mwGlob: dict[str, Any], application: QApplication
    ) -> None:
        """Set up global references, thread pool, flags, and profile."""
        self.mwGlob = mwGlob
        self.application = application
        self.threadPool = QThreadPool()
        self.threadPool.setMaxThreadCount(30)
        self.expireData: bool = False
        self.onlineMode: bool = False
        self.statusOperationRunning: int = 0
        self.config = loadProfileStart(self.mwGlob["configDir"])
        self.deviceStat: dict[str, bool | None] = {
            "mount": None,
            "refraction": None,
            "dome": None,
            "cover": None,
            "camera": None,
            "filter": None,
            "sensor1Weather": None,
            "sensor2Weather": None,
            "sensor3Weather": None,
            "sensor4Weather": None,
            "directWeather": None,
            "seeingWeather": None,
            "telescope": None,
            "power": None,
            "relay": None,
            "plateSolve": None,
            "remote": None,
            "measure": None,
        }
        self._logStartupInfo()

    def _logStartupInfo(self) -> None:
        """Push initial lifecycle messages into the message queue."""
        profile = self.config.get("profileName", "-")
        workDir = self.mwGlob["workDir"]
        self.messageQueue.put(
            (1, "System", "Lifecycle", "MountWizzard4 started...")
        )
        self.messageQueue.put((1, "System", "Workdir", f"[{workDir}]"))
        self.messageQueue.put((1, "System", "Profile", f"[{profile}]"))

    def _initMount(self) -> None:
        """Create the mount device and load ephemeris data."""
        self.mount = MountDevice(
            app=self,
            host=None,
            MAC="00.c0.08.87.35.db",
            pathToData=self.mwGlob["dataDir"],
            verbose=True,
        )
        topo = self.initConfig()
        self.mount.obsSite.location = topo
        self.ephemeris = self.mount.obsSite.loader("de440_mw4.bsp")

    def _initDevices(self) -> None:
        """Instantiate all hardware subsystems."""
        self.relay = KMRelay()
        self.sensor1Weather = SensorWeather(self)
        self.sensor2Weather = SensorWeather(self)
        self.sensor3Weather = SensorWeather(self)
        self.sensor4Weather = SensorWeather(self)
        self.directWeather = DirectWeather(self)
        self.seeingWeather = SeeingWeather(self)
        self.cover = Cover(self)
        self.dome = Dome(self)
        self.camera = Camera(self)
        self.filter = Filter(self)
        self.focuser = Focuser(self)
        self.telescope = Telescope(self)
        self.power = PegasusUPB(self)
        self.data = DataPoint(self)
        self.hipparcos = Hipparcos(self)
        self.measure = MeasureData(self)
        self.remote = Remote(self)
        self.plateSolve = PlateSolve(self)

    def _initGui(self) -> None:
        """Create, configure, and show the main window."""
        self.mainW = MainWindow(self)
        self.mainW.initConfig()
        self.mainW.show()

    def _initTimers(self) -> None:
        """Set up the cyclic timer manager and start the mount timers."""
        self.mount.startMountTimers()
        self.timerMgr = CyclicTimerManager(app=self, parent=self)
        self.timerMgr.start()

    def _connectSignals(self, test: int) -> None:
        """Wire up application-level signal connections."""
        self.application.aboutToQuit.connect(self.aboutToQuit)
        self.operationRunning.connect(self.storeStatusOperationRunning)
        if test:
            self.update10s.connect(self.quit)
        if len(sys.argv) > 1:
            self.messageQueue.put(
                (1, "System", "Arguments", sys.argv[1])
            )

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def initConfig(self) -> Topos:
        """Apply logging level and return the topocentric location."""
        setCustomLoggingLevel(self.config.get("loglevel", "DEBUG"))
        lat = self.config.get("topoLat", 51.47)
        lon = self.config.get("topoLon", 0)
        elev = self.config.get("topoElev", 46)
        topo = wgs84.latlon(
            longitude_degrees=lon, latitude_degrees=lat, elevation_m=elev
        )
        return topo

    def storeConfig(self) -> None:
        """Persist current configuration back to the config dict."""
        self.config["loglevel"] = logging.getLevelName(self.log.level)
        location = self.mount.obsSite.location
        if location is not None:
            self.config["topoLat"] = float(location.latitude.degrees)
            self.config["topoLon"] = float(location.longitude.degrees)
            self.config["topoElev"] = float(location.elevation.m)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def storeStatusOperationRunning(self, status: int) -> None:
        """Store the current operation-running status flag."""
        self.statusOperationRunning = status

    def aboutToQuit(self) -> None:
        """Stop all timers when the application is about to quit."""
        self.timerMgr.stop()
        self.mount.stopAllMountTimers()

    def quit(self) -> None:
        """Gracefully shut down the application."""
        self.deviceStat["mount"] = False
        self.aboutToQuit()
        self.messageQueue.put(
            (1, "System", "Lifecycle", "MountWizzard4 manual stopped")
        )
        self.application.quit()
