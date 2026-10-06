# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
import platform
from mw4.base.appProtocol import AppProtocol
from mw4.base.signalsDevices import Signals
from mw4.logic.lightPanel.lightPanelAlpaca import LightPanelAlpaca
from mw4.logic.lightPanel.lightPanelIndi import LightPanelIndi
from typing import Any

if platform.system() == "Windows":
    from mw4.logic.lightPanel.lightPanelAscom import LightPanelAscom


class LightPanel:
    log = logging.getLogger("MW4")
    DEVICE_TYPE: str = "covercalibrator"

    def __init__(self, app: AppProtocol) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        self.framework: str = ""
        self.run: dict[str, Any] = {
            "indi": LightPanelIndi(self),
            "alpaca": LightPanelAlpaca(self),
        }
        if platform.system() == "Windows":
            self.run["ascom"] = LightPanelAscom(self)

    def startCommunication(self) -> None:
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()

    def lightOn(self) -> None:
        self.run[self.framework].lightOn()

    def lightOff(self) -> None:
        self.run[self.framework].lightOff()

    def lightIntensity(self, value: float) -> None:
        self.run[self.framework].lightIntensity(value)
