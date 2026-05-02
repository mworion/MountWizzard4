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
# Licence APL2.0
#
###########################################################
import logging
import platform
from mw4.base.signalsDevices import Signals
from mw4.logic.lightPanel.lightPanelAlpaca import LightPanelAlpaca
from mw4.logic.lightPanel.lightPanelIndi import LightPanelIndi
from typing import Any

if platform.system() == "Windows":
    from mw4.logic.lightPanel.lightPanelAscom import LightPanelAscom


class LightPanel:
    log = logging.getLogger("MW4")

    def __init__(self, app: Any) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        self.loadConfig: bool = True
        self.updateRate: int = 1000
        self.deviceType: str = ""
        self.defaultConfig: dict[str, Any] = {"framework": "", "frameworks": {}}
        self.framework: str = ""
        self.run: dict[str, Any] = {
            "indi": LightPanelIndi(self),
            "alpaca": LightPanelAlpaca(self),
        }

        if platform.system() == "Windows":
            self.run["ascom"] = LightPanelAscom(self)

        for fw in self.run:
            self.defaultConfig["frameworks"].update({fw: self.run[fw].defaultConfig})

    def startCommunication(self) -> None:
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()

    def lightOn(self) -> None:
        self.run[self.framework].lightOn()

    def lightOff(self) -> None:
        self.run[self.framework].lightOff()

    def lightIntensity(self, value: float) -> None:
        self.run[self.framework].lightIntensity(value)
