# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import threading
from mw4.base import tpool
from PySide6.QtCore import QThreadPool
from unittest import mock


def test_workerSignals_hasRequiredAttributes():
    signals = tpool.WorkerSignals()
    assert hasattr(signals, "finished")
    assert hasattr(signals, "error")
    assert hasattr(signals, "result")


def test_workerSignals_canConnect(qtbot):
    signals = tpool.WorkerSignals()
    received = []
    signals.finished.connect(lambda: received.append("finished"))
    signals.finished.emit()
    assert received == ["finished"]


def test_clearPrintErrorStack():
    def testFunc():
        raise RuntimeError

    a = tpool.Worker(testFunc)
    a.run()


def test_worker_hasSignalsAttribute():
    a = tpool.Worker(lambda: "test")
    assert a.signals is not None


def test_worker_run_emitsFinishedSignal(qtbot):
    a = tpool.Worker(lambda: "test")
    a.tryAcquire()
    with qtbot.waitSignal(a.signals.finished):
        a.run()


def test_worker_run_emitsResultSignal(qtbot):
    a = tpool.Worker(lambda: "value")
    a.tryAcquire()
    with qtbot.waitSignal(a.signals.result):
        a.run()


def test_worker_run_doesNotEmitErrorOnSuccess(qtbot):
    a = tpool.Worker(lambda: None)
    a.tryAcquire()
    with qtbot.assertNotEmitted(a.signals.error):
        a.run()


def test_worker_run_emitsErrorOnException(qtbot):
    def testFunc():
        raise RuntimeError("Test")

    a = tpool.Worker(testFunc)
    a.tryAcquire()
    with qtbot.waitSignal(a.signals.error):
        a.run()


def test_worker_run_handlesUnexpectedException(qtbot):
    def testFunc():
        raise ZeroDivisionError("boom")

    a = tpool.Worker(testFunc)
    a.tryAcquire()
    with qtbot.waitSignal(a.signals.error):
        a.run()
    assert not a.locked
    assert a.tryAcquire()
    a.release()


def test_worker_run_releasesWhenAcquired():
    a = tpool.Worker(lambda: None)
    a.tryAcquire()
    a.run()
    assert not a.locked
    assert a.tryAcquire()
    a.release()


def test_worker_run_doesNotReleaseWhenNotAcquired():
    a = tpool.Worker(lambda: None)
    a.run()
    assert not a.locked
    assert a.tryAcquire()
    a.release()


def test_worker_tryAcquire_busy():
    a = tpool.Worker(lambda: None)
    assert a.tryAcquire()
    assert a.locked
    assert not a.tryAcquire()
    a.release()
    assert not a.locked


def test_worker_release_notAcquired():
    a = tpool.Worker(lambda: None)
    a.release()
    assert not a.locked
    assert a.tryAcquire()
    a.release()


def test_worker_releaseFromOtherThread():
    a = tpool.Worker(lambda: None)
    assert a.tryAcquire()
    thread = threading.Thread(target=a.run)
    thread.start()
    thread.join(timeout=5)
    assert not a.locked
    assert a.tryAcquire()
    a.release()


def test_worker_releaseFromPool():
    pool = QThreadPool()
    worker = tpool.startWorker(None, pool, lambda: 42)
    assert pool.waitForDone(5000)
    assert not worker.locked
    assert worker.tryAcquire()
    worker.release()


def test_worker_setCallbacks_rebind():
    first = []
    second = []
    a = tpool.Worker(lambda: None)
    a.setCallbacks(first.append, None)
    a.signals.result.emit(1)
    a.setCallbacks(second.append, None)
    a.signals.result.emit(2)
    assert first == [1]
    assert second == [2]
    assert a.resultMethod == second.append


def test_worker_setCallbacks_sameNoReconnect():
    received = []
    a = tpool.Worker(lambda: None)
    a.setCallbacks(received.append, None)
    a.setCallbacks(received.append, None)
    a.signals.result.emit(1)
    assert received == [1]


def test_worker_setCallbacks_remove():
    received = []
    a = tpool.Worker(lambda: None)
    a.setCallbacks(None, lambda: received.append("f"))
    a.setCallbacks(None, None)
    a.signals.finished.emit()
    assert received == []
    assert a.finishedMethod is None


def test_setupWorker_returnsWorkerInstance():
    worker = tpool.setupWorker(lambda: None)
    assert isinstance(worker, tpool.Worker)
    assert not worker.locked


def test_setupWorker_connectsResultAndFinishedMethods():
    resultReceived = []
    finishedReceived = []
    worker = tpool.setupWorker(
        lambda value: value,
        "arg",
        resultMethod=resultReceived.append,
        finishedMethod=lambda: finishedReceived.append("finished"),
    )
    worker.signals.result.emit("arg")
    worker.signals.finished.emit()
    assert resultReceived == ["arg"]
    assert finishedReceived == ["finished"]


def test_setupWorker_passesArgsAndKwargsToWorker():
    received = []

    def target(a, b, c=None):
        received.append((a, b, c))
        return (a, b, c)

    worker = tpool.setupWorker(target, 1, 2, c=3)
    worker.run()
    assert received == [(1, 2, 3)]


def test_setupWorker_noMethodsConnectedWhenNone():
    worker = tpool.setupWorker(lambda: None, resultMethod=None, finishedMethod=None)
    assert worker.resultMethod is None
    assert worker.finishedMethod is None


def test_startWorker_guardBlocks():
    pool = mock.Mock()
    worker = tpool.startWorker(None, pool, lambda: None, guard=lambda: False)
    assert worker is None
    pool.start.assert_not_called()


def test_startWorker_guardAllows():
    pool = mock.Mock()
    worker = tpool.startWorker(None, pool, lambda: None, guard=lambda: True)
    pool.start.assert_called_once_with(worker)
    worker.release()


def test_startWorker_busyBlocksStarting():
    pool = mock.Mock()
    worker = tpool.setupWorker(lambda: None)
    worker.tryAcquire()
    result = tpool.startWorker(worker, pool, lambda: None)
    assert result is worker
    pool.start.assert_not_called()
    worker.release()


def test_startWorker_updateArgsKwargsOnReuse():
    pool = mock.Mock()
    worker = tpool.setupWorker(lambda x, y: (x, y), 1, 2)
    result = tpool.startWorker(worker, pool, lambda x, y, z: (x, y, z), 10, 20, z=30)
    assert result is worker
    assert worker.args == (10, 20)
    assert worker.kwargs == {"z": 30}
    pool.start.assert_called_once_with(worker)
    worker.release()


def test_startWorker_updateCallbacksOnReuse():
    pool = mock.Mock()
    first = []
    second = []
    worker = tpool.startWorker(None, pool, lambda: 1, resultMethod=first.append)
    worker.run()
    tpool.startWorker(worker, pool, lambda: 2, resultMethod=second.append)
    worker.run()
    assert first == [1]
    assert second == [1]
    assert worker.resultMethod == second.append


def test_startWorker_keepsCallbacksWhenBusy():
    pool = mock.Mock()
    first = []
    worker = tpool.startWorker(None, pool, lambda: 1, resultMethod=first.append)
    tpool.startWorker(worker, pool, lambda: 2, resultMethod=print)
    assert worker.resultMethod == first.append
    worker.release()


def test_startWorker_acquired():
    pool = mock.Mock()
    worker = tpool.startWorker(None, pool, lambda: None)
    assert worker.locked
    assert not worker.tryAcquire()
    worker.run()
    assert worker.tryAcquire()
    worker.release()


def test_startWorker_usesExistingWorker():
    pool = mock.Mock()
    existing = tpool.setupWorker(lambda: "existing")
    worker = tpool.startWorker(existing, pool, lambda: None)
    assert worker is existing
    pool.start.assert_called_once_with(existing)
    existing.release()


def test_startWorker_doesNotUpdateArgsWhenBusy():
    pool = mock.Mock()
    worker = tpool.setupWorker(lambda x, y: (x, y), 1, 2)
    worker.tryAcquire()
    result = tpool.startWorker(worker, pool, lambda x, y: (x, y), 10, 20)
    assert result is worker
    assert worker.args == (1, 2)
    pool.start.assert_not_called()
    worker.release()


def test_startWorker_logsDebugWhenBusy(caplog):
    pool = mock.Mock()

    def targetFunc():
        pass

    worker = tpool.setupWorker(targetFunc)
    worker.tryAcquire()
    with caplog.at_level("DEBUG"):
        result = tpool.startWorker(worker, pool, targetFunc)
    assert result is worker
    assert "Worker targetFunc busy, skipped" in caplog.text
    pool.start.assert_not_called()
    worker.release()


def test_worker_tryAcquire_setsStartTime():
    a = tpool.Worker(lambda: None)
    assert a.startTime is None
    assert a.elapsed() == 0.0
    a.tryAcquire()
    assert a.startTime is not None
    duration = a.release()
    assert duration >= 0
    assert a.startTime is None


def test_worker_release_notAcquiredReturnsNone():
    a = tpool.Worker(lambda: None)
    assert a.release() is None


def test_worker_run_logsSlowRun(caplog):
    def targetFunc():
        pass

    a = tpool.Worker(targetFunc)
    a.tryAcquire()
    a.startTime -= 10
    with caplog.at_level("WARNING"):
        a.run()
    assert "Worker targetFunc finished after" in caplog.text
    assert "(slow)" in caplog.text


def test_worker_run_noLogOnFastRun(caplog):
    a = tpool.Worker(lambda: None)
    a.tryAcquire()
    with caplog.at_level("WARNING"):
        a.run()
    assert "slow" not in caplog.text


def test_startWorker_logsElapsedWhenBusy(caplog):
    pool = mock.Mock()

    def targetFunc():
        pass

    worker = tpool.setupWorker(targetFunc)
    worker.tryAcquire()
    worker.startTime -= 12
    with caplog.at_level("DEBUG"):
        tpool.startWorker(worker, pool, targetFunc)
    assert "busy, skipped (running for 12." in caplog.text
    worker.release()
