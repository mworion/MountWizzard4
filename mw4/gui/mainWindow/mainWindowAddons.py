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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from gui.mainWaddon.tabAlmanac import Almanac
from gui.mainWaddon.tabAsteroid import Asteroid
from gui.mainWaddon.tabComet import Comet
from gui.mainWaddon.tabEnvironWeather import EnvironWeather
from gui.mainWaddon.tabEnvironSeeing import EnvironSeeing
from gui.mainWaddon.tabImage_Manage import ImageManage
from gui.mainWaddon.tabImage_Stats import ImageStats
from gui.mainWaddon.tabModel import Model
from gui.mainWaddon.tabModel_Manage import ModelManage
from gui.mainWaddon.tabModel_Status import ModelStatus
from gui.mainWaddon.tabModel_BuildPoints import BuildPoints
from gui.mainWaddon.tabPower import Power
from gui.mainWaddon.tabMount import Mount
from gui.mainWaddon.tabMountCommand import MountCommand
from gui.mainWaddon.tabMountMove import MountMove
from gui.mainWaddon.tabMountSett import MountSett
from gui.mainWaddon.tabTools_Rename import Rename
from gui.mainWaddon.tabSat_Search import SatSearch
from gui.mainWaddon.tabSat_Track import SatTrack
from gui.mainWaddon.tabSett_Device import SettDevice
from gui.mainWaddon.tabSett_Dome import SettDome
from gui.mainWaddon.tabSett_Update import SettUpdate
from gui.mainWaddon.tabSett_Misc import SettMisc
from gui.mainWaddon.tabSett_Mount import SettMount
from gui.mainWaddon.tabSett_ParkPos import SettParkPos
from gui.mainWaddon.tabSett_Relay import SettRelay
from gui.mainWaddon.tabTools_IERSTime import IERSTime


class MainWindowAddons:
    """ """

    __all__ = ["MainWindowAddons"]

    def __init__(self, mainW):
        self.mainW = mainW
        self.app = mainW.app

        self.addons = {
            "Almanac": Almanac(mainW),
            "SettUpdate": SettUpdate(mainW),  # set isOnline state first
            "Asteroid": Asteroid(mainW),
            "BuildPoints": BuildPoints(mainW),
            "Comet": Comet(mainW),
            "EnvironWeather": EnvironWeather(mainW),
            "EnvironSeeing": EnvironSeeing(mainW),
            "ImageMange": ImageManage(mainW),
            "ImageStats": ImageStats(mainW),
            "ManageModel": ModelManage(mainW),
            "Model": Model(mainW),
            "ModelStatus": ModelStatus(mainW),
            "Mount": Mount(mainW),
            "MountCommand": MountCommand(mainW),
            "MountMove": MountMove(mainW),
            "MountSett": MountSett(mainW),
            "Power": Power(mainW),
            "Rename": Rename(mainW),
            "SatSearch": SatSearch(mainW),
            "SatTrack": SatTrack(mainW),
            "SettDevice": SettDevice(mainW),
            "SettDome": SettDome(mainW),
            "SettMisc": SettMisc(mainW),
            "SettMount": SettMount(mainW),
            "SettParkPos": SettParkPos(mainW),
            "SellRelay": SettRelay(mainW),
            "IERSTime": IERSTime(mainW),
        }

    def initConfig(self) -> None:
        """ """
        for addon in self.addons:
            if hasattr(self.addons[addon], "initConfig"):
                self.addons[addon].initConfig()

    def storeConfig(self) -> None:
        """ """
        for addon in self.addons:
            if hasattr(self.addons[addon], "storeConfig"):
                self.addons[addon].storeConfig()

    def setupIcons(self) -> None:
        """ """
        for addon in self.addons:
            if hasattr(self.addons[addon], "setupIcons"):
                self.addons[addon].setupIcons()

    def updateColorSet(self) -> None:
        """ """
        for addon in self.addons:
            if hasattr(self.addons[addon], "updateColorSet"):
                self.addons[addon].updateColorSet()
