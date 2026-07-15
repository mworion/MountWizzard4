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
import os
import sys
from collections.abc import Callable
from PySide6.QtCore import QMutex, QObject, QRunnable, QThreadPool, Signal, Slot
from types import TracebackType
from typing import Any


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(object)
    result = Signal(object)


class Worker(QRunnable):
    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.setAutoDelete(False)
        self.log = logging.getLogger("MW4")
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def formatTbFrame(self, tb: TracebackType) -> str:
        """Build a formatted string for a single traceback frame."""
        file = os.path.basename(tb.tb_frame.f_code.co_filename)
        line = tb.tb_lineno
        fnName = getattr(self.fn, "__name__", repr(self.fn))
        eStr = f"fn: [{fnName}], file: [{file}], line: {line} "
        return eStr

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)

        except Exception as e:
            # as we want to send a clear message to the log file
            _, _, tb = sys.exc_info()

            # moving toward the end of the trace; collect frames then join once
            parts = [f"{e} {self.formatTbFrame(tb)}"]
            while tb.tb_next is not None:
                tb = tb.tb_next
                parts.append(self.formatTbFrame(tb))
            parts.append(f" - excType: [{type(e)}], excValue: [{e}]")
            eStr = "".join(parts)
            self.log.critical(eStr)
            try:
                if self.signals is not None:
                    self.signals.error.emit(eStr)
            except RuntimeError:
                pass

        else:
            try:
                if self.signals is not None:
                    self.signals.result.emit(result)
            except RuntimeError:
                pass

        finally:
            try:
                if self.signals is not None:
                    self.signals.finished.emit()
            except RuntimeError:
                pass


def startWorker(
    threadPool: QThreadPool,
    target: Callable[..., Any],
    clearMethod: Callable[..., Any] | None = None,
    *args: Any,
    mutex: QMutex | None = None,
    useResult: bool = False,
    guard: Callable[[], bool] | None = None,
    **kwargs: Any,
) -> Worker | None:
    """
    Build and start a Worker on the given threadPool. An optional guard
    callable can veto execution (returning False), and an optional mutex is
    tryLock-ed to prevent overlapping runs. The created Worker is returned so
    the caller can keep an explicit reference alive; None is returned when the
    guard or mutex prevents starting.
    """
    if guard is not None and not guard():
        return None
    if mutex is not None and not mutex.tryLock():
        return None
    worker = Worker(target, *args, **kwargs)
    sig = worker.signals.result if useResult else worker.signals.finished
    if clearMethod is not None:
        sig.connect(clearMethod)
    threadPool.start(worker)
    return worker
