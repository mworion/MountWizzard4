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
import logging
import platform

# external packages

# local imports
from base.signalsDevices import Signals
from logic.cover.coverIndi import CoverIndi
from logic.cover.coverAlpaca import CoverAlpaca

if platform.system() == "Windows":
    from logic.cover.coverAscom import CoverAscom


class Cover:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, app):
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data = {}
        self.loadConfig: bool = True
        self.updateRate: int = 1000
        self.deviceType: str = ""
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.framework = ""
        self.run = {
            "indi": CoverIndi(self),
            "alpaca": CoverAlpaca(self),
        }

        if platform.system() == "Windows":
            self.run["ascom"] = CoverAscom(self)

        for fw in self.run:
            self.defaultConfig["frameworks"].update({fw: self.run[fw].defaultConfig})

    def startCommunication(self) -> None:
        """ """
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        """ """
        self.run[self.framework].stopCommunication()

    def closeCover(self) -> None:
        """ """
        self.run[self.framework].closeCover()

    def openCover(self) -> None:
        """ """
        self.run[self.framework].openCover()

    def haltCover(self) -> None:
        """ """
        self.run[self.framework].haltCover()

    def lightOn(self) -> None:
        """ """
        self.run[self.framework].lightOn()

    def lightOff(self) -> None:
        """ """
        self.run[self.framework].lightOff()

    def lightIntensity(self, value: float) -> None:
        """ """
        self.run[self.framework].lightIntensity(value)
