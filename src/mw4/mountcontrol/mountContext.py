# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from mw4.mountcontrol.firmware import Firmware
    from mw4.mountcontrol.mount import DeviceConfigMount
    from mw4.mountcontrol.mountSignals import MountSignals
    from mw4.mountcontrol.obsSite import ObsSite
    from pathlib import Path
    from PySide6.QtCore import QThreadPool, SignalInstance


class MountContext(Protocol):
    """Structural type of the parent object handed to the mountcontrol
    sub-objects. It lists only the members they access, so MountDevice and
    test fakes satisfy it without inheritance. All imports are type-only to
    avoid import cycles with mount.py.
    """

    config: DeviceConfigMount
    loggingTrace: bool
    mountIsUp: bool
    signals: MountSignals
    obsSite: ObsSite
    firmware: Firmware
    threadPool: QThreadPool
    pathToData: Path
    domeConfig: dict[str, Any]
    updateDomeSettings: SignalInstance
