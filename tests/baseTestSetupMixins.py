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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from queue import Queue

# external packages
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool
from skyfield.api import wgs84, load, Loader

# local import


class Power:
    class PowerSignals(QObject):
        version = pyqtSignal()

    signals = PowerSignals()
    data = {}

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

        @staticmethod
        def setTLE(line0='', line1='', line2=''):
            return

        @staticmethod
        def slewTLE(julD=0, duration=0):
            return

        @staticmethod
        def calcTLE():
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

    class MountSetting:
        meridianLimitSlew = 0
        meridianLimitTrack = 0
        horizonLimitHigh = 0
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

    class MountSignals(QObject):
        locationDone = pyqtSignal()
        settingDone = pyqtSignal()
        pointDone = pyqtSignal()
        firmwareDone = pyqtSignal()
        calcTLEdone = pyqtSignal()
        getTLEdone = pyqtSignal()
        alert = pyqtSignal()
        slewFinished = pyqtSignal()
        calcTrajectoryDone = pyqtSignal()
        trajectoryProgress = pyqtSignal()

    class MountObsSite:

        class Location:
            latitude = None
            longitude = None
            elevation = None

        Alt = None
        Az = None
        haJNowTarget = None
        decJNowTarget = None
        piersideTarget = None
        angularPosRA = None
        angularPosDEC = None
        raJNow = None
        decJNow = None
        haJNow = None
        AzTarget = None
        AltTarget = None
        pierside = None
        location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
        ts = load.timescale(builtin=True)
        timeJD = ts.now()
        loader = Loader('tests/temp', verbose=False)
        status = 0
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
        def moveEast():
            return True

        @staticmethod
        def moveWest():
            return True

        @staticmethod
        def moveSouth():
            return True

        @staticmethod
        def startSlewing():
            return True

        @staticmethod
        def setTargetAltAz(alt_degrees=0,
                           az_degrees=0):
            return True

        @staticmethod
        def setTargetRaDec(ra_hours=0,
                           dec_degrees=0):
            return True

    signals = MountSignals()
    obsSite = MountObsSite()
    geometry = MountGeometry()
    firmware = MountFirmware()
    setting = MountSetting()
    satellite = MountSatellite()

    bootMount = None
    shutdown = None
    host = None

    @staticmethod
    def getLocation():
        return True

    @staticmethod
    def calcTLE():
        return

    @staticmethod
    def getTLE():
        return


class Automation:
    installPath = None

    @staticmethod
    def uploadTLEData():
        return

    @staticmethod
    def uploadMPCData(comets=False):
        return

    @staticmethod
    def uploadEarthRotationData():
        return


class Dome:
    class DomeSignals(QObject):
        slewFinished = pyqtSignal()

    domeShutterWidth = 0.6
    offGEM = 0
    offLAT = 0
    offNorth = 0
    offEast = 0
    domeRadius = 1.0
    data = {}
    signals = DomeSignals()

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
                 altitude=0):
        return

    @staticmethod
    def followDome(azimuth=0,
                   altitude=0):
        return


class Relay:
    class RelaySignals(QObject):
        statusReady = pyqtSignal()

    signals = RelaySignals()


class Camera:
    class CameraSignals(QObject):
        saved = pyqtSignal()

    signals = CameraSignals()


class Astrometry:
    class AstrometrySignals(QObject):
        done = pyqtSignal()

    signals = AstrometrySignals()


class OnlineWeather:
    class OnlineWeatherSignals(QObject):
        done = pyqtSignal()

    signals = OnlineWeatherSignals()


class Data:
    @staticmethod
    def loadHorizonP(fileName=''):
        return

    @staticmethod
    def saveHorizonP(fileName=''):
        return

    @staticmethod
    def isAboveHorizon(a):
        return


class App(QObject):
    config = {'mainW': {}}
    deviceStat = {}
    update10s = pyqtSignal()
    update1s = pyqtSignal()
    update3s = pyqtSignal()
    update30m = pyqtSignal()
    update1h = pyqtSignal()
    sendSatelliteData = pyqtSignal()
    updateDomeSettings = pyqtSignal()
    drawHorizonPoints = pyqtSignal()
    redrawHemisphere = pyqtSignal()
    message = pyqtSignal(str, int)
    messageQueue = Queue()
    mount = Mount()
    power = Power()
    dome = Dome()
    relay = Relay()
    data = Data()
    camera = Camera()
    automation = Automation()
    astrometry = Astrometry()
    onlineWeather = OnlineWeather()
    ephemeris = load('tests/testData/de421_23.bsp')
    mwGlob = {'modelDir': 'tests/model',
              'imageDir': 'tests/image',
              'dataDir': 'tests/data',
              'configDir': 'tests/config',
              }
    uiWindows = {}
    threadPool = QThreadPool()
