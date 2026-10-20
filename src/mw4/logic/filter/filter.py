# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from mw4.base import platformInfo
from mw4.base.appProtocol import HasThreadPool
from mw4.base.signalsDevices import Signals
from mw4.logic.filter.filterAlpaca import FilterAlpaca
from mw4.logic.filter.filterIndi import FilterIndi
from typing import Any

if platformInfo.IS_WINDOWS:
    from mw4.logic.filter.filterAscom import FilterAscom


class Filter:
    log = logging.getLogger("MW4")
    DEVICE_TYPE: str = "filterwheel"

    def __init__(self, app: HasThreadPool) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        self.framework: str = ""
        self.run: dict[str, Any] = {
            "indi": FilterIndi(self),
            "alpaca": FilterAlpaca(self),
        }
        platformInfo.registerWindowsBackends(
            self.run,
            {
                "ascom": lambda: FilterAscom(self),
            },
        )

    def startCommunication(self) -> None:
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()

    def sendFilterNumber(self, filterNumber: int = 1) -> None:
        if self.framework not in self.run:
            return
        self.run[self.framework].sendFilterNumber(filterNumber=filterNumber)
