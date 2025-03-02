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
from logic.powerswitch.pegasusUPBIndi import PegasusUPBIndi
from logic.powerswitch.pegasusUPBAscom import PegasusUPBAscom
from logic.powerswitch.pegasusUPBAlpaca import PegasusUPBAlpaca


class PegasusUPB:
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
            "indi": PegasusUPBIndi(self.app, self.signals, self.data),
            "alpaca": PegasusUPBAlpaca(self.app, self.signals, self.data),
        }
        if platform.system() == "Windows":
            self.run["ascom"] = PegasusUPBAscom(self.app, self.signals, self.data)

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
