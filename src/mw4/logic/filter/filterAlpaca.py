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


class FilterAlpaca(AlpacaClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.data = parent.data

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        names = self.getDeviceProp("Names")
        if names is None:
            return

        for i, name in enumerate(names):
            if name is None:
                continue
            self.data[f"FILTER_NAME.FILTER_SLOT_NAME_{i:1.0f}"] = name

    def pollData(self) -> None:
        position = self.getDeviceProp("Position")
        if position == -1 or position is None:
            return
        self.storePropertyToData(position, "FILTER_SLOT.FILTER_SLOT_VALUE")

    def sendFilterNumber(self, filterNumber: int = 0) -> None:
        self.setDevicePropQueued("Position", filterNumber)
