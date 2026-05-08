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
from typing import Any


class TelescopeAlpaca(AlpacaClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.data = parent.data

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        self.getAndStoreDeviceProp("ApertureDiameter", "TELESCOPE_INFO.TELESCOPE_APERTURE")
        self.getAndStoreDeviceProp("FocalLength", "TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH")
