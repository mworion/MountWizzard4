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

# external packages
from PyQt5.QtCore import QObject, pyqtSignal

# local import


class Data:

    horizonP = []
    buildP = []

    @staticmethod
    def generateCelestialEquator():
        return [(0, 0)]

    @staticmethod
    def clearBuildP():
        return


class Hipparcos:
    @staticmethod
    def calculateAlignStarPositionsAltAz():
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

    signals = DomeSignals()


class Mount(QObject):
    class MountSetting:
        meridianLimitSlew = 0
        meridianLimitTrack = 0
        horizonLimitHigh = 0
        horizonLimitLow = 0

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
        haJNowTarget = None
        decJNowTarget = None
        piersideTarget = None
        location = Location()

        @staticmethod
        def setTargetAltAz(alt_degrees=None, az_degrees=None):
            return

        @staticmethod
        def startSlewing():
            return

    signals = MountSignals()
    setting = MountSetting()
    obsSite = MountObsSite()


class App(QObject):
    config = {}
    update10s = pyqtSignal()
    update0_1s = pyqtSignal()
    message = pyqtSignal(str, int)
    redrawHemisphere = pyqtSignal()
    mount = Mount()
    dome = Dome()
    data = Data()
    hipparcos = Hipparcos()
    deviceStat = {}

