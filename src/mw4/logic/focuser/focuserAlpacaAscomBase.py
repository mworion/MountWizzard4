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
from typing import Any


class FocuserAlpacaAscomBase:
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None:
        self.getAndStoreDeviceProp("Position", "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION")

    def move(self, position: int) -> None:
        self.callDeviceMethodQueued("Move", Position=position)

    def halt(self) -> None:
        self.callDeviceMethodQueued("Halt")
