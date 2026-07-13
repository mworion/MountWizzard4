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
import pytest
from mw4.base.timeManager import (
    CYCLIC_SCHEDULE,
    START_SCHEDULE,
    TICK_INTERVAL_MS,
    TimeManager,
)
from PySide6.QtCore import QObject
from skyfield.api import load


class MockApp(QObject):
    """Minimal app stub with the signal attributes needed by CyclicTimerManager."""

    def __init__(self):
        super().__init__()
        self.config = {}


@pytest.fixture()
def mock_app(qapp):
    return MockApp()


@pytest.fixture()
def mgr(mock_app):
    return TimeManager(app=mock_app)


@pytest.fixture()
def ts():
    """Fixture for Skyfield timescale."""
    return load.timescale()


def test_init(mgr):
    assert mgr.counter == 0
    assert mgr.isStopped is False
    assert mgr.timer is not None
    assert not mgr.timer.isActive()


def test_start_stop(mgr):
    mgr.start()
    assert mgr.timer.isActive()
    mgr.stop()
    assert not mgr.timer.isActive()
    assert mgr.isStopped is True


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


def test_on_tick_does_not_emit_after_stop(mgr):
    """Test that onTick returns early if isStopped is True."""
    mgr.stop()
    assert mgr.isStopped is True
    initial_counter = mgr.counter
    mgr.onTick()
    assert mgr.counter == initial_counter


def _collect_emitted(mock_app, mgr, method_name, counter_value):
    """Set the counter and call the named method, returning emitted signal names."""
    emitted = []
    for _, sig_name in CYCLIC_SCHEDULE:
        getattr(mgr, sig_name).connect(lambda name=sig_name: emitted.append(name))
    for _, sig_name in START_SCHEDULE:
        getattr(mgr, sig_name).connect(lambda name=sig_name: emitted.append(name))
    mgr.counter = counter_value
    getattr(mgr, method_name)()
    return emitted


def test_emit_cyclic_always_fires_update0_1s(mock_app, mgr):
    for counter in [1, 2, 7, 13, 99]:
        emitted = _collect_emitted(mock_app, mgr, "emitCyclic", counter)
        assert "update0_1s" in emitted, f"update0_1s should fire at counter={counter}"


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
        assert "start3s" not in emitted, f"start3s should not fire at counter={counter}"


def test_on_tick_emits_signals(mock_app, mgr):
    """onTick should increment the counter and emit cyclic + start signals."""
    emitted = []
    mgr.update0_1s.connect(lambda: emitted.append("update0_1s"))
    mgr.onTick()
    assert mgr.counter == 1
    assert "update0_1s" in emitted


def test_schedules_are_not_empty():
    assert len(CYCLIC_SCHEDULE) > 0
    assert len(START_SCHEDULE) > 0


def test_time_zone_string_utc_true(mgr):
    """Test timeZoneString returns UTC message when unitTimeUTC is True."""
    mgr.unitTimeUTC = True
    result = mgr.timeZoneString()
    assert result == "(time is UTC)"


def test_time_zone_string_utc_false(mgr):
    """Test timeZoneString returns local message when unitTimeUTC is False."""
    mgr.unitTimeUTC = False
    result = mgr.timeZoneString()
    assert result == "(time is local)"


def test_convert_time_utc_true(mgr, ts):
    """Test convertTime uses UTC format when unitTimeUTC is True."""
    mgr.unitTimeUTC = True
    test_time = ts.utc(2024, 6, 13, 12, 0, 0)
    format_string = "%Y-%m-%d %H:%M:%S"
    result = mgr.convertTime(test_time, format_string)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "2024" in result


def test_convert_time_utc_false(mgr, ts):
    """Test convertTime uses local timezone when unitTimeUTC is False."""
    mgr.unitTimeUTC = False
    test_time = ts.utc(2024, 6, 13, 12, 0, 0)
    format_string = "%Y-%m-%d %H:%M:%S"
    result = mgr.convertTime(test_time, format_string)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "2024" in result
