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
from mw4.base.alpacaClass import AlpacaClass
from mw4.logic.filter.filterAlpacaAscomBase import FilterAlpacaAscomBase
from typing import Any


class FilterAlpaca(FilterAlpacaAscomBase, AlpacaClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent)
        self.deviceType = parent.DEVICE_TYPE

    def startCommunication(self) -> None:
        if not self.createAlpacaDevice(self.deviceType):
            self.msg.emit(2, "ALPACA", "Device type error", self.config.deviceName)
            return
        super().startCommunication()
