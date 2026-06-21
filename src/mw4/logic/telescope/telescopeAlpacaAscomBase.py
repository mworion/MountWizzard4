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


class TelescopeAlpacaAscomBase(AlpacaAscomCommon):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        aperture = self.getDeviceProp("ApertureDiameter")
        if aperture:
            self.data["TELESCOPE_INFO.TELESCOPE_APERTURE"] = float(aperture) * 1000
        focalLength = self.getDeviceProp("FocalLength")
        if focalLength:
            self.data["TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH"] = float(focalLength) * 1000
