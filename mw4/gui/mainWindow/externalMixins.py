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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from gui.mainWmixin.runBasic import BasicRun
from gui.mainWmixin.tabAlmanac import Almanac
from gui.mainWmixin.tabAnalysis import Analysis
from gui.mainWmixin.tabAsteroid import Asteroid
from gui.mainWmixin.tabBuildPoints import BuildPoints
from gui.mainWmixin.tabComet import Comet
from gui.mainWmixin.tabEnvironWeather import EnvironWeather
from gui.mainWmixin.tabEnvironSeeing import EnvironSeeing
from gui.mainWmixin.tabImage_Manage import ImageManage
from gui.mainWmixin.tabImage_Stats import ImagsStats
from gui.mainWmixin.tabManageModel import ManageModel
from gui.mainWmixin.tabModel import Model
from gui.mainWmixin.tabMount import Mount
from gui.mainWmixin.tabPower import Power
from gui.mainWmixin.tabMountSett import MountSett
from gui.mainWmixin.tabRelay import Relay
from gui.mainWmixin.tabTools_Rename import Rename
from gui.mainWmixin.tabSat_Search import SatSearch
from gui.mainWmixin.tabSat_Track import SatTrack
from gui.mainWmixin.tabSett_Device import SettDevice
from gui.mainWmixin.tabSett_Dome import SettDome
from gui.mainWmixin.tabSett_Misc import SettMisc
from gui.mainWmixin.tabSett_Mount import SettMount
from gui.mainWmixin.tabSett_ParkPos import SettParkPos
from gui.mainWmixin.tabSett_Relay import SettRelay
from gui.mainWmixin.tabTools_IERSTime import IERSTime


class ExternalMixins:
    """
    """

    __all__ = ['ExternalMixins']

    def __init__(self, mainW):
        super().__init__()

        self.mainW = mainW
        self.app = mainW.app
        self.mixins = [
            Almanac(mainW),
            Analysis(mainW),
            Asteroid(mainW),
            BasicRun(mainW),
            BuildPoints(mainW),
            Comet(mainW),
            EnvironWeather(mainW),
            EnvironSeeing(mainW),
            ImageManage(mainW),
            ImagsStats(mainW),
            ManageModel(mainW),
            Model(mainW),
            Mount(mainW),
            MountSett(mainW),
            Power(mainW),
            Relay(mainW),
            Rename(mainW),
            SatSearch(mainW),
            SatTrack(mainW),
            SettDevice(mainW),
            SettDome(mainW),
            SettMisc(mainW),
            SettMount(mainW),
            SettParkPos(mainW),
            SettRelay(mainW),
            IERSTime(mainW),
        ]

    def initConfig(self) -> None:
        """
        """
        for mixin in self.mixins:
            if hasattr(mixin, 'initConfig'):
                mixin.initConfig()

    def storeConfig(self) -> None:
        """
        """
        for mixin in self.mixins:
            if hasattr(mixin, 'storeConfig'):
                mixin.storeConfig()

    def setupIcons(self) -> None:
        """
        """
        for mixin in self.mixins:
            if hasattr(mixin, 'setupIcons'):
                mixin.setupIcons()
