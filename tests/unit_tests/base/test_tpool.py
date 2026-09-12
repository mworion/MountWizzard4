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
    def testFunc():
        return "test"

    a = tpool.Worker(testFunc)
    assert a.signals is not None


def test_worker_run_emitsFinishedSignal(qtbot):
    def testFunc():
        return "test"

    a = tpool.Worker(testFunc)
    a.mutex.lock()
    with qtbot.waitSignal(a.signals.finished):
        a.run()


def test_worker_run_emitsResultSignal(qtbot):
    def testFunc():
        return "value"

    a = tpool.Worker(testFunc)
    a.mutex.lock()
    with qtbot.waitSignal(a.signals.result):
        a.run()


def test_worker_run_doesNotEmitErrorOnSuccess(qtbot):
    def testFunc():
        return

    a = tpool.Worker(testFunc)
    a.mutex.lock()
    with qtbot.assertNotEmitted(a.signals.error):
        a.run()


def test_worker_run_emitsErrorOnException(qtbot):
    def testFunc():
        raise RuntimeError("Test")

    a = tpool.Worker(testFunc)
    a.mutex.lock()
    with qtbot.waitSignal(a.signals.error):
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
    worker.mutex.unlock()


def test_startWorker_mutexBlocks():
    pool = mock.Mock()
    # Mock Worker to return a worker with a pre-locked mutex
    with mock.patch("mw4.base.tpool.Worker") as MockWorker:
        mock_worker = mock.Mock()
        mock_worker.mutex.tryLock.return_value = False
        MockWorker.return_value = mock_worker

        worker = tpool.startWorker(pool, lambda: None)
        assert worker is None
        pool.start.assert_not_called()


def test_startWorker_mutexAcquired():
    pool = mock.Mock()
    worker = tpool.startWorker(pool, lambda: None)
    assert worker is not None
    # Mutex should be locked after startWorker
    assert not worker.mutex.tryLock()
    # Actually run the worker to unlock the mutex
    worker.run()
    # Now mutex should be unlocked
    assert worker.mutex.tryLock()
    worker.mutex.unlock()
    # Clean up worker reference
    del worker


def test_startWorker_startsAndReturnsWorker():
    pool = mock.Mock()
    worker = tpool.startWorker(pool, lambda: None)
    assert isinstance(worker, tpool.Worker)
    pool.start.assert_called_once_with(worker)
    worker.mutex.unlock()


def test_startWorker_resultMethodOptional():
    pool = mock.Mock()
    worker = tpool.startWorker(pool, lambda: None, resultMethod=None)
    assert worker is not None
    worker.mutex.unlock()


def test_startWorker_connectsResultMethodToResult():
    pool = mock.Mock()
    received = []
    worker = tpool.startWorker(
        pool, lambda: "test_value", resultMethod=lambda value: received.append(value)
    )
    worker.signals.result.emit("test_value")
    assert received == ["test_value"]
    worker.mutex.unlock()


def test_startWorker_connectsFinishedMethod():
    pool = mock.Mock()
    received = []
    worker = tpool.startWorker(
        pool,
        lambda: None,
        finishedMethod=lambda: received.append("finished"),
    )
    assert worker is not None
    worker.signals.finished.emit()
    assert received == ["finished"]
    worker.mutex.unlock()


def test_startWorker_connectsBothMethods():
    pool = mock.Mock()
    result_received = []
    finished_received = []
    worker = tpool.startWorker(
        pool,
        lambda: "test_value",
        resultMethod=lambda value: result_received.append(value),
        finishedMethod=lambda: finished_received.append("finished"),
    )
    assert worker is not None
    worker.signals.result.emit("test_value")
    worker.signals.finished.emit()
    assert result_received == ["test_value"]
    assert finished_received == ["finished"]
    worker.mutex.unlock()


def test_startWorker_mutexUnlockedAfterWorkerFinishes():
    pool = mock.Mock()
    worker = tpool.startWorker(pool, lambda: None)
    assert worker is not None
    assert not worker.mutex.tryLock()
    # Actually run the worker to unlock the mutex
    worker.run()
    # Now mutex should be unlocked
    assert worker.mutex.tryLock()
    worker.mutex.unlock()
    # Clean up worker reference
    del worker
