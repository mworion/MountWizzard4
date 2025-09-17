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
from base.indiClass import IndiClass


class FilterIndi(IndiClass):
    """ """

    UPDATE_RATE = 1

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals

    def sendFilterNumber(self, filterNumber: int = 1) -> None:
        """ """
        if self.device is None:
            return

        filterNo = self.device.getNumber("FILTER_SLOT")
        filterNo["FILTER_SLOT_VALUE"] = filterNumber
        self.client.sendNewNumber(
            deviceName=self.deviceName,
            propertyName="FILTER_SLOT",
            elements=filterNo,
        )
