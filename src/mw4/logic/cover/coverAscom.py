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
from mw4.base.ascomClass import AscomClass
from typing import Any


class CoverAscom(AscomClass):
    COVERSTATES: list[str] = ["NotPresent", "Closed", "Moving", "Open", "Unknown", "Error"]

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

        self.signals = parent.signals
        self.data = parent.data

    def pollData(self) -> None:
        state = self.getAscomProperty("CoverState")
        if state is None:
            return
        self.storePropertyToData(self.COVERSTATES[int(state)], "Status.Cover")

    def closeCover(self) -> None:
        self.callAscomMethodQueued("CloseCover")

    def openCover(self) -> None:
        self.callAscomMethodQueued("OpenCover")

    def haltCover(self) -> None:
        self.callAscomMethodQueued("HaltCover")
