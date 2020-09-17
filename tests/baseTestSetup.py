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


class Dome(QObject):
    class DomeSignals(QObject):
        azimuth = pyqtSignal()
        deviceDisconnected = pyqtSignal()
        deviceConnected = pyqtSignal()
        serverDisconnected = pyqtSignal()

    signals = DomeSignals()


class Mount(QObject):
    class MountSignals(QObject):
        settingDone = pyqtSignal()
        pointDone = pyqtSignal()

    signals = MountSignals()


class App(QObject):
    config = {}
    update10s = pyqtSignal()
    update0_1s = pyqtSignal()
    redrawHemisphere = pyqtSignal()
    mount = Mount()
    dome = Dome()
    data = Data()
