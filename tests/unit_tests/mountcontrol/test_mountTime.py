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

import numpy as np
import pytest
from mw4.mountcontrol.mountTime import MountTime
from mw4.mountcontrol.obsSite import MountStatus
from PySide6.QtCore import QThreadPool
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function():
    app = App()
    m = app.mount
    m.app = app
    m.threadPool = app.threadPool
    m.config.hostAddress = "192.168.1.1"
    m.config.port = 3040
    m.config.syncTimeNone = False
    m.config.syncTimeNotTrack = False
    m.mountIsUp = False
    m.MountStatus = MountStatus
    mountTime = MountTime(parent=m)
    yield mountTime


def test_mountTime_init(function):
    assert function.parent is not None
    assert function.app is not None
    assert function.threadPool is not None
    assert function.timePC is not None
    assert function.rtt == 0
    assert len(function.rtt_MA) == 25
    assert len(function._timeDiff) == 25
    assert function.workerCycleMountUp is None
    assert function.mutexCycleMountUp is not None
    assert function.workerPollSyncClock is None
    assert function.mutexPollSyncClock is not None


def test_timeDiff_property_initial(function):
    assert function.timeDiff == 0.0


def test_timeDiff_property_with_values(function):
    function._timeDiff = np.array([1.0, 2.0, 3.0] + [0.0] * 22)
    expected = np.mean(function._timeDiff)
    assert function.timeDiff == pytest.approx(expected)


def test_timeDiff_property_type(function):
    result = function.timeDiff
    assert isinstance(result, float)


def test_runnerMountUp_ping_none(function):
    function.parent.mountIsUp = False
    function.errorCounter = 5
    with (
        mock.patch("mw4.mountcontrol.mountTime.ping", return_value=None),
        mock.patch.object(function.parent.signals, "mountIsUp") as mock_signal,
    ):
        function.runnerMountUp()
        assert function.parent.mountIsUp is False
        assert function.errorCounter == 4
        mock_signal.emit.assert_not_called()


def test_runnerMountUp_ping_false(function):
    function.parent.mountIsUp = False
    function.errorCounter = 5
    with (
        mock.patch("mw4.mountcontrol.mountTime.ping", return_value=False),
        mock.patch.object(function.parent.signals, "mountIsUp") as mock_signal,
    ):
        function.runnerMountUp()
        assert function.parent.mountIsUp is False
        assert function.errorCounter == 4
        mock_signal.emit.assert_not_called()


def test_runnerMountUp_socket_exception(function):
    function.parent.mountIsUp = False
    function.rtt_MA = np.zeros(25)
    function.errorCounter = 5
    with (
        mock.patch("mw4.mountcontrol.mountTime.ping", return_value=0.05),
        mock.patch("socket.socket") as mock_socket,
    ):
        mock_socket.return_value.__enter__.return_value.connect.side_effect = Exception(
            "Connection failed"
        )
        function.runnerMountUp()
        assert function.rtt_MA[0] == pytest.approx(0.05)
        assert function.errorCounter == 4


def test_runnerMountUp_socket_success(function):
    function.parent.mountIsUp = False
    function.rtt_MA = np.zeros(25)
    function.errorCounter = 2
    with (
        mock.patch("mw4.mountcontrol.mountTime.ping", return_value=0.05),
        mock.patch("socket.socket"),
        mock.patch.object(function.parent.signals, "mountIsUp"),
    ):
        function.runnerMountUp()
        assert function.rtt_MA[0] == pytest.approx(0.05)
        assert function.errorCounter == 5
        function.parent.signals.mountIsUp.emit.assert_called_with(True)


def test_runnerMountUp_rtt_moving_average(function):
    function.rtt_MA = np.zeros(25)
    function.rtt = 0
    with (
        mock.patch("mw4.mountcontrol.mountTime.ping", return_value=0.1),
        mock.patch("socket.socket"),
        mock.patch.object(function.parent.signals, "mountIsUp"),
    ):
        function.runnerMountUp()
        assert function.rtt_MA[0] == pytest.approx(0.1)
        function.runnerMountUp()
        assert function.rtt == pytest.approx(np.mean(function.rtt_MA))


def test_runnerMountUp_ping_none_error_counter_zero(function):
    function.parent.mountIsUp = False
    function.errorCounter = 0
    with mock.patch("mw4.mountcontrol.mountTime.ping", return_value=None):
        function.runnerMountUp()
        assert function.parent.mountIsUp is False
        assert function.errorCounter == 0


def test_runnerMountUp_ping_false_error_counter_zero(function):
    function.parent.mountIsUp = False
    function.errorCounter = 0
    with mock.patch("mw4.mountcontrol.mountTime.ping", return_value=False):
        function.runnerMountUp()
        assert function.parent.mountIsUp is False
        assert function.errorCounter == 0


def test_runnerMountUp_socket_exception_error_counter_zero(function):
    function.parent.mountIsUp = False
    function.rtt_MA = np.zeros(25)
    function.errorCounter = 0
    with (
        mock.patch("mw4.mountcontrol.mountTime.ping", return_value=0.05),
        mock.patch("socket.socket") as mock_socket,
    ):
        mock_socket.return_value.__enter__.return_value.connect.side_effect = Exception(
            "Connection failed"
        )
        function.runnerMountUp()
        assert function.rtt_MA[0] == pytest.approx(0.05)
        assert function.errorCounter == 0


def test_clearMountUp(function):
    function.mutexCycleMountUp.lock()
    function.clearMountUp()


def test_checkMountUp_locked(function):
    function.mutexCycleMountUp.lock()
    with mock.patch.object(QThreadPool, "start") as start:
        function.checkMountUp()
        assert not start.called
    function.mutexCycleMountUp.unlock()


def test_checkMountUp_unlocked(function):
    function.mutexCycleMountUp.unlock()
    with mock.patch.object(QThreadPool, "start") as start:
        function.checkMountUp()
        assert start.called
        assert function.workerCycleMountUp is not None
    function.clearMountUp()


def test_adjustClock_positive_delta(function):
    with mock.patch("mw4.mountcontrol.mountTime.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (True, "1", "")

        result = function.adjustClock(100)

        assert result is True
        mock_conn_instance.communicate.assert_called_once()
        call_args = mock_conn_instance.communicate.call_args
        assert ":NUtim+100" in call_args[0][0]


def test_adjustClock_negative_delta(function):
    with mock.patch("mw4.mountcontrol.mountTime.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (True, "1", "")

        result = function.adjustClock(-100)

        assert result is True
        call_args = mock_conn_instance.communicate.call_args
        assert ":NUtim-100" in call_args[0][0]


def test_adjustClock_zero_delta(function):
    with mock.patch("mw4.mountcontrol.mountTime.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (True, "1", "")

        result = function.adjustClock(0)

        assert result is True
        call_args = mock_conn_instance.communicate.call_args
        assert call_args[0][0] == ":NUtim+000#"


def test_adjustClock_communicate_failure(function):
    with mock.patch("mw4.mountcontrol.mountTime.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (False, "", "")

        result = function.adjustClock(50)

        assert result is False


def test_syncClock_sync_disabled(function):
    function.parent.config.syncTimeNone = True
    function.parent.mountIsUp = True
    with mock.patch.object(function, "adjustClock"):
        function.syncClock()
        function.adjustClock.assert_not_called()
    function.parent.config.syncTimeNone = False


def test_syncClock_mount_not_up(function):
    function.parent.mountIsUp = False
    with mock.patch.object(function, "adjustClock"):
        function.syncClock()
        function.adjustClock.assert_not_called()
    function.parent.mountIsUp = True


def test_syncClock_tracking_mode_disabled_when_tracking(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNotTrack = True
    function.parent.obsSite.status = function.parent.MountStatus.TRACKING
    with mock.patch.object(function, "adjustClock"):
        function.syncClock()
        function.adjustClock.assert_not_called()
    function.parent.config.syncTimeNotTrack = False


def test_syncClock_satellite_following_mode_disabled(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNotTrack = True
    function.parent.obsSite.status = function.parent.MountStatus.FOLLOWING_SATELLITE
    with mock.patch.object(function, "adjustClock"):
        function.syncClock()
        function.adjustClock.assert_not_called()
    function.parent.config.syncTimeNotTrack = False


def test_syncClock_delta_too_small(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = function.parent.MountStatus.STOPPED
    function._timeDiff = np.array([0.005] + [0.0] * 24)
    with mock.patch.object(function, "adjustClock"):
        function.syncClock()
        function.adjustClock.assert_not_called()


def test_syncClock_delta_within_bounds(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = function.parent.MountStatus.STOPPED
    function._timeDiff = np.full(25, 0.05)
    with mock.patch.object(function, "adjustClock", return_value=True):
        function.syncClock()
        function.adjustClock.assert_called_once()
        delta = int(0.05 * 1000)
        function.adjustClock.assert_called_with(delta)


def test_syncClock_delta_max_clamping(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = function.parent.MountStatus.STOPPED
    function._timeDiff = np.full(25, 2.0)
    with mock.patch.object(function, "adjustClock", return_value=True):
        function.syncClock()
        function.adjustClock.assert_called_once()
        delta = int(2.0 * 1000)
        expected_delta = int(max(min(delta, 999), -999))
        function.adjustClock.assert_called_with(expected_delta)


def test_syncClock_delta_negative_clamping(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = function.parent.MountStatus.STOPPED
    function._timeDiff = np.full(25, -2.0)
    with mock.patch.object(function, "adjustClock", return_value=True):
        function.syncClock()
        function.adjustClock.assert_called_once()
        delta = int(-2.0 * 1000)
        expected_delta = int(max(min(delta, 999), -999))
        function.adjustClock.assert_called_with(expected_delta)


def test_syncClock_adjustClock_failure(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = function.parent.MountStatus.STOPPED
    function._timeDiff = np.full(25, 0.05)
    with (
        mock.patch.object(function, "adjustClock", return_value=False),
        mock.patch.object(function.log, "warning"),
    ):
        function.syncClock()
        function.log.warning.assert_called_once()


def test_pollSyncClock_mount_not_up(function):
    function.parent.mountIsUp = False
    with mock.patch.object(QThreadPool, "start") as start:
        function.pollSyncClock()
        assert not start.called


def test_pollSyncClock_locked(function):
    function.parent.mountIsUp = True
    function.mutexPollSyncClock.lock()
    with mock.patch.object(QThreadPool, "start") as start:
        function.pollSyncClock()
        assert not start.called
    function.mutexPollSyncClock.unlock()


def test_pollSyncClock_unlocked(function):
    function.parent.mountIsUp = True
    function.mutexPollSyncClock.unlock()
    with mock.patch.object(QThreadPool, "start") as start:
        function.pollSyncClock()
        assert start.called
        assert function.workerPollSyncClock is not None
    function.clearPollSyncClock()


def test_clearPollSyncClock(function):
    function.mutexPollSyncClock.lock()
    function.clearPollSyncClock()


def test_pollSyncClock_communicate_failure(function):
    function.parent.mountIsUp = True
    with mock.patch("mw4.mountcontrol.mountTime.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (False, "", "")

        initial_timeDiff = function._timeDiff.copy()
        function.runnerPollSyncClock()
        np.testing.assert_array_equal(function._timeDiff, initial_timeDiff)


def test_pollSyncClock_success(function):
    function.parent.mountIsUp = True
    function.rtt = 0.01
    with mock.patch("mw4.mountcontrol.mountTime.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (True, ["2460000.5"], "")

        function.runnerPollSyncClock()

        assert mock_connection.called
        call_args = mock_conn_instance.communicate.call_args
        assert call_args[0][0] == ":GJD1#"
        assert function._timeDiff[0] != 0


def test_pollSyncClock_updates_timeDiff_array(function):
    function.parent.mountIsUp = True
    function.rtt = 0.01
    function._timeDiff = np.zeros(25)
    with mock.patch("mw4.mountcontrol.mountTime.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (True, ["2460000.5"], "")

        initial_last_element = function._timeDiff[-1]
        function.runnerPollSyncClock()
        assert function._timeDiff[-1] == pytest.approx(initial_last_element)
        assert function._timeDiff[0] != initial_last_element
