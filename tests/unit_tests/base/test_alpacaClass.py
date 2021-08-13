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

# external packages
import PyQt5
import pytest
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject

# local import
from base.alpacaClass import AlpacaClass


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = AlpacaClass(app=Test(), data={}, threadPool=QThreadPool())

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


def test_getInitialConfig_1():
    with mock.patch.object(app.client,
                           'connected',
                           return_value=False):
        suc = app.getInitialConfig()
        assert not suc


def test_getInitialConfig_2():
    app.serverConnected = False
    app.deviceConnected = False
    with mock.patch.object(app.client,
                           'connected',
                           return_value=True):
        suc = app.getInitialConfig()
        assert suc
        assert app.serverConnected
        assert app.deviceConnected
        assert app.data['DRIVER_INFO.DRIVER_NAME'] is None
        assert app.data['DRIVER_INFO.DRIVER_VERSION'] is None
        assert app.data['DRIVER_INFO.DRIVER_EXEC'] == ''


def test_startTimer():
    suc = app.startTimer()
    assert suc


def test_stopTimer():
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'stop'):
        suc = app.stopTimer()
        assert suc


def test_pollStatus_1():
    app.deviceConnected = True
    with mock.patch.object(app.client,
                           'connected',
                           return_value=False):
        suc = app.workerPollStatus()
        assert not suc
        assert not app.deviceConnected


def test_pollStatus_2():
    app.deviceConnected = False
    with mock.patch.object(app.client,
                           'connected',
                           return_value=True):
        suc = app.workerPollStatus()
        assert suc
        assert app.deviceConnected


def test_pollStatus_3():
    app.deviceConnected = True
    with mock.patch.object(app.client,
                           'connected',
                           return_value=True):
        suc = app.workerPollStatus()
        assert suc
        assert app.deviceConnected


def test_pollStatus_4():
    app.deviceConnected = False
    with mock.patch.object(app.client,
                           'connected',
                           return_value=False):
        suc = app.workerPollStatus()
        assert not suc
        assert not app.deviceConnected


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


def test_startCommunication():
    with mock.patch.object(app,
                           'startTimer'):
        suc = app.startCommunication()
        assert suc


def test_stopCommunication():
    app.deviceConnected = True
    app.serverConnected = True
    with mock.patch.object(app,
                           'stopTimer'):
        suc = app.stopCommunication()
        assert suc
        assert not app.serverConnected
        assert not app.deviceConnected


def test_discoverDevices_1():
    with mock.patch.object(app.client,
                           'discoverDevices',
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
    with mock.patch.object(app.client,
                           'discoverDevices',
                           return_value=[]):
        val = app.discoverDevices('dome')
        assert val == []
