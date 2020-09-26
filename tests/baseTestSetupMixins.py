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
from skyfield.api import Topos, load

# local import


class Mount(QObject):
    class MountGeometry:
        offNorth = 0
        offEast = 0
        offVert = 0
        domeRadius = 0
        offGemPlate = 0

    class MountSignals(QObject):
        locationDone = pyqtSignal()

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
        location = Topos(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
        ts = load.timescale(builtin=True)
        timeJD = ts.now()

    signals = MountSignals()
    obsSite = MountObsSite()
    geometry = MountGeometry()
    host = None


class App(QObject):
    update10s = pyqtSignal()
    update1s = pyqtSignal()
    update30m = pyqtSignal()
    message = pyqtSignal(str, int)
    messageQueue = Queue()
    mount = Mount()
    ephemeris = load('tests/testData/de421_23.bsp')


