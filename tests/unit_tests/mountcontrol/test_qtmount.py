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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import os
import socket

# external packages
import wakeonlan
from PyQt5.QtCore import QThreadPool, QTimer

# local imports
from mountcontrol.qtmount import MountSignals
from mountcontrol.qtmount import Mount
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    m = Mount(host='localhost',
              pathToData=os.getcwd() + '/data',
              verbose=False,
              threadPool=QThreadPool())
    yield m


def test_mountSignals(function):
    MountSignals()


def test_waitTimeFlip_1(function):
    function.waitTimeFlip = 1
    assert function._waitTimeFlip == 1000


def test_waitTimeFlip_2(function):
    function._waitTimeFlip = 2000
    assert function.waitTimeFlip == 2


def test_waitSettlingTime(function):
    suc = function.waitAfterSettlingAndEmit()
    assert suc


def test_startTimers(function):
    with mock.patch.object(QTimer,
                           'start'):
        suc = function.startTimers()
        assert suc


def test_stopTimers(function):
    with mock.patch.object(QTimer,
                           'stop'):
        suc = function.stopTimers()
        assert suc


def test_startDomeTimer(function):
    with mock.patch.object(QTimer,
                           'start'):
        suc = function.startDomeTimer()
        assert suc


def test_stopDomeTimer(function):
    with mock.patch.object(QTimer,
                           'stop'):
        suc = function.stopDomeTimer()
        assert suc


def test_startClockTimer(function):
    with mock.patch.object(QTimer,
                           'start'):
        suc = function.startClockTimer()
        assert suc


def test_stopClockTimer(function):
    with mock.patch.object(QTimer,
                           'stop'):
        suc = function.stopClockTimer()
        assert suc


def test_resetData_1(function):
    suc = function.resetData()
    assert suc


def test_checkMountUp_1(function):
    with mock.patch.object(socket.socket,
                           'connect',
                           side_effect=Exception):
        function.checkMountUp()
        assert not function.mountUp


def test_checkMountUp_2(function):
    with mock.patch.object(socket.socket,
                           'connect'):
        with mock.patch.object(socket.socket,
                               'shutdown'):
            with mock.patch.object(socket.socket,
                                   'close'):
                function.checkMountUp()
                assert function.mountUp


def test_errorCycleCheckMountUp(function):
    function.errorCycleCheckMountUp('test')


def test_clearCycleCheckMountUp_1(function):
    suc = function.clearCycleCheckMountUp()
    assert suc


def test_cycleCheckMountUp_1(function):
    function.host = ()
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleCheckMountUp()
        assert not suc


def test_cycleCheckMountUp_2(function):
    function.host = ('localhost', 80)
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.cycleCheckMountUp()
        assert suc


def test_errorCyclePointing_1(function):
    suc = function.errorCyclePointing('test')
    assert suc


def test_clearCyclePointing_1(function):
    function.obsSite.flipped = False
    suc = function.clearCyclePointing()
    assert suc


def test_clearCyclePointing_2(function):
    function.obsSite.flipped = True
    function.obsSite.status = 1
    function.statusAlert = False
    suc = function.clearCyclePointing()
    assert suc
    assert function.statusAlert


def test_clearCyclePointing_3(function):
    function.obsSite.status = 0
    function.statusAlert = False
    suc = function.clearCyclePointing()
    assert suc
    assert not function.statusAlert


def test_clearCyclePointing_4(function):
    function.obsSite.status = 0
    function.statusSlew = False
    suc = function.clearCyclePointing()
    assert suc
    assert function.statusSlew


def test_clearCyclePointing_5(function):
    function.obsSite.status = 2
    function.statusSlew = False
    suc = function.clearCyclePointing()
    assert suc
    assert not function.statusSlew


def test_cyclePointing_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cyclePointing()
        assert suc


def test_cyclePointing_2(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cyclePointing()
        assert suc


def test_cyclePointing_3(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
            suc = function.cyclePointing()
            assert not suc


def test_errorCycleSetting(function):
    function.errorCycleSetting('test')


def test_clearCycleSetting_1(function):
    suc = function.clearCycleSetting()
    assert suc


def test_cycleSetting_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleSetting()
        assert suc


def test_cycleSetting_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleSetting()
        assert not suc


def test_errorGetAlign(function):
    function.errorGetAlign('test')


def test_clearGetAlign_1(function):
    suc = function.clearGetAlign()
    assert suc


def test_GetAlign_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getAlign()
        assert suc


def test_GetAlign_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getAlign()
        assert not suc


def test_errorGetNames(function):
    suc = function.errorGetNames('test')
    assert suc


def test_clearGetNames_1(function):
    suc = function.clearGetNames()
    assert suc


def test_GetNames_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getNames()
        assert suc


def test_GetNames_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getNames()
        assert not suc


def test_errorGetFW(function):
    function.errorGetFW('test')


def test_clearGetFW_1(function):
    suc = function.clearGetFW()
    assert suc


def test_GetFW_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getFW()
        assert suc


def test_GetFW_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getFW()
        assert not suc


def test_errorGetLocation(function):
    function.errorGetLocation('test')


def test_clearGetLocation_1(function):
    suc = function.clearGetLocation()
    assert suc


def test_GetLocation_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getLocation()
        assert suc


def test_GetLocation_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getLocation()
        assert not suc


def test_errorCalcTLE(function):
    function.errorCalcTLE('test')


def test_clearCalcTLE_1(function):
    suc = function.clearCalcTLE()
    assert suc


def test_CalcTLE_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.calcTLE(1234567)
        assert suc


def test_CalcTLE_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.calcTLE(1234567)
        assert not suc


def test_errorStatTLE(function):
    function.errorStatTLE('test')


def test_clearStatTLE_1(function):
    suc = function.clearStatTLE()
    assert suc


def test_StatTLE_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.statTLE()
        assert suc


def test_StatTLE_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.statTLE()
        assert not suc


def test_errorGetTLE(function):
    function.errorGetTLE('test')


def test_clearGetTLE_1(function):
    suc = function.clearGetTLE()
    assert suc


def test_GetTLE_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getTLE()
        assert suc


def test_GetTLE_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.getTLE()
        assert not suc


def test_bootMount_1(function):

    function._MAC = None
    with mock.patch.object(wakeonlan,
                           'send_magic_packet'):
        suc = function.bootMount()
        assert not suc


def test_bootMount_2(function):

    function._MAC = '00:00:00:00:00:00'
    with mock.patch.object(wakeonlan,
                           'send_magic_packet'):
        suc = function.bootMount()
        assert suc


def test_bootMount_3(function):

    function._MAC = '00:00:00:00:00:00'
    with mock.patch.object(wakeonlan,
                           'send_magic_packet'):
        suc = function.bootMount(bAddress='255.255.255.255')
        assert suc


def test_bootMount_4(function):

    function._MAC = '00:00:00:00:00:00'
    with mock.patch.object(wakeonlan,
                           'send_magic_packet'):
        suc = function.bootMount(bAddress='255.255.255.255',
                                 bPort=9)
        assert suc


def test_shutdown_1(function):
    function.mountUp = True
    with mock.patch.object(function.obsSite,
                           'shutdown',
                           return_value=True):
        suc = function.shutdown()
        assert suc
        assert not function.mountUp


def test_shutdown_2(function):
    function.mountUp = True
    with mock.patch.object(function.obsSite,
                           'shutdown',
                           return_value=False):
        suc = function.shutdown()
        assert not suc
        assert function.mountUp


def test_errorDome(function):
    function.errorDome('test')


def test_clearDome_1(function):
    suc = function.clearDome()
    assert suc


def test_cycleDome_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleDome()
        assert suc


def test_cycleDome_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleDome()
        assert not suc


def test_errorClock(function):
    function.errorClock('test')


def test_clearClock_1(function):
    suc = function.clearClock()
    assert suc


def test_cycleClock_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleClock()
        assert suc


def test_cycleClock_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleClock()
        assert not suc


def test_errorCalcTrajectory(function):
    function.errorCalcTrajectory('test')


def test_clearCalcTrajectory_1(function):
    suc = function.clearCalcTrajectory()
    assert suc


def test_calcTrajectory_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.calcTrajectory()
        assert suc


def test_calcTrajectory_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.calcTrajectory()
        assert not suc


def test_workerProgTrajectory_2(function):
    alt = [10, 20, 30]
    az = [10, 20, 30]
    with mock.patch.object(function.satellite,
                           'progTrajectory'):
        suc = function.workerProgTrajectory(alt, az)
        assert suc


def test_errorProgTrajectory(function):
    function.errorProgTrajectory('test')


def test_clearProgTrajectory_1(function):
    suc = function.clearProgTrajectory()
    assert suc


def test_progTrajectory_1(function):
    function.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.progTrajectory(12345678)
        assert suc


def test_progTrajectory_2(function):
    function.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.progTrajectory(12345678)
        assert not suc
