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
import logging

# external packages
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool
from skyfield.api import wgs84, load

# local import
import resource.resources as res
res.qInitResources()


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


class Telescope:
    focalLength = 0
    aperture = 0


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
    checkFastDownload = False


class Measure:
    data = {}
    devices = {}


class Data:

    horizonP = []
    buildP = []

    @staticmethod
    def generateCelestialEquator():
        return [(0, 0)]

    @staticmethod
    def clearBuildP():
        return

    @staticmethod
    def addHorizonP(a, b):
        return

    @staticmethod
    def delHorizonP(a):
        return

    @staticmethod
    def addBuildP(value=None, position=None):
        return

    @staticmethod
    def delBuildP(a):
        return


class Hipparcos:
    @staticmethod
    def calculateAlignStarPositionsAltAz():
        return

    @staticmethod
    def getAlignStarRaDecFromName():
        return

    az = []
    alt = []
    name = []


class Dome(QObject):
    class DomeSignals(QObject):
        azimuth = pyqtSignal()
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

    @staticmethod
    def avoidFirstOvershoot():
        return

    signals = DomeSignals()
    data = {}
    domeShutterWidth = 0


class Mount(QObject):
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
        webInterfaceStat = 0

        @staticmethod
        def setWebInterface(a):
            return

    class MountSignals(QObject):
        settingDone = pyqtSignal()
        pointDone = pyqtSignal()

    class MountObsSite:

        class Location:
            latitude = None
            longitude = None
            elevation = None

        Alt = None
        Az = None
        haJNow = None
        haJNowTarget = None
        decJNowTarget = None
        piersideTarget = None
        angularPosRA = None
        angularPosDEC = None
        AzTarget = None
        AltTarget = None
        location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
        ts = load.timescale(builtin=True)
        timeJD = ts.now()

        @staticmethod
        def setTargetAltAz(alt_degrees=None, az_degrees=None):
            return

        @staticmethod
        def setTargetRaDec(ra_hours=None, dec_degrees=None):
            return

        @staticmethod
        def startSlewing(slewType=None):
            return

    signals = MountSignals()
    setting = MountSetting()
    obsSite = MountObsSite()
    geometry = MountGeometry()
    host = None


class MainW:
    lastGenerator = None


class App(QObject):
    config = {}
    update10s = pyqtSignal()
    update0_1s = pyqtSignal()
    update1s = pyqtSignal()
    message = pyqtSignal(str, int)
    redrawHemisphere = pyqtSignal()
    updatePointMarker = pyqtSignal()
    updateDomeSettings = pyqtSignal()
    drawBuildPoints = pyqtSignal()
    enableEditPoints = pyqtSignal(object)
    drawHorizonPoints = pyqtSignal()
    sendSatelliteData = pyqtSignal()
    showAnalyse = pyqtSignal(object)
    showImage = pyqtSignal(object)
    messageQueue = Queue()
    mount = Mount()
    dome = Dome()
    data = Data()
    camera = Camera()
    measure = Measure()
    hipparcos = Hipparcos()
    telescope = Telescope()
    astrometry = Astrometry()
    mainW = MainW()
    deviceStat = {}
    threadPool = QThreadPool()
    mwGlob = {'modelDir': 'tests/workDir/model',
              'imageDir': 'tests/workDir/image',
              'configDir': 'tests/workDir/config',
              'dataDir': 'tests/workDir/data',
              'modelDir': 'tests/workDir/model',
              }
