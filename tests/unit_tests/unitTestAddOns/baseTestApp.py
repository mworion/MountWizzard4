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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from pathlib import Path
from queue import Queue

import numpy as np
from astropy import log as astropy_log
from packaging.version import Version

# external packages
from PySide6.QtCore import QObject, QThreadPool, QTimer, Signal
from skyfield.api import Angle, Loader, load, load_file, wgs84

from mw4.base.signalsDevices import Signals

astropy_log.setLevel("ERROR")

# local import


class PlateSolve:
    signals = Signals()
    framework = None
    run = {}
    deviceName = ""
    defaultConfig = {"framework": "", "frameworks": {}}

    @staticmethod
    def solve(a, b):
        return

    @staticmethod
    def abort():
        return

    @staticmethod
    def checkAvailability():
        return True, True


class Camera:
    class CameraSignals(QObject):
        saved = Signal()
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)
        exposed = Signal()
        downloaded = Signal()

    signals = CameraSignals()
    exposureTime = 0
    exposureTime1 = 0
    exposureTimeN = 0
    binning = 1
    binning1 = 1
    binningN = 1
    focalLength = 100
    subFrame = 100
    fastReadout = False
    data = {}
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}

    run = {"indi": "dummy"}

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


class Cover:
    class CoverSignals(QObject):
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    signals = CoverSignals()
    data = {}
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}

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


class Dome:
    class DomeSignals(QObject):
        message = Signal(object)
        azimuth = Signal()
        slewed = Signal()
        deviceDisconnected = Signal()
        deviceConnected = Signal()
        serverDisconnected = Signal()

    domeShutterWidth = 0.6
    offGEM = 0
    offLAT = 0
    offNorth = 0
    offEast = 0
    domeRadius = 1.0
    clearOpening = 1
    data = {}
    framework = None
    signals = DomeSignals()
    defaultConfig = {"framework": "", "frameworks": {}}

    @staticmethod
    def slewDome(altitude=None, azimuth=None, piersideT=None, haT=None, decT=None, lat=None):
        return

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


class SensorWeather:
    class SensorWeatherSignals(QObject):
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    signals = SensorWeatherSignals()
    data = {}
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}


class OnlineWeather:
    class OnlineWeatherSignals(QObject):
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    signals = OnlineWeatherSignals()
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}
    data = {}


class DirectWeather:
    class DirectWeatherSignals(QObject):
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    signals = DirectWeatherSignals()
    data = {}
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}


class SeeingWeather:
    class SeeingWeatherSignals(QObject):
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)
        update = Signal()

    signals = SeeingWeatherSignals()
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}
    data = {}


class Filter:
    class FilterSignals(QObject):
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    signals = FilterSignals()
    data = {}
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}

    @staticmethod
    def sendFilterNumber(filterNumber=None):
        return

    @staticmethod
    def sendFilterName(filterName=None):
        return


class Focuser:
    class FocuserSignals(QObject):
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    signals = FocuserSignals()
    framework = None
    data = {}
    defaultConfig = {"framework": "", "frameworks": {}}

    @staticmethod
    def move():
        return

    @staticmethod
    def halt():
        return


class Measure:
    class MeasureSignals(QObject):
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    class CSV:
        csvFilename = ""

    signals = MeasureSignals()
    data = {}
    framework = None
    devices = {}
    defaultConfig = {"framework": "", "frameworks": {}}
    run = {"csv": CSV()}


class Relay:
    class RelaySignals(QObject):
        message = Signal(object)
        statusReady = Signal()
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    signals = RelaySignals()
    data = {}
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}
    timerTask = QTimer()

    @staticmethod
    def getRelay():
        return

    @staticmethod
    def pulse(a):
        return

    @staticmethod
    def switch(a):
        return


class Remote:
    class RemoteSignals(QObject):
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    signals = RemoteSignals()
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}


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
    defaultConfig = {"framework": "", "frameworks": {}}

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


class Power:
    class PowerSignals(QObject):
        version = Signal()
        message = Signal(object)
        serverConnected = Signal()
        serverDisconnected = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    signals = PowerSignals()
    data = {}
    framework = None
    defaultConfig = {"framework": "", "frameworks": {}}

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
    buildP = []
    horizonP = []
    SOLVED = 0
    UNPROCESSED = 1
    FAILED = 2

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
    def loadBuildP():
        return

    @staticmethod
    def genGrid(minAlt=None, maxAlt=None, numbRows=None, numbCols=None, keep=None):
        return

    @staticmethod
    def genAlign(altBase=None, azBase=None, numberBase=None, keep=None):
        return

    @staticmethod
    def genGreaterCircle(stepHA, StepDEC, distFlip ):
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
    def setStatusBuildP(a, b):
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
    def sort():
        return

    @staticmethod
    def setStatusBuildP(a, b):
        return

    def isAboveHorizon(self, point):
        """
        isAboveHorizon calculates for a given point the relationship to the actual horizon
        and determines if this point is above the horizon line. for that there will be a
        linear interpolation for the horizon line points.

        :param point:
        :return:
        """
        if point[1] > 360:
            point = (point[0], 360)

        if point[1] < 0:
            point = (point[0], 0)

        x = range(0, 361)

        if self.horizonP:
            xRef = [i[1] for i in self.horizonP]
            yRef = [i[0] for i in self.horizonP]

        else:
            xRef = [0]
            yRef = [0]

        y = np.interp(x, xRef, yRef)

        if point[0] > y[int(point[1])]:
            return True

        else:
            return False


class Mount(QObject):
    class MountSatellite:
        class Name:
            name = ""
            jdStart = 1
            jdEnd = 1
            flip = False
            message = ""
            altitude = None
            azimuth = None

        tleParams = Name()
        trajectoryParams = Name()
        settlingTime = 0

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
        starList = []
        nameList = []
        numberStars = 1
        errorRMS = 1
        terms = 1
        positionAngle = Angle(degrees=0)
        polarError = Angle(degrees=0)
        orthoError = Angle(degrees=0)
        azimuthError = Angle(degrees=0)
        altitudeError = Angle(degrees=0)
        altitudeTurns = 0
        azimuthTurns = 0

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
        product = "test"
        hardware = "test"
        vString = Version("0.0.0")
        date = "test"
        time = "test"

        @staticmethod
        def checkNewer(a):
            return True

    class MountGeometry:
        offNorth = 0
        offEast = 0
        offVert = 0
        offNorthGEM = 0
        offEastGEM = 0
        offVertGEM = 0
        offPlateOTA = 0
        domeRadius = 0
        offGemPlate = 0
        domeRadius = 100

    class MountSetting:
        meridianLimitSlew = 3
        meridianLimitTrack = 4
        horizonLimitHigh = 90
        horizonLimitLow = 0
        timeToFlip = 0
        statusUnattendedFlip = False
        statusDualAxisTracking = False
        statusRefraction = False
        refractionTemp = 0
        refractionPress = 0
        wakeOnLan = False
        typeConnection = 1
        trackingRate = 60.2
        slewRateMin = 0
        slewRateMax = 1
        webInterfaceStat = True
        UTCExpire = None
        gpsSynced = True
        weatherTemperature = 0.0
        weatherPressure = 1000.0
        weatherDewPoint = 0.0
        weatherHumidity = 50
        weatherAge = 1
        settleTime = 0

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
        mountUp = Signal()
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
        Alt = Angle(degrees=0)
        Az = Angle(degrees=0)
        haJNowTarget = Angle(hours=0)
        decJNowTarget = Angle(degrees=0)
        piersideTarget = None
        angularPosRA = Angle(degrees=0)
        angularPosDEC = Angle(degrees=0)
        errorAngularPosRA = Angle(degrees=0)
        errorAngularPosDEC = Angle(degrees=0)
        raJNow = Angle(hours=0)
        decJNow = Angle(degrees=0)
        haJNow = Angle(hours=0)
        AzTarget = Angle(degrees=0)
        AltTarget = Angle(degrees=0)
        pierside = "E"
        timeSidereal = Angle(hours=12)
        location = wgs84.latlon(latitude_degrees=20, longitude_degrees=10, elevation_m=500)
        ts = load.timescale(builtin=True)
        timeJD = ts.tt_jd(2459580.5)
        timeDiff = 0
        loader = Loader("tests/work/data", verbose=False)
        status = 0
        statusSat = "E"
        UTC2TT = 69.184

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

    signals = MountSignals()
    obsSite = MountObsSite()
    geometry = MountGeometry()
    firmware = MountFirmware()
    setting = MountSetting()
    satellite = MountSatellite()
    model = MountModel()

    host = None

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


class MainW:
    class Test(QObject):
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

        tabsMovable = CheckBox()
        offLAT = LineEdit()

    ui = Test()
    gameControllerRunning = False


class App(QObject):
    config = {"mainW": {}}
    deviceStat = {
        "dome": False,
        "mount": False,
        "camera": False,
        "plateSolve": False,
    }
    statusOperationRunning = 0
    tabsMovable = Signal(object)
    update10s = Signal()
    timer0_1s = QTimer()
    update0_1s = Signal()
    update1s = Signal()
    update3s = Signal()
    update30s = Signal(bool)
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
    messageQueue = Queue()
    plateSolve = PlateSolve()
    camera = Camera()
    cover = Cover()
    data = Data()
    filter = Filter()
    focuser = Focuser()
    measure = Measure()
    mount = Mount()
    sensor1Weather = SensorWeather()
    sensor2Weather = SensorWeather()
    sensor3Weather = SensorWeather()
    onlineWeather = OnlineWeather()
    directWeather = DirectWeather()
    seeingWeather = SeeingWeather()
    power = Power()
    dome = Dome()
    relay = Relay()
    remote = Remote()
    telescope = Telescope()
    hipparcos = Hipparcos()

    ephemeris = load_file("tests/testData/de440_mw4.bsp")
    mwGlob = {
        "modelDir": Path("tests/work/model"),
        "imageDir": Path("tests/work/image"),
        "dataDir": Path("tests/work/data"),
        "workDir": Path("tests/work"),
        "measureDir": Path("tests/work/measure"),
        "tempDir": Path("tests/work/temp"),
        "configDir": Path("tests/work/config"),
        "logDir": Path("tests/work/log"),
    }
    uiWindows = {}
    mainW = MainW()
    threadPool = QThreadPool()
    __version__ = "test"

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
