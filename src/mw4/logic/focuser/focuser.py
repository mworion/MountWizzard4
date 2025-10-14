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
from mw4.logic.focuser.focuserAlpaca import FocuserAlpaca
from mw4.logic.focuser.focuserIndi import FocuserIndi

if platform.system() == "Windows":
    from mw4.logic.focuser.focuserAscom import FocuserAscom


class Focuser:
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
            "indi": FocuserIndi(self),
            "alpaca": FocuserAlpaca(self),
        }

        if platform.system() == "Windows":
            self.run["ascom"] = FocuserAscom(self)

        for fw in self.run:
            self.defaultConfig["frameworks"].update({fw: self.run[fw].defaultConfig})

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
