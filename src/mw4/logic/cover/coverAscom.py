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
    coverStates = ["NotPresent", "Closed", "Moving", "Open", "Unknown", "Error"]

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

        self.signals = parent.signals
        self.data = parent.data

    def workerPollData(self) -> None:
        state = self.getAscomProperty("CoverState")
        stateText = self.coverStates[state]
        self.storePropertyToData(stateText, "Status.Cover")

    def closeCover(self) -> None:
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.CloseCover)

    def openCover(self) -> None:
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.OpenCover)

    def haltCover(self) -> None:
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.HaltCover)
