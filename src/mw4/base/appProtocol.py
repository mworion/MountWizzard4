# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from mw4.base.bootstrap import MwGlob
    from mw4.base.deviceRegistry import DeviceRegistry
    from mw4.base.timeManager import TimeManager
    from mw4.gui.mainWindow.mainWindow import MainWindow
    from mw4.logic.buildData.buildpoints import BuildPoint
    from mw4.logic.buildData.hipparcos import Hipparcos
    from PySide6.QtCore import QThreadPool, Signal
    from queue import Queue
    from skyfield.jpllib import SpiceKernel


@runtime_checkable
class AppProtocol(Protocol):
    """Structural type of the application surface used by devices, windows
    and tabs. It lists only the members that consumers access, so both
    MountWizzard4 and the test stub App satisfy it without inheritance.
    All mw4 imports are type-only, so importing this module at runtime never
    creates an import cycle.
    """

    __version__: str
    MAX_THREAD_COUNT: int

    # --- state ---
    mwGlob: MwGlob
    threadPool: QThreadPool
    isOnline: bool
    statusOperationRunning: int
    messageQueue: Queue
    config: dict[str, Any]
    timeMgr: TimeManager
    dReg: DeviceRegistry
    buildPoint: BuildPoint
    hipparcos: Hipparcos
    ephemeris: SpiceKernel
    mainW: MainWindow

    # --- signals ---
    msg: Signal
    colorChange: Signal
    playSound: Signal
    showImage: Signal
    showAnalyse: Signal
    timebaseChanged: Signal
    onlineModeChanged: Signal
    hidModeChanged: Signal
    relayChanged: Signal
    parkChanged: Signal
    redrawHemisphere: Signal
    redrawHorizon: Signal
    updatePointMarker: Signal
    drawBuildPoints: Signal
    buildPointsChanged: Signal
    operationRunning: Signal
    updateDomeSettings: Signal
    remoteCommand: Signal
    refreshModel: Signal
    refreshName: Signal
    sendSatelliteData: Signal
    updateSatellite: Signal
    showSatellite: Signal

    # --- configuration ---
    def initConfig(self) -> None: ...

    def storeConfig(self) -> None: ...
