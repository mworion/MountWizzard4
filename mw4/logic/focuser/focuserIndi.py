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


class FocuserIndi(IndiClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals

    def move(self, position: int) -> None:
        """ """
        if self.device is None:
            return
        pos = self.device.getNumber("ABS_FOCUS_POSITION")
        pos["FOCUS_ABSOLUTE_POSITION"] = position
        self.client.sendNewNumber(
            deviceName=self.deviceName,
            propertyName="ABS_FOCUS_POSITION",
            elements=pos,
        )

    def halt(self) -> None:
        """ """
        if self.device is None:
            return
        pos = self.device.getNumber("ABS_FOCUS_POSITION")
        self.client.sendNewNumber(
            deviceName=self.deviceName,
            propertyName="ABS_FOCUS_POSITION",
            elements=pos,
        )
