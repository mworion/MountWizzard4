############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.mainWaddon.tabAlmanac import Almanac
from mw4.gui.mainWaddon.tabAsteroid import Asteroid
from mw4.gui.mainWaddon.tabComet import Comet
from mw4.gui.mainWaddon.tabEnviron_Seeing import EnvironSeeing
from mw4.gui.mainWaddon.tabEnviron_Weather import EnvironWeather
from mw4.gui.mainWaddon.tabImage_Manage import ImageManage
from mw4.gui.mainWaddon.tabImage_Stats import ImageStats
from mw4.gui.mainWaddon.tabModel import Model
from mw4.gui.mainWaddon.tabModel_BuildPoints import BuildPoints
from mw4.gui.mainWaddon.tabModel_Manage import ModelManage
from mw4.gui.mainWaddon.tabModel_Status import ModelStatus
from mw4.gui.mainWaddon.tabMount import Mount
from mw4.gui.mainWaddon.tabMount_Command import MountCommand
from mw4.gui.mainWaddon.tabMount_Move import MountMove
from mw4.gui.mainWaddon.tabMount_Park import Park
from mw4.gui.mainWaddon.tabMount_Sett import MountSett
from mw4.gui.mainWaddon.tabPower import Power
from mw4.gui.mainWaddon.tabRelay import Relay
from mw4.gui.mainWaddon.tabSat_Search import SatSearch
from mw4.gui.mainWaddon.tabSat_Track import SatTrack
from mw4.gui.mainWaddon.tabTools_IERSTime import IERSTime
from mw4.gui.mainWaddon.tabTools_Rename import Rename
from typing import Any


class MainWindowAddons:
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app

        self.addons: dict[str, TabAddon] = {
            "Almanac": Almanac(mainW),
            "Asteroid": Asteroid(mainW),
            "BuildPoints": BuildPoints(mainW),
            "Comet": Comet(mainW),
            "EnvironWeather": EnvironWeather(mainW),
            "EnvironSeeing": EnvironSeeing(mainW),
            "ImageManage": ImageManage(mainW),
            "ImageStats": ImageStats(mainW),
            "ManageModel": ModelManage(mainW),
            "Model": Model(mainW),
            "ModelStatus": ModelStatus(mainW),
            "Mount": Mount(mainW),
            "MountCommand": MountCommand(mainW),
            "MountMove": MountMove(mainW),
            "MountSett": MountSett(mainW),
            "Park": Park(mainW),
            "Power": Power(mainW),
            "Relay": Relay(mainW),
            "Rename": Rename(mainW),
            "SatSearch": SatSearch(mainW),
            "SatTrack": SatTrack(mainW),
            "IERSTime": IERSTime(mainW),
        }

    def initConfig(self) -> None:
        for addon in self.addons.values():
            addon.initConfig()

    def storeConfig(self) -> None:
        for addon in self.addons.values():
            addon.storeConfig()

    def setupIcons(self) -> None:
        for addon in self.addons.values():
            addon.setupIcons()

    def updateColorSet(self) -> None:
        for addon in self.addons.values():
            addon.updateColorSet()
