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
import builtins
import pytest

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)

# external packages
import PyQt5
from PyQt5.QtTest import QTest
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
import win32com.client

# local import
from base.ascomClass import AscomClass
from base.loggerMW import setupLogging

setupLogging()


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

    app.propertyExceptions = ['Connected']
    app.client = Test()
    app.connectClient()
    assert app.propertyExceptions == []


def test_disconnectClient():
    class Test:
        connected = False

    app.propertyExceptions = ['Connected']
    app.client = Test()
    app.disconnectClient()
    assert app.propertyExceptions == []


def test_isClientConnected():
    class Test:
        connected = False

    app.client = Test()
    app.isClientConnected()


def test_workerConnectAscomDevice_1():
    class Client:
        connected = False

    app.serverConnected = False
    app.deviceConnected = False
    app.client = Client()
    with mock.patch.object(QTest,
                           'qWait'):
        with mock.patch.object(app,
                               'connectClient',
                               side_effect=Exception):
            suc = app.workerConnectAscomDevice()
            assert not suc
            assert not app.serverConnected
            assert not app.deviceConnected


def test_workerConnectAscomDevice_2():
    class Client:
        connected = False

    app.serverConnected = False
    app.deviceConnected = False
    app.client = Client()
    with mock.patch.object(QTest,
                           'qWait'):
        suc = app.workerConnectAscomDevice()
        assert suc
        assert app.serverConnected
        assert app.deviceConnected


def test_getInitialConfig_1():
    class Test:
        connected = False
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    app.client = Test()
    suc = app.workerGetInitialConfig()
    assert suc
    assert app.data['DRIVER_INFO.DRIVER_NAME'] == 'test'
    assert app.data['DRIVER_INFO.DRIVER_VERSION'] == '1'
    assert app.data['DRIVER_INFO.DRIVER_EXEC'] == 'test1'


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


def test_getAscomProperty_1():
    app.propertyExceptions = ['Connect']
    val = app.getAscomProperty('Connect')
    assert val is None


def test_getAscomProperty_2():
    app.propertyExceptions = ['Test']
    with mock.patch.object(builtins,
                           'eval',
                           side_effect=Exception):
        val = app.getAscomProperty('Connect')
        assert val is None
        assert 'Connect' in app.propertyExceptions


def test_getAscomProperty_3():
    class Client:
        Connect = True

    app.client = Client()
    app.propertyExceptions = ['Test']
    val = app.getAscomProperty('Connect')
    assert val


def test_callAscomMethod_1():
    app.propertyExceptions = ['Connect']
    suc = app.callAscomMethod('Connect', True)
    assert not suc


def test_callAscomMethod_2():
    app.propertyExceptions = ['Test']
    with mock.patch.object(builtins,
                           'exec',
                           side_effect=Exception):
        suc = app.callAscomMethod('Connect', True)
        assert not suc
        assert 'Connect' in app.propertyExceptions


def test_callAscomMethod_3():
    class Client:
        Connect = False

    app.client = Client()
    app.propertyExceptions = ['Test']
    with mock.patch.object(app.client,
                           'Connect'):
        suc = app.callAscomMethod('Connect', True)
        assert suc
        assert app.client


def test_callAscomMethod_4():
    class Client:
        Connect = False

    app.client = Client()
    app.propertyExceptions = ['Test']
    with mock.patch.object(app.client,
                           'Connect'):
        suc = app.callAscomMethod('Connect', (True, 1))
        assert suc
        assert app.client


def test_setAscomProperty_1():
    app.propertyExceptions = ['Connect']
    suc = app.setAscomProperty('Connect', True)
    assert not suc


def test_setAscomProperty_2():
    app.propertyExceptions = ['Test']
    with mock.patch.object(builtins,
                           'exec',
                           side_effect=Exception):
        suc = app.setAscomProperty('Connect', True)
        assert not suc
        assert 'Connect' in app.propertyExceptions


def test_setAscomProperty_3():
    class Client:
        Connect = False

    app.client = Client()
    app.propertyExceptions = ['Test']
    suc = app.setAscomProperty('Connect', True)
    assert suc
    assert app.client


def test_storeAscomProperty_1():
    app.data = {'YES': 0}

    res = app.storePropertyToData(None, 'YES')
    assert not res
    assert 'YES' not in app.data


def test_storeAscomProperty_2():
    app.data = {'YES': 0,
                'NO': 0}

    res = app.storePropertyToData(None, 'YES', 'NO')
    assert not res
    assert 'YES' not in app.data
    assert 'NO' not in app.data


def test_storeAscomProperty_3():
    app.data = {'YES': 0,
                'NO': 0}

    res = app.storePropertyToData(10, 'YES', 'NO')
    assert res
    assert 'YES' in app.data
    assert 'NO' in app.data


def test_storeAscomProperty_4():
    app.data = {}

    res = app.storePropertyToData(10, 'YES', 'NO')
    assert res
    assert 'YES' in app.data
    assert 'NO' in app.data


def test_storeAscomProperty_5():
    app.data = {'NO': 0}

    res = app.storePropertyToData(None, 'YES', 'NO')
    assert not res
    assert 'YES' not in app.data
    assert 'NO' not in app.data


def test_getAndStoreAscomProperty():
    with mock.patch.object(app,
                           'getAscomProperty'):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.getAndStoreAscomProperty(10, 'YES', 'NO')
            assert suc


def test_pollStatus_1():
    class Test:
        connected = False
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    app.serverConnected = False
    app.deviceConnected = False
    app.client = Test()

    suc = app.workerPollStatus()
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

    suc = app.workerPollStatus()
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

    suc = app.workerPollStatus()
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
        suc = app.workerPollStatus()
        assert not suc


def test_callerInitUnInit_1():
    def test():
        return 1
    result = app.callerInitUnInit(test)
    assert result == 1


def test_callMethodThreaded_1():
    def test():
        return

    app.deviceConnected = False
    suc = app.callMethodThreaded(test)
    assert not suc


def test_callMethodThreaded_2():
    def test():
        return

    app.deviceConnected = False
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.callMethodThreaded(test, check=False)
        assert suc


def test_callMethodThreaded_3():
    def test():
        return

    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.callMethodThreaded(test, cb_fin=test, cb_res=test)
        assert suc


def test_callMethodThreaded_4():
    def test():
        return

    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.callMethodThreaded(test, 10, 20, cb_fin=test, cb_res=test)
        assert suc


def test_callMethodThreaded_5():
    def test():
        return

    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.callMethodThreaded(test, 10, 20)
        assert suc


def test_processPolledData():
    app.processPolledData()


def test_workerPollData():
    app.workerPollData()


def test_pollData():
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.pollData()
        assert suc


def test_pollStatus():
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.pollStatus()
        assert suc


def test_getInitialConfig():
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.getInitialConfig()
        assert suc


def test_startCommunication_1():
    app.deviceName = 'test'
    with mock.patch.object(app,
                           'callMethodThreaded'):
        with mock.patch.object(win32com.client.dynamic,
                               'Dispatch'):
            suc = app.startCommunication()
            assert suc


def test_startCommunication_2():
    app.deviceName = 'test'
    with mock.patch.object(win32com.client.dynamic,
                           'Dispatch',
                           side_effect=Exception()):
        suc = app.startCommunication()
        assert not suc


def test_startCommunication_3():
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
        suc = app.stopCommunication()
        assert suc
        assert not app.serverConnected
        assert not app.deviceConnected


def test_stopCommunication_2():
    app.deviceConnected = True
    app.serverConnected = True
    app.deviceName = 'test'
    app.client = 'test'
    with mock.patch.object(app,
                           'disconnectClient',
                           side_effect=Exception()):
        with mock.patch.object(app,
                               'stopTimer'):
            suc = app.stopCommunication()
            assert suc
            assert not app.serverConnected
            assert not app.deviceConnected


def test_stopCommunication_3():
    class Test:
        connected = False

    app.deviceConnected = True
    app.serverConnected = True
    app.deviceName = 'test'
    app.client = Test()
    with mock.patch.object(app,
                           'stopTimer'):
        suc = app.stopCommunication()
        assert suc
        assert not app.serverConnected
        assert not app.deviceConnected
