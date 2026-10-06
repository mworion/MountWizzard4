# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon
from typing import Any


class TelescopeAlpacaAscomBase(AlpacaAscomCommon):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        aperture = self.getDeviceProp("ApertureDiameter")
        if aperture:
            self.data["TELESCOPE_INFO.TELESCOPE_APERTURE"] = float(aperture) * 1000
        focalLength = self.getDeviceProp("FocalLength")
        if focalLength:
            self.data["TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH"] = float(focalLength) * 1000
