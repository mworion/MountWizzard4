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

# external packages
import PyQt5
import pytest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
import requests

# local import
from base.sgproClass import SGProClass
from base.loggerMW import setupLogging
from base.driverDataClass import Signals

setupLogging()


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = SGProClass(app=Test(), data={}, threadPool=QThreadPool())
        app.signals = Signals()
        yield
        app.threadPool.waitForDone(1000)


def test_properties_1():
    app.deviceName = 'test'
    app.deviceName = 'test:2'


def test_requestProperty_1():
    app.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'post',
                           return_value=Response()):
        val = app.requestProperty('test', {'test': 1})
        assert val is 'test'


def test_requestProperty_2():
    app.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Response()):
        val = app.requestProperty('test')
        assert val is 'test'


def test_requestProperty_3():
    app.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.Timeout,
                           return_value=Response()):
        val = app.requestProperty('test')
        assert val is None


def test_requestProperty_4():
    app.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           side_effect=requests.exceptions.ConnectionError,
                           return_value=Response()):
        val = app.requestProperty('test')
        assert val is None


def test_requestProperty_5():
    app.deviceName = 'test'

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception,
                           return_value=Response()):
        val = app.requestProperty('test')
        assert val is None


def test_requestProperty_6():
    app.deviceName = 'test'

    class Response:
        status_code = 400

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Response()):
        val = app.requestProperty('test')
        assert val is None


def test_sgConnectDevice_1():
    app.deviceName = 'test test'
    app.DEVICE_TYPE = 'Camera'
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc = app.sgConnectDevice()
        assert not suc


def test_sgConnectDevice_2():
    app.deviceName = 'test test'
    app.DEVICE_TYPE = 'Camera'
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = app.sgConnectDevice()
        assert suc


def test_sgDisconnectDevice_1():
    app.deviceName = 'test test'
    app.DEVICE_TYPE = 'Camera'
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc = app.sgDisconnectDevice()
        assert not suc


def test_sgDisconnectDevice_2():
    app.deviceName = 'test test'
    app.DEVICE_TYPE = 'Camera'
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = app.sgDisconnectDevice()
        assert suc


def test_sgEnumerateDevice_1():
    app.deviceName = 'test test'
    app.DEVICE_TYPE = 'Camera'
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc = app.sgEnumerateDevice()
        assert not suc


def test_sgEnumerateDevice_2():
    app.deviceName = 'test test'
    app.DEVICE_TYPE = 'Camera'
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Devices': True}):
        suc = app.sgEnumerateDevice()
        assert suc


def test_workerConnectDevice_1():
    app.deviceName = 'Remote defined'
    suc = app.workerConnectDevice()
    assert suc


def test_workerConnectDevice_2():
    app.serverConnected = False
    app.deviceConnected = False
    with mock.patch.object(app,
                           'sgConnectDevice',
                           return_value=True):
        suc = app.workerConnectDevice()
        assert suc
        assert not app.serverConnected
        assert not app.deviceConnected


def test_workerConnectDevice_3():
    app.serverConnected = True
    app.deviceConnected = True
    with mock.patch.object(app,
                           'sgConnectDevice',
                           return_value=False):
        suc = app.workerConnectDevice()
        assert not suc
        assert not app.serverConnected
        assert not app.deviceConnected


def test_startTimer():
    suc = app.startTimer()
    assert suc


def test_stopTimer():
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'stop'):
        suc = app.stopTimer()
        assert suc


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


def test_workerGetInitialConfig_1():
    app.workerGetInitialConfig()


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


def test_workerPollStatus_1():
    app.DEVICE_TYPE = 'Camera'
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollStatus()
            assert not suc


def test_workerPollStatus_2():
    app.DEVICE_TYPE = 'Camera'

    app.deviceConnected = True
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'State': 'DISCONNECTED',
                                         'Message': 'test'}):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollStatus()
            assert suc
            assert not app.deviceConnected


def test_workerPollStatus_3():
    app.DEVICE_TYPE = 'Camera'
    app.deviceConnected = False
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'State': 'DISCONNECTED',
                                         'Message': 'test'}):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollStatus()
            assert suc
            assert not app.deviceConnected


def test_workerPollStatus_4():
    app.DEVICE_TYPE = 'Camera'
    app.deviceConnected = True
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'State': 'test',
                                         'Message': 'test'}):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollStatus()
            assert suc
            assert app.deviceConnected


def test_workerPollStatus_5():
    app.DEVICE_TYPE = 'Camera'
    app.deviceConnected = False
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'State': 'test',
                                         'Message': 'test'}):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollStatus()
            assert suc
            assert app.deviceConnected


def test_pollStatus_1():
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.pollStatus()
        assert suc


def test_startCommunication_1():
    app.serverConnected = False
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.startCommunication()
        assert suc
        assert app.serverConnected


def test_stopCommunication_1():
    app.deviceConnected = True
    app.serverConnected = True
    app.deviceName = 'test'
    with mock.patch.object(app,
                           'stopTimer'):
        with mock.patch.object(app,
                               'sgDisconnectDevice'):
            suc = app.stopCommunication()
            assert suc
            assert not app.serverConnected
            assert not app.deviceConnected


def test_discoverDevices_1():
    with mock.patch.object(app,
                           'sgEnumerateDevice',
                           return_value=[]):
        val = app.discoverDevices()
        assert val == []


def test_discoverDevices_2():
    with mock.patch.object(app,
                           'sgEnumerateDevice',
                           return_value=['test']):
        val = app.discoverDevices()
        assert val == ['test']
