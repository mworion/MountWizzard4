# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from PySide6.QtCore import QObject, Signal
from typing import Any


class RemoteDeviceShutdown(QObject):
    signalRemoteShutdown = Signal()


class DriverData:
    log = logging.getLogger("MW4")

    def __init__(self, data: dict) -> None:
        self.data: dict = data

    def storePropertyToData(self, value: Any, element: str) -> None:
        if value is None and element in self.data:
            del self.data[element]
        else:
            self.data[element] = value
