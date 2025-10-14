############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
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
from mw4.base.signalsDevices import Signals
from mw4.logic.filter.filterAlpaca import FilterAlpaca
from mw4.logic.filter.filterIndi import FilterIndi

if platform.system() == "Windows":
    from mw4.logic.filter.filterAscom import FilterAscom


class Filter:
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
            "indi": FilterIndi(self),
            "alpaca": FilterAlpaca(self),
        }

        if platform.system() == "Windows":
            self.run["ascom"] = FilterAscom(self)

        for fw in self.run:
            self.defaultConfig["frameworks"].update({fw: self.run[fw].defaultConfig})

    def startCommunication(self) -> None:
        """ """
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        """ """
        self.run[self.framework].stopCommunication()

    def sendFilterNumber(self, filterNumber: int = 1) -> None:
        """ """
        if self.framework not in self.run:
            return
        self.run[self.framework].sendFilterNumber(filterNumber=filterNumber)
