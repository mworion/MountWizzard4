# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import numpy as np
import pytest
import wakeonlan
from mw4.base import tpool
from mw4.mountcontrol.mountStatus import MountStatus
from mw4.mountcontrol.mountTimeConnectivity import MountTimeConnectivity
from PySide6.QtCore import QThreadPool
from unittest import mock


def buildMountTimeConnectivity(mountContext):
    mountContext.config.hostAddress = "192.168.1.1"
    mountContext.config.port = 3040
    mountContext.config.syncTimeNone = False
    mountContext.config.syncTimeNotTrack = False
    mountContext.mountIsUp = False
    return MountTimeConnectivity(parent=mountContext)


def releaseWorker(worker):
    worker.release()


@pytest.fixture(autouse=True, scope="module")
def function(mountContext):
    mountTime = buildMountTimeConnectivity(mountContext)
    yield mountTime
    # Cleanup: ensure all workers are finished and all mutexes are unlocked
    if hasattr(mountTime, "workerCycleMountUp") and mountTime.workerCycleMountUp is not None:
        mountTime.workerCycleMountUp.signals.finished.emit()
        del mountTime.workerCycleMountUp
    if hasattr(mountTime, "workerPollSyncClock") and mountTime.workerPollSyncClock is not None:
        mountTime.workerPollSyncClock.signals.finished.emit()
        del mountTime.workerPollSyncClock
    # Wait for thread pool to finish
    if hasattr(mountTime, "threadPool") and mountTime.threadPool is not None:
        mountTime.threadPool.waitForDone()


def test_mountTimeConnectivity_init(mountContext):
    function = buildMountTimeConnectivity(mountContext)
    assert function.parent is not None
    assert function.threadPool is not None
    assert function.timePC is not None
    assert function.rtt == 0
    assert len(function.rtt_MA) == 25
    assert len(function._timeDiff) == 25
    assert function.workerCycleMountUp is None
    assert function.workerPollSyncClock is None


def test_timeDiff_property_initial(mountContext):
    assert buildMountTimeConnectivity(mountContext).timeDiff == 0.0


def test_timeDiff_property_with_values(function):
    function._timeDiff = np.array([1.0, 2.0, 3.0] + [0.0] * 22)
    expected = np.mean(function._timeDiff)
    assert function.timeDiff == pytest.approx(expected)


def test_timeDiff_property_type(function):
    result = function.timeDiff
    assert isinstance(result, float)


def test_runnerMountUp_no_host_address(function):
    original_address = function.parent.config.hostAddress
    function.parent.mountIsUp = True
    function.parent.config.hostAddress = ""
    with mock.patch.object(function.parent.signals, "mountIsUp") as mock_signal:
        function.runnerMountUp()
        mock_signal.emit.assert_called_once_with(False)
    function.parent.config.hostAddress = original_address


@pytest.mark.parametrize(
    "ping_return,socket_fails",
    [
        (None, False),
        (False, False),
        (0.05, True),
    ],
)
def test_runnerMountUp_error_counter_decrements(function, ping_return, socket_fails):
    function.parent.mountIsUp = False
    function.errorCounter = 5
    function.rtt_MA = np.zeros(25)

    if socket_fails:
        with (
            mock.patch("mw4.mountcontrol.mountTimeConnectivity.ping", return_value=ping_return),
            mock.patch("socket.socket") as mock_socket,
        ):
            mock_socket.return_value.__enter__.return_value.connect.side_effect = OSError(
                "Connection failed"
            )
            function.runnerMountUp()
            assert function.rtt_MA[0] == pytest.approx(ping_return)
    else:
        with mock.patch("mw4.mountcontrol.mountTimeConnectivity.ping", return_value=ping_return):
            function.runnerMountUp()

    assert function.parent.mountIsUp is False
    assert function.errorCounter == 4


def test_runnerMountUp_socket_success(function):
    function.parent.mountIsUp = False
    function.rtt_MA = np.zeros(25)
    function.errorCounter = 2
    with (
        mock.patch("mw4.mountcontrol.mountTimeConnectivity.ping", return_value=0.05),
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
        mock.patch("mw4.mountcontrol.mountTimeConnectivity.ping", return_value=0.1),
        mock.patch("socket.socket"),
        mock.patch.object(function.parent.signals, "mountIsUp"),
    ):
        function.runnerMountUp()
        assert function.rtt_MA[0] == pytest.approx(0.1)
        function.runnerMountUp()
        assert function.rtt == pytest.approx(np.mean(function.rtt_MA))


@pytest.mark.parametrize(
    "ping_return,socket_fails",
    [
        (None, False),
        (False, False),
        (0.05, True),
    ],
)
def test_runnerMountUp_error_counter_zero(function, ping_return, socket_fails):
    function.parent.mountIsUp = False
    function.errorCounter = 0
    function.rtt_MA = np.zeros(25)

    if socket_fails:
        with (
            mock.patch("mw4.mountcontrol.mountTimeConnectivity.ping", return_value=ping_return),
            mock.patch("socket.socket") as mock_socket,
        ):
            mock_socket.return_value.__enter__.return_value.connect.side_effect = OSError(
                "Connection failed"
            )
            function.runnerMountUp()
            assert function.rtt_MA[0] == pytest.approx(ping_return)
    else:
        with mock.patch("mw4.mountcontrol.mountTimeConnectivity.ping", return_value=ping_return):
            function.runnerMountUp()

    assert function.errorCounter == 0


def test_checkMountUp_locked(function):
    worker = function.workerCycleMountUp
    if worker is None:
        worker = tpool.setupWorker(lambda: None)
    worker.tryAcquire()
    function.workerCycleMountUp = worker
    with mock.patch.object(QThreadPool, "start") as start:
        result = function.checkMountUp()
        assert result is None
        assert not start.called
    worker.release()


def test_checkMountUp_unlocked(function):
    function.workerCycleMountUp = None
    with mock.patch.object(QThreadPool, "start"):
        function.checkMountUp()
        assert function.workerCycleMountUp is not None
    releaseWorker(function.workerCycleMountUp)
    function.workerCycleMountUp = None


@pytest.mark.parametrize(
    "delta,expected_cmd",
    [
        (100, ":NUtim+100#"),
        (-100, ":NUtim-100#"),
        (0, ":NUtim+000#"),
    ],
)
def test_deltaAdjustClock(function, delta, expected_cmd):
    with mock.patch("mw4.mountcontrol.mountTimeConnectivity.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (True, "1", "")

        result = function.deltaAdjustClock(delta)

        assert result is True
        mock_conn_instance.communicate.assert_called_once()
        call_args = mock_conn_instance.communicate.call_args
        assert call_args[0][0] == expected_cmd


def test_deltaAdjustClock_communicate_failure(function):
    with mock.patch("mw4.mountcontrol.mountTimeConnectivity.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (False, "", "")

        result = function.deltaAdjustClock(50)

        assert result is False


def test_absolutAdjustClock_success(function):
    with mock.patch("mw4.mountcontrol.mountTimeConnectivity.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (True, "1", "")

        result = function.absolutAdjustClock()

        assert result is True
        mock_conn_instance.communicate.assert_called_once()
        call_args = mock_conn_instance.communicate.call_args
        assert ":SUDT" in call_args[0][0]
        assert call_args[0][0].endswith("#")


def test_absolutAdjustClock_communicate_failure(function):
    with mock.patch("mw4.mountcontrol.mountTimeConnectivity.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (False, "", "")

        result = function.absolutAdjustClock()

        assert result is False


def test_syncClock_sync_disabled(function):
    function.parent.config.syncTimeNone = True
    function.parent.mountIsUp = True
    with mock.patch.object(function, "deltaAdjustClock"):
        function.syncClock()
        function.deltaAdjustClock.assert_not_called()
    function.parent.config.syncTimeNone = False


def test_syncClock_mount_not_up(function):
    function.parent.mountIsUp = False
    with mock.patch.object(function, "deltaAdjustClock"):
        function.syncClock()
        function.deltaAdjustClock.assert_not_called()
    function.parent.mountIsUp = True


def test_syncClock_tracking_mode_disabled_when_tracking(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNotTrack = True
    function.parent.obsSite.status = MountStatus.TRACKING
    with mock.patch.object(function, "deltaAdjustClock"):
        function.syncClock()
        function.deltaAdjustClock.assert_not_called()
    function.parent.config.syncTimeNotTrack = False


def test_syncClock_satellite_following_mode_disabled(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNotTrack = True
    function.parent.obsSite.status = MountStatus.FOLLOWING_SATELLITE
    with mock.patch.object(function, "deltaAdjustClock"):
        function.syncClock()
        function.deltaAdjustClock.assert_not_called()
    function.parent.config.syncTimeNotTrack = False


def test_syncClock_delta_too_small(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = MountStatus.STOPPED
    function._timeDiff = np.array([0.005] + [0.0] * 24)
    with mock.patch.object(function, "deltaAdjustClock"):
        function.syncClock()
        function.deltaAdjustClock.assert_not_called()


@pytest.mark.parametrize(
    "time_diff_val,expected_delta",
    [
        (0.05, 50),
        (0.5, 500),
        (-0.5, -500),
    ],
)
def test_syncClock_delta_clamping(function, time_diff_val, expected_delta):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = MountStatus.STOPPED
    function._timeDiff = np.full(25, time_diff_val)
    with mock.patch.object(function, "deltaAdjustClock", return_value=True):
        function.syncClock()
        function.deltaAdjustClock.assert_called_once_with(expected_delta)


def test_syncClock_absolutAdjustClock_called_for_large_delta(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = MountStatus.STOPPED
    function._timeDiff = np.full(25, 2.0)
    with (
        mock.patch.object(function, "deltaAdjustClock") as mock_delta,
        mock.patch.object(function, "absolutAdjustClock", return_value=True) as mock_abs,
    ):
        function.syncClock()
        mock_abs.assert_called_once()
        mock_delta.assert_not_called()


def test_syncClock_adjustClock_failure(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = MountStatus.STOPPED
    function._timeDiff = np.full(25, 0.05)
    with (
        mock.patch.object(function, "deltaAdjustClock", return_value=False),
        mock.patch.object(function.log, "warning"),
    ):
        function.syncClock()
        function.log.warning.assert_called_once()


def test_syncClock_absolutAdjustClock_failure(function):
    function.parent.mountIsUp = True
    function.parent.config.syncTimeNone = False
    function.parent.config.syncTimeNotTrack = False
    function.parent.obsSite.status = MountStatus.STOPPED
    function._timeDiff = np.full(25, 2.0)
    with (
        mock.patch.object(function, "absolutAdjustClock", return_value=False),
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
    worker = function.workerPollSyncClock
    if worker is None:
        worker = tpool.setupWorker(lambda: None)
    worker.tryAcquire()
    function.workerPollSyncClock = worker
    with mock.patch.object(QThreadPool, "start") as start:
        result = function.pollSyncClock()
        assert result is None
        assert not start.called
    worker.release()


def test_pollSyncClock_unlocked(function):
    function.parent.mountIsUp = True
    function.workerPollSyncClock = None
    with mock.patch.object(QThreadPool, "start"):
        function.pollSyncClock()
        assert function.workerPollSyncClock is not None
    releaseWorker(function.workerPollSyncClock)
    function.workerPollSyncClock = None


def test_pollSyncClock_communicate_failure(function):
    function.parent.mountIsUp = True
    with mock.patch("mw4.mountcontrol.mountTimeConnectivity.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (False, "", "")

        initial_timeDiff = function._timeDiff.copy()
        function.runnerPollSyncClock()
        np.testing.assert_array_equal(function._timeDiff, initial_timeDiff)


def test_pollSyncClock_success(function):
    function.parent.mountIsUp = True
    function.rtt = 0.01
    with mock.patch("mw4.mountcontrol.mountTimeConnectivity.Connection") as mock_connection:
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
    with mock.patch("mw4.mountcontrol.mountTimeConnectivity.Connection") as mock_connection:
        mock_conn_instance = mock.Mock()
        mock_connection.return_value = mock_conn_instance
        mock_conn_instance.communicate.return_value = (True, ["2460000.5"], "")

        initial_last_element = function._timeDiff[-1]
        function.runnerPollSyncClock()
        assert function._timeDiff[-1] == pytest.approx(initial_last_element)
        assert function._timeDiff[0] != initial_last_element


def test_setStatus_sets_mount_not_up(function):
    function.parent.mountIsUp = True
    with mock.patch.object(function.parent.signals, "mountIsUp"):
        function.setMountStatusOff("Test status")
        assert function.parent.mountIsUp is False


def test_setStatus_emits_signal(function):
    with mock.patch.object(function.parent.signals, "mountIsUp") as mock_signal:
        function.setMountStatusOff("Test message")
        mock_signal.emit.assert_called_once_with(False)


def test_setStatus_decrements_error_counter(function):
    function.errorCounter = 5
    with mock.patch.object(function.parent.signals, "mountIsUp"):
        function.setMountStatusOff("Test status")
        assert function.errorCounter == 4


def test_setStatus_logs_when_counter_positive(function):
    function.errorCounter = 5
    test_message = "Test error message"
    with (
        mock.patch.object(function.parent.signals, "mountIsUp"),
        mock.patch.object(function.log, "info") as mock_log,
    ):
        function.setMountStatusOff(test_message)
        mock_log.assert_called_once_with(test_message)


def test_setStatus_no_log_when_counter_zero(function):
    function.errorCounter = 0
    with (
        mock.patch.object(function.parent.signals, "mountIsUp"),
        mock.patch.object(function.log, "info") as mock_log,
    ):
        function.setMountStatusOff("Test message")
        mock_log.assert_not_called()


def test_setStatus_no_decrement_when_counter_zero(function):
    function.errorCounter = 0
    with mock.patch.object(function.parent.signals, "mountIsUp"):
        function.setMountStatusOff("Test status")
        assert function.errorCounter == 0


@pytest.mark.parametrize(
    "initial_counter,expected_counter",
    [
        (1, 0),
        (5, 4),
        (10, 9),
    ],
)
def test_setStatus_decrement_various_counters(function, initial_counter, expected_counter):
    function.errorCounter = initial_counter
    with mock.patch.object(function.parent.signals, "mountIsUp"):
        function.setMountStatusOff("Test status")
        assert function.errorCounter == expected_counter


@pytest.mark.parametrize(
    "log_message",
    [
        "No host address",
        "Host: [192.168.1.1] not resolved",
        "Timeout: [192.168.1.1] no response",
        "No mount at [192.168.1.1], error [Connection refused]",
    ],
)
def test_setStatus_logs_different_messages(function, log_message):
    function.errorCounter = 1
    with (
        mock.patch.object(function.parent.signals, "mountIsUp"),
        mock.patch.object(function.log, "info") as mock_log,
    ):
        function.setMountStatusOff(log_message)
        mock_log.assert_called_once_with(log_message)


def test_setStatus_multiple_calls_decrements_progressively(function):
    function.errorCounter = 3
    with mock.patch.object(function.parent.signals, "mountIsUp"):
        function.setMountStatusOff("Message 1")
        assert function.errorCounter == 2
        function.setMountStatusOff("Message 2")
        assert function.errorCounter == 1
        function.setMountStatusOff("Message 3")
        assert function.errorCounter == 0
        function.setMountStatusOff("Message 4")
        assert function.errorCounter == 0


def test_setStatus_called_with_empty_string(function):
    function.errorCounter = 5
    with (
        mock.patch.object(function.parent.signals, "mountIsUp"),
        mock.patch.object(function.log, "info") as mock_log,
    ):
        function.setMountStatusOff("")
        mock_log.assert_called_once_with("")
        assert function.errorCounter == 4


def test_bootMount_1(function):
    function.parent.config.MAC = None

    def mock_wake_side_effect(mac, host, port):
        if mac is None:
            raise ValueError("MAC address cannot be None")

    with mock.patch.object(wakeonlan, "wake", side_effect=mock_wake_side_effect):
        suc = function.bootMount()
        assert not suc


def test_bootMount_2(function):
    function.parent.config.MAC = "00:00:00:00:00:00"
    with mock.patch.object(wakeonlan, "wake"):
        suc = function.bootMount()
        assert suc


def test_bootMount_3(function):
    function.parent.config.MAC = "00:00:00:00:00:00"
    function.parent.config.wolAddress = "255.255.255.255"
    with mock.patch.object(wakeonlan, "wake"):
        suc = function.bootMount()
        assert suc


def test_bootMount_4(function):
    function.parent.config.MAC = "00:00:00:00:00:00"
    function.parent.config.wolAddress = "255.255.255.255"
    function.parent.config.wolPort = 9
    with mock.patch.object(wakeonlan, "wake"):
        suc = function.bootMount()
        assert suc


def test_bootMount_5(function):
    function.parent.config.MAC = "00:00:00:00:00:00"
    function.parent.config.wolAddress = "255.255.255.255"
    function.parent.config.wolPort = 9
    with mock.patch.object(wakeonlan, "wake", side_effect=OSError):
        suc = function.bootMount()
        assert not suc


def test_bootMount_6(function):
    function.parent.config.MAC = "00:00:00:00:00:00"
    function.parent.config.wolAddress = "255.255.255.255"
    function.parent.config.wolPort = 9
    with mock.patch.object(wakeonlan, "wake", side_effect=ValueError):
        suc = function.bootMount()
        assert not suc


def test_bootMount_7(function):
    function.parent.config.MAC = "00:00:00:00:00:00"
    function.parent.config.wolAddress = "255.255.255.255"
    function.parent.config.wolPort = 9
    with mock.patch.object(wakeonlan, "wake") as mockWake:
        suc = function.bootMount()
        mockWake.assert_called_once_with(
            "00:00:00:00:00:00",
            host="255.255.255.255",
            port=9,
        )
        assert suc


def test_bootMount_8_debug_log(function):
    function.parent.config.MAC = "00:00:00:00:00:00"
    function.parent.config.wolAddress = "255.255.255.255"
    function.parent.config.wolPort = 9
    with (
        mock.patch.object(wakeonlan, "wake"),
        mock.patch.object(function.log, "debug") as mockDebug,
    ):
        function.bootMount()
        mockDebug.assert_called_once()
        assert "MAC:" in mockDebug.call_args[0][0]
        assert "255.255.255.255" in mockDebug.call_args[0][0]
        assert "9" in mockDebug.call_args[0][0]


def test_bootMount_9_warning_log_on_exception(function):
    function.parent.config.MAC = "00:00:00:00:00:00"
    function.parent.config.wolAddress = "255.255.255.255"
    function.parent.config.wolPort = 9
    test_error = OSError("Connection failed")
    with (
        mock.patch.object(wakeonlan, "wake", side_effect=test_error),
        mock.patch.object(function.log, "warning") as mockWarning,
    ):
        suc = function.bootMount()
        mockWarning.assert_called_once()
        assert "Boot mount failed" in mockWarning.call_args[0][0]
        assert not suc


def test_shutdown_1(function):
    function.parent.mountIsUp = True
    with mock.patch.object(function.parent.obsSite, "shutdown", return_value=True, create=True):
        suc = function.shutdown()
        assert suc
        assert not function.parent.mountIsUp


def test_shutdown_2(function):
    function.parent.mountIsUp = True
    with mock.patch.object(function.parent.obsSite, "shutdown", return_value=False, create=True):
        suc = function.shutdown()
        assert not suc
        assert function.parent.mountIsUp


def test_bootMount_10(function):
    function.parent.config.MAC = "00:00:00:00:00:00"
    function.parent.config.wolAddress = "255.255.255.255"
    function.parent.config.wolPort = 0
    with mock.patch.object(wakeonlan, "wake"):
        suc = function.bootMount()
        assert suc
