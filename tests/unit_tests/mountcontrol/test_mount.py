############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import os
import socket
from pathlib import Path

# external packages
import wakeonlan
from PySide6.QtCore import QThreadPool, QTimer
from skyfield.api import wgs84, Angle

# local imports
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mountcontrol.mountSignals import MountSignals
from mountcontrol.mount import MountDevice
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope="module")
def function():
    m = MountDevice(
        app=App(),
        host=None,
        MAC="00:00:00:00:00:00",
        pathToData=Path(os.getcwd() + "/data"),
        verbose=False,
    )
    yield m


def test_mountSignals(function):
    MountSignals()


def test_properties(function):
    function.MAC = "00:00:00:00:00:00"
    assert function.MAC == "00:00:00:00:00:00"


def test_waitTimeFlip_1(function):
    function.waitTimeFlip = 1
    assert function._waitTimeFlip == 1000


def test_waitTimeFlip_2(function):
    function._waitTimeFlip = 2000
    assert function.waitTimeFlip == 2


def test_waitSettlingTime(function):
    function.waitAfterSettlingAndEmit()


def test_startTimers(function):
    with mock.patch.object(QTimer, "start"):
        function.startMountTimers()


def test_stopTimers(function):
    with mock.patch.object(QTimer, "stop"):
        function.stopAllMountTimers()


def test_startDomeTimer(function):
    with mock.patch.object(QTimer, "start"):
        function.startDomeTimer()


def test_stopDomeTimer(function):
    with mock.patch.object(QTimer, "stop"):
        function.stopDomeTimer()


def test_startClockTimer(function):
    with mock.patch.object(QTimer, "start"):
        function.startMountClockTimer()


def test_stopClockTimer(function):
    with mock.patch.object(QTimer, "stop"):
        function.stopMountClockTimer()


def test_resetData_1(function):
    function.resetData()


def test_startupMountData_1(function):
    function.mountUpLastStatus = False
    with mock.patch.object(function, "cycleSetting"):
        with mock.patch.object(function, "getFW"):
            with mock.patch.object(function, "getLocation"):
                with mock.patch.object(function, "getTLE"):
                    function.startupMountData(True)
                    assert function.mountUpLastStatus


def test_startupMountData_2(function):
    function.mountUpLastStatus = False
    function.startupMountData(False)
    assert not function.mountUpLastStatus


def test_startupMountData_3(function):
    function.mountUpLastStatus = True
    with mock.patch.object(function, "resetData"):
        function.startupMountData(False)
        assert not function.mountUpLastStatus


def test_startupMountData_4(function):
    function.mountUpLastStatus = True
    function.startupMountData(True)
    assert function.mountUpLastStatus


def test_checkMountUp_1(function):
    with mock.patch.object(socket.socket, "connect", side_effect=socket.timeout):
        function.checkMountUp()
        assert not function.mountUp


def test_checkMountUp_2(function):
    with mock.patch.object(socket.socket, "connect"):
        with mock.patch.object(socket.socket, "shutdown"):
            with mock.patch.object(socket.socket, "close"):
                function.checkMountUp()
                assert function.mountUp


def test_clearCycleCheckMountUp_1(function):
    function.clearCycleCheckMountUp()


def test_cycleCheckMountUp_1(function):
    function.host = ()
    with mock.patch.object(QThreadPool, "start"):
        function.cycleCheckMountUp()


def test_cycleCheckMountUp_2(function):
    function.host = ("localhost", 80)
    with mock.patch.object(function.threadPool, "start"):
        function.cycleCheckMountUp()


def test_clearCyclePointing_1(function):
    function.obsSite.flipped = False
    function.clearCyclePointing()


def test_clearCyclePointing_2(function):
    function.obsSite.flipped = True
    function.obsSite.status = 1
    function.statusAlert = False
    function.clearCyclePointing()
    assert function.statusAlert


def test_clearCyclePointing_3(function):
    function.obsSite.status = 0
    function.statusAlert = False
    function.clearCyclePointing()
    assert not function.statusAlert


def test_clearCyclePointing_4(function):
    function.obsSite.status = 0
    function.statusSlew = False
    function.clearCyclePointing()
    assert function.statusSlew


def test_clearCyclePointing_5(function):
    function.obsSite.status = 2
    function.statusSlew = False
    function.clearCyclePointing()
    assert not function.statusSlew


def test_cyclePointing_1(function):
    with mock.patch.object(QThreadPool, "start"):
        function.cyclePointing()


def test_clearCycleSetting_1(function):
    function.clearCycleSetting()


def test_cycleSetting_1(function):
    with mock.patch.object(QThreadPool, "start"):
        function.cycleSetting()


def test_clearGetAlign_1(function):
    function.clearGetAlign()


def test_GetAlign_1(function):
    with mock.patch.object(QThreadPool, "start"):
        function.getAlign()


def test_clearGetNames_1(function):
    function.clearGetNames()


def test_GetNames_1(function):
    with mock.patch.object(QThreadPool, "start"):
        function.getNames()


def test_clearGetFW_1(function):
    function.clearGetFW()


def test_GetFW_1(function):
    with mock.patch.object(QThreadPool, "start"):
        function.getFW()


def test_clearGetLocation_1(function):
    function.clearGetLocation()


def test_GetLocation_1(function):
    with mock.patch.object(QThreadPool, "start"):
        function.getLocation()


def test_clearCalcTLE_1(function):
    function.clearCalcTLE()


def test_CalcTLE_1(function):
    with mock.patch.object(QThreadPool, "start"):
        function.calcTLE(1234567)


def test_clearStatTLE_1(function):
    function.clearStatTLE()


def test_StatTLE_1(function):
    with mock.patch.object(QThreadPool, "start"):
        function.statTLE()


def test_clearGetTLE_1(function):
    function.clearGetTLE()


def test_GetTLE_1(function):
    with mock.patch.object(QThreadPool, "start"):
        function.getTLE()


def test_bootMount_1(function):
    function._MAC = None
    with mock.patch.object(wakeonlan, "send_magic_packet"):
        suc = function.bootMount()
        assert not suc


def test_bootMount_2(function):
    function._MAC = "00:00:00:00:00:00"
    with mock.patch.object(wakeonlan, "send_magic_packet"):
        suc = function.bootMount()
        assert suc


def test_bootMount_3(function):
    function._MAC = "00:00:00:00:00:00"
    with mock.patch.object(wakeonlan, "send_magic_packet"):
        suc = function.bootMount(bAddress="255.255.255.255")
        assert suc


def test_bootMount_4(function):
    function._MAC = "00:00:00:00:00:00"
    with mock.patch.object(wakeonlan, "send_magic_packet"):
        suc = function.bootMount(bAddress="255.255.255.255", bPort=9)
        assert suc


def test_shutdown_1(function):
    function.mountUp = True
    with mock.patch.object(function.obsSite, "shutdown", return_value=True):
        suc = function.shutdown()
        assert suc
        assert not function.mountUp


def test_shutdown_2(function):
    function.mountUp = True
    with mock.patch.object(function.obsSite, "shutdown", return_value=False):
        suc = function.shutdown()
        assert not suc
        assert function.mountUp


def test_clearDome_1(function):
    function.clearDome()


def test_cycleDome_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cycleDome()


def test_cycleDome_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.cycleDome()


def test_cycleClock_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cycleClock()


def test_cycleClock_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool, "start"):
        function.cycleClock()


def test_workerProgTrajectory_1(function):
    alt = [10, 20, 30]
    az = [10, 20, 30]
    with mock.patch.object(function.satellite, "addTrajectoryPoint"):
        suc = function.workerProgTrajectory(alt, az, True)
        assert suc


def test_workerProgTrajectory_2(function):
    alt = [10, 20, 30]
    az = [10, 20, 30]
    with mock.patch.object(function.satellite, "addTrajectoryPoint"):
        suc = function.workerProgTrajectory(alt, az, False)
        assert not suc


def test_clearProgTrajectory_1(function):
    function.clearProgTrajectory()


def test_progTrajectory_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.progTrajectory(start=1, alt=[10], az=[10])


def test_progTrajectory_2(function):
    function.mountUp = False
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
    with mock.patch.object(function.obsSite, "setTargetAltAz", return_value=True):
        with mock.patch.object(
            function, "calcTransformationMatricesTarget", return_value=(10, 5, 0, 0, 0)
        ):
            valAlt, valAz = function.calcMountAltAzToDomeAltAz(10, 5)
            assert valAlt == 10
            assert valAz == 5


def test_calcMountAltAzToDomeAltAz_2(function):
    with mock.patch.object(function.obsSite, "setTargetAltAz", return_value=False):
        valAlt, valAz = function.calcMountAltAzToDomeAltAz(10, 5)
        assert valAlt is None
        assert valAz is None
