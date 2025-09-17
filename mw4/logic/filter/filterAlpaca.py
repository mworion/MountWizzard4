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
from base.alpacaClass import AlpacaClass


class FilterAlpaca(AlpacaClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.data = parent.data

    def workerGetInitialConfig(self) -> None:
        """ """
        super().workerGetInitialConfig()
        names = self.getAlpacaProperty("names")
        if names is None:
            return

        for i, name in enumerate(names):
            if name is None:
                continue
            self.data[f"FILTER_NAME.FILTER_SLOT_NAME_{i:1.0f}"] = name

    def workerPollData(self) -> None:
        """ """
        if not self.deviceConnected:
            return

        position = self.getAlpacaProperty("position")
        if position == -1 or position is None:
            return
        self.storePropertyToData(position, "FILTER_SLOT.FILTER_SLOT_VALUE")

    def sendFilterNumber(self, filterNumber: int = 0) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.setAlpacaProperty("position", Position=filterNumber)
