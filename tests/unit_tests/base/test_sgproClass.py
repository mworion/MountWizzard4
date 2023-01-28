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

# external packages
import PyQt5
import pytest
from PyQt5.QtCore import QTimer
import requests

# local import
from base.sgproClass import SGProClass
from base.loggerMW import setupLogging
from base.driverDataClass import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    with mock.patch.object(QTimer,
                           'start'):
        func = SGProClass(app=App(), data={})
        func.signals = Signals()
        yield func


def test_properties_1(function):
    function.deviceName = 'test'
    function.deviceName = 'test:2'


def test_requestProperty_1(function):
    function.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'post',
                           return_value=Response()):
        val = function.requestProperty('test', {'test': 1})
        assert val is 'test'


def test_requestProperty_2(function):
    function.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Response()):
        val = function.requestProperty('test')
        assert val is 'test'


def test_requestProperty_3(function):
    function.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout,
                           return_value=Response()):
        val = function.requestProperty('test')
        assert val is None


def test_requestProperty_4(function):
    function.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError,
                           return_value=Response()):
        val = function.requestProperty('test')
        assert val is None


def test_requestProperty_5(function):
    function.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception,
                           return_value=Response()):
        val = function.requestProperty('test')
        assert val is None


def test_requestProperty_6(function):
    function.deviceName = 'test'

    class Response:
        status_code = 400

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Response()):
        val = function.requestProperty('test')
        assert val is None


def test_sgConnectDevice_1(function):
    function.deviceName = 'test test'
    function.DEVICE_TYPE = 'Camera'
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc = function.sgConnectDevice()
        assert not suc


def test_sgConnectDevice_2(function):
    function.deviceName = 'test test'
    function.DEVICE_TYPE = 'Camera'
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = function.sgConnectDevice()
        assert suc


def test_sgDisconnectDevice_1(function):
    function.deviceName = 'test test'
    function.DEVICE_TYPE = 'Camera'
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc = function.sgDisconnectDevice()
        assert not suc


def test_sgDisconnectDevice_2(function):
    function.deviceName = 'test test'
    function.DEVICE_TYPE = 'Camera'
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = function.sgDisconnectDevice()
        assert suc


def test_sgEnumerateDevice_1(function):
    function.deviceName = 'test test'
    function.DEVICE_TYPE = 'Camera'
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc = function.sgEnumerateDevice()
        assert not suc


def test_sgEnumerateDevice_2(function):
    function.deviceName = 'test test'
    function.DEVICE_TYPE = 'Camera'
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Devices': True}):
        suc = function.sgEnumerateDevice()
        assert suc


def test_workerConnectDevice_1(function):
    function.deviceName = 'SGPro controlled'
    suc = function.workerConnectDevice()
    assert suc


def test_workerConnectDevice_2(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(function,
                           'sgConnectDevice',
                           return_value=True):
        suc = function.workerConnectDevice()
        assert suc
        assert not function.serverConnected
        assert not function.deviceConnected


def test_workerConnectDevice_3(function):
    function.serverConnected = True
    function.deviceConnected = True
    with mock.patch.object(function,
                           'sgConnectDevice',
                           return_value=False):
        suc = function.workerConnectDevice()
        assert not suc
        assert not function.serverConnected
        assert not function.deviceConnected


def test_startTimer(function):
    suc = function.startTimer()
    assert suc


def test_stopTimer(function):
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'stop'):
        suc = function.stopTimer()
        assert suc


def test_processPolledData(function):
    function.processPolledData()


def test_workerPollData(function):
    function.workerPollData()


def test_pollData_1(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.pollData()
        assert suc


def test_pollData_2(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.pollData()
        assert not suc


def test_workerGetInitialConfig_1(function):
    function.workerGetInitialConfig()


def test_getInitialConfig_1(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.getInitialConfig()
        assert suc


def test_workerPollStatus_1(function):
    function.DEVICE_TYPE = 'Camera'
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        with mock.patch.object(function,
                               'storePropertyToData'):
            suc = function.workerPollStatus()
            assert not suc


def test_workerPollStatus_2(function):
    function.DEVICE_TYPE = 'Camera'

    function.deviceConnected = True
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'State': 'DISCONNECTED',
                                         'Message': 'test'}):
        with mock.patch.object(function,
                               'storePropertyToData'):
            with mock.patch.object(function,
                                   'getInitialConfig'):
                suc = function.workerPollStatus()
                assert suc
                assert not function.deviceConnected


def test_workerPollStatus_3(function):
    function.DEVICE_TYPE = 'Camera'
    function.deviceConnected = False
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'State': 'DISCONNECTED',
                                         'Message': 'test'}):
        with mock.patch.object(function,
                               'storePropertyToData'):
            with mock.patch.object(function,
                                   'getInitialConfig'):
                suc = function.workerPollStatus()
                assert suc
                assert not function.deviceConnected


def test_workerPollStatus_4(function):
    function.DEVICE_TYPE = 'Camera'
    function.deviceConnected = True
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'State': 'test',
                                         'Message': 'test'}):
        with mock.patch.object(function,
                               'storePropertyToData'):
            with mock.patch.object(function,
                                   'getInitialConfig'):
                suc = function.workerPollStatus()
                assert suc
                assert function.deviceConnected


def test_workerPollStatus_5(function):
    function.DEVICE_TYPE = 'Camera'
    function.deviceConnected = False
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'State': 'test',
                                         'Message': 'test'}):
        with mock.patch.object(function,
                               'storePropertyToData'):
            with mock.patch.object(function,
                                   'getInitialConfig'):
                suc = function.workerPollStatus()
                assert suc
                assert function.deviceConnected


def test_pollStatus_1(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.pollStatus()
        assert suc


def test_startCommunication_1(function):
    function.serverConnected = False
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.startCommunication()
        assert suc
        assert function.serverConnected


def test_stopCommunication_1(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = 'test'
    with mock.patch.object(function,
                           'stopTimer'):
        with mock.patch.object(function,
                               'sgDisconnectDevice'):
            suc = function.stopCommunication()
            assert suc
            assert not function.serverConnected
            assert not function.deviceConnected


def test_discoverDevices_1(function):
    with mock.patch.object(function,
                           'sgEnumerateDevice',
                           return_value=[]):
        val = function.discoverDevices()
        assert val == []


def test_discoverDevices_2(function):
    with mock.patch.object(function,
                           'sgEnumerateDevice',
                           return_value=['test']):
        val = function.discoverDevices()
        assert val == ['test']
