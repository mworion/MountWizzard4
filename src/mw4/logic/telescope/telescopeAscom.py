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
from mw4.logic.telescope.telescopeAlpacaAscomBase import TelescopeAlpacaAscomBase


class TelescopeAscom(TelescopeAlpacaAscomBase, AscomClass):
    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        aperture = self.getDeviceProp("ApertureDiameter")
        if isinstance(aperture, float):
            self.data["TELESCOPE_INFO.TELESCOPE_APERTURE"] = aperture * 1000
        focalLength = self.getDeviceProp("FocalLength")
        if isinstance(focalLength, float):
            self.data["TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH"] = focalLength * 1000
