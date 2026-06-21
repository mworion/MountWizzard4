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
import logging
import platform
from mw4.base.signalsDevices import Signals
from mw4.logic.cover.coverAlpaca import CoverAlpaca
from mw4.logic.cover.coverIndi import CoverIndi
from collections.abc import Any

if platform.system() == "Windows":
    from mw4.logic.cover.coverAscom import CoverAscom


class Cover:
    log = logging.getLogger("MW4")
    DEVICE_TYPE: str = "covercalibrator"

    def __init__(self, app: Any) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        self.framework: str = ""
        self.run: dict[str, Any] = {
            "indi": CoverIndi(self),
            "alpaca": CoverAlpaca(self),
        }
        if platform.system() == "Windows":
            self.run["ascom"] = CoverAscom(self)

    def startCommunication(self) -> None:
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()

    def closeCover(self) -> None:
        self.run[self.framework].closeCover()

    def openCover(self) -> None:
        self.run[self.framework].openCover()

    def haltCover(self) -> None:
        self.run[self.framework].haltCover()
