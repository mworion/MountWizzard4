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
        self.mutex = QMutex()
        self.locked = False
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

        except (OSError, ValueError, RuntimeError, TypeError, AttributeError, KeyError) as e:
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
            self.signals.error.emit(eStr)
        except Exception as e:
            # any unexpected exception must not escape into the pool thread and
            # must still release the mutex through the finally block below
            eStr = f"Unhandled worker exception: [{type(e)}], [{e}]"
            self.log.critical(eStr)
            self.signals.error.emit(eStr)
        else:
            self.signals.result.emit(result)
        finally:
            # only unlock when this run actually acquired the mutex via
            # startWorker; a directly started worker never locked it
            if self.locked:
                self.locked = False
                self.mutex.unlock()
            self.signals.finished.emit()


def setupWorker(
    target: Callable[..., Any],
    *args: Any,
    resultMethod: Callable[..., Any] | None = None,
    finishedMethod: Callable[..., Any] | None = None,
    **kwargs: Any,
) -> Worker | None:
    worker = Worker(target, *args, **kwargs)
    if resultMethod is not None:
        worker.signals.result.connect(resultMethod)
    if finishedMethod is not None:
        worker.signals.finished.connect(finishedMethod)
    return worker


def startWorker(
    worker: Worker | None,
    threadPool: QThreadPool,
    target: Callable[..., Any],
    *args: Any,
    resultMethod: Callable[..., Any] | None = None,
    finishedMethod: Callable[..., Any] | None = None,
    guard: Callable[[], bool] | None = None,
    **kwargs: Any,
) -> Worker | None:

    if guard is not None and not guard():
        return None
    reuse = worker is not None
    if not reuse:
        worker = setupWorker(
            target, *args, resultMethod=resultMethod, finishedMethod=finishedMethod, **kwargs
        )
    if not worker.mutex.tryLock():
        return worker
    if reuse:
        worker.args = args
        worker.kwargs = kwargs
    worker.locked = True
    threadPool.start(worker)
    return worker
