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
# Re-export all stubs so that existing test imports remain unchanged.
from mw4.base.deviceRegistry import DeviceRegistry
from pathlib import Path
from PySide6.QtCore import QObject, QThreadPool, QTimer, Signal
from queue import Queue
from skyfield.api import load_file
from tests.unit_tests.unitTestAddOns.deviceStubs import (  # noqa: F401
    CSV,
    Camera,
    CameraSignals,
    Cover,
    CoverSignals,
    Data,
    DirectWeather,
    DirectWeatherSignals,
    Dome,
    DomeSignals,
    Filter,
    FilterSignals,
    Focuser,
    FocuserSignals,
    Hipparcos,
    LightPanel,
    LightPanelSignals,
    Measure,
    MeasureSignals,
    OnlineWeather,
    OnlineWeatherSignals,
    PlateSolve,
    Power,
    PowerSignals,
    Relay,
    RelaySignals,
    Remote,
    RemoteSignals,
    SeeingWeather,
    SeeingWeatherSignals,
    SensorWeather,
    SensorWeatherSignals,
    Telescope,
)
from tests.unit_tests.unitTestAddOns.guiStubs import (  # noqa: F401
    CheckBox,
    LineEdit,
    MainW,
)
from tests.unit_tests.unitTestAddOns.mountStubs import (  # noqa: F401
    Mount,
    MountFirmware,
    MountGeometry,
    MountModel,
    MountObsSite,
    MountSatellite,
    MountSetting,
    MountSignals,
    Name,
)


class App(QObject):
    __version__ = "test"
    tabsMovable = Signal(object)
    update10s = Signal()
    timerMgr = QTimer()
    update0_1s = Signal()
    update1s = Signal()
    update3s = Signal()
    update30s = Signal()
    update3m = Signal()
    update30m = Signal()
    start3s = Signal()
    hostChanged = Signal()
    sendSatelliteData = Signal(object, object)
    updateSatellite = Signal(object, object)
    showSatellite = Signal(object, object, object, object, object)
    updateDomeSettings = Signal()
    drawHorizonPoints = Signal()
    drawBuildPoints = Signal()
    redrawHemisphere = Signal()
    refreshModel = Signal()
    refreshName = Signal()
    redrawHorizon = Signal()
    showAnalyse = Signal(object)
    showImage = Signal(object)
    updatePointMarker = Signal()
    operationRunning = Signal(object)
    colorChange = Signal()
    virtualStop = Signal()
    mountOff = Signal()
    mountOn = Signal()
    buildPointsChanged = Signal()
    playSound = Signal(object)
    msg = Signal(object, object, object, object)
    remoteCommand = Signal(object)
    gameABXY = Signal(object)
    gamePMH = Signal(object)
    gameDirection = Signal(object)
    gameSL = Signal(object, object)
    gameSR = Signal(object, object)

    def __init__(self):
        super().__init__()
        self.config = {"mainW": {}}
        self.deviceStat = {
            "dome": False,
            "mount": False,
            "camera": False,
            "plateSolve": False,
        }
        self.statusOperationRunning = 0
        self.messageQueue = Queue()
        self.plateSolve = PlateSolve()
        self.camera = Camera()
        self.cover = Cover()
        self.lightPanel = LightPanel()
        self.data = Data()
        self.filter = Filter()
        self.focuser = Focuser()
        self.measure = Measure()
        self.mount = Mount()
        self.sensor1Weather = SensorWeather()
        self.sensor2Weather = SensorWeather()
        self.sensor3Weather = SensorWeather()
        self.sensor4Weather = SensorWeather()
        self.directWeather = DirectWeather()
        self.seeingWeather = SeeingWeather()
        self.power = Power()
        self.dome = Dome()
        self.relay = Relay()
        self.remote = Remote()
        self.telescope = Telescope()
        self.hipparcos = Hipparcos()

        self.ephemeris = load_file("tests/testData/de440_mw4.bsp")
        self.mwGlob = {
            "modelDir": Path("tests/work/model"),
            "imageDir": Path("tests/work/image"),
            "dataDir": Path("tests/work/data"),
            "workDir": Path("tests/work"),
            "measureDir": Path("tests/work/measure"),
            "tempDir": Path("tests/work/temp"),
            "configDir": Path("tests/work/config"),
            "logDir": Path("tests/work/log"),
        }
        self.uiWindows = {}
        self.mainW = MainW()
        self.deviceRegistry = DeviceRegistry()
        self.threadPool = QThreadPool()
        self.onlineMode = False

    @staticmethod
    def loadConfig():
        return

    @staticmethod
    def saveConfig():
        return

    @staticmethod
    def blendConfig(a, b):
        return a

    @staticmethod
    def storeConfig():
        return

    @staticmethod
    def initConfig():
        return

    @staticmethod
    def getActiveDrivers() -> dict:
        """Return an empty driver mapping (overridden per test as needed)."""
        return {}

    @staticmethod
    def quit():
        return
