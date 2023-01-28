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
from PyQt5.QtCore import QThreadPool, QTimer
import requests

# local import
import base.alpacaClass
from base.alpacaClass import AlpacaClass
from base.loggerMW import setupLogging
from base.driverDataClass import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():

    with mock.patch.object(QTimer,
                           'start'):
        func = AlpacaClass(app=App(), data={})
        func.signals = Signals()
        yield func


def test_properties_1(function):
    function.host = ('localhost', 11111)
    function.hostaddress = 'localhost'
    function.port = 11111
    function.deviceName = 'test'
    function.deviceName = 'test:2'
    function.apiVersion = 1
    function.protocol = 1


def test_properties_2(function):
    host = function.host
    assert host == ('localhost', 11111)
    assert function.hostaddress == 'localhost'
    assert function.port == 11111
    assert function.deviceName == ''
    assert function.apiVersion == 1
    assert function.protocol == 'http'


def test_properties_3(function):
    function.deviceName = 'test:camera:3'
    assert function.deviceName == 'test:camera:3'
    assert function.deviceType == 'camera'
    assert function.number == 3


def test_baseUrl_1(function):
    function.deviceName = 'test:camera:3'
    val = function.generateBaseUrl()
    assert val == 'http://localhost:11111/api/v1/camera/3'


def test_discoverAPIVersion_1(function):
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception()):
        val = function.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_2(function):
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout):
        val = function.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_3(function):
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError):
        val = function.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_4(function):
    class Test:
        status_code = 400
        text = 'test'

    function.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_5(function):
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_6(function):
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.discoverAPIVersion()
        assert val == 'test'


def test_discoverAlpacaDevices_1(function):
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception):
        val = function.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_2(function):
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout):
        val = function.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_3(function):
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError):
        val = function.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_4(function):
    class Test:
        status_code = 400
        text = 'test'

    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_5(function):
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_6(function):
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.discoverAlpacaDevices()
        assert val == 'test'


def test_getAlpacaProperty_1(function):
    val = function.getAlpacaProperty('')
    assert val is None


def test_getAlpacaProperty_3(function):
    function.deviceName = 'test'
    function.propertyExceptions = ['test']
    val = function.getAlpacaProperty('test')
    assert val is None


def test_getAlpacaProperty_4(function):
    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout):
        val = function.getAlpacaProperty('test')
        assert val is None


def test_getAlpacaProperty_5(function):
    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError):
        val = function.getAlpacaProperty('test')
        assert val is None


def test_getAlpacaProperty_6(function):
    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception):
        val = function.getAlpacaProperty('test')
        assert val is None


def test_getAlpacaProperty_7(function):
    class Test:
        status_code = 400
        text = 'test'
    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.getAlpacaProperty('test')
        assert val is None


def test_getAlpacaProperty_8(function):
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg'}

    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.getAlpacaProperty('test')
        assert val is None
        assert 'test' in function.propertyExceptions


def test_getAlpacaProperty_9(function):
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.getAlpacaProperty('test')
        assert val == 'test'


def test_getAlpacaProperty_10(function):
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'imagearray'}

    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.getAlpacaProperty('imagearray')
        assert val == 'imagearray'


def test_setAlpacaProperty_1(function):
    val = function.setAlpacaProperty('')
    assert val is None


def test_setAlpacaProperty_3(function):
    function.deviceName = 'test'
    function.propertyExceptions = ['test']
    val = function.setAlpacaProperty('test')
    assert val is None


def test_setAlpacaProperty_4(function):
    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           side_effect=requests.exceptions.Timeout):
        val = function.setAlpacaProperty('test')
        assert val is None


def test_setAlpacaProperty_5(function):
    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           side_effect=requests.exceptions.ConnectionError):
        val = function.setAlpacaProperty('test')
        assert val is None


def test_setAlpacaProperty_6(function):
    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           side_effect=Exception):
        val = function.setAlpacaProperty('test')
        assert val is None


def test_setAlpacaProperty_7(function):
    class Test:
        status_code = 400
        text = 'test'
    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           return_value=Test()):
        val = function.setAlpacaProperty('test')
        assert val is None


def test_setAlpacaProperty_8(function):
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg'}

    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           return_value=Test()):
        val = function.setAlpacaProperty('test')
        assert val is None
        assert 'test' in function.propertyExceptions


def test_setAlpacaProperty_9(function):
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    function.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           return_value=Test()):
        val = function.setAlpacaProperty('test')
        assert val == {'ErrorNumber': 0,
                       'ErrorMessage': 'msg',
                       'Value': 'test'}


def test_getAndStoreAlpacaProperty(function):
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        with mock.patch.object(function,
                               'storePropertyToData'):
            suc = function.getAndStoreAlpacaProperty(10, 'YES', 'NO')
            assert suc


def test_workerConnectDevice_1(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(base.alpacaClass,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
            with mock.patch.object(function,
                                   'getAlpacaProperty',
                                   return_value=False):
                suc = function.workerConnectDevice()
                assert not suc
                assert not function.serverConnected
                assert not function.deviceConnected


def test_workerConnectDevice_2(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(base.alpacaClass,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
            with mock.patch.object(function,
                                   'getAlpacaProperty',
                                   return_value=True):
                suc = function.workerConnectDevice()
                assert suc
                assert function.serverConnected
                assert function.deviceConnected


def test_startTimer(function):
    suc = function.startTimer()
    assert suc


def test_stopTimer(function):
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'stop'):
        suc = function.stopTimer()
        assert suc


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value='test'):
        suc = function.workerGetInitialConfig()
        assert suc
        assert function.data['DRIVER_INFO.DRIVER_NAME'] == 'test'
        assert function.data['DRIVER_INFO.DRIVER_VERSION'] == 'test'
        assert function.data['DRIVER_INFO.DRIVER_EXEC'] == 'test'


def test_workerPollStatus_1(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=False):
        suc = function.workerPollStatus()
        assert not suc
        assert not function.deviceConnected


def test_workerPollStatus_2(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=True):
        suc = function.workerPollStatus()
        assert suc
        assert function.deviceConnected


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


def test_pollStatus_1(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.pollStatus()
        assert suc


def test_pollStatus_2(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.pollStatus()
        assert not suc


def test_getInitialConfig_1(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.getInitialConfig()
        assert suc


def test_getInitialConfig_2(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.getInitialConfig()
        assert not suc


def test_startCommunication(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.startCommunication()
        assert suc


def test_stopCommunication_1(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = 'test'
    with mock.patch.object(function,
                           'stopTimer'):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
            suc = function.stopCommunication()
            assert suc
            assert not function.serverConnected
            assert not function.deviceConnected


def test_discoverDevices_1(function):
    with mock.patch.object(function,
                           'discoverAlpacaDevices',
                           return_value=[{'DeviceName': 'test',
                                          'DeviceNumber': 1,
                                          'DeviceType': 'Dome',
                                          },
                                         {'DeviceName': 'test1',
                                          'DeviceNumber': 3,
                                          'DeviceType': 'Dome',
                                          },
                                         ]):
        val = function.discoverDevices('dome')
        assert val == ['test:dome:1', 'test1:dome:3']


def test_discoverDevices_2(function):
    with mock.patch.object(function,
                           'discoverAlpacaDevices',
                           return_value=[]):
        val = function.discoverDevices('dome')
        assert val == []
