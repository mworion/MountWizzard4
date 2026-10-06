# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon
from typing import Any


class FocuserAlpacaAscomBase(AlpacaAscomCommon):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None:
        self.getAndStoreDeviceProp("Position", "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION")

    def move(self, position: int) -> None:
        self.callDeviceMethodQueued("Move", Position=position)

    def halt(self) -> None:
        self.callDeviceMethodQueued("Halt")
