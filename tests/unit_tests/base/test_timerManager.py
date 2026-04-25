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
import pytest
from mw4.base.timerManager import (
    CYCLIC_SCHEDULE,
    START_SCHEDULE,
    TICK_INTERVAL_MS,
    CyclicTimerManager,
)
from PySide6.QtCore import QObject, Signal


class MockApp(QObject):
    """Minimal app stub with the signal attributes needed by CyclicTimerManager."""

    update0_1s = Signal()
    update1s = Signal()
    update3s = Signal()
    update10s = Signal()
    update30s = Signal()
    update3m = Signal()
    update30m = Signal()
    start3s = Signal()


@pytest.fixture()
def mock_app(qapp):
    return MockApp()


@pytest.fixture()
def mgr(mock_app):
    return CyclicTimerManager(app=mock_app)


def test_init(mgr):
    assert mgr.counter == 0
    assert mgr.timer is not None
    assert not mgr.timer.isActive()


def test_start_stop(mgr):
    mgr.start()
    assert mgr.timer.isActive()
    mgr.stop()
    assert not mgr.timer.isActive()


def test_counter_read_write(mgr):
    assert mgr.counter == 0
    mgr.counter = 42
    assert mgr.counter == 42


def test_tick_interval():
    assert TICK_INTERVAL_MS == 100


def test_on_tick_increments_counter(mgr):
    assert mgr.counter == 0
    mgr.onTick()
    assert mgr.counter == 1
    mgr.onTick()
    assert mgr.counter == 2


def _collect_emitted(mock_app, mgr, method_name, counter_value):
    """Set the counter and call the named method, returning emitted signal names."""
    emitted = []
    for _, sig_name in CYCLIC_SCHEDULE:
        getattr(mock_app, sig_name).connect(
            lambda name=sig_name: emitted.append(name)
        )
    for _, sig_name in START_SCHEDULE:
        getattr(mock_app, sig_name).connect(
            lambda name=sig_name: emitted.append(name)
        )
    mgr.counter = counter_value
    getattr(mgr, method_name)()
    return emitted


def test_emit_cyclic_always_fires_update0_1s(mock_app, mgr):
    for counter in [1, 2, 7, 13, 99]:
        emitted = _collect_emitted(mock_app, mgr, "emitCyclic", counter)
        assert "update0_1s" in emitted, (
            f"update0_1s should fire at counter={counter}"
        )


def test_emit_cyclic_update1s(mock_app, mgr):
    """update1s fires when counter % 10 == 0, i.e. counter = 10,20,30..."""
    emitted = _collect_emitted(mock_app, mgr, "emitCyclic", 10)
    assert "update1s" in emitted

    emitted = _collect_emitted(mock_app, mgr, "emitCyclic", 11)
    assert "update1s" not in emitted


def test_emit_cyclic_update3s(mock_app, mgr):
    """update3s fires when counter % 30 == 0, i.e. counter = 30,60,90..."""
    emitted = _collect_emitted(mock_app, mgr, "emitCyclic", 30)
    assert "update3s" in emitted

    emitted = _collect_emitted(mock_app, mgr, "emitCyclic", 31)
    assert "update3s" not in emitted


def test_emit_cyclic_update10s(mock_app, mgr):
    """update10s fires when counter % 100 == 0, i.e. counter = 100,200,..."""
    emitted = _collect_emitted(mock_app, mgr, "emitCyclic", 100)
    assert "update10s" in emitted

    emitted = _collect_emitted(mock_app, mgr, "emitCyclic", 101)
    assert "update10s" not in emitted


def test_emit_cyclic_update30s(mock_app, mgr):
    """update30s fires when counter % 300 == 0, i.e. counter = 300,600..."""
    emitted = _collect_emitted(mock_app, mgr, "emitCyclic", 300)
    assert "update30s" in emitted


def test_emit_cyclic_update3m(mock_app, mgr):
    """update3m fires when counter % 1800 == 0, i.e. counter = 1800,3600..."""
    emitted = _collect_emitted(mock_app, mgr, "emitCyclic", 1800)
    assert "update3m" in emitted


def test_emit_cyclic_update30m(mock_app, mgr):
    """update30m fires when counter % 36000 == 0, i.e. counter = 36000..."""
    emitted = _collect_emitted(mock_app, mgr, "emitCyclic", 36000)
    assert "update30m" in emitted


def test_emit_cyclic_no_crash_various_counters(mock_app, mgr):
    """Smoke test with the same counter values used in the original test_mainApp."""
    for counter in [1, 5, 20, 80, 275, 575, 1788, 5987, 17986, 35985]:
        mgr.counter = counter
        mgr.emitCyclic()


def test_emit_start_fires_at_tick_30(mock_app, mgr):
    emitted = _collect_emitted(mock_app, mgr, "emitStart", 30)
    assert "start3s" in emitted


def test_emit_start_does_not_fire_at_other_ticks(mock_app, mgr):
    for counter in [10, 29, 31, 50, 100, 300]:
        emitted = _collect_emitted(mock_app, mgr, "emitStart", counter)
        assert "start3s" not in emitted, (
            f"start3s should not fire at counter={counter}"
        )


def test_on_tick_emits_signals(mock_app, mgr):
    """onTick should increment the counter and emit cyclic + start signals."""
    emitted = []
    mock_app.update0_1s.connect(lambda: emitted.append("update0_1s"))
    mgr.onTick()
    assert mgr.counter == 1
    assert "update0_1s" in emitted


def test_schedules_are_not_empty():
    assert len(CYCLIC_SCHEDULE) > 0
    assert len(START_SCHEDULE) > 0

