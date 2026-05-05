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
from mw4.base.alpacaClass import AlpacaClass
from typing import Any


class CoverAlpaca(AlpacaClass):
    COVER_STATES: list[str] = [
        "NotPresent", "Closed", "Moving", "Open", "Unknown", "Error"
    ]

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.alpacaSignals = parent.signals
        self.data = parent.data

    def pollData(self) -> None:
        state = self.getDeviceProp("CoverState")
        if state is None:
            return
        self.storePropertyToData(self.COVER_STATES[int(state)], "Status.Cover")

    def closeCover(self) -> None:
        self.callDeviceMethod("CloseCover")

    def openCover(self) -> None:
        self.callDeviceMethod("OpenCover")

    def haltCover(self) -> None:
        self.callDeviceMethod("HaltCover")
