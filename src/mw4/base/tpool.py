# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
import threading
import time
import traceback
from collections.abc import Callable
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, SignalInstance, Slot
from typing import Any

# runs longer than this (seconds) are logged as slow
SLOW_WORKER_THRESHOLD = 5.0


def fnNameOf(fn: Callable[..., Any]) -> str:
    """Readable name for logging; partials and callables lack __name__."""
    return getattr(fn, "__name__", repr(fn))


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
        self.startTime: float | None = None
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
        self.startTime = time.monotonic()
        return True

    def elapsed(self) -> float:
        if self.startTime is None:
            return 0.0
        return time.monotonic() - self.startTime

    def release(self) -> float | None:
        if not self.locked:
            return None
        duration = self.elapsed()
        self.startTime = None
        self.locked = False
        self.busyLock.release()
        return duration

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

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)

        except Exception as e:
            # no exception may escape into the pool thread; the busy flag is
            # still released through the finally block below
            fnName = fnNameOf(self.fn)
            eStr = f"Worker exception in [{fnName}]: [{type(e).__name__}], [{e}]"
            self.log.critical("%s\n%s", eStr, traceback.format_exc())
            self.signals.error.emit(eStr)
        else:
            self.signals.result.emit(result)
        finally:
            # only releases when this run acquired the flag via startWorker; a
            # directly started worker never acquired it
            duration = self.release()
            if duration is not None and duration > SLOW_WORKER_THRESHOLD:
                fnName = fnNameOf(self.fn)
                self.log.warning("Worker %s finished after %.1fs (slow)", fnName, duration)
            self.signals.finished.emit()


def setupWorker(
    target: Callable[..., Any],
    *args: Any,
    resultMethod: Callable[..., Any] | None = None,
    finishedMethod: Callable[..., Any] | None = None,
    **kwargs: Any,
) -> Worker:
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
    if worker is None:
        worker = setupWorker(
            target, *args, resultMethod=resultMethod, finishedMethod=finishedMethod, **kwargs
        )
    if not worker.tryAcquire():
        fnName = fnNameOf(target)
        log.debug("Worker %s busy, skipped (running for %.1fs)", fnName, worker.elapsed())
        return worker
    if reuse:
        # a reused worker gets the arguments and callbacks of this call; this is
        # only done when it is idle, so a running call keeps its callbacks
        worker.args = args
        worker.kwargs = kwargs
        worker.setCallbacks(resultMethod, finishedMethod)
    threadPool.start(worker)
    return worker
