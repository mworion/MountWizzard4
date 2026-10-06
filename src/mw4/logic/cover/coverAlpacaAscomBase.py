# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon
from typing import Any, ClassVar


class CoverAlpacaAscomBase(AlpacaAscomCommon):
    COVERSTATES: ClassVar[list[str]] = [
        "NotPresent",
        "Closed",
        "Moving",
        "Open",
        "Unknown",
        "Error",
    ]

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None:
        state = self.getDeviceProp("CoverState")
        if state is None:
            return
        self.storePropertyToData(self.COVERSTATES[int(state)], "Status.Cover")
        if state == 1:
            self.data["CAP_PARK.PARK"] = True
        elif state == 3:
            self.data["CAP_PARK.PARK"] = False
        else:
            self.data["CAP_PARK.PARK"] = None

    def closeCover(self) -> None:
        self.callDeviceMethodQueued("CloseCover")

    def openCover(self) -> None:
        self.callDeviceMethodQueued("OpenCover")

    def haltCover(self) -> None:
        self.callDeviceMethodQueued("HaltCover")
