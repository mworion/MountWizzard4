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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from queue import Queue

# external packages
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool
from skyfield.api import wgs84, load

# local import


class Measure:
    class MeasureSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = MeasureSignals()


class Remote:
    class RemoteSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = RemoteSignals()


class Focuser:
    class FocuserSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = FocuserSignals()


class Telescope:
    class TelescopeSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = TelescopeSignals()


class Filter:
    class FilterSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = FilterSignals()


class Cover:
    class CoverSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = CoverSignals()


class Power:
    class PowerSignals(QObject):
        message = pyqtSignal(object)
        version = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = PowerSignals()


class Relay:
    class RelaySignals(QObject):
        message = pyqtSignal(object)
        statusReady = pyqtSignal()
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = RelaySignals()


class OnlineWeather:
    class OnlineWeatherSignals(QObject):
        message = pyqtSignal(object)
        dataReceived = pyqtSignal()
        connected = pyqtSignal()
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = OnlineWeatherSignals()


class DirectWeather:
    class DirectWeatherSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = DirectWeatherSignals()


class SensorWeather:
    class SensorWeatherSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = SensorWeatherSignals()


class PowerWeather:
    class PowerWeatherSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = PowerWeatherSignals()


class Skymeter:
    class SkymeterSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = SkymeterSignals()


class Astrometry:
    class AstrometrySignals(QObject):
        done = pyqtSignal(object)
        result = pyqtSignal(object)
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    @staticmethod
    def solve():
        return

    @staticmethod
    def abort():
        return

    signals = AstrometrySignals()
    run = {}
    solveThreading = None


class Camera:
    class CameraSignals(QObject):
        deviceDisconnected = pyqtSignal()
        deviceConnected = pyqtSignal()
        serverDisconnected = pyqtSignal()
        integrated = pyqtSignal()
        saved = pyqtSignal(object)
        message = pyqtSignal(object)

    @staticmethod
    def expose(imagePath=None,
               expTime=None,
               binning=None,
               subFrame=None,
               fastReadout=None,
               focalLength=None):
        return

    @staticmethod
    def abort():
        return

    signals = CameraSignals()
    expTime = 0
    expTimeN = 0
    binning = 1
    binningN = 1
    subFrame = 100
    fastDownload = False


class Dome(QObject):
    class DomeSignals(QObject):
        message = pyqtSignal(object)
        azimuth = pyqtSignal()
        slewFinished = pyqtSignal()
        deviceDisconnected = pyqtSignal()
        deviceConnected = pyqtSignal()
        serverDisconnected = pyqtSignal()

    @staticmethod
    def slewDome(altitude=None,
                 azimuth=None,
                 piersideT=None,
                 haT=None,
                 decT=None,
                 lat=None):
        return

    signals = DomeSignals()
    data = {}
    domeShutterWidth = 0


class Mount(QObject):
    class MountSetting:
        setSlewSpeedMax = 0
        setSlewSpeedHigh = 0
        setSlewSpeedMed = 0
        setSlewSpeedLow = 0

    class MountModel:
        starList = []

    class MountGeometry:
        offNorth = 0
        offEast = 0
        offVert = 0
        domeRadius = 0
        offGemPlate = 0

    class MountSignals(QObject):
        locationDone = pyqtSignal()
        firmwareDone = pyqtSignal()
        settingDone = pyqtSignal()
        alignDone = pyqtSignal()
        namesDone = pyqtSignal()
        calcTLEdone = pyqtSignal()
        getTLEdone = pyqtSignal()
        alert = pyqtSignal()
        mountUp = pyqtSignal()
        slewFinished = pyqtSignal()
        pointDone = pyqtSignal()

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
        AzTarget = None
        AltTarget = None
        location = wgs84.latlon(latitude_degrees=0,
                                longitude_degrees=0,
                                elevation_m=0)
        ts = load.timescale(builtin=True)
        timeJD = ts.now()

    signals = MountSignals()
    obsSite = MountObsSite()
    setting = MountSetting()
    geometry = MountGeometry()
    model = MountModel()
    host = None


class Automation:
    installPath = None
    updaterApp = None
    automateFast = False
    automateSlow = False


class App(QObject):
    config = {'mainW': {}}
    deviceStat = {}
    update10s = pyqtSignal()
    update1s = pyqtSignal()
    update3s = pyqtSignal()
    update30s = pyqtSignal()
    update30m = pyqtSignal()
    colorChange = pyqtSignal()
    hostChanged = pyqtSignal()
    switchHemisphere = pyqtSignal(object)
    remoteCommand = pyqtSignal(object)
    message = pyqtSignal(str, int)
    messageQueue = Queue()
    mount = Mount()
    dome = Dome()
    camera = Camera()
    astrometry = Astrometry()
    sensorWeather = SensorWeather()
    onlineWeather = OnlineWeather()
    directWeather = DirectWeather()
    powerWeather = PowerWeather()
    skymeter = Skymeter()
    automation = Automation()
    relay = Relay()
    power = Power()
    cover = Cover()
    filter = Filter()
    focuser = Focuser()
    telescope = Telescope()
    remote = Remote()
    measure = Measure()

    uiWindows = {}
    __version__ = 'test'
    threadPool = QThreadPool()
    ephemeris = load('tests/testData/de421_23.bsp')
    mwGlob = {'modelDir': 'tests/workDir/model',
              'imageDir': 'tests/workDir/image'}


