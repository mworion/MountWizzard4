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
import wakeonlan
from mw4.mountcontrol.mount import MountDevice
from mw4.mountcontrol.mountSignals import MountSignals
from PySide6.QtCore import QThreadPool
from skyfield.api import Angle, wgs84
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function():
    m = MountDevice(
        app=App(),
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
    function.resetAfterStart()


def test_collectData_1(function):
    function.obsSite.statusSlew = True
    function.collectData()


def test_waitAfterSettlingAndEmit(function):
    function.waitAfterSettlingAndEmit()


def test_stopAllMountTimers(function):
    with mock.patch.object(function.settlingWait, "stop") as mockStop:
        function.stopAllMountTimers()
        mockStop.assert_called_once()


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
        function.workerCyclePointing.mutex.unlock()
        function.workerCyclePointing.signals.finished.emit()
        function.workerCyclePointing = None


def test_cyclePointing_3(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cyclePointing()
        assert function.workerCyclePointing is not None
    if function.workerCyclePointing is not None:
        function.workerCyclePointing.mutex.unlock()
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
        function.workerCycleSetting.mutex.unlock()
        function.workerCycleSetting.signals.finished.emit()
        function.workerCycleSetting = None


def test_cycleSetting_3(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cycleSetting()
        assert function.workerCycleSetting is not None
    if function.workerCycleSetting is not None:
        function.workerCycleSetting.mutex.unlock()
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
        function.workerGetModel.mutex.unlock()
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
        function.workerGetNames.mutex.unlock()
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
        function.workerGetFW.mutex.unlock()
        function.workerGetFW = None


def test_resultGetLocation_1(function):
    function.resultGetLocation()


def test_GetLocation_1(function):
    function.mountIsUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.getLocation()


def test_GetLocation_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.getLocation()
    if function.workerGetLocation is not None:
        function.workerGetLocation.mutex.unlock()
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
        function.workerCalcTLE.mutex.unlock()
        function.workerCalcTLE.signals.finished.emit()
        function.workerCalcTLE = None


def test_CalcTLE_3(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.calcTLE(1234567)
        assert function.workerCalcTLE is not None
    if function.workerCalcTLE is not None:
        function.workerCalcTLE.mutex.unlock()
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
        function.workerStatTLE.mutex.unlock()
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
        function.workerGetTLE.mutex.unlock()
        function.workerGetTLE.signals.finished.emit()
        function.workerGetTLE = None


def test_GetTLE_3(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.getTLE()
        assert function.workerGetTLE is not None
    if function.workerGetTLE is not None:
        function.workerGetTLE.mutex.unlock()
        function.workerGetTLE.signals.finished.emit()
        function.workerGetTLE = None


def test_bootMount_1(function):
    function.config.MAC = None
    with mock.patch.object(wakeonlan, "wake"):
        suc = function.bootMount()
        assert not suc


def test_bootMount_2(function):
    function.config.MAC = "00:00:00:00:00:00"
    with mock.patch.object(wakeonlan, "wake"):
        suc = function.bootMount()
        assert suc


def test_bootMount_3(function):
    function.config.MAC = "00:00:00:00:00:00"
    function.config.wolAddress = "255.255.255.255"
    with mock.patch.object(wakeonlan, "wake"):
        suc = function.bootMount()
        assert suc


def test_bootMount_4(function):
    function.config.MAC = "00:00:00:00:00:00"
    function.config.wolAddress = "255.255.255.255"
    function.config.wolPort = 9
    with mock.patch.object(wakeonlan, "wake"):
        suc = function.bootMount()
        assert suc


def test_bootMount_5(function):
    function.config.MAC = "00:00:00:00:00:00"
    function.config.wolAddress = "255.255.255.255"
    function.config.wolPort = 9
    with mock.patch.object(wakeonlan, "wake", side_effect=OSError):
        suc = function.bootMount()
        assert not suc


def test_bootMount_6(function):
    function.config.MAC = "00:00:00:00:00:00"
    function.config.wolAddress = "255.255.255.255"
    function.config.wolPort = 9
    with mock.patch.object(wakeonlan, "wake", side_effect=ValueError):
        suc = function.bootMount()
        assert not suc


def test_bootMount_7(function):
    function.config.MAC = "00:00:00:00:00:00"
    function.config.wolAddress = "255.255.255.255"
    function.config.wolPort = 9
    with mock.patch.object(wakeonlan, "wake") as mockWake:
        suc = function.bootMount()
        mockWake.assert_called_once_with(
            "00:00:00:00:00:00",
            host="255.255.255.255",
            port=9,
        )
        assert suc


def test_bootMount_8_debug_log(function):
    function.config.MAC = "00:00:00:00:00:00"
    function.config.wolAddress = "255.255.255.255"
    function.config.wolPort = 9
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
    function.config.MAC = "00:00:00:00:00:00"
    function.config.wolAddress = "255.255.255.255"
    function.config.wolPort = 9
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
    function.mountIsUp = True
    with mock.patch.object(function.obsSite, "shutdown", return_value=True):
        suc = function.shutdown()
        assert suc
        assert not function.mountIsUp


def test_shutdown_2(function):
    function.mountIsUp = True
    with mock.patch.object(function.obsSite, "shutdown", return_value=False):
        suc = function.shutdown()
        assert not suc
        assert function.mountIsUp


def test_runnerProgTrajectory_1(function):
    alt = [10, 20, 30]
    az = [10, 20, 30]
    with mock.patch.object(function.satellite, "addTrajectoryPoint"):
        suc = function.runnerProgTrajectory(alt, az, True)
        assert suc


def test_runnerProgTrajectory_2(function):
    alt = [10, 20, 30]
    az = [10, 20, 30]
    with (
        mock.patch.object(function.satellite, "addTrajectoryPoint"),
        mock.patch.object(function.satellite, "preCalcTrajectory"),
    ):
        suc = function.runnerProgTrajectory(alt, az, False)
        assert not suc


def test_resultProgTrajectory_1(function):
    function.resultProgTrajectory()


def test_progTrajectory_1(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.progTrajectory(start=1, alt=[10], az=[10])
    if function.workerTrajectory is not None:
        function.workerTrajectory.mutex.unlock()
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


def test_collectData_no_slew(function):
    function.obsSite.statusSlew = False
    function.raRef = 100.0
    function.decRef = 50.0
    function.collectData()
    assert function.raRef == 100.0
    assert function.decRef == 50.0


def test_bootMount_with_bAddress_only(function):
    function.config.MAC = "00:00:00:00:00:00"
    function.config.wolAddress = "255.255.255.255"
    function.config.wolPort = 0
    with mock.patch.object(wakeonlan, "wake"):
        suc = function.bootMount()
        assert suc


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
