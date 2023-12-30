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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from queue import Queue

# external packages
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool, QTimer
from skyfield.api import wgs84, load, Loader, Angle
import numpy as np

# local import


class Automation:
    installPath = None
    updaterApp = None
    automateFast = False
    automateSlow = False

    @staticmethod
    def uploadTLEData():
        return

    @staticmethod
    def uploadMPCData(comets=False):
        return

    @staticmethod
    def uploadEarthRotationData():
        return


class PlateSolve:
    class PlateSolveSignals(QObject):
        done = pyqtSignal()
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = PlateSolveSignals()
    framework = None
    run = {}
    deviceName = ''
    defaultConfig = {'framework': '',
                     'frameworks': {}}

    @staticmethod
    def solveThreading():
        return

    @staticmethod
    def abort():
        return

    @staticmethod
    def checkAvailability():
        return True, True


class Camera:
    class CameraSignals(QObject):
        saved = pyqtSignal()
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)
        exposeReady = pyqtSignal()
        exposed = pyqtSignal()
        downloaded = pyqtSignal()

    run = {'indi': 'dummy'}

    @staticmethod
    def expose(imagePath=None,
               expTime=None,
               binning=None,
               subFrame=None,
               fastReadout=None,
               focalLength=None,
               ra=None,
               dec=None):
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

    signals = CameraSignals()
    expTime = 0
    expTimeN = 0
    binning = 1
    binningN = 1
    subFrame = 100
    fastDownload = False
    data = {}
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}


class Cover:
    class CoverSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = CoverSignals()
    data = {}
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}

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
        message = pyqtSignal(object)
        azimuth = pyqtSignal()
        slewFinished = pyqtSignal()
        deviceDisconnected = pyqtSignal()
        deviceConnected = pyqtSignal()
        serverDisconnected = pyqtSignal()

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
    defaultConfig = {'framework': '',
                     'frameworks': {}}

    @staticmethod
    def slewDome(altitude=None,
                 azimuth=None,
                 piersideT=None,
                 haT=None,
                 decT=None,
                 lat=None):
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
    def slewDome(azimuth=0,
                 altitude=0,
                 follow=False):
        return

    @staticmethod
    def followDome(azimuth=0,
                   altitude=0):
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


class Skymeter:
    class SkymeterSignals(QObject):
        version = pyqtSignal()
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = SkymeterSignals()
    data = {}
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}


class DirectWeather:
    class DirectWeatherSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = DirectWeatherSignals()
    data = {}
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}


class OnlineWeather:
    class OnlineWeatherSignals(QObject):
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = OnlineWeatherSignals()
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}
    data = {}


class SeeingWeather:
    class SeeingWeatherSignals(QObject):
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)
        update = pyqtSignal()

    signals = SeeingWeatherSignals()
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}
    data = {}


class SensorWeather:
    class SensorWeatherSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = SensorWeatherSignals()
    data = {}
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}


class PowerWeather:
    class PowerWeatherSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = PowerWeatherSignals()
    data = {}
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}


class Filter:
    class FilterSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = FilterSignals()
    data = {}
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}

    @staticmethod
    def sendFilterNumber(filterNumber=None):
        return

    @staticmethod
    def sendFilterName(filterName=None):
        return


class Focuser:
    class FocuserSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = FocuserSignals()
    framework = None
    data = {}
    defaultConfig = {'framework': '',
                     'frameworks': {}}

    @staticmethod
    def move():
        return

    @staticmethod
    def halt():
        return


class Measure:
    class MeasureSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    class CSV:
        csvFilename = ''

    signals = MeasureSignals()
    data = {}
    framework = None
    devices = {}
    defaultConfig = {'framework': '',
                     'frameworks': {}}
    run = {'csv': CSV()}


class Relay:
    class RelaySignals(QObject):
        message = pyqtSignal(object)
        statusReady = pyqtSignal()
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = RelaySignals()
    data = {}
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}
    timerTask = QTimer()

    @staticmethod
    def getRelay():
        return

    @staticmethod
    def pulse():
        return

    @staticmethod
    def switch(a):
        return


class Remote:
    class RemoteSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = RemoteSignals()
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}


class Telescope:
    class TelescopeSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    class Test:
        deviceName = ''

    signals = TelescopeSignals()
    data = {}
    framework = None
    run = {'indi': Test()}
    focalLength = 100
    aperture = 100
    defaultConfig = {'framework': '',
                     'frameworks': {}}

    @staticmethod
    def stopCommunication():
        return

    @staticmethod
    def startCommunication(loadConfig=None):
        return


class Hipparcos:
    name = ['test']
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
        version = pyqtSignal()
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = PowerSignals()
    data = {}
    framework = None
    defaultConfig = {'framework': '',
                     'frameworks': {}}

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

    @staticmethod
    def loadHorizonP(fileName=''):
        return

    @staticmethod
    def saveHorizonP(fileName=''):
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
    def genGrid(minAlt=None,
                maxAlt=None,
                numbRows=None,
                numbCols=None,
                keep=None):
        return

    @staticmethod
    def genAlign(altBase=None,
                 azBase=None,
                 numberBase=None,
                 keep=None):
        return

    @staticmethod
    def genGreaterCircle(selection=None,
                         keep=None):
        return

    @staticmethod
    def generateDSOPath(ha=None,
                        dec=None,
                        timeJD=None,
                        location=None,
                        numberPoints=None,
                        keep=None):
        return

    @staticmethod
    def generateGoldenSpiral(numberPoints=None,
                             keep=None):
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
            name = ''
            jdStart = 1
            jdEnd = 1
            flip = False
            message = ''
            altitude = None
            azimuth = None

        tleParams = Name()
        trajectoryParams = Name()
        settlingTime = 0

        @staticmethod
        def setTLE(line0='', line1='', line2=''):
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
        def setTrackingOffsets(Time=None,
                               RA=None,
                               DEC=None,
                               DECcorr=None):
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
        def programAlign():
            return

        @staticmethod
        def clearAlign():
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
        product = 'test'
        hardware = 'test'
        vString = '12345'
        date = 'test'
        time = 'test'

        @staticmethod
        def checkNewer(a):
            return True

    class MountGeometry:
        offNorth = 0
        offEast = 0
        offVert = 0
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
        def setRefractionParam(temperature=None,
                               pressure=None):
            return True

    class MountSignals(QObject):
        locationDone = pyqtSignal()
        settingDone = pyqtSignal()
        pointDone = pyqtSignal()
        mountUp = pyqtSignal()
        firmwareDone = pyqtSignal()
        calcTLEdone = pyqtSignal()
        getTLEdone = pyqtSignal()
        alignDone = pyqtSignal()
        alert = pyqtSignal()
        namesDone = pyqtSignal()
        slewFinished = pyqtSignal()
        calcTrajectoryDone = pyqtSignal(object)
        trajectoryProgress = pyqtSignal(object)

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
        pierside = 'E'
        timeSidereal = Angle(hours=12)
        location = wgs84.latlon(latitude_degrees=20, longitude_degrees=10,
                                elevation_m=500)
        ts = load.timescale(builtin=True)
        timeJD = ts.tt_jd(2459580.5)
        timeDiff = 0
        loader = Loader('tests/workDir', verbose=False)
        status = 0
        statusSat = 'E'
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
        def setTargetAltAz(alt_degrees=0,
                           az_degrees=0):
            return True

        @staticmethod
        def setTargetRaDec(ra_hours=0,
                           dec_degrees=0):
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
    def startClockTimer():
        return

    @staticmethod
    def stopClockTimer():
        return

    @staticmethod
    def calcTransformationMatricesTarget():
        return

    @staticmethod
    def calcMountAltAzToDomeAltAz():
        return

    @staticmethod
    def calcTransformationMatricesActual():
        return 1, 1, [0, 0, 0], [0, 0, 0], [0, 0, 0]

    @staticmethod
    def syncPositionToTarget():
        return

    @staticmethod
    def getAlign():
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

        tabsMovable = CheckBox()
    ui = Test()


class App(QObject):
    config = {'mainW': {}}
    deviceStat = {}
    statusOperationRunning = 0
    tabsMovable = pyqtSignal(object)
    update10s = pyqtSignal()
    timer0_1s = QTimer()
    update0_1s = pyqtSignal()
    update1s = pyqtSignal()
    update3s = pyqtSignal()
    update30s = pyqtSignal(bool)
    update10m = pyqtSignal()
    update30m = pyqtSignal()
    update1h = pyqtSignal()
    start1s = pyqtSignal()
    start3s = pyqtSignal()
    start5s = pyqtSignal()
    start10s = pyqtSignal()
    hostChanged = pyqtSignal()
    sendSatelliteData = pyqtSignal()
    updateDomeSettings = pyqtSignal()
    drawHorizonPoints = pyqtSignal()
    drawBuildPoints = pyqtSignal()
    redrawHemisphere = pyqtSignal()
    redrawHorizon = pyqtSignal()
    showAnalyse = pyqtSignal(object)
    showImage = pyqtSignal(object)
    updatePointMarker = pyqtSignal()
    operationRunning = pyqtSignal(object)
    colorChange = pyqtSignal()
    virtualStop = pyqtSignal()
    mountOff = pyqtSignal()
    mountOn = pyqtSignal()
    buildPointsChanged = pyqtSignal()
    playSound = pyqtSignal(object)
    msg = pyqtSignal(object, object, object, object)
    remoteCommand = pyqtSignal(object)
    gameABXY = pyqtSignal(object)
    gamePMH = pyqtSignal(object)
    gameDirection = pyqtSignal(object)
    game_sL = pyqtSignal(object, object)
    game_sR = pyqtSignal(object, object)
    messageQueue = Queue()

    plateSolve = PlateSolve()
    automation = Automation()
    camera = Camera()
    cover = Cover()

    data = Data()
    directWeather = DirectWeather()
    filter = Filter()
    focuser = Focuser()
    measure = Measure()
    mount = Mount()
    onlineWeather = OnlineWeather()
    seeingWeather = SeeingWeather()
    power = Power()
    powerWeather = PowerWeather()
    dome = Dome()
    relay = Relay()
    remote = Remote()
    sensorWeather = SensorWeather()
    skymeter = Skymeter()
    telescope = Telescope()
    hipparcos = Hipparcos()

    ephemeris = load('tests/testData/de440_mw4.bsp')
    mwGlob = {'modelDir': 'tests/workDir/model',
              'imageDir': 'tests/workDir/image',
              'dataDir': 'tests/workDir/data',
              'workDir': 'tests/workDir',
              'measureDir': 'tests/workDir/measure',
              'tempDir': 'tests/workDir/temp',
              'configDir': 'tests/workDir/config',
              }
    uiWindows = {}
    mainW = MainW()
    threadPool = QThreadPool()
    __version__ = 'test'

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
