############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from mw4.base.bootstrap import MwGlob
    from mw4.base.deviceRegistry import DeviceRegistry
    from mw4.base.timeManager import TimeManager
    from mw4.gui.mainWindow.mainWindow import MainWindow
    from mw4.logic.buildData.buildpoints import BuildPoint
    from mw4.logic.buildData.hipparcos import Hipparcos
    from PySide6.QtCore import QThreadPool, SignalInstance
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
    msg: SignalInstance
    colorChange: SignalInstance
    playSound: SignalInstance
    showImage: SignalInstance
    showAnalyse: SignalInstance
    timebaseChanged: SignalInstance
    onlineModeChanged: SignalInstance
    hidModeChanged: SignalInstance
    relayChanged: SignalInstance
    parkChanged: SignalInstance
    redrawHemisphere: SignalInstance
    redrawHorizon: SignalInstance
    updatePointMarker: SignalInstance
    drawBuildPoints: SignalInstance
    buildPointsChanged: SignalInstance
    operationRunning: SignalInstance
    updateDomeSettings: SignalInstance
    remoteCommand: SignalInstance
    refreshModel: SignalInstance
    refreshName: SignalInstance
    sendSatelliteData: SignalInstance
    updateSatellite: SignalInstance
    showSatellite: SignalInstance

    # --- configuration ---
    def initConfig(self) -> None: ...

    def storeConfig(self) -> None: ...
