# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
import platform
from mw4.base.appProtocol import AppProtocol
from mw4.base.signalsDevices import Signals
from mw4.logic.focuser.focuserAlpaca import FocuserAlpaca
from mw4.logic.focuser.focuserIndi import FocuserIndi
from typing import Any

if platform.system() == "Windows":
    from mw4.logic.focuser.focuserAscom import FocuserAscom


class Focuser:
    log = logging.getLogger("MW4")
    DEVICE_TYPE: str = "focuser"

    def __init__(self, app: AppProtocol) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        self.framework: str = ""
        self.run: dict[str, Any] = {
            "indi": FocuserIndi(self),
            "alpaca": FocuserAlpaca(self),
        }
        if platform.system() == "Windows":
            self.run["ascom"] = FocuserAscom(self)

    def startCommunication(self) -> None:
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()

    def move(self, position: int) -> None:
        self.run[self.framework].move(position=position)

    def halt(self) -> None:
        self.run[self.framework].halt()
