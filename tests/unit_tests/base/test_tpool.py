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


from mw4.base import tpool
from PySide6.QtCore import QMutex
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
        raise Exception

    a = tpool.Worker(testFunc)
    a.run()


def test_worker_hasSignalsAttribute():
    def testFunc():
        return "test"

    a = tpool.Worker(testFunc)
    assert a.signals is not None


def test_worker_run_emitsFinishedSignal(qtbot):
    def testFunc():
        return "test"

    a = tpool.Worker(testFunc)
    with qtbot.waitSignal(a.signals.finished):
        a.run()


def test_worker_run_emitsResultSignal(qtbot):
    def testFunc():
        return "value"

    a = tpool.Worker(testFunc)
    with qtbot.waitSignal(a.signals.result):
        a.run()


def test_worker_run_doesNotEmitErrorOnSuccess(qtbot):
    def testFunc():
        return

    a = tpool.Worker(testFunc)
    with qtbot.assertNotEmitted(a.signals.error):
        a.run()


def test_worker_run_emitsErrorOnException(qtbot):
    def testFunc():
        raise Exception("Test")

    a = tpool.Worker(testFunc)
    with qtbot.waitSignal(a.signals.error):
        a.run()


def test_worker_run_swallowsRuntimeErrorOnResult():
    def testFunc():
        return "x"

    a = tpool.Worker(testFunc)
    a.signals = mock.Mock()
    a.signals.result.emit.side_effect = RuntimeError
    a.signals.finished.emit.side_effect = RuntimeError
    a.run()


def test_worker_run_swallowsRuntimeErrorOnError():
    def testFunc():
        raise Exception("boom")

    a = tpool.Worker(testFunc)
    a.signals = mock.Mock()
    a.signals.error.emit.side_effect = RuntimeError
    a.signals.finished.emit.side_effect = RuntimeError
    a.run()


def test_startWorker_guardBlocks():
    pool = mock.Mock()
    worker = tpool.startWorker(pool, lambda: None, guard=lambda: False)
    assert worker is None
    pool.start.assert_not_called()


def test_startWorker_guardAllows():
    pool = mock.Mock()
    worker = tpool.startWorker(pool, lambda: None, guard=lambda: True)
    assert worker is not None
    pool.start.assert_called_once_with(worker)


def test_startWorker_mutexBlocks():
    pool = mock.Mock()
    mutex = QMutex()
    mutex.lock()
    worker = tpool.startWorker(pool, lambda: None, mutex=mutex)
    assert worker is None
    pool.start.assert_not_called()
    mutex.unlock()


def test_startWorker_mutexAcquired():
    pool = mock.Mock()
    mutex = QMutex()
    worker = tpool.startWorker(pool, lambda: None, mutex=mutex)
    assert worker is not None
    assert not mutex.tryLock()
    mutex.unlock()


def test_startWorker_startsAndReturnsWorker():
    pool = mock.Mock()
    worker = tpool.startWorker(pool, lambda: None)
    assert isinstance(worker, tpool.Worker)
    pool.start.assert_called_once_with(worker)


def test_startWorker_clearMethodOptional():
    pool = mock.Mock()
    worker = tpool.startWorker(pool, lambda: None, clearMethod=None)
    assert worker is not None


def test_startWorker_connectsClearMethodToFinished():
    pool = mock.Mock()
    received = []
    worker = tpool.startWorker(
        pool, lambda: None, clearMethod=lambda: received.append("finished")
    )
    worker.signals.finished.emit()
    assert received == ["finished"]


def test_startWorker_connectsClearMethodToResult():
    pool = mock.Mock()
    received = []
    worker = tpool.startWorker(
        pool,
        lambda: None,
        clearMethod=lambda r: received.append(r),
        useResult=True,
    )
    worker.signals.result.emit("value")
    assert received == ["value"]
