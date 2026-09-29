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
import sys
import threading
from collections.abc import Callable
from pathlib import Path
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, SignalInstance, Slot
from types import TracebackType
from typing import Any


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(object)


class Worker(QRunnable):
    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.setAutoDelete(False)
        self.log = logging.getLogger("MW4")
        # busy flag: acquired in the calling (GUI) thread by startWorker and
        # released in the pool thread at the end of run. threading.Lock may be
        # released by any thread, a QMutex must be unlocked by its owner thread.
        self.busyLock = threading.Lock()
        self.locked = False
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.resultMethod: Callable[..., Any] | None = None
        self.finishedMethod: Callable[..., Any] | None = None

    def tryAcquire(self) -> bool:
        if not self.busyLock.acquire(blocking=False):
            return False
        self.locked = True
        return True

    def release(self) -> None:
        if not self.locked:
            return
        self.locked = False
        self.busyLock.release()

    @staticmethod
    def rebind(
        signal: SignalInstance,
        old: Callable[..., Any] | None,
        new: Callable[..., Any] | None,
    ) -> None:
        if old == new:
            return
        if old is not None:
            signal.disconnect(old)
        if new is not None:
            signal.connect(new)

    def setCallbacks(
        self,
        resultMethod: Callable[..., Any] | None,
        finishedMethod: Callable[..., Any] | None,
    ) -> None:
        self.rebind(self.signals.result, self.resultMethod, resultMethod)
        self.rebind(self.signals.finished, self.finishedMethod, finishedMethod)
        self.resultMethod = resultMethod
        self.finishedMethod = finishedMethod

    def formatTbFrame(self, tb: TracebackType) -> str:
        """Build a formatted string for a single traceback frame."""
        file = Path(tb.tb_frame.f_code.co_filename).name
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
            # must still release the busy flag through the finally block below
            eStr = f"Unhandled worker exception: [{type(e)}], [{e}]"
            self.log.critical(eStr)
            self.signals.error.emit(eStr)
        else:
            self.signals.result.emit(result)
        finally:
            # only releases when this run acquired the flag via startWorker; a
            # directly started worker never acquired it
            self.release()
            self.signals.finished.emit()


def setupWorker(
    target: Callable[..., Any],
    *args: Any,
    resultMethod: Callable[..., Any] | None = None,
    finishedMethod: Callable[..., Any] | None = None,
    **kwargs: Any,
) -> Worker | None:
    worker = Worker(target, *args, **kwargs)
    worker.setCallbacks(resultMethod, finishedMethod)
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
    log = logging.getLogger("MW4")

    if guard is not None and not guard():
        return None
    reuse = worker is not None
    if not reuse:
        worker = setupWorker(
            target, *args, resultMethod=resultMethod, finishedMethod=finishedMethod, **kwargs
        )
    if not worker.tryAcquire():
        fnName = getattr(target, "__name__", repr(target))
        log.debug(f"Worker {fnName} busy, skipped")
        return worker
    if reuse:
        # a reused worker gets the arguments and callbacks of this call; this is
        # only done when it is idle, so a running call keeps its callbacks
        worker.args = args
        worker.kwargs = kwargs
        worker.setCallbacks(resultMethod, finishedMethod)
    threadPool.start(worker)
    return worker
