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
from mw4.base.indiClass import IndiClass
from typing import Any


class CoverIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def closeCover(self) -> None:
        self.txQ.put((self.deviceName, "CAP_PARK", {"PARK": "On"}))

    def openCover(self) -> None:
        self.txQ.put((self.deviceName, "CAP_PARK", {"UNPARK": "On"}))

    @staticmethod
    def haltCover() -> None:
        pass
