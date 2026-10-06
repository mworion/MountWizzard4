# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from pathlib import Path
from PySide6.QtCore import QObject, Signal


class Signals(QObject):
    deviceConnected = Signal(str)
    deviceDisconnected = Signal(str)
    exposed = Signal(Path)
    downloaded = Signal(Path)
    saved = Signal(Path)
    azimuth = Signal(object)
    slewed = Signal(str)
    message = Signal(str)
    version = Signal(int)
    result = Signal(object)
