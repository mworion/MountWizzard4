# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.mountcontrol.mount import MountDevice
from mw4.mountcontrol.mountSignals import MountSignals
from mw4.mountcontrol.mountStatus import MountStatus
from PySide6.QtCore import QThreadPool
from skyfield.api import Angle, wgs84
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    m = MountDevice(
        app=makeApp(),
        verbose=False,
    )
    m.config.MAC = "00:00:00:00:00:00"
    yield m


def test_mountSignals(function):
    MountSignals()


def test_properties_MAC(function):
    function.config.MAC = "00:00:00:00:00:00"
    assert function.config.MAC == "00:00:00:00:00:00"


def test_properties_waitTimeFlip_1(function):
    function.waitTimeFlip = 1
    assert function._waitTimeFlip == 1000


def test_properties_waitTimeFlip_2(function):
    function._waitTimeFlip = 2000
    assert function.waitTimeFlip == 2


def test_resetAfterStart(function):
    with mock.patch.object(function.mountData, "reset") as mockReset:
        function.resetAfterStart()
        mockReset.assert_called_once()


def test_collectData(function):
    with mock.patch.object(function.mountData, "collect") as mockCollect:
        function.collectData()
        mockCollect.assert_called_once()


def test_data_property(function):
    assert function.data is function.mountData.data


def test_connectTimers(function):
    timeMgr = mock.MagicMock()
    function.app.timeMgr = timeMgr
    function.connectTimers()
    conn = function.mountTimeConn
    timeMgr.update1s.connect.assert_any_call(conn.checkMountUp)
    timeMgr.update1s.connect.assert_any_call(function.collectData)
    timeMgr.update30s.connect.assert_any_call(conn.syncClock)
    timeMgr.update30s.connect.assert_any_call(function.cycleStaticSetting)
    timeMgr.update0_5s.connect.assert_called_once_with(function.cyclePointing)
    timeMgr.update3s.connect.assert_called_once_with(function.cycleSetting)
    timeMgr.start3s.connect.assert_called_once_with(function.resetAfterStart)


def test_waitAfterSettlingAndEmit(function):
    function.waitAfterSettlingAndEmit()


def test_stopAllMountTimers(function):
    with mock.patch.object(function.settlingWait, "stop") as mockStop:
        function.stopAllMountTimers()
        mockStop.assert_called_once()


def test_stopCommunication_resetsMountState(function):
    function.mountIsUp = True
    function.mountData.data["oldMount"] = 1.0
    function.statusAlert = True
    function.statusSlew = True
    function.obsSite.statusSlew = True
    function.obsSite.statusSat = "T"
    with (
        mock.patch.object(function, "stopAllMountTimers") as mockStopTimers,
        mock.patch("mw4.mountcontrol.mount.stopWorkers") as mockStopWorkers,
        mock.patch.object(function.mountTimeConn, "reset") as mockReset,
        mock.patch.object(function.signals, "deviceDisconnected") as mockDisconnected,
    ):
        function.stopCommunication()

    mockStopTimers.assert_called_once()
    mockStopWorkers.assert_called_once()
    mockReset.assert_called_once()
    mockDisconnected.emit.assert_called_once_with("mount")
    assert not function.mountIsUp
    assert not function.mountData.data
    assert not function.statusAlert
    assert not function.statusSlew
    assert function.obsSite.status == MountStatus.ERROR
    assert not function.obsSite.statusSlew
    assert function.obsSite.statusSat == "E"


def test_processMountStatus_ignoresOldGeneration(function):
    generation = function.mountTimeConn.connectionGeneration
    with mock.patch.object(function.signals, "mountIsUp") as mockSignal:
        function.processMountStatus(generation - 1, True)
        mockSignal.emit.assert_not_called()
        function.processMountStatus(generation, True)
        mockSignal.emit.assert_called_once_with(True)


@pytest.mark.parametrize(
    ("runner", "poll", "finish", "result"),
    [
        ("runnerCyclePointing", "obsSite", "finishCyclePointing", "resultCyclePointing"),
        ("runnerCycleSetting", "setting", "finishCycleSetting", "resultCycleSetting"),
    ],
)
def test_cycleResultRequiresCurrentConnection(function, runner, poll, finish, result):
    generation = function.mountTimeConn.connectionGeneration
    method = "pollPointing" if poll == "obsSite" else "pollSetting"
    with mock.patch.object(getattr(function, poll), method, return_value=True):
        response = getattr(function, runner)(generation)
    with mock.patch.object(function, result) as callback:
        function.mountIsUp = False
        getattr(function, finish)(response)
        function.mountIsUp = True
        getattr(function, finish)((generation - 1, *response[1:]))
        callback.assert_not_called()
        getattr(function, finish)(response)
        callback.assert_called_once_with(True)


@pytest.mark.parametrize(
    ("runner", "finish", "objectName", "poll", "field"),
    [
        ("runnerCyclePointing", "finishCyclePointing", "obsSite", "pollPointing", "_status"),
        ("runnerCycleSetting", "finishCycleSetting", "setting", "pollSetting", "slewRate"),
        (
            "runnerCycleStaticSetting",
            "finishCycleStaticSetting",
            "setting",
            "pollStaticSetting",
            "_typeConnection",
        ),
    ],
)
def test_stalePollCannotChangeMountValues(function, runner, finish, objectName, poll, field):
    target = getattr(function, objectName)
    original = getattr(target, field)
    generation = function.mountTimeConn.connectionGeneration

    def pollNewValue(staged):
        setattr(staged, field, 123)
        return True

    with mock.patch.object(type(target), poll, pollNewValue):
        response = getattr(function, runner)(generation)
    assert getattr(target, field) == original
    function.mountIsUp = True
    function.mountTimeConn.connectionGeneration += 1
    getattr(function, finish)(response)
    assert getattr(target, field) == original
    getattr(function, finish)((function.mountTimeConn.connectionGeneration, False, *response[2:]))
    assert getattr(target, field) == original
    if runner == "runnerCycleStaticSetting":
        getattr(function, finish)((function.mountTimeConn.connectionGeneration, True, response[2]))
        assert getattr(target, field) == 123
        setattr(target, field, original)


def test_settingPollRefreshesStaticValuesForNewConnection(function):
    function.mountIsUp = True
    generation = function.mountTimeConn.connectionGeneration
    function.staticSettingGeneration = generation - 1
    function.setting.staticRead = True

    def pollSetting(staged):
        assert not staged.staticRead
        staged.staticRead = True
        staged._typeConnection = 2
        return True

    with mock.patch.object(type(function.setting), "pollSetting", pollSetting):
        response = function.runnerCycleSetting(generation)
    with mock.patch.object(function, "resultCycleSetting"):
        function.finishCycleSetting(response)
    assert function.staticSettingGeneration == generation
    assert function.setting.typeConnection == 2
    with mock.patch.object(type(function.setting), "pollSetting", return_value=True):
        response = function.runnerCycleSetting(generation)
    assert response[2].staticRead


def test_failedStaticReadDoesNotOverwriteNewerStaticResult(function):
    function.mountIsUp = True
    generation = function.mountTimeConn.connectionGeneration
    function.staticSettingGeneration = generation - 1
    function.setting.staticRead = True

    def pollSetting(staged):
        assert not staged.staticRead
        return True

    with mock.patch.object(type(function.setting), "pollSetting", pollSetting):
        response = function.runnerCycleSetting(generation)
    function.staticSettingGeneration = generation
    function.setting.typeConnection = 3
    with mock.patch.object(function, "resultCycleSetting"):
        function.finishCycleSetting(response)
    assert function.setting.staticRead
    assert function.setting.typeConnection == 3


def test_settingPollDoesNotOverwriteNewerStaticResult(function):
    function.mountIsUp = True
    generation = function.mountTimeConn.connectionGeneration
    function.staticSettingGeneration = generation
    function.setting.staticRead = True
    function.setting.typeConnection = 2
    with mock.patch.object(type(function.setting), "pollSetting", return_value=True):
        response = function.runnerCycleSetting(generation)
    function.setting.typeConnection = 3
    with mock.patch.object(function, "resultCycleSetting"):
        function.finishCycleSetting(response)
    assert function.setting.typeConnection == 3


def test_startupMountData_1(function):
    function.mountIsUp = False
    with (
        mock.patch.object(function, "cycleSetting"),
        mock.patch.object(function, "getFW"),
        mock.patch.object(function, "getLocation"),
        mock.patch.object(function, "getTLE"),
        mock.patch.object(function.obsSite, "setHighPrecision"),
    ):
        function.startupMountData(True)
        assert function.mountIsUp


def test_startupMountData_2(function):
    function.mountIsUp = True
    function.startupMountData(False)
    assert not function.mountIsUp


def test_startupMountData_3(function):
    function.mountIsUp = False
    function.startupMountData(False)
    assert not function.mountIsUp


def test_startupMountData_4(function):
    function.mountIsUp = True
    function.startupMountData(True)
    assert function.mountIsUp


def test_startupMountData_5(function):
    function.mountIsUp = True
    with mock.patch.object(function.signals, "deviceDisconnected") as mockSignal:
        function.signals.mountIsUp.emit(False)
        mockSignal.emit.assert_called_once_with("mount")
    assert not function.mountIsUp


def test_resultCyclePointing_1(function):
    function.obsSite.flipped = False
    function.resultCyclePointing(True)


def test_resultCyclePointing_2(function):
    function.obsSite.flipped = True
    function.obsSite.status = 1
    function.statusAlert = False
    function.resultCyclePointing(True)
    assert function.statusAlert


def test_resultCyclePointing_3(function):
    function.obsSite.status = 0
    function.statusAlert = False
    function.resultCyclePointing(True)
    assert not function.statusAlert


def test_resultCyclePointing_4(function):
    function.obsSite.statusSlew = True
    function.resultCyclePointing(True)
    assert function.statusSlew


def test_resultCyclePointing_5(function):
    function.obsSite.statusSlew = False
    function.statusSlew = True
    function.resultCyclePointing(True)
    assert not function.statusSlew


def test_cyclePointing_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.cyclePointing()
        assert function.workerCyclePointing is None


def test_cyclePointing_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cyclePointing()
        assert function.workerCyclePointing is not None
    if function.workerCyclePointing is not None:
        function.workerCyclePointing.release()
        function.workerCyclePointing.signals.finished.emit()
        function.workerCyclePointing = None


def test_cyclePointing_3(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cyclePointing()
        assert function.workerCyclePointing is not None
    if function.workerCyclePointing is not None:
        function.workerCyclePointing.release()
        function.workerCyclePointing.signals.finished.emit()
        function.workerCyclePointing = None


def test_resultCycleSetting_1(function):
    function.resultCycleSetting(True)


def test_cycleSetting_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.cycleSetting()
        assert function.workerCycleSetting is None


def test_cycleSetting_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cycleSetting()
        assert function.workerCycleSetting is not None
    if function.workerCycleSetting is not None:
        function.workerCycleSetting.release()
        function.workerCycleSetting.signals.finished.emit()
        function.workerCycleSetting = None


def test_cycleSetting_3(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cycleSetting()
        assert function.workerCycleSetting is not None
    if function.workerCycleSetting is not None:
        function.workerCycleSetting.release()
        function.workerCycleSetting.signals.finished.emit()
        function.workerCycleSetting = None


def test_resultGetModel_1(function):
    function.resultGetModel()


def test_getModel_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.getModel()


def test_getModel_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.getModel()
    if function.workerGetModel is not None:
        function.workerGetModel.release()
        function.workerGetModel = None


def test_resultGetNames_1(function):
    function.resultGetNames()


def test_GetNames_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.getNames()


def test_GetNames_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.getNames()
    if function.workerGetNames is not None:
        function.workerGetNames.release()
        function.workerGetNames = None


def test_resultGetFW_1(function):
    function.resultGetFW()


def test_GetFW_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.getFW()


def test_GetFW_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.getFW()
    if function.workerGetFW is not None:
        function.workerGetFW.release()
        function.workerGetFW = None


def test_resultGetLocation_1(function):
    function.resultGetLocation()


def test_resultGetLocation_2(function):
    with mock.patch.object(function.geometry, "loadParametersFromConfig") as mockLoad:
        function.resultGetLocation()
        mockLoad.assert_called_once()


def test_GetLocation_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.getLocation()


def test_GetLocation_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.getLocation()
    if function.workerGetLocation is not None:
        function.workerGetLocation.release()
        function.workerGetLocation = None


def test_resultCalcTLE_1(function):
    function.resultCalcTLE()


def test_CalcTLE_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.calcTLE(1234567)
        assert function.workerCalcTLE is None


def test_CalcTLE_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.calcTLE(1234567)
        assert function.workerCalcTLE is not None
    if function.workerCalcTLE is not None:
        function.workerCalcTLE.release()
        function.workerCalcTLE.signals.finished.emit()
        function.workerCalcTLE = None


def test_CalcTLE_3(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.calcTLE(1234567)
        assert function.workerCalcTLE is not None
    if function.workerCalcTLE is not None:
        function.workerCalcTLE.release()
        function.workerCalcTLE.signals.finished.emit()
        function.workerCalcTLE = None


def test_resultStatTLE_1(function):
    function.resultStatTLE()


def test_StatTLE_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.statTLE()


def test_StatTLE_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.statTLE()
    if function.workerStatTLE is not None:
        function.workerStatTLE.release()
        function.workerStatTLE = None


def test_resultGetTLE_1(function):
    function.resultGetTLE()


def test_GetTLE_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.getTLE()
        assert function.workerGetTLE is None


def test_GetTLE_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.getTLE()
        assert function.workerGetTLE is not None
    if function.workerGetTLE is not None:
        function.workerGetTLE.release()
        function.workerGetTLE.signals.finished.emit()
        function.workerGetTLE = None


def test_GetTLE_3(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.getTLE()
        assert function.workerGetTLE is not None
    if function.workerGetTLE is not None:
        function.workerGetTLE.release()
        function.workerGetTLE.signals.finished.emit()
        function.workerGetTLE = None


def test_runnerProgTrajectory_1(function):
    alt = [10, 20, 30]
    az = [10, 20, 30]
    with (
        mock.patch.object(function.satellite, "addTrajectoryPoint"),
        mock.patch.object(function.satellite, "preCalcTrajectory") as mockPre,
    ):
        function.runnerProgTrajectory(alt, az, True)
        mockPre.assert_called_once_with(replay=True)


def test_runnerProgTrajectory_2(function):
    alt = [10, 20, 30]
    az = [10, 20, 30]
    with (
        mock.patch.object(function.satellite, "addTrajectoryPoint"),
        mock.patch.object(function.satellite, "preCalcTrajectory"),
    ):
        function.runnerProgTrajectory(alt, az, False)


def test_resultProgTrajectory_1(function):
    function.resultProgTrajectory()


def test_progTrajectory_1(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.progTrajectory(start=1, alt=[10], az=[10])
    if function.workerTrajectory is not None:
        function.workerTrajectory.release()
        function.workerTrajectory = None


def test_progTrajectory_2(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.progTrajectory(start=1, alt=[10], az=[10])


def test_calcTransformationMatricesTarget(function):
    function.obsSite.raJNowTarget = Angle(hours=12)
    function.obsSite.timeSidereal = Angle(hours=12)
    function.obsSite.decJNowTarget = Angle(degrees=10)
    function.obsSite.location = wgs84.latlon(
        latitude_degrees=49, longitude_degrees=11, elevation_m=500
    )
    function.obsSite.piersideTarget = "E"
    function.calcTransformationMatricesTarget()


def test_calcTransformationMatricesActual(function):
    function.obsSite.raJNow = Angle(hours=12)
    function.obsSite.timeSidereal = Angle(hours=12)
    function.obsSite.decJNow = Angle(degrees=10)
    function.obsSite.location = wgs84.latlon(
        latitude_degrees=49, longitude_degrees=11, elevation_m=500
    )
    function.obsSite.pierside = "E"
    function.calcTransformationMatricesActual()


def test_calcMountAltAzToDomeAltAz_1(function):
    with (
        mock.patch.object(function.obsSite, "setTargetAltAz", return_value=True),
        mock.patch.object(
            function, "calcTransformationMatricesTarget", return_value=(10, 5, 0, 0, 0)
        ),
    ):
        valAlt, valAz = function.calcMountAltAzToDomeAltAz(10, 5)
        assert valAlt == 10
        assert valAz == 5


def test_calcMountAltAzToDomeAltAz_2(function):
    with mock.patch.object(function.obsSite, "setTargetAltAz", return_value=False):
        valAlt, valAz = function.calcMountAltAzToDomeAltAz(10, 5)
        assert valAlt is None
        assert valAz is None


def test_resultCyclePointing_alert_status_1_98(function):
    function.obsSite.status = 98
    function.statusAlert = False
    with mock.patch.object(function.signals, "alert"):
        function.resultCyclePointing(True)
        assert function.statusAlert


def test_resultCyclePointing_alert_status_99(function):
    function.obsSite.status = 99
    function.statusAlert = False
    with mock.patch.object(function.signals, "alert"):
        function.resultCyclePointing(True)
        assert function.statusAlert


def test_resultCyclePointing_settlingWait(function):
    function.obsSite.status = 0
    function.obsSite.flipped = True
    function._waitTimeFlip = 5000
    function.obsSite.statusSlew = False
    function.statusSlew = True
    with mock.patch.object(function.settlingWait, "start"):
        function.resultCyclePointing(True)
        assert function.settlingWait.start.called


def test_resultCyclePointing_flippedConsumed(function):
    function.obsSite.status = 0
    function.obsSite.flipped = True
    function._waitTimeFlip = 5000
    function.obsSite.statusSlew = False
    function.statusSlew = True
    with mock.patch.object(function.settlingWait, "start") as mockStart:
        function.resultCyclePointing(True)
        mockStart.assert_called_once_with(5000)
    assert not function.obsSite.flipped
    function.statusSlew = True
    with mock.patch.object(function.settlingWait, "start") as mockStart:
        function.resultCyclePointing(True)
        mockStart.assert_called_once_with(0)


def test_resultStatTLE_signal(function):
    with mock.patch.object(function.signals, "statTLEdone"):
        function.resultStatTLE()
        assert function.signals.statTLEdone.emit.called


def test_resultGetTLE_signal(function):
    with mock.patch.object(function.signals, "getTLEdone"):
        function.resultGetTLE()
        assert function.signals.getTLEdone.emit.called


def test_resultCalcTLE_signal(function):
    with mock.patch.object(function.signals, "calcTLEdone"):
        function.resultCalcTLE()
        assert function.signals.calcTLEdone.emit.called


def test_resultProgTrajectory_signal(function):
    with mock.patch.object(function.signals, "calcTrajectoryDone"):
        function.resultProgTrajectory()
        assert function.signals.calcTrajectoryDone.emit.called


def test_waitTimeFlip_setter_rejects_negative(function):
    with pytest.raises(ValueError):
        function.waitTimeFlip = -1


def test_resultCyclePointing_6(function):
    received = []
    function.signals.alert.connect(lambda: received.append(1))
    function.obsSite.status = 1
    function.statusAlert = True
    function.resultCyclePointing(True)
    function.signals.alert.disconnect()
    assert received == []
    assert function.statusAlert


def test_resultCyclePointing_7(function):
    received = []
    function.signals.pointDone.connect(received.append)
    function.resultCyclePointing(False)
    function.signals.pointDone.disconnect()
    assert received == []


def test_resultCycleSetting_2(function):
    received = []
    function.signals.settingDone.connect(received.append)
    function.resultCycleSetting(False)
    function.signals.settingDone.disconnect()
    assert received == []


def test_resultCycleSetting_changed(function):
    function.setting.changed = {"timeToFlip"}
    received = []
    function.signals.settingChanged.connect(received.append)
    function.resultCycleSetting(True)
    function.signals.settingChanged.disconnect()
    function.setting.changed = set()
    assert received == [function.setting]


def test_resultCycleSetting_unchanged(function):
    function.setting.changed = set()
    received = []
    function.signals.settingChanged.connect(received.append)
    function.resultCycleSetting(True)
    function.signals.settingChanged.disconnect()
    assert received == []


def test_cycleStaticSetting_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.cycleStaticSetting()
        assert function.workerCycleStaticSetting is None


def test_cycleStaticSetting_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cycleStaticSetting()
        assert function.workerCycleStaticSetting is not None
    if function.workerCycleStaticSetting is not None:
        function.workerCycleStaticSetting.release()
        function.workerCycleStaticSetting.signals.finished.emit()
        function.workerCycleStaticSetting = None
