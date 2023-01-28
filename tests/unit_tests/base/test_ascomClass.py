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
import platform
import builtins
import pytest

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)

# external packages
import PyQt5
from PyQt5.QtCore import QThreadPool, QTimer
import win32com.client

# local import
from base.ascomClass import AscomClass
import base.ascomClass
from base.loggerMW import setupLogging
from base.driverDataClass import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():

    with mock.patch.object(QTimer,
                           'start'):
        func = AscomClass(app=App(), data={})
        func.signals = Signals()
        yield func


def test_startTimer(function):
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        suc = function.startTimer()
        assert suc


def test_stopTimer(function):
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'stop'):
        suc = function.stopTimer()
        assert suc


def test_getAscomProperty_1(function):
    function.propertyExceptions = ['Connected']
    val = function.getAscomProperty('Connected')
    assert val is None


def test_getAscomProperty_2(function):
    function.propertyExceptions = ['test']
    with mock.patch.object(base.ascomClass,
                           'eval',
                           side_effect=Exception):
        val = function.getAscomProperty('Connected')
        assert val is None
        assert 'Connected' in function.propertyExceptions


def test_getAscomProperty_3(function):
    class Client:
        connect = True

    function.client = Client()
    function.propertyExceptions = ['test']
    with mock.patch.object(base.ascomClass,
                           'eval',
                           return_value='1'):
        val = function.getAscomProperty('Connected')
        assert val


def test_getAscomProperty_4(function):
    class Client:
        connect = True
        imagearray = None

    function.client = Client()
    function.propertyExceptions = ['test']
    with mock.patch.object(base.ascomClass,
                           'eval',
                           return_value='1'):
        val = function.getAscomProperty('ImageArray')
        assert val


def test_setAscomProperty_1(function):
    function.propertyExceptions = ['Connected']
    suc = function.setAscomProperty('Connected', True)
    assert not suc


def test_setAscomProperty_2(function):
    function.propertyExceptions = ['test']
    with mock.patch.object(base.ascomClass,
                           'exec',
                           side_effect=Exception):
        suc = function.setAscomProperty('Connected', True)
        assert not suc
        assert 'Connect' not in function.propertyExceptions


def test_setAscomProperty_3(function):
    function.propertyExceptions = ['test']
    with mock.patch.object(base.ascomClass,
                           'exec',
                           side_effect=Exception):
        suc = function.setAscomProperty('Names', True)
        assert not suc
        assert 'Names' in function.propertyExceptions


def test_setAscomProperty_4(function):
    class Client:
        Connect = False

    function.client = Client()
    function.propertyExceptions = ['test']
    suc = function.setAscomProperty('Connected', True)
    assert suc
    assert function.client


def test_callAscomMethod_1(function):
    function.propertyExceptions = ['Connected']
    suc = function.callAscomMethod('Connected', True)
    assert not suc


def test_callAscomMethod_2(function):
    function.propertyExceptions = ['Test']
    with mock.patch.object(base.ascomClass,
                           'exec',
                           side_effect=Exception):
        suc = function.callAscomMethod('Connected', True)
        assert not suc
        assert 'Connected' in function.propertyExceptions


def test_callAscomMethod_3(function):
    class Client:
        Connect = False

    function.client = Client()
    function.propertyExceptions = ['Test']
    with mock.patch.object(base.ascomClass,
                           'exec'):
        suc = function.callAscomMethod('Connected', True)
        assert suc
        assert function.client


def test_getAndStoreAscomProperty(function):
    with mock.patch.object(function,
                           'getAscomProperty'):
        with mock.patch.object(function,
                               'storePropertyToData'):
            suc = function.getAndStoreAscomProperty(10, 'YES', 'NO')
            assert suc


def test_workerConnectDevice_1(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(base.ascomClass,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'setAscomProperty'):
            with mock.patch.object(function,
                                   'getAscomProperty',
                                   return_value=False):
                suc = function.workerConnectDevice()
                assert not suc
                assert not function.serverConnected
                assert not function.deviceConnected


def test_workerConnectDevice_2(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(base.ascomClass,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'setAscomProperty'):
            with mock.patch.object(function,
                                   'getAscomProperty',
                                   return_value=True):
                suc = function.workerConnectDevice()
                assert suc
                assert function.serverConnected
                assert function.deviceConnected


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(function,
                           'getAndStoreAscomProperty',
                           return_value='test'):
        suc = function.workerGetInitialConfig()
        assert suc


def test_pollStatus_1(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=False):
        suc = function.workerPollStatus()
        assert not suc
        assert not function.deviceConnected


def test_pollStatus_2(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=True):
        suc = function.workerPollStatus()
        assert suc
        assert function.deviceConnected


def test_callerInitUnInit_1(function):
    def test():
        return 1
    result = function.callerInitUnInit(test)
    assert result == 1


def test_callMethodThreaded_1(function):
    def test():
        return

    function.deviceConnected = False
    suc = function.callMethodThreaded(test)
    assert not suc


def test_callMethodThreaded_2(function):
    def test():
        return

    function.deviceConnected = True
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.callMethodThreaded(test, cb_fin=test, cb_res=test)
        assert suc


def test_callMethodThreaded_3(function):
    def test():
        return

    function.deviceConnected = True
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.callMethodThreaded(test, 10, 20, cb_fin=test, cb_res=test)
        assert suc


def test_callMethodThreaded_4(function):
    def test():
        return

    function.deviceConnected = True
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.callMethodThreaded(test, 10, 20)
        assert suc


def test_processPolledData(function):
    function.processPolledData()


def test_workerPollData(function):
    function.workerPollData()


def test_pollData(function):
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.pollData()
        assert suc


def test_pollStatus(function):
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.pollStatus()
        assert suc


def test_getInitialConfig(function):
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.getInitialConfig()
        assert suc


def test_startCommunication_1(function):
    function.deviceName = 'test'
    with mock.patch.object(function.threadPool,
                           'start'):
        with mock.patch.object(win32com.client.dynamic,
                               'Dispatch'):
            suc = function.startCommunication()
            assert suc


def test_startCommunication_2(function):
    function.deviceName = 'test'
    with mock.patch.object(win32com.client.dynamic,
                           'Dispatch',
                           side_effect=Exception()):
        suc = function.startCommunication()
        assert not suc


def test_startCommunication_3(function):
    suc = function.startCommunication()
    assert not suc


def test_stopCommunication_1(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = 'test'
    with mock.patch.object(function,
                           'stopTimer'):
        with mock.patch.object(function,
                               'setAscomProperty'):
            suc = function.stopCommunication()
            assert suc


def test_stopCommunication_2(function):
    function.client = 1
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = 'test'
    with mock.patch.object(function,
                           'stopTimer'):
        with mock.patch.object(function,
                               'setAscomProperty'):
            suc = function.stopCommunication()
            assert suc
            assert not function.serverConnected
            assert not function.deviceConnected
