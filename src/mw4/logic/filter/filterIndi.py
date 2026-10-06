# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.indiClass import IndiClass
from typing import Any


class FilterIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def sendFilterNumber(self, filterNumber: int = 1) -> None:
        self.txQ.put((self.config.deviceName, "FILTER_SLOT", {"FILTER_SLOT_VALUE": filterNumber}))
