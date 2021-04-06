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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import platform

# external packages
import PyQt5
import pytest
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
if platform.system() == 'Windows':
    import win32com.client
    import pythoncom

# local import
from base.ascomClass import AscomClass


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = AscomClass(app=Test(), data={}, threadPool=QThreadPool())

    yield

    app.threadPool.waitForDone(1000)


def test_connectClient():
    class Test:
        connected = False

    app.client = Test()
    app.connectClient()


def test_disconnectClient():
    class Test:
        connected = False

    app.client = Test()
    app.disconnectClient()


def test_isClientConnected():
    class Test:
        connected = False

    app.client = Test()
    app.isClientConnected()


def test_getInitialConfig_1():
    class Test:
        connected = False
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    app.serverConnected = False
    app.deviceConnected = False
    app.client = Test()
    suc = app.getInitialConfig()
    assert suc
    assert app.serverConnected
    assert app.deviceConnected
    assert app.data['DRIVER_INFO.DRIVER_NAME'] == 'test'
    assert app.data['DRIVER_INFO.DRIVER_VERSION'] == '1'
    assert app.data['DRIVER_INFO.DRIVER_EXEC'] == 'test1'


def test_getInitialConfig_2():
    class Test:
        connected = False
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    app.serverConnected = False
    app.deviceConnected = False
    app.client = Test()
    with mock.patch.object(app,
                           'connectClient',
                           side_effect=Exception):
        suc = app.getInitialConfig()
        assert not suc


def test_startTimer():
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        suc = app.startTimer()
        assert suc


def test_stopTimer():
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'stop'):
        suc = app.stopTimer()
        assert suc


def test_dataEntry_1():
    app.data = {'YES': 0}

    res = app.dataEntry(None, 'YES')
    assert res
    assert 'YES' not in app.data


def test_dataEntry_2():
    app.data = {'YES': 0,
                'NO': 0}

    res = app.dataEntry(None, 'YES', 'NO')
    assert res
    assert 'YES' not in app.data
    assert 'NO' not in app.data


def test_dataEntry_3():
    app.data = {'YES': 0,
                'NO': 0}

    res = app.dataEntry(10, 'YES', 'NO')
    assert not res
    assert 'YES' in app.data
    assert 'NO' in app.data


def test_pollStatus_1():
    class Test:
        connected = False
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    app.serverConnected = False
    app.deviceConnected = False
    app.client = Test()

    suc = app.pollStatusWorker()
    assert not suc
    assert not app.deviceConnected


def test_pollStatus_2():
    class Test:
        connected = False
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    app.serverConnected = False
    app.deviceConnected = True
    app.client = Test()

    suc = app.pollStatusWorker()
    assert not suc
    assert not app.deviceConnected


def test_pollStatus_3():
    class Test:
        connected = True
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    app.serverConnected = False
    app.deviceConnected = False
    app.client = Test()

    suc = app.pollStatusWorker()
    assert suc
    assert app.deviceConnected


def test_pollStatus_4():
    class Test:
        connected = True
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    app.serverConnected = False
    app.deviceConnected = False
    app.client = Test()
    with mock.patch.object(app,
                           'isClientConnected',
                           side_effect=Exception()):
        suc = app.pollStatusWorker()
        assert not suc


def test_callMethodThreaded_1():
    def test():
        return

    app.deviceConnected = False
    suc = app.callMethodThreaded(test)
    assert not suc


def test_callMethodThreaded_2():
    def test():
        return

    app.deviceConnected = True
    suc = app.callMethodThreaded(test)
    assert suc


def test_processPolledData():
    app.processPolledData()


def test_workerPollData():
    app.workerPollData()


def test_pollData_1():
    app.deviceConnected = False
    suc = app.pollData()
    assert not suc


def test_pollData_2():
    app.deviceConnected = True
    suc = app.pollData()
    assert suc


def test_startPollStatus():
    suc = app.pollStatus()
    assert suc


def test_startCommunication_1():
    if platform.system() != 'Windows':
        return

    app.deviceName = 'test'
    with mock.patch.object(app,
                           'startTimer'):
        with mock.patch.object(pythoncom,
                               'CoInitialize'):
            with mock.patch.object(win32com.client.dynamic,
                                   'Dispatch'):
                suc = app.startCommunication()
                assert suc


def test_startCommunication_2():
    if platform.system() != 'Windows':
        return

    app.deviceName = 'test'
    with mock.patch.object(app,
                           'startTimer'):
        with mock.patch.object(pythoncom,
                               'CoInitialize'):
            with mock.patch.object(win32com.client.dynamic,
                                   'Dispatch',
                                   side_effect=Exception()):
                suc = app.startCommunication()
                assert not suc


def test_startCommunication_3():
    if platform.system() != 'Windows':
        return

    suc = app.startCommunication()
    assert not suc


def test_stopCommunication_1():
    if platform.system() != 'Windows':
        return

    app.deviceConnected = True
    app.serverConnected = True
    app.deviceName = 'test'
    with mock.patch.object(app,
                           'stopTimer'):
        with mock.patch.object(pythoncom,
                               'CoUninitialize'):
            suc = app.stopCommunication()
            assert suc
            assert not app.serverConnected
            assert not app.deviceConnected


def test_stopCommunication_2():
    if platform.system() != 'Windows':
        return

    app.deviceConnected = True
    app.serverConnected = True
    app.deviceName = 'test'
    app.client = 'test'
    with mock.patch.object(app,
                           'disconnectClient',
                           side_effect=Exception()):
        with mock.patch.object(app,
                               'stopTimer'):
            with mock.patch.object(pythoncom,
                               'CoUninitialize'):
                suc = app.stopCommunication()
                assert suc
                assert not app.serverConnected
                assert not app.deviceConnected
