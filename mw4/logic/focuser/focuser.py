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
from logic.focuser.focuserIndi import FocuserIndi
from logic.focuser.focuserAlpaca import FocuserAlpaca

if platform.system() == "Windows":
    from logic.focuser.focuserAscom import FocuserAscom


class Focuser:
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
            "indi": FocuserIndi(self.app, self.signals, self.data),
            "alpaca": FocuserAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == "Windows":
            self.run["ascom"] = FocuserAscom(self.app, self.signals, self.data)

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
    def loadConfig(self, value: bool):
        for fw in self.run:
            self.run[fw].loadConfig = value

    def startCommunication(self) -> None:
        """ """
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        """ """
        self.run[self.framework].stopCommunication()

    def move(self, position: int) -> None:
        """ """
        self.run[self.framework].move(position=position)

    def halt(self) -> None:
        """ """
        self.run[self.framework].halt()
