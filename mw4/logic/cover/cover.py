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
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.framework = ""
        self.run = {
            "indi": CoverIndi(self.app, self.signals, self.data),
            "alpaca": CoverAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == "Windows":
            self.run["ascom"] = CoverAscom(self.app, self.signals, self.data)

        for fw in self.run:
            self.defaultConfig["frameworks"].update({fw: self.run[fw].defaultConfig})

    @property
    def updateRate(self):
        return self.run[self.framework].updateRate

    @updateRate.setter
    def updateRate(self, value):
        value = int(value)
        for fw in self.run:
            self.run[fw].updateRate = value

    @property
    def loadConfig(self):
        return self.run[self.framework].loadConfig

    @loadConfig.setter
    def loadConfig(self, value):
        value = bool(value)
        for fw in self.run:
            self.run[fw].loadConfig = value

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
