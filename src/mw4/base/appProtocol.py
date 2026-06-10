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
"""Application Protocol: structural type for app interface used by tests."""

from __future__ import annotations

from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from mw4.base.deviceRegistry import DeviceRegistry
    from PySide6.QtCore import QThreadPool, Signal
    from skyfield.jpllib import SpiceKernel


# --- Narrow capability protocols ----------------------------------------


class HasThreadPool(Protocol):
    """Protocol for objects providing thread pool access."""

    threadPool: QThreadPool
    MAX_THREAD_COUNT: int


class HasMessageBus(Protocol):
    """Protocol for objects providing message bus access."""

    # msg.emit(level: int, source: str, title: str, body: str)
    msg: Signal
    messageQueue: Queue


class HasDeviceRegistry(Protocol):
    """Protocol for objects providing device registry access."""

    dReg: DeviceRegistry
    config: dict[str, Any]


class HasCyclicSignals(Protocol):
    """Protocol for objects providing cyclic timer signals."""

    update0_1s: Signal
    update1s: Signal
    update3s: Signal
    update10s: Signal
    update30s: Signal
    update3m: Signal
    update30m: Signal
    start3s: Signal


# --- Aggregate application protocol ------------------------------------


@runtime_checkable
class AppProtocol(
    HasThreadPool,
    HasMessageBus,
    HasDeviceRegistry,
    HasCyclicSignals,
    Protocol,
):
    """Structural type describing the surface of MountWizzard4 that the rest
    of the application is allowed to depend on.

    Anything (including the test ``App`` stub) that exposes the listed
    attributes satisfies this protocol — no inheritance required.
    """

    __version__: str
    mwGlob: dict[str, Path]
    ephemeris: SpiceKernel
    onlineMode: bool
    statusOperationRunning: int

    # Operational signals (kept small on purpose; expand only as needed).
    operationRunning: Signal
    stopDevices: Signal
    startDevice: Signal
    stopDevice: Signal
    colorChange: Signal
    playSound: Signal
