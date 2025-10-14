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
from mw4.logic.powerswitch.pegasusUPBAlpaca import PegasusUPBAlpaca
from mw4.logic.powerswitch.pegasusUPBAscom import PegasusUPBAscom
from mw4.logic.powerswitch.pegasusUPBIndi import PegasusUPBIndi


class PegasusUPB:
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
            "indi": PegasusUPBIndi(self),
            "alpaca": PegasusUPBAlpaca(self),
        }
        if platform.system() == "Windows":
            self.run["ascom"] = PegasusUPBAscom(self)

        for fw in self.run:
            self.defaultConfig["frameworks"].update({fw: self.run[fw].defaultConfig})

    def startCommunication(self) -> None:
        """ """
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        """ """
        self.run[self.framework].stopCommunication()

    def togglePowerPort(self, port: str) -> None:
        """ """
        self.run[self.framework].togglePowerPort(port=port)

    def togglePowerPortBoot(self, port: str) -> None:
        """ """
        self.run[self.framework].togglePowerPortBoot(port=port)

    def toggleHubUSB(self) -> None:
        """ """
        self.run[self.framework].toggleHubUSB()

    def togglePortUSB(self, port: str) -> None:
        """ """
        self.run[self.framework].togglePortUSB(port=port)

    def toggleAutoDew(self) -> None:
        """ """
        self.run[self.framework].toggleAutoDew()

    def sendDew(self, port: str, value: float) -> None:
        """ """
        self.run[self.framework].sendDew(port=port, value=value)

    def sendAdjustableOutput(self, value: float) -> None:
        """ """
        self.run[self.framework].sendAdjustableOutput(value=value)

    def reboot(self) -> None:
        """ """
        self.run[self.framework].reboot()
