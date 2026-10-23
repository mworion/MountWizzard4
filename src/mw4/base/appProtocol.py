# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from mw4.base.appSignals import AppSignals
    from mw4.base.bootstrap import MwGlob
    from mw4.base.timeManager import TimeManager
    from mw4.deviceRegistry import DeviceRegistry
    from mw4.gui.mainWindow.mainWindow import MainWindow
    from mw4.logic.controllers.model.buildpoints import BuildPoint
    from mw4.logic.controllers.model.hipparcos import Hipparcos
    from mw4.logic.profiles.config import ProfileConfig
    from PySide6.QtCore import QThreadPool
    from queue import Queue
    from skyfield.jpllib import SpiceKernel


@runtime_checkable
class HasConfig(Protocol):
    """Application version and configuration access."""

    __version__: str
    config: ProfileConfig

    def initConfig(self) -> None: ...

    def storeConfig(self) -> None: ...


@runtime_checkable
class HasThreadPool(Protocol):
    """Shared thread pool for workers."""

    threadPool: QThreadPool
    MAX_THREAD_COUNT: int


@runtime_checkable
class HasDevices(Protocol):
    """Device registry."""

    dReg: DeviceRegistry


@runtime_checkable
class HasMessaging(Protocol):
    """Grouped signals (including msg and playSound) and the message queue."""

    signals: AppSignals
    messageQueue: Queue


@runtime_checkable
class HasTime(Protocol):
    """Time manager and astronomical reference data."""

    timeMgr: TimeManager
    ephemeris: SpiceKernel
    hipparcos: Hipparcos


@runtime_checkable
class HasMountState(Protocol):
    """Online state, running operation and global paths."""

    isOnline: bool
    statusOperationRunning: int
    mwGlob: MwGlob


@runtime_checkable
class HasBuildPoints(Protocol):
    """Build point data."""

    buildPoint: BuildPoint


@runtime_checkable
class HasMainWindow(Protocol):
    """Main window reference."""

    mainW: MainWindow


@runtime_checkable
class AppProtocol(
    HasConfig,
    HasThreadPool,
    HasDevices,
    HasMessaging,
    HasTime,
    HasMountState,
    HasBuildPoints,
    HasMainWindow,
    Protocol,
):
    """Structural type of the complete application surface, the composition
    of all role protocols. Consumers should declare the smallest role
    protocol they need. Both MountWizzard4 and the test stub App satisfy it
    without inheritance. All mw4 imports are type-only, so importing this
    module at runtime never creates an import cycle.
    """
