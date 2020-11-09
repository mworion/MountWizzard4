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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from queue import Queue

# external packages
from PyQt5.QtCore import QObject, pyqtSignal
from skyfield.api import Topos, load, Loader

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

        tleParams = Name()

        @staticmethod
        def setTLE(line0='', line1='', line2=''):
            return

        @staticmethod
        def slewTLE():
            return

    class MountFirmware:
        product = 'test'
        hardware = 'test'
        vString = '12345'
        date = 'test'
        time = 'test'

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

    class MountSignals(QObject):
        locationDone = pyqtSignal()
        settingDone = pyqtSignal()
        pointDone = pyqtSignal()
        firmwareDone = pyqtSignal()
        calcTLEdone = pyqtSignal()
        getTLEdone = pyqtSignal()

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
        location = Topos(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
        ts = load.timescale(builtin=True)
        timeJD = ts.now()
        loader = Loader('tests/temp')
        status = 0

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


class Automation:
    installPath = None

    @staticmethod
    def uploadTLEData():
        return

    @staticmethod
    def uploadMPCData():
        return

    @staticmethod
    def uploadEarthRotationData():
        return

class App(QObject):
    config = {'mainW': {}}
    deviceStat = {}
    update10s = pyqtSignal()
    update1s = pyqtSignal()
    update3s = pyqtSignal()
    update30m = pyqtSignal()
    sendSatelliteData = pyqtSignal()
    message = pyqtSignal(str, int)
    messageQueue = Queue()
    mount = Mount()
    power = Power()
    automation = Automation()
    ephemeris = load('tests/testData/de421_23.bsp')
    mwGlob = {'modelDir': 'tests/model',
              'imageDir': 'tests/image',
              'dataDir': 'tests/data',
              }
    uiWindows = {}


