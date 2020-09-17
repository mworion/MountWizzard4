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

    signals = MountSignals()
    setting = MountSetting()


class App(QObject):
    config = {}
    update10s = pyqtSignal()
    update0_1s = pyqtSignal()
    redrawHemisphere = pyqtSignal()
    mount = Mount()
    dome = Dome()
    data = Data()
    hipparcos = Hipparcos()

