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
import logging
import sys
from queue import Queue

# external packages
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QThreadPool, QTimer
from skyfield.api import wgs84
from importlib_metadata import version

# local import
from base.loggerMW import setCustomLoggingLevel
from mountcontrol.mount import MountDevice
from gui.mainWindow.mainWindow import MainWindow
from logic.powerswitch.kmRelay import KMRelay
from logic.modeldata.buildpoints import DataPoint
from logic.modeldata.hipparcos import Hipparcos
from logic.dome.dome import Dome
from logic.camera.camera import Camera
from logic.filter.filter import Filter
from logic.focuser.focuser import Focuser
from logic.environment.sensorWeather import SensorWeather
from logic.environment.onlineWeather import OnlineWeather
from logic.environment.directWeather import DirectWeather
from logic.environment.seeingWeather import SeeingWeather
from logic.cover.cover import Cover
from logic.telescope.telescope import Telescope
from logic.powerswitch.pegasusUPB import PegasusUPB
from logic.measure.measure import MeasureData
from logic.remote.remote import Remote
from logic.plateSolve.plateSolve import PlateSolve
from logic.profiles.profile import loadProfileStart


class MountWizzard4(QObject):
    """ """

    __version__ = version("mountwizzard4")

    log = logging.getLogger("MW4")

    material = Signal(object, object)
    msg = Signal(object, object, object, object)
    messageQueue = Queue()
    tabsMovable = Signal(object)
    redrawHemisphere = Signal()
    redrawHorizon = Signal()
    updatePointMarker = Signal()
    drawBuildPoints = Signal()
    operationRunning = Signal(object)
    playSound = Signal(object)
    buildPointsChanged = Signal()
    drawHorizonPoints = Signal()
    updateDomeSettings = Signal()
    sendSatelliteData = Signal()
    refreshModel = Signal()
    refreshName = Signal()
    updateSatellite = Signal(object, object)
    showSatellite = Signal(object, object, object, object, object)
    showImage = Signal(object)
    showAnalyse = Signal(object)
    remoteCommand = Signal(object)
    colorChange = Signal()
    hostChanged = Signal()
    virtualStop = Signal()
    mountOff = Signal()
    mountOn = Signal()

    gameABXY = Signal(object)
    gamePMH = Signal(object)
    gameDirection = Signal(object)
    game_sL = Signal(object, object)
    game_sR = Signal(object, object)

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
    start1s = Signal()
    start3s = Signal()
    start5s = Signal()
    start10s = Signal()
    start30s = Signal()

    def __init__(self, mwGlob: dict, application: QApplication):
        super().__init__()
        self.mwGlob = mwGlob
        self.application = application
        self.threadPool = QThreadPool()
        self.threadPool.setMaxThreadCount(30)
        self.expireData = False
        self.mainW = None
        self.timerCounter = 0
        self.statusOperationRunning = 0
        self.config = loadProfileStart(self.mwGlob["configDir"])
        self.deviceStat = {
            "dome": None,
            "mount": None,
            "camera": None,
            "plateSolve": None,
            "refraction": None,
            "sensor1Weather": None,
            "sensor2Weather": None,
            "sensor3Weather": None,
            "onlineWeather": None,
            "directWeather": None,
            "seeingWeather": None,
            "cover": None,
            "telescope": None,
            "power": None,
            "remote": None,
            "relay": None,
            "measure": None,
        }
        profile = self.config.get("profileName", "-")
        workDir = self.mwGlob["workDir"]
        self.messageQueue.put((1, "System", "Lifecycle", "MountWizzard4 started..."))
        self.messageQueue.put((1, "System", "Workdir", f"{workDir}"))
        self.messageQueue.put((1, "System", "Profile", f"Base: {profile}"))
        # initialize commands to mount
        self.mount = MountDevice(
            app=self,
            host=None,
            MAC="00.c0.08.87.35.db",
            pathToData=self.mwGlob["dataDir"],
            verbose=True,
        )
        # setting location to last know config
        topo = self.initConfig()
        self.mount.obsSite.location = topo
        self.ephemeris = self.mount.obsSite.loader("de440_mw4.bsp")
        self.relay = KMRelay()
        self.sensor1Weather = SensorWeather(self)
        self.sensor2Weather = SensorWeather(self)
        self.sensor3Weather = SensorWeather(self)
        self.onlineWeather = OnlineWeather(self)
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
        self.mainW = MainWindow(self)
        self.mainW.initConfig()

        self.mount.startMountTimers()
        self.timer0_1s = QTimer()
        self.timer0_1s.setSingleShot(False)
        self.timer0_1s.timeout.connect(self.sendCyclic)
        self.timer0_1s.start(100)
        self.application.aboutToQuit.connect(self.aboutToQuit)
        self.operationRunning.connect(self.storeStatusOperationRunning)

        if (self.mwGlob["workDir"] / "test.run").is_file():
            self.update3s.connect(self.quit)
        if len(sys.argv) > 1:
            self.messageQueue.put((1, "System", "Arguments", sys.argv[1]))

    def storeStatusOperationRunning(self, status: int) -> None:
        """ """
        self.statusOperationRunning = status

    def initConfig(self) -> wgs84:
        """ """
        config = self.config.get("mainW", {})
        if config.get("loglevelTrace", False):
            level = "TRACE"
        elif config.get("loglevelDebug", False):
            level = "DEBUG"
        else:
            level = "INFO"
        setCustomLoggingLevel(level)

        lat = self.config.get("topoLat", 51.47)
        lon = self.config.get("topoLon", 0)
        elev = self.config.get("topoElev", 46)

        topo = wgs84.latlon(longitude_degrees=lon, latitude_degrees=lat, elevation_m=elev)
        return topo

    def storeConfig(self) -> None:
        """ """
        location = self.mount.obsSite.location
        if location is not None:
            self.config["topoLat"] = location.latitude.degrees
            self.config["topoLon"] = location.longitude.degrees
            self.config["topoElev"] = location.elevation.m

    def sendStart(self):
        """ """
        if self.timerCounter == 10:
            self.start1s.emit()
        if self.timerCounter == 30:
            self.start3s.emit()
        if self.timerCounter == 50:
            self.start5s.emit()
        if self.timerCounter == 100:
            self.start10s.emit()
        if self.timerCounter == 300:
            self.start30s.emit()

    def sendCyclic(self) -> None:
        """ """
        self.timerCounter += 1
        if self.timerCounter % 1 == 0:
            self.update0_1s.emit()
        if (self.timerCounter + 5) % 10 == 0:
            self.update1s.emit()
        if (self.timerCounter + 10) % 30 == 0:
            self.update3s.emit()
        if (self.timerCounter + 20) % 100 == 0:
            self.update10s.emit()
        if (self.timerCounter + 25) % 300 == 0:
            self.update30s.emit()
        if (self.timerCounter + 25) % 600 == 0:
            self.update60s.emit()
        if (self.timerCounter + 12) % 1800 == 0:
            self.update3m.emit()
        if (self.timerCounter + 13) % 6000 == 0:
            self.update10m.emit()
        if (self.timerCounter + 14) % 18000 == 0:
            self.update30m.emit()
        if (self.timerCounter + 15) % 36000 == 0:
            self.update1h.emit()
        self.sendStart()

    def aboutToQuit(self) -> None:
        """ """
        self.timer0_1s.stop()
        self.mount.stopAllMountTimers()

    def quit(self) -> None:
        """ """
        self.deviceStat["mount"] = False
        self.aboutToQuit()
        self.messageQueue.put((1, "System", "Lifecycle", "MountWizzard4 manual stopped"))
        self.application.quit()
