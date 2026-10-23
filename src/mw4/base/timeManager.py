# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from dateutil.tz import tzlocal
from mw4.base.appProtocol import AppProtocol
from PySide6.QtCore import QObject, QTimer, Signal, SignalInstance
from skyfield.api import Time
from typing import cast

TICK_INTERVAL_MS: int = 100
CYCLIC_SCHEDULE: list[tuple[int, str]] = [
    (1, "update0_1s"),
    (5, "update0_5s"),
    (10, "update1s"),
    (30, "update3s"),
    (100, "update10s"),
    (300, "update30s"),
    (1800, "update3m"),
    (18000, "update30m"),
]
START_SCHEDULE: list[tuple[int, str]] = [
    (10, "start1s"),
    (30, "start3s"),
]


class TimeManager(QObject):
    log = logging.getLogger("MW4")

    # --- Cyclic update signals (emitted every 100ms tick) ---
    update0_1s = Signal()
    update0_5s = Signal()
    update1s = Signal()
    update3s = Signal()
    update10s = Signal()
    update30s = Signal()
    update3m = Signal()
    update30m = Signal()
    # --- Startup signals (emitted once after 1s) ---
    start1s = Signal()
    start3s = Signal()

    def __init__(self, app: AppProtocol) -> None:
        super().__init__()
        self.app: QObject = app
        self.counter: int = 0
        self.isStopped: bool = False
        self.timer: QTimer = QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.onTick)
        self.unitTimeUTC: bool = True
        self.signalByName: dict[str, SignalInstance] = {
            "update0_1s": self.update0_1s,
            "update0_5s": self.update0_5s,
            "update1s": self.update1s,
            "update3s": self.update3s,
            "update10s": self.update10s,
            "update30s": self.update30s,
            "update3m": self.update3m,
            "update30m": self.update30m,
            "start1s": self.start1s,
            "start3s": self.start3s,
        }

    def start(self) -> None:
        self.log.debug("Starting TimeManager")
        self.isStopped = False
        self.timer.start(TICK_INTERVAL_MS)

    def stop(self) -> None:
        self.log.debug("Stopping TimeManager")
        self.isStopped = True
        self.timer.stop()

    def onTick(self) -> None:
        if self.isStopped:
            return
        self.counter += 1
        self.emitCyclic()
        self.emitStart()

    def emitCyclic(self) -> None:
        for interval, signalName in CYCLIC_SCHEDULE:
            if self.counter % interval == 0:
                self.signalByName[signalName].emit()

    def emitStart(self) -> None:
        for tick, signalName in START_SCHEDULE:
            if self.counter == tick:
                self.signalByName[signalName].emit()

    def timeZoneString(self) -> str:
        if self.unitTimeUTC:
            return "(time is UTC)"
        else:
            return "(time is local)"

    def convertTime(self, value: Time, fString: str) -> str:
        if self.unitTimeUTC:
            return cast(str, value.utc_strftime(fString))
        else:
            # pyrefly: ignore[missing-attribute]
            return value.astimezone(tzlocal()).strftime(fString)
