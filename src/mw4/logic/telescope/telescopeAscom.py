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
from mw4.base.ascomClass import AscomClass


class TelescopeAscom(AscomClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals

    def workerGetInitialConfig(self):
        """ """
        super().workerGetInitialConfig()

        value = self.getAscomProperty("ApertureDiameter")
        if isinstance(value, float):
            value = value * 1000

        self.storePropertyToData(value, "TELESCOPE_INFO.TELESCOPE_APERTURE")

        value = self.getAscomProperty("FocalLength")
        if isinstance(value, float):
            value = value * 1000

        self.storePropertyToData(value, "TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH")
