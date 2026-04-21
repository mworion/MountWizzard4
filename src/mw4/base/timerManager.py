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
# Licence APL2.0
#
###########################################################
from PySide6.QtCore import QObject, QTimer

TICK_INTERVAL_MS: int = 100
CYCLIC_SCHEDULE: list[tuple[int, str]] = [
    (1, "update0_1s"),
    (1 * 10, "update1s"),
    (3 * 10, "update3s"),
    (10 * 10, "update10s"),
    (30 * 10, "update30s"),
    (3 * 60 * 10, "update3m"),
    (30 * 60 * 10, "update30m"),
]
START_SCHEDULE: list[tuple[int, str]] = [
    (30, "start3s"),
]


class CyclicTimerManager(QObject):
    def __init__(self, app: QObject, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.app: QObject = app
        self.counter: int = 0
        self.timer: QTimer = QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.onTick)

    def start(self) -> None:
        self.timer.start(TICK_INTERVAL_MS)

    def stop(self) -> None:
        self.timer.stop()

    def onTick(self) -> None:
        self.counter += 1
        self.emitCyclic()
        self.emitStart()

    def emitCyclic(self) -> None:
        for interval, signalName in CYCLIC_SCHEDULE:
            if self.counter % interval == 0:
                getattr(self.app, signalName).emit()

    def emitStart(self) -> None:
        for tick, signalName in START_SCHEDULE:
            if self.counter == tick:
                getattr(self.app, signalName).emit()
