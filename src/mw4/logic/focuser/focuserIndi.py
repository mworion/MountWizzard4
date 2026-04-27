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
from mw4.base.indiClass import IndiClass
from typing import Any


class FocuserIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def move(self, position: int) -> None:
        self.txQ.put((self.deviceName, "ABS_FOCUS_POSITION", {"FOCUS_ABSOLUTE_POSITION": position}))

    def halt(self) -> None:
        pass
