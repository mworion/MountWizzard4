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


class FilterAscom(AscomClass):
    """ """

    CYCLE_POLL_DATA = 1000

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals

    def workerGetInitialConfig(self) -> None:
        """ """
        super().workerGetInitialConfig()
        names = self.getAscomProperty("Names")
        if names is None:
            return

        for i, name in enumerate(names):
            self.storePropertyToData(name, f"FILTER_NAME.FILTER_SLOT_NAME_{i:1.0f}")

    def workerPollData(self) -> None:
        """ """
        position = self.getAscomProperty("Position")
        if position == -1 or position is None:
            return
        self.storePropertyToData(position, "FILTER_SLOT.FILTER_SLOT_VALUE")

    def sendFilterNumber(self, filterNumber: int = 0) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.setAscomProperty("Position", filterNumber)
