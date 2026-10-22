# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from collections.abc import Callable
from mw4.base import platformInfo
from mw4.base.appProtocol import HasThreadPool
from mw4.base.signalsDevices import Signals
from typing import Any, ClassVar


class DeviceFacade[AppT: HasThreadPool]:
    """common part of all device facades: back-end table, signals, start and stop."""

    log = logging.getLogger("MW4")
    DEVICE_TYPE: ClassVar[str] = ""

    def __init__(self, app: AppT) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        self.framework: str = ""
        self.run: dict[str, Any] = {}

    def buildBackends(
        self,
        backends: dict[str, Callable[[Any], Any]],
        windowsBackends: dict[str, Callable[[], Any]] | None = None,
    ) -> None:
        """creates the back-ends; Windows-only ones are given as factories."""
        self.run = {name: backend(self) for name, backend in backends.items()}
        platformInfo.registerWindowsBackends(self.run, windowsBackends or {})

    def startCommunication(self) -> None:
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()
