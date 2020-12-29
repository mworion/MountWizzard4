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
# written in python3 , (c) 2019, 2020 by mworion
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


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global m
    m = Mount(host='127.0.0.1',
              pathToData=os.getcwd() + '/data',
              verbose=True)
    yield


def test_mountClass():
    test = Mount(host='127.0.0.1',
                 pathToData=os.getcwd() + '/data',
                 verbose=True,
                 threadPool=QThreadPool())
    del test


def test_mountSignals():
    MountSignals()


def test_settlingTime_1():
    m.settlingTime = 1
    assert m._settlingTime == 1000


def test_settlingTime_2():
    m._settlingTime = 2000
    assert m.settlingTime == 2


def test_waitSettlingTime(qtbot):
    with qtbot.waitSignal(m.signals.slewFinished):
        suc = m.waitSettlingAndEmit()
        assert suc


def test_startTimers():
    with mock.patch.object(QTimer,
                           'start'):
        m.startTimers()


def test_stopTimers():
    with mock.patch.object(QTimer,
                           'stop'):
        with mock.patch.object(QThreadPool,
                               'waitForDone'):
            m.stopTimers()


def test_resetData_1(qtbot):
    with qtbot.waitSignal(m.signals.pointDone):
        m.resetData()


def test_resetData_2(qtbot):
    with qtbot.waitSignal(m.signals.settingDone):
        m.resetData()


def test_resetData_3(qtbot):
    with qtbot.waitSignal(m.signals.alignDone):
        m.resetData()


def test_resetData_4(qtbot):
    with qtbot.waitSignal(m.signals.namesDone):
        m.resetData()


def test_resetData_5(qtbot):
    with qtbot.waitSignal(m.signals.firmwareDone):
        m.resetData()


def test_resetData_6(qtbot):
    with qtbot.waitSignal(m.signals.locationDone):
        m.resetData()


def test_checkMountUp_1():
    with mock.patch.object(socket.socket,
                           'connect',
                           side_effect=Exception):
        m.checkMountUp()
        assert not m.mountUp


def test_checkMountUp_2():
    with mock.patch.object(socket.socket,
                           'connect'):
        with mock.patch.object(socket.socket,
                               'shutdown'):
            with mock.patch.object(socket.socket,
                                   'close'):
                m.checkMountUp()
                assert m.mountUp


def test_errorCycleCheckMountUp():
    m.errorCycleCheckMountUp('test')


def test_clearCycleCheckMountUp_1(qtbot):
    with qtbot.waitSignal(m.signals.mountUp):
        m.cycleCheckMountUp()


def test_cycleCheckMountUp_1(qtbot):
    m.host = ()
    suc = m.cycleCheckMountUp()
    assert not suc


def test_cycleCheckMountUp_2(qtbot):
    m.host = ('localhost', 80)
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = m.cycleCheckMountUp()
        assert suc


def test_errorCyclePointing_1():
    suc = m.errorCyclePointing('test')
    assert suc


def test_clearCyclePointing_1(qtbot):
    with qtbot.waitSignal(m.signals.pointDone):
        m.clearCyclePointing()


def test_clearCyclePointing_2(qtbot):
    m.obsSite.status = 1
    m.statusAlert = False
    suc = m.clearCyclePointing()
    assert suc
    assert m.statusAlert


def test_clearCyclePointing_3(qtbot):
    m.obsSite.status = 0
    m.statusAlert = False
    suc = m.clearCyclePointing()
    assert suc
    assert not m.statusAlert


def test_clearCyclePointing_4(qtbot):
    m.obsSite.status = 0
    m.statusSlew = False
    suc = m.clearCyclePointing()
    assert suc
    assert m.statusSlew


def test_clearCyclePointing_5(qtbot):
    m.obsSite.status = 2
    m.statusSlew = False
    suc = m.clearCyclePointing()
    assert suc
    assert not m.statusSlew


def test_cyclePointing_1(qtbot):
    m.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.assertNotEmitted(m.signals.pointDone):
            suc = m.cyclePointing()
            assert suc


def test_cyclePointing_2(qtbot):
    m.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.assertNotEmitted(m.signals.pointDone):
            suc = m.cyclePointing()
            assert suc


def test_cyclePointing_3(qtbot):
    m.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
            suc = m.cyclePointing()
            assert not suc


def test_errorCycleSetting():
    m.errorCycleSetting('test')


def test_clearCycleSetting_1(qtbot):
    with qtbot.waitSignal(m.signals.settingDone):
        m.clearCycleSetting()


def test_cycleSetting_1(qtbot):
    m.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.assertNotEmitted(m.signals.settingDone):
            suc = m.cycleSetting()
            assert suc


def test_cycleSetting_2(qtbot):
    m.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.waitSignal(m.signals.settingDone):
            suc = m.cycleSetting()
            assert not suc


def test_errorGetAlign():
    m.errorGetAlign('test')


def test_clearGetAlign_1(qtbot):
    with qtbot.waitSignal(m.signals.alignDone):
        m.clearGetAlign()


def test_GetAlign_1(qtbot):
    m.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.assertNotEmitted(m.signals.alignDone):
            suc = m.getAlign()
            assert suc


def test_GetAlign_2(qtbot):
    m.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.waitSignal(m.signals.alignDone):
            suc = m.getAlign()
            assert not suc


def test_errorGetNames():
    m.errorGetNames('test')


def test_clearGetNames_1(qtbot):
    with qtbot.waitSignal(m.signals.namesDone):
        m.clearGetNames()


def test_GetNames_1(qtbot):
    m.mountUp = True
    with qtbot.assertNotEmitted(m.signals.namesDone):
        suc = m.getNames()
        assert suc


def test_GetNames_2(qtbot):
    m.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.waitSignal(m.signals.namesDone):
            suc = m.getNames()
            assert not suc


def test_errorGetFW():
    m.errorGetFW('test')


def test_clearGetFW_1(qtbot):
    with qtbot.waitSignal(m.signals.firmwareDone):
        m.clearGetFW()


def test_GetFW_1(qtbot):
    m.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.assertNotEmitted(m.signals.firmwareDone):
            suc = m.getFW()
            assert suc


def test_GetFW_2(qtbot):
    m.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.waitSignal(m.signals.firmwareDone):
            suc = m.getFW()
            assert not suc


def test_errorGetLocation():
    m.errorGetLocation('test')


def test_clearGetLocation_1(qtbot):
    with qtbot.waitSignal(m.signals.locationDone):
        m.clearGetLocation()


def test_GetLocation_1(qtbot):
    m.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.assertNotEmitted(m.signals.locationDone):
            suc = m.getLocation()
            assert suc


def test_GetLocation_2(qtbot):
    m.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.waitSignal(m.signals.locationDone):
            suc = m.getLocation()
            assert not suc


def test_errorCalcTLE():
    m.errorCalcTLE('test')


def test_clearCalcTLE_1(qtbot):
    with qtbot.waitSignal(m.signals.calcTLEdone):
        m.clearCalcTLE()


def test_CalcTLE_1(qtbot):
    m.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.assertNotEmitted(m.signals.calcTLEdone):
            suc = m.calcTLE()
            assert suc


def test_CalcTLE_2(qtbot):
    m.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.waitSignal(m.signals.calcTLEdone):
            suc = m.calcTLE()
            assert not suc


def test_errorStatTLE():
    m.errorStatTLE('test')


def test_clearStatTLE_1(qtbot):
    with qtbot.waitSignal(m.signals.statTLEdone):
        m.clearStatTLE()


def test_StatTLE_1(qtbot):
    m.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.assertNotEmitted(m.signals.statTLEdone):
            suc = m.statTLE()
            assert suc


def test_StatTLE_2(qtbot):
    m.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.waitSignal(m.signals.statTLEdone):
            suc = m.statTLE()
            assert not suc


def test_errorGetTLE():
    m.errorGetTLE('test')


def test_clearGetTLE_1(qtbot):
    with qtbot.waitSignal(m.signals.getTLEdone):
        m.clearGetTLE()


def test_GetTLE_1(qtbot):
    m.mountUp = True
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.assertNotEmitted(m.signals.getTLEdone):
            suc = m.getTLE()
            assert suc


def test_GetTLE_2(qtbot):
    m.mountUp = False
    with mock.patch.object(QThreadPool,
                           'start'):
        with qtbot.waitSignal(m.signals.getTLEdone):
            suc = m.getTLE()
            assert not suc


def test_bootMount_1():

    m._MAC = None
    with mock.patch.object(wakeonlan,
                           'send_magic_packet'):
        suc = m.bootMount()
        assert not suc


def test_bootMount_2():

    m._MAC = '00:00:00:00:00:00'
    with mock.patch.object(wakeonlan,
                           'send_magic_packet'):
        suc = m.bootMount()
        assert suc


def test_shutdown_1():
    m.mountUp = True
    with mock.patch.object(m.obsSite,
                           'shutdown',
                           return_value=True):
        suc = m.shutdown()
        assert suc
        assert not m.mountUp


def test_shutdown_2():
    m.mountUp = True
    with mock.patch.object(m.obsSite,
                           'shutdown',
                           return_value=False):
        suc = m.shutdown()
        assert not suc
        assert m.mountUp
