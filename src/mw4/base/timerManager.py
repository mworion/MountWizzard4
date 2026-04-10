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
"""Cyclic timer management with named interval constants."""
from PySide6.QtCore import QObject, QTimer

TICK_INTERVAL_MS: int = 100

# Cyclic schedule: (interval_in_ticks, phase_offset, signal_attribute_name)
# A signal is emitted when ``(counter + offset) % interval == 0``.
CYCLIC_SCHEDULE: list[tuple[int, int, str]] = [
    (1, 0, "update0_1s"),
    (1 * 10, 5, "update1s"),
    (3 * 10, 10, "update3s"),
    (30 * 10, 25, "update30s"),
    (3 * 60 * 10, 12, "update3m"),
    (30 * 60 * 10, 15, "update30m"),
]

# Start schedule: (tick_count, signal_attribute_name)
# Each signal is emitted exactly once when the counter reaches ``tick_count``.
START_SCHEDULE: list[tuple[int, str]] = [
    (30, "start3s"),
]


class CyclicTimerManager(QObject):
    """Manages a 100 ms tick timer and emits cyclic signals on a host app."""

    def __init__(self, app: QObject, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._app: QObject = app
        self.counter: int = 0
        self._timer: QTimer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._onTick)


    def start(self) -> None:
        """Start the cyclic timer."""
        self._timer.start(TICK_INTERVAL_MS)

    def stop(self) -> None:
        """Stop the cyclic timer."""
        self._timer.stop()

    def _onTick(self) -> None:
        """Handle a single timer tick."""
        self.counter += 1
        self.emitCyclic()
        self.emitStart()

    def emitCyclic(self) -> None:
        """Emit cyclic signals whose interval divides the current counter."""
        for interval, offset, signalName in CYCLIC_SCHEDULE:
            if (self.counter + offset) % interval == 0:
                getattr(self._app, signalName).emit()

    def emitStart(self) -> None:
        """Emit one-shot start signals at their designated tick counts."""
        for tick, signalName in START_SCHEDULE:
            if self.counter == tick:
                getattr(self._app, signalName).emit()
