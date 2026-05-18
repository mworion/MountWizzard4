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
from typing import Any


class FocuserAscom(AscomClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def pollData(self) -> None:
        self.getAndStoreAscomProperty("Position", "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION")

    def move(self, position: int) -> None:
        self.callAscomMethodQueued("Move", Position=position)

    def halt(self) -> None:
        self.callAscomMethodQueued("Halt")
