############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class TelescopeAscom(AscomClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()

        value = self.getAscomProperty("ApertureDiameter")
        if isinstance(value, float):
            value = value * 1000

        self.storePropertyToData(value, "TELESCOPE_INFO.TELESCOPE_APERTURE")

        value = self.getAscomProperty("FocalLength")
        if isinstance(value, float):
            value = value * 1000

        self.storePropertyToData(value, "TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH")
        return True
