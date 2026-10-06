# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.indiClass import IndiClass
from typing import Any


class FocuserIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def move(self, position: int) -> None:
        self.txQ.put(
            (
                self.config.deviceName,
                "ABS_FOCUS_POSITION",
                {"FOCUS_ABSOLUTE_POSITION": position},
            )
        )

    def halt(self) -> None:
        pass
