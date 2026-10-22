# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.logic.drivers.dome.domeAlpacaAscomBase import DomeAlpacaAscomBase
from mw4.logic.drivers.frameworks.alpacaClass import AlpacaClass


class DomeAlpaca(DomeAlpacaAscomBase, AlpacaClass):
    def __init__(self, parent: object) -> None:
        self.deviceType: str = "dome"
        super().__init__(parent)
