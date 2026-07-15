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
import logging
import numpy as np
import socket
from mw4.base.tpool import Worker, startWorker
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.convert import valueToFloat
from mw4.mountcontrol.obsSite import MountStatus
from ping3 import ping
from PySide6.QtCore import QMutex
from skyfield.timelib import Time
from typing import Any


class MountTime:
    log = logging.getLogger("MW4")
    SOCKET_TIMEOUT = 0.2

    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.app = parent.app
        self.threadPool = parent.threadPool
        self.ts = parent.obsSite.ts
        self.timePC: Time = self.ts.now()
        self._timeDiff = np.full(25, 0.0)
        self.rtt: float = 0
        self.rtt_MA: np.ndarray = np.zeros(25)
        self.workerCycleMountUp: Worker | None = None
        self.workerPollSyncClock: Worker | None = None
        self.mutexCycleMountUp = QMutex()
        self.mutexPollSyncClock = QMutex()
        self.app.timeMgr.update1s.connect(self.checkMountUp)
        self.app.timeMgr.update30s.connect(self.syncClock)
        self.app.timeMgr.update1s.connect(self.pollSyncClock)

    @property
    def timeDiff(self) -> float:
        return float(np.mean(self._timeDiff))

    def runnerMountUp(self) -> None:
        rttLocal = ping(self.parent.config.hostAddress)
        if rttLocal is None:
            self.parent.mountIsUp = False
            self.log.info(f"Host: [{self.parent.config.hostAddress}] not resolved")
            return
        if rttLocal is False:
            self.parent.mountIsUp = False
            self.log.info(f"Timeout: [{self.parent.config.hostAddress}[ no response")
            return
        self.rtt_MA = np.roll(self.rtt_MA, 1)
        self.rtt_MA[0] = rttLocal
        self.rtt = np.mean(self.rtt_MA)
        try:
            with socket.socket() as client:
                client.settimeout(self.SOCKET_TIMEOUT)
                client.connect((self.parent.config.hostAddress, self.parent.config.port))
                client.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            self.log.error(f"No mount at [{self.parent.config.hostAddress}], error [{e}]")
        else:
            self.parent.signals.mountIsUp.emit(True)

    def clearMountUp(self) -> None:
        self.mutexCycleMountUp.unlock()

    def checkMountUp(self) -> None:
        worker = startWorker(
            self.threadPool,
            self.runnerMountUp,
            self.clearMountUp,
            mutex=self.mutexCycleMountUp,
        )
        if worker is not None:
            self.workerCycleMountUp = worker

    def adjustClock(self, delta: int) -> bool:
        conn = Connection(self.parent)
        sign = "+" if delta >= 0 else "-"
        delta = abs(delta)
        commandString = f":NUtim{sign}{delta:03.0f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def syncClock(self) -> None:
        if self.parent.config.syncTimeNone or not self.parent.mountIsUp:
            return
        mountTracks = self.app.dReg["mount"].obsSite.status in [
            MountStatus.TRACKING,
            MountStatus.FOLLOWING_SATELLITE,
        ]
        if mountTracks and self.parent.config.syncTimeNotTrack:
            return

        delta = self.timeDiff * 1000
        if abs(delta) < 1:
            return
        delta = int(max(min(delta, 999), -999))
        if not self.adjustClock(delta):
            self.log.warning(f"Clock sync failed with delta {delta} ms")

    def clearPollSyncClock(self) -> None:
        self.mutexPollSyncClock.unlock()

    def runnerPollSyncClock(self) -> None:
        conn = Connection(self.parent)
        commandString = ":GJD1#"
        suc, response, _ = conn.communicate(commandString)
        if not suc:
            return

        self.timePC = self.ts.now()
        timeMount = valueToFloat(response[0])
        timeMount = self.ts.tt_jd(timeMount + self.parent.obsSite.UTC2TT)
        self._timeDiff = np.roll(self._timeDiff, 1)
        delta = (self.timePC - timeMount) * 86400 - self.rtt
        self._timeDiff[0] = delta

    def pollSyncClock(self) -> None:
        worker = startWorker(
            self.threadPool,
            self.runnerPollSyncClock,
            self.clearPollSyncClock,
            mutex=self.mutexPollSyncClock,
            guard=lambda: self.parent.mountIsUp,
        )
        if worker is not None:
            self.workerPollSyncClock = worker
