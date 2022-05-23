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
from unittest.mock import patch

# external packages
import PyQt5
import pytest
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
import requests

# local import
import base.alpacaClass
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.alpacaClass import AlpacaClass
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
        app = AlpacaClass(app=Test(), data={}, threadPool=QThreadPool())
        app.signals = Signals()
        yield
        app.threadPool.waitForDone(1000)


def test_properties_1():
    app.host = ('localhost', 11111)
    app.hostaddress = 'localhost'
    app.port = 11111
    app.deviceName = 'test'
    app.deviceName = 'test:2'
    app.apiVersion = 1
    app.protocol = 1


def test_properties_2():
    host = app.host
    assert host == ('localhost', 11111)
    assert app.hostaddress == 'localhost'
    assert app.port == 11111
    assert app.deviceName == ''
    assert app.apiVersion == 1
    assert app.protocol == 'http'


def test_properties_3():
    app.deviceName = 'test:camera:3'
    assert app.deviceName == 'test:camera:3'
    assert app.deviceType == 'camera'
    assert app.number == 3


def test_baseUrl_1():
    app.deviceName = 'test:camera:3'
    val = app.generateBaseUrl()
    assert val == 'http://localhost:11111/api/v1/camera/3'


def test_discoverAPIVersion_1():
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception()):
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_2():
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout):
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_3():
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError):
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_4():
    class Test:
        status_code = 400
        text = 'test'

    app.deviceName = 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_5():
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
        val = app.discoverAPIVersion()
        assert val is None


def test_discoverAPIVersion_6():
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
        val = app.discoverAPIVersion()
        assert val == 'test'


def test_discoverAlpacaDevices_1():
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception):
        val = app.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_2():
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout):
        val = app.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_3():
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError):
        val = app.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_4():
    class Test:
        status_code = 400
        text = 'test'

    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_5():
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
        val = app.discoverAlpacaDevices()
        assert val is None


def test_discoverAlpacaDevices_6():
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
        val = app.discoverAlpacaDevices()
        assert val == 'test'


def test_getAlpacaProperty_1():
    val = app.getAlpacaProperty('')
    assert val is None


def test_getAlpacaProperty_3():
    app.deviceName = 'test'
    app.propertyExceptions = ['test']
    val = app.getAlpacaProperty('test')
    assert val is None


def test_getAlpacaProperty_4():
    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout):
        val = app.getAlpacaProperty('test')
        assert val is None


def test_getAlpacaProperty_5():
    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError):
        val = app.getAlpacaProperty('test')
        assert val is None


def test_getAlpacaProperty_6():
    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception):
        val = app.getAlpacaProperty('test')
        assert val is None


def test_getAlpacaProperty_7():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.getAlpacaProperty('test')
        assert val is None


def test_getAlpacaProperty_8():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg'}

    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.getAlpacaProperty('test')
        assert val is None
        assert 'test' in app.propertyExceptions


def test_getAlpacaProperty_9():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.getAlpacaProperty('test')
        assert val == 'test'


def test_setAlpacaProperty_1():
    val = app.setAlpacaProperty('')
    assert val is None


def test_setAlpacaProperty_3():
    app.deviceName = 'test'
    app.propertyExceptions = ['test']
    val = app.setAlpacaProperty('test')
    assert val is None


def test_setAlpacaProperty_4():
    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           side_effect=requests.exceptions.Timeout):
        val = app.setAlpacaProperty('test')
        assert val is None


def test_setAlpacaProperty_5():
    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           side_effect=requests.exceptions.ConnectionError):
        val = app.setAlpacaProperty('test')
        assert val is None


def test_setAlpacaProperty_6():
    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           side_effect=Exception):
        val = app.setAlpacaProperty('test')
        assert val is None


def test_setAlpacaProperty_7():
    class Test:
        status_code = 400
        text = 'test'
    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           return_value=Test()):
        val = app.setAlpacaProperty('test')
        assert val is None


def test_setAlpacaProperty_8():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 1,
                    'ErrorMessage': 'msg'}

    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           return_value=Test()):
        val = app.setAlpacaProperty('test')
        assert val is None
        assert 'test' in app.propertyExceptions


def test_setAlpacaProperty_9():
    class Test:
        status_code = 200
        text = 'test'

        @staticmethod
        def json():
            return {'ErrorNumber': 0,
                    'ErrorMessage': 'msg',
                    'Value': 'test'}

    app.deviceName = 'test'
    with mock.patch.object(requests,
                           'put',
                           return_value=Test()):
        val = app.setAlpacaProperty('test')
        assert val == {'ErrorNumber': 0,
                       'ErrorMessage': 'msg',
                       'Value': 'test'}


def test_getAndStoreAlpacaProperty():
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.getAndStoreAlpacaProperty(10, 'YES', 'NO')
            assert suc


def test_workerConnectDevice_1():
    app.serverConnected = False
    app.deviceConnected = False
    with mock.patch.object(base.alpacaClass,
                           'sleepAndEvents'):
        with mock.patch.object(app,
                               'setAlpacaProperty'):
            with mock.patch.object(app,
                                   'getAlpacaProperty',
                                   return_value=False):
                suc = app.workerConnectDevice()
                assert not suc
                assert not app.serverConnected
                assert not app.deviceConnected


def test_workerConnectDevice_2():
    app.serverConnected = False
    app.deviceConnected = False
    with mock.patch.object(base.alpacaClass,
                           'sleepAndEvents'):
        with mock.patch.object(app,
                               'setAlpacaProperty'):
            with mock.patch.object(app,
                                   'getAlpacaProperty',
                                   return_value=True):
                suc = app.workerConnectDevice()
                assert suc
                assert app.serverConnected
                assert app.deviceConnected


def test_startTimer():
    suc = app.startTimer()
    assert suc


def test_stopTimer():
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'stop'):
        suc = app.stopTimer()
        assert suc


def test_workerGetInitialConfig_1():
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value='test'):
        suc = app.workerGetInitialConfig()
        assert suc
        assert app.data['DRIVER_INFO.DRIVER_NAME'] == 'test'
        assert app.data['DRIVER_INFO.DRIVER_VERSION'] == 'test'
        assert app.data['DRIVER_INFO.DRIVER_EXEC'] == 'test'


def test_workerPollStatus_1():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=False):
        suc = app.workerPollStatus()
        assert not suc
        assert not app.deviceConnected


def test_workerPollStatus_2():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=True):
        suc = app.workerPollStatus()
        assert suc
        assert app.deviceConnected


def test_processPolledData():
    app.processPolledData()


def test_workerPollData():
    app.workerPollData()


def test_pollData_1():
    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.pollData()
        assert suc


def test_pollData_2():
    app.deviceConnected = False
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.pollData()
        assert not suc


def test_pollStatus_1():
    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.pollStatus()
        assert suc


def test_pollStatus_2():
    app.deviceConnected = False
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.pollStatus()
        assert not suc


def test_getInitialConfig_1():
    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.getInitialConfig()
        assert suc


def test_getInitialConfig_2():
    app.deviceConnected = False
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.getInitialConfig()
        assert not suc


def test_startCommunication():
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.startCommunication()
        assert suc


def test_stopCommunication_1():
    app.deviceConnected = True
    app.serverConnected = True
    app.deviceName = 'test'
    with mock.patch.object(app,
                           'stopTimer'):
        with mock.patch.object(app,
                               'setAlpacaProperty'):
            suc = app.stopCommunication()
            assert suc
            assert not app.serverConnected
            assert not app.deviceConnected


def test_discoverDevices_1():
    with mock.patch.object(app,
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
        val = app.discoverDevices('dome')
        assert val == ['test:dome:1', 'test1:dome:3']


def test_discoverDevices_2():
    with mock.patch.object(app,
                           'discoverAlpacaDevices',
                           return_value=[]):
        val = app.discoverDevices('dome')
        assert val == []
