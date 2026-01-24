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
import numpy as np
from mw4.base.signalsDevices import Signals
from packaging.version import Version
from pathlib import Path
from PySide6.QtCore import QObject, QThreadPool, QTimer, Signal
from queue import Queue
from skyfield.api import Angle, Loader, load, load_file, wgs84


class PlateSolve:
    def __init__(self):
        self.signals = Signals()
        self.framework = None
        self.run = {}
        self.deviceName = ""
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}

    @staticmethod
    def solve(a, b):
        return

    @staticmethod
    def abort():
        return

    @staticmethod
    def checkAvailability():
        return True, True


class CameraSignals(QObject):
    saved = Signal()
    message = Signal(object)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)
    exposed = Signal()
    downloaded = Signal()


class Camera:
    def __init__(self):
        self.signals = CameraSignals()
        self.exposureTime = 0
        self.exposureTime1 = 0
        self.exposureTimeN = 0
        self.binning = 1
        self.binning1 = 1
        self.binningN = 1
        self.focalLength = 100
        self.subFrame = 100
        self.fastReadout = False
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def expose(
        imagePath=None,
        exposureTime=None,
        binning=None,
        subFrame=None,
        fastReadout=None,
        focalLength=None,
        ra=None,
        dec=None,
    ):
        return

    @staticmethod
    def abort():
        return

    @staticmethod
    def sendCoolerTemp(temperature=None):
        return

    @staticmethod
    def sendOffset(offset=None):
        return

    @staticmethod
    def sendGain(gain=None):
        return

    @staticmethod
    def sendDownloadMode(fastReadout=None):
        return

    @staticmethod
    def sendCoolerSwitch(coolerOn=None):
        return

    @staticmethod
    def stopCommunication():
        return

    @staticmethod
    def startCommunication(loadConfig=None):
        return


class CoverSignals(QObject):
    message = Signal(object)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Cover:
    def __init__(self):
        self.signals = CoverSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def closeCover():
        return

    @staticmethod
    def openCover():
        return

    @staticmethod
    def haltCover():
        return

    @staticmethod
    def lightOn():
        return

    @staticmethod
    def lightOff():
        return

    @staticmethod
    def lightIntensity():
        return


class DomeSignals(QObject):
    message = Signal(object)
    azimuth = Signal()
    slewed = Signal()
    deviceDisconnected = Signal()
    deviceConnected = Signal()
    serverDisconnected = Signal()


class Dome:
    def __init__(self):
        self.domeShutterWidth = 0.6
        self.offGEM = 0
        self.offLAT = 0
        self.offNorth = 0
        self.offEast = 0
        self.domeRadius = 1.0
        self.clearOpening = 1
        self.data = {}
        self.framework = None
        self.signals = DomeSignals()
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def abortSlew():
        return

    @staticmethod
    def openShutter():
        return

    @staticmethod
    def closeShutter():
        return

    @staticmethod
    def slewDome(azimuth=0, altitude=0, follow=False):
        return

    @staticmethod
    def followDome(azimuth=0, altitude=0):
        return

    @staticmethod
    def avoidFirstOvershoot():
        return

    @staticmethod
    def slewCW():
        return

    @staticmethod
    def slewCCW():
        return


class SensorWeatherSignals(QObject):
    message = Signal(object)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class SensorWeather:
    def __init__(self):
        self.signals = SensorWeatherSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}


class OnlineWeatherSignals(QObject):
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class OnlineWeather:
    def __init__(self):
        self.signals = OnlineWeatherSignals()
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.data = {}


class DirectWeatherSignals(QObject):
    message = Signal(object)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class DirectWeather:
    def __init__(self):
        self.signals = DirectWeatherSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}


class SeeingWeatherSignals(QObject):
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)
    update = Signal()


class SeeingWeather:
    def __init__(self):
        self.signals = SeeingWeatherSignals()
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}
        self.data = {}


class FilterSignals(QObject):
    message = Signal(object)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Filter:
    def __init__(self):
        self.signals = FilterSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def sendFilterNumber(filterNumber=None):
        return

    @staticmethod
    def sendFilterName(filterName=None):
        return


class FocuserSignals(QObject):
    message = Signal(object)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Focuser:
    def __init__(self):
        self.signals = FocuserSignals()
        self.framework = None
        self.data = {}
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def move():
        return

    @staticmethod
    def halt():
        return


class MeasureSignals(QObject):
    message = Signal(object)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class CSV:
    csvFilename = ""


class Measure:
    def __init__(self):
        self.signals = MeasureSignals()
        self.data = {}
        self.framework = None
        self.devices = {}
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.run = {"csv": CSV()}


class RelaySignals(QObject):
    message = Signal(object)
    statusReady = Signal()
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Relay:
    def __init__(self):
        self.signals = RelaySignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.timerTask = QTimer()

    @staticmethod
    def getRelay():
        return

    @staticmethod
    def pulse(a):
        return

    @staticmethod
    def switch(a):
        return


class RemoteSignals(QObject):
    message = Signal(object)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Remote:
    def __init__(self):
        self.signals = RemoteSignals()
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {}}


class Telescope:
    class TelescopeSignals(QObject):
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    class Test:
        deviceName = ""

    signals = TelescopeSignals()
    data = {}
    framework = None
    run = {"indi": Test()}
    focalLength = 100
    aperture = 100
    defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}

    @staticmethod
    def stopCommunication():
        return

    @staticmethod
    def startCommunication(loadConfig=None):
        return


class Hipparcos:
    name = ["test"]
    az = [10]
    alt = [10]

    @staticmethod
    def calculateAlignStarPositionsAltAz():
        return

    @staticmethod
    def getAlignStarRaDecFromName():
        return


class PowerSignals(QObject):
    version = Signal()
    message = Signal(object)
    serverConnected = Signal()
    serverDisconnected = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Power:
    def __init__(self):
        self.signals = PowerSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {}}

    @staticmethod
    def sendDew(port=None, value=None):
        return True

    @staticmethod
    def togglePowerPort(port=None):
        return True

    @staticmethod
    def togglePowerPortBoot(port=None):
        return True

    @staticmethod
    def toggleHubUSB():
        return True

    @staticmethod
    def togglePortUSB(port=None):
        return True

    @staticmethod
    def toggleAutoDew():
        return True

    @staticmethod
    def reboot():
        return True

    @staticmethod
    def sendAdjustableOutput(value=None):
        return True


class Data:
    SOLVED = 0
    UNPROCESSED = 1
    FAILED = 2

    def __init__(self):
        self.buildP = []
        self.horizonP = []

    @staticmethod
    def loadHorizonP(fileName=""):
        return

    @staticmethod
    def saveHorizonP(fileName=""):
        return

    @staticmethod
    def clear():
        return

    @staticmethod
    def clearBuildP():
        return

    @staticmethod
    def deleteCloseMeridian():
        return

    @staticmethod
    def addBuildP():
        return

    @staticmethod
    def saveBuildP():
        return

    @staticmethod
    def loadBuildP(a):
        return

    @staticmethod
    def genGrid(minAlt=None, maxAlt=None, numbRows=None, numbCols=None, keep=None):
        return

    @staticmethod
    def genAlign(altBase=None, azBase=None, numberBase=None, keep=None):
        return

    @staticmethod
    def genGreaterCircle(stepHA, StepDEC, distFlip):
        return

    @staticmethod
    def generateDSOPath(
        ha=None, dec=None, timeJD=None, location=None, numberPoints=None, keep=None
    ):
        return

    @staticmethod
    def generateGoldenSpiral(numberPoints=None, keep=None):
        return

    @staticmethod
    def generateCelestialEquator():
        return

    @staticmethod
    def deleteBelowHorizon():
        return

    @staticmethod
    def deleteCloseHorizonLine(a):
        return

    @staticmethod
    def ditherPoints():
        return

    @staticmethod
    def sortActualPierside():
        return

    @staticmethod
    def sortDomeAz():
        return

    @staticmethod
    def sortAz():
        return

    @staticmethod
    def sortAlt():
        return

    @staticmethod
    def setStatusBuildP(a, b):
        return

    @staticmethod
    def setStatusBuildPSolved(a):
        return

    @staticmethod
    def setStatusBuildPFailed(a):
        return

    @staticmethod
    def setStatusBuildPUnprocessed(a):
        return

    @staticmethod
    def isAboveHorizon(point):
        return True


class Name:
    def __init__(self):
        self.name = ""
        self.jdStart = 1
        self.jdEnd = 1
        self.flip = False
        self.message = ""
        self.altitude = None
        self.azimuth = None


class MountSatellite:
    def __init__(self):
        self.tleParams = Name()
        self.trajectoryParams = Name()
        self.settlingTime = 0

    @staticmethod
    def setTLE(line0="", line1="", line2=""):
        return

    @staticmethod
    def slewTLE(julD=0, duration=0):
        return

    @staticmethod
    def calcTLE():
        return

    @staticmethod
    def calcTrajectory():
        return

    @staticmethod
    def setTrackingOffsets(Time=None, RA=None, DEC=None, DECcorr=None):
        return

    @staticmethod
    def clearTrackingOffsets():
        return


class MountModel:
    def __init__(self):
        self.starList = []
        self.nameList = []
        self.numberStars = 1
        self.errorRMS = 1
        self.terms = 1
        self.positionAngle = Angle(degrees=0)
        self.polarError = Angle(degrees=0)
        self.orthoError = Angle(degrees=0)
        self.azimuthError = Angle(degrees=0)
        self.altitudeError = Angle(degrees=0)
        self.altitudeTurns = 0
        self.azimuthTurns = 0

    @staticmethod
    def programModelFromStarList():
        return

    @staticmethod
    def clearModel():
        return

    @staticmethod
    def deleteName():
        return

    @staticmethod
    def storeName(a):
        return

    @staticmethod
    def loadName(a):
        return

    @staticmethod
    def parseStars(a, b):
        return

    @staticmethod
    def addStar(a):
        return

    @staticmethod
    def deletePoint(a):
        return


class MountFirmware:
    def __init__(self):
        self.product = "test"
        self.hardware = "test"
        self.vString = Version("0.0.0")
        self.date = "test"
        self.time = "test"

    @staticmethod
    def checkNewer(a):
        return True

    @staticmethod
    def isHW2024():
        return True

    @staticmethod
    def isHW2012():
        return True


class MountGeometry:
    def __init__(self):
        self.offNorth = 0
        self.offEast = 0
        self.offVert = 0
        self.offNorthGEM = 0
        self.offEastGEM = 0
        self.offVertGEM = 0
        self.offPlateOTA = 0
        self.domeRadius = 0
        self.offGemPlate = 0
        self.domeRadius = 100


class MountSetting:
    def __init__(self):
        self.meridianLimitSlew = 3
        self.meridianLimitTrack = 4
        self.horizonLimitHigh = 90
        self.horizonLimitLow = 0
        self.timeToFlip = 0
        self.statusUnattendedFlip = False
        self.statusDualAxisTracking = False
        self.statusRefraction = False
        self.refractionTemp = 0
        self.refractionPress = 0
        self.wakeOnLan = "None"
        self.autoPowerOn = "None"
        self.typeConnection = 1
        self.trackingRate = 60.2
        self.slewRateMin = 0
        self.slewRateMax = 1
        self.webInterfaceStat = True
        self.UTCExpire = None
        self.gpsSynced = True
        self.weatherTemperature = 0.0
        self.weatherPressure = 1000.0
        self.weatherDewPoint = 0.0
        self.weatherHumidity = 50
        self.weatherAge = 1
        self.settleTime = 0

    @staticmethod
    def timeToMeridian():
        return 0

    @staticmethod
    def setMeridianLimitSlew():
        return True

    @staticmethod
    def setMeridianLimitTrack():
        return True

    @staticmethod
    def setHorizonLimitLow():
        return True

    @staticmethod
    def setHorizonLimitHigh():
        return True

    @staticmethod
    def setSlewRate():
        return True

    @staticmethod
    def setUnattendedFlip():
        return True

    @staticmethod
    def setDualAxisTracking():
        return True

    @staticmethod
    def setRefractionTemp(a):
        return True

    @staticmethod
    def setRefractionPress(a):
        return True

    @staticmethod
    def setRefraction():
        return True

    @staticmethod
    def setWOL():
        return True

    @staticmethod
    def setAutoPower():
        return True

    @staticmethod
    def setSlewSpeedMax():
        return True

    @staticmethod
    def setSlewSpeedHigh():
        return True

    @staticmethod
    def setSlewSpeedMed():
        return True

    @staticmethod
    def setSlewSpeedLow():
        return True

    @staticmethod
    def checkRateSidereal():
        return False

    @staticmethod
    def checkRateLunar():
        return False

    @staticmethod
    def checkRateSolar():
        return False

    @staticmethod
    def setLunarTracking():
        return True

    @staticmethod
    def setSolarTracking():
        return True

    @staticmethod
    def setSiderealTracking():
        return True

    @staticmethod
    def setWebInterface():
        return True

    @staticmethod
    def setDirectWeatherUpdateType(a):
        return True

    @staticmethod
    def setSettleTime(a):
        return True

    @staticmethod
    def setRefractionParam(temperature=20, pressure=900):
        return True


class MountSignals(QObject):
    locationDone = Signal()
    settingDone = Signal()
    pointDone = Signal()
    mountIsUp = Signal()
    firmwareDone = Signal()
    calcTLEdone = Signal()
    getTLEdone = Signal()
    getModelDone = Signal()
    alert = Signal()
    namesDone = Signal()
    slewed = Signal()
    calcTrajectoryDone = Signal(object)
    calcProgress = Signal(object)


class MountObsSite:
    def __init__(self):
        self.Alt = Angle(degrees=0)
        self.Az = Angle(degrees=0)
        self.haJNowTarget = Angle(hours=0)
        self.decJNowTarget = Angle(degrees=0)
        self.angularPosRA = Angle(degrees=0)
        self.angularPosDEC = Angle(degrees=0)
        self.errorAngularPosRA = Angle(degrees=0)
        self.errorAngularPosDEC = Angle(degrees=0)
        self.raJNow = Angle(hours=0)
        self.decJNow = Angle(degrees=0)
        self.haJNow = Angle(hours=0)
        self.AzTarget = Angle(degrees=0)
        self.AltTarget = Angle(degrees=0)
        self.pierside = "E"
        self.piersideTarget = "E"
        self.timeSidereal = Angle(hours=12)
        self.location = wgs84.latlon(latitude_degrees=20, longitude_degrees=10, elevation_m=500)
        self.ts = load.timescale(builtin=True)
        self.timeJD = self.ts.tt_jd(2459580.5)
        self.timeDiff = 0
        self.loader = Loader("tests/work/data", verbose=False)
        self.status = 0
        self.statusSat = "E"
        self.UTC2TT = 69.184

    @staticmethod
    def setLongitude(a):
        return True

    @staticmethod
    def setLatitude(a):
        return True

    @staticmethod
    def setElevation(a):
        return True

    @staticmethod
    def startTracking():
        return True

    @staticmethod
    def stopTracking():
        return True

    @staticmethod
    def park():
        return True

    @staticmethod
    def unpark():
        return True

    @staticmethod
    def flip():
        return True

    @staticmethod
    def stop():
        return True

    @staticmethod
    def stopMoveAll():
        return True

    @staticmethod
    def moveNorth():
        return True

    @staticmethod
    def stopMoveNorth():
        return True

    @staticmethod
    def moveEast():
        return True

    @staticmethod
    def stopMoveEast():
        return True

    @staticmethod
    def moveWest():
        return True

    @staticmethod
    def stopMoveWest():
        return True

    @staticmethod
    def moveSouth():
        return True

    @staticmethod
    def stopMoveSouth():
        return True

    @staticmethod
    def startSlewing(slewType=None):
        return True

    @staticmethod
    def adjustClock(a):
        return True

    @staticmethod
    def setTargetAltAz(alt_degrees=0, az_degrees=0):
        return True

    @staticmethod
    def setTargetRaDec(ra_hours=0, dec_degrees=0):
        return True

    @staticmethod
    def setLocation(loc):
        return True

    @staticmethod
    def syncPositionToTarget():
        return True

    @staticmethod
    def parkOnActualPosition():
        return True


class Mount(QObject):
    def __init__(self):
        self.signals = MountSignals()
        self.obsSite = MountObsSite()
        self.geometry = MountGeometry()
        self.firmware = MountFirmware()
        self.setting = MountSetting()
        self.satellite = MountSatellite()
        self.model = MountModel()
        self.host = None

    @staticmethod
    def bootMount():
        return True

    @staticmethod
    def shutdown():
        return True

    @staticmethod
    def getLocation():
        return True

    @staticmethod
    def calcTLE():
        return

    @staticmethod
    def getTLE():
        return

    @staticmethod
    def progTrajectory():
        return

    @staticmethod
    def startMountClockTimer():
        return

    @staticmethod
    def stopMountClockTimer():
        return

    @staticmethod
    def calcTransformationMatricesTarget():
        return

    @staticmethod
    def calcMountAltAzToDomeAltAz():
        return

    @staticmethod
    def calcTransformationMatricesActual():
        return (1, 1, np.array([0, 0, 0]), np.array([0, 0, 0]), np.array([0, 0, 0]))

    @staticmethod
    def syncPositionToTarget():
        return

    @staticmethod
    def getModel():
        return

    @staticmethod
    def getNames():
        return


class CheckBox:
    checked = False

    def isChecked(self):
        return self.checked

    def setChecked(self, value):
        self.checked = value


class LineEdit:
    valueFloat = 0

    def value(self):
        return self.valueFloat

    def setValue(self, value):
        self.valueFloat = value


class Test(QObject):
    def __init__(self):
        self.tabsMovable = CheckBox()
        self.offLAT = LineEdit()


class MainW:
    def __init__(self):
        self.ui = Test()
        self.gameControllerRunning = False


class App(QObject):
    __version__ = "test"
    tabsMovable = Signal(object)
    update10s = Signal()
    timer0_1s = QTimer()
    update0_1s = Signal()
    update1s = Signal()
    update3s = Signal()
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
    game_sL = Signal(object, object)
    game_sR = Signal(object, object)

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
    def quit():
        return
