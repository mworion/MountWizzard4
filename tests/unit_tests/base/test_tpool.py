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
