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
# written in python3, (c) 2019-2022 by mworion
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
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
import win32com.client

# local import
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.ascomClass import AscomClass
import base.ascomClass
from base.loggerMW import setupLogging
from base.driverDataClass import Signals

setupLogging()


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        message = pyqtSignal(str, int)
        messageN = pyqtSignal(object, object, object, object)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = AscomClass(app=Test(), data={}, threadPool=QThreadPool())
        app.signals = Signals()
        yield
        app.threadPool.waitForDone(1000)


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
    app.propertyExceptions = ['connect']
    val = app.getAscomProperty('Connect')
    assert val is None


def test_getAscomProperty_2():
    app.propertyExceptions = ['test']
    with mock.patch.object(builtins,
                           'eval',
                           side_effect=Exception):
        val = app.getAscomProperty('Connect')
        assert val is None
        assert 'connect' in app.propertyExceptions


def test_getAscomProperty_3():
    class Client:
        connect = True

    app.client = Client()
    app.propertyExceptions = ['test']
    val = app.getAscomProperty('Connect')
    assert val


def test_setAscomProperty_1():
    app.propertyExceptions = ['connect']
    suc = app.setAscomProperty('Connect', True)
    assert not suc


def test_setAscomProperty_2():
    app.propertyExceptions = ['test']
    with mock.patch.object(builtins,
                           'exec',
                           side_effect=Exception):
        suc = app.setAscomProperty('Connect', True)
        assert not suc
        assert 'Connect' not in app.propertyExceptions


def test_setAscomProperty_3():
    app.propertyExceptions = ['test']
    with mock.patch.object(builtins,
                           'exec',
                           side_effect=Exception):
        suc = app.setAscomProperty('Names', True)
        assert not suc
        assert 'names' in app.propertyExceptions


def test_setAscomProperty_4():
    class Client:
        Connect = False

    app.client = Client()
    app.propertyExceptions = ['test']
    suc = app.setAscomProperty('Connect', True)
    assert suc
    assert app.client


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


def test_getAndStoreAscomProperty():
    with mock.patch.object(app,
                           'getAscomProperty'):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.getAndStoreAscomProperty(10, 'YES', 'NO')
            assert suc


def test_workerConnectDevice_1():
    app.serverConnected = False
    app.deviceConnected = False
    with mock.patch.object(base.ascomClass,
                           'sleepAndEvents'):
        with mock.patch.object(app,
                               'setAscomProperty'):
            with mock.patch.object(app,
                                   'getAscomProperty',
                                   return_value=False):
                suc = app.workerConnectDevice()
                assert not suc
                assert not app.serverConnected
                assert not app.deviceConnected


def test_workerConnectDevice_2():
    app.serverConnected = False
    app.deviceConnected = False
    with mock.patch.object(base.ascomClass,
                           'sleepAndEvents'):
        with mock.patch.object(app,
                               'setAscomProperty'):
            with mock.patch.object(app,
                                   'getAscomProperty',
                                   return_value=True):
                suc = app.workerConnectDevice()
                assert suc
                assert app.serverConnected
                assert app.deviceConnected


def test_workerGetInitialConfig_1():
    with mock.patch.object(app,
                           'getAndStoreAscomProperty',
                           return_value='test'):
        suc = app.workerGetInitialConfig()
        assert suc


def test_pollStatus_1():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=False):
        suc = app.workerPollStatus()
        assert not suc
        assert not app.deviceConnected


def test_pollStatus_2():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=True):
        suc = app.workerPollStatus()
        assert suc
        assert app.deviceConnected


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

    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.callMethodThreaded(test, cb_fin=test, cb_res=test)
        assert suc


def test_callMethodThreaded_3():
    def test():
        return

    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.callMethodThreaded(test, 10, 20, cb_fin=test, cb_res=test)
        assert suc


def test_callMethodThreaded_4():
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
    with mock.patch.object(app.threadPool,
                           'start'):
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
    app.deviceConnected = True
    app.serverConnected = True
    app.deviceName = 'test'
    with mock.patch.object(app,
                           'stopTimer'):
        with mock.patch.object(app,
                               'setAscomProperty'):
            suc = app.stopCommunication()
            assert suc


def test_stopCommunication_2():
    app.client = 1
    app.deviceConnected = True
    app.serverConnected = True
    app.deviceName = 'test'
    with mock.patch.object(app,
                           'stopTimer'):
        with mock.patch.object(app,
                               'setAscomProperty'):
            suc = app.stopCommunication()
            assert suc
            assert not app.serverConnected
            assert not app.deviceConnected
