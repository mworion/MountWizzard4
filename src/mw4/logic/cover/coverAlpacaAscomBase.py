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
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon
from typing import Any


class CoverAlpacaAscomBase(AlpacaAscomCommon):
    COVERSTATES: list[str] = [
        "NotPresent",
        "Closed",
        "Moving",
        "Open",
        "Unknown",
        "Error",
    ]

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None:
        state = self.getDeviceProp("CoverState")
        if state is None:
            return
        self.storePropertyToData(self.COVERSTATES[int(state)], "Status.Cover")

    def closeCover(self) -> None:
        self.callDeviceMethodQueued("CloseCover")

    def openCover(self) -> None:
        self.callDeviceMethodQueued("OpenCover")

    def haltCover(self) -> None:
        self.callDeviceMethodQueued("HaltCover")
