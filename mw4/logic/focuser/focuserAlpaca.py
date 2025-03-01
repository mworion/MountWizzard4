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
from base.alpacaClass import AlpacaClass


class FocuserAlpaca(AlpacaClass):
    """ """

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals
        self.data = data

    def workerPollData(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.getAndStoreAlpacaProperty(
            "position", "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION"
        )

    def move(self, position: int) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.setAlpacaProperty("move", Position=position)

    def halt(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.getAlpacaProperty("halt")
