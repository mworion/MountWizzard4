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


class Focuser:
    class FocuserSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = FocuserSignals()


class Power:
    class PowerSignals(QObject):
        message = pyqtSignal(object)
        version = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = PowerSignals()
    data = {}


class Skymeter:
    class SkymeterSignals(QObject):
        message = pyqtSignal(object)
        serverConnected = pyqtSignal()
        serverDisconnected = pyqtSignal(object)
        deviceConnected = pyqtSignal(object)
        deviceDisconnected = pyqtSignal(object)

    signals = SkymeterSignals()
    data = {}


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


