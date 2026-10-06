# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.indiClass import IndiClass
from typing import Any


class LightPanelIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def lightOn(self) -> None:
        self.txQ.put((self.config.deviceName, "FLAT_LIGHT_CONTROL", {"FLAT_LIGHT_ON": "On"}))

    def lightOff(self) -> None:
        self.txQ.put((self.config.deviceName, "FLAT_LIGHT_CONTROL", {"FLAT_LIGHT_OFF": "On"}))

    def lightIntensity(self, value: float) -> None:
        self.txQ.put(
            (
                self.config.deviceName,
                "FLAT_LIGHT_INTENSITY",
                {"FLAT_LIGHT_INTENSITY_VALUE": value},
            )
        )
