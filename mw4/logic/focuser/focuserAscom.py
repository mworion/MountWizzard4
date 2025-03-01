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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class FocuserAscom(AscomClass):
    """ """

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals

    def workerPollData(self):
        """
        """
        self.getAndStoreAscomProperty("Position", "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION")

    def move(self, position: int) -> None:
        """
        """
        if not self.deviceConnected:
            return
        self.client.move(position)

    def halt(self) -> None:
        """
        """
        if not self.deviceConnected:
            return
        self.getAscomProperty("Halt")
