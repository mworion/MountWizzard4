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
from logic.telescope.telescopeIndi import TelescopeIndi
from logic.telescope.telescopeAlpaca import TelescopeAlpaca

if platform.system() == "Windows":
    from logic.telescope.telescopeAscom import TelescopeAscom


class Telescope:
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
        self.framework = ""
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.run = {
            "indi": TelescopeIndi(self),
            "alpaca": TelescopeAlpaca(self),
        }
        if platform.system() == "Windows":
            self.run["ascom"] = TelescopeAscom(self)

        for fw in self.run:
            self.defaultConfig["frameworks"].update({fw: self.run[fw].defaultConfig})

    def startCommunication(self) -> None:
        """ """
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        """ """
        self.run[self.framework].stopCommunication()
