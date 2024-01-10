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
import pytest
from unittest import mock

# external packages

# local import
from PyQt5.QtCore import QTimer
from indibase.indiBase import Device
from base.indiClass import IndiClass
import base.indiClass
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from base.driverDataClass import Signals

host_ip = 'astro-mount.fritz.box'


class S(IndiClass):
    def __init__(self, app=None, data=None):
        self.signals = Signals()
        self.data = data
        super().__init__(app=app, data=None)
        self.SHOW_COMM = True


@pytest.fixture(autouse=True, scope='function')
def function():

    with mock.patch.object(QTimer,
                           'start'):
        func = S(app=App(), data={})
        yield func


def test_properties(function):
    function.deviceName = 'test'
    assert function.deviceName == 'test'
    function.host = ('localhost', 7624)
    assert function.host == ('localhost', 7624)
    function.hostaddress = 'localhost'
    assert function.hostaddress == 'localhost'
    function.port = 7624
    assert function.port == 7624


def test_serverConnected_1(function):
    function.deviceName = ''
    suc = function.serverConnected()
    assert not suc


def test_serverConnected_2(function):
    function.deviceName = 'test'
    with mock.patch.object(function.client,
                           'watchDevice',
                           return_value=True) as call:
        suc = function.serverConnected()
        assert suc
        call.assert_called_with('test')


def test_serverDisconnected(function):
    suc = function.serverDisconnected({'test': 'test'})
    assert suc


def test_newDevice_1(function):
    function.deviceName = 'false'
    with mock.patch.object(function.client,
                           'getDevice',
                           return_value=None):
        suc = function.newDevice('test')
        assert suc
        assert None is function.device


def test_newDevice_2(function):
    function.deviceName = 'test'
    with mock.patch.object(function.client,
                           'getDevice',
                           return_value=Device()):
        suc = function.newDevice('test')
        assert suc
        assert function.device is not None


def test_removeDevice_1(function):
    function.deviceName = 'test'
    function.device = Device()
    function.data = {'test': 1}
    suc = function.removeDevice('foo')
    assert not suc


def test_removeDevice_2(function):
    function.deviceName = 'test'
    function.device = Device()
    function.data = {'test': 1}
    suc = function.removeDevice('test')
    assert suc
    assert function.data == {}
    assert function.device is None


def test_startRetry_1(function):
    function.deviceName = ''
    suc = function.startRetry()
    assert not suc


def test_startRetry_2(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client.connected = True
    with mock.patch.object(function.client,
                           'connectServer',
                           return_value=True):
        suc = function.startRetry()
        assert not suc


def test_startRetry_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client.connected = False
    with mock.patch.object(function.client,
                           'connectServer',
                           return_value=True):
        suc = function.startRetry()
        assert suc


def test_startCommunication_1(function):
    function.data = {}
    with mock.patch.object(function.client,
                           'connectServer',
                           return_value=False):
        with mock.patch.object(function.timerRetry,
                               'start'):
            suc = function.startCommunication()
            assert suc


def test_startCommunication_2(function):
    function.data = {}
    with mock.patch.object(function.client,
                           'connectServer',
                           return_value=True):
        with mock.patch.object(function.timerRetry,
                               'start'):
            suc = function.startCommunication()
            assert suc


def test_stopCommunication_1(function):
    with mock.patch.object(function.client,
                           'disconnectServer',
                           return_value=False):
        suc = function.stopCommunication()
        assert not suc


def test_stopCommunication_2(function):
    with mock.patch.object(function.client,
                           'disconnectServer',
                           return_value=True):
        suc = function.stopCommunication()
        assert suc


def test_connectDevice1(function):
    with mock.patch.object(function.client,
                           'connectDevice',
                           return_value=False):
        suc = function.connectDevice('test', 'test')
        assert not suc


def test_connectDevice2(function):
    with mock.patch.object(function.client,
                           'connectDevice',
                           return_value=False):
        suc = function.connectDevice('test', 'CONNECTION')
        assert not suc


def test_connectDevice3(function):
    function.deviceName = 'test'
    with mock.patch.object(function.client,
                           'connectDevice',
                           return_value=True):
        suc = function.connectDevice('test', 'CONNECTION')
        assert suc


def test_connectDevice4(function):
    function.deviceName = 'test'
    with mock.patch.object(function.client,
                           'connectDevice',
                           return_value=False):
        suc = function.connectDevice('test', 'CONNECTION')
        assert not suc


def test_loadDefaultConfig_1(function):
    function.loadIndiConfigFlag = False
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'test': 1}):
        suc = function.loadIndiConfig('test')
        assert not suc


def test_loadDefaultConfig_2(function):
    function.loadIndiConfigFlag = True
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'test': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.loadIndiConfig('test')
            assert not suc


def test_loadDefaultConfig_3(function):
    function.loadIndiConfigFlag = True
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'test': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.loadIndiConfig('test')
            assert suc


def test_setUpdateConfig_1(function):
    function.deviceName = ''
    function.loadConfig = True
    with mock.patch.object(function,
                           'loadIndiConfig'):
        suc = function.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_2(function):
    function.deviceName = 'test'
    function.loadConfig = True
    with mock.patch.object(function,
                           'loadIndiConfig'):
        suc = function.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_3(function):
    function.deviceName = 'test'
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    with mock.patch.object(function,
                           'loadIndiConfig'):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.setUpdateConfig('test')
            assert suc


def test_convertIndigoProperty_1(function):
    function.INDIGO = {'test': 'test1'}
    val = function.convertIndigoProperty('test')
    assert val == 'test1'


def test_updateNumber_1(function):
    suc = function.updateNumber('telescope', 'test')
    assert not suc


def test_updateNumber_2(function):
    function.device = Device()
    suc = function.updateNumber('telescope', 'test')
    assert not suc


def test_updateNumber_3(function):
    function.data = {}
    function.device = Device()
    function.deviceName = 'telescope'
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'test': 1}):
        suc = function.updateNumber('telescope', 'test')
        assert suc


def test_updateText_1(function):
    suc = function.updateText('telescope', 'test')
    assert not suc


def test_updateText_2(function):
    function.device = Device()
    suc = function.updateText('telescope', 'test')
    assert not suc


def test_updateText_3(function):
    function.data = {}
    function.device = Device()
    function.deviceName = 'telescope'
    with mock.patch.object(function.device,
                           'getText',
                           return_value={'test': 1}):
        suc = function.updateText('telescope', 'test')
        assert suc


def test_updateSwitch_1(function):
    suc = function.updateSwitch('telescope', 'test')
    assert not suc


def test_updateSwitch_2(function):
    function.device = Device()
    suc = function.updateSwitch('telescope', 'test')
    assert not suc


def test_updateSwitch_3(function):
    function.data = {}
    function.device = Device()
    function.deviceName = 'telescope'
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'test': 1}):
        suc = function.updateSwitch('telescope', 'test')
        assert suc


def test_updateSwitch_4(function):
    function.data = {}
    function.device = Device()
    function.deviceName = 'telescope'
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'test': 1}):
        suc = function.updateSwitch('telescope', 'PROFILE')
        assert suc


def test_updateLight_1(function):
    suc = function.updateLight('telescope', 'test')
    assert not suc


def test_updateLight_2(function):
    function.device = Device()
    suc = function.updateLight('telescope', 'test')
    assert not suc


def test_updateLight_3(function):
    function.data = {}
    function.device = Device()
    function.deviceName = 'telescope'
    with mock.patch.object(function.device,
                           'getLight',
                           return_value={'test': 1}):
        suc = function.updateLight('telescope', 'test')
        assert suc


def test_updateBLOB_1(function):
    suc = function.updateBLOB('telescope', 'test')
    assert not suc


def test_updateBLOB_2(function):
    function.device = Device()
    suc = function.updateBLOB('telescope', 'test')
    assert not suc


def test_updateBLOB_3(function):
    function.device = Device()
    function.deviceName = 'telescope'
    suc = function.updateBLOB('telescope', 'test')
    assert suc


def test_removePrefix_1(function):
    value = function.removePrefix('', '')
    assert value == ''


def test_removePrefix_2(function):
    value = function.removePrefix('NOT should not be shown', 'NOT')
    assert value == 'should not be shown'


def test_updateMessage_1(function):
    function.messages = False
    suc = function.updateMessage('test', 'text')
    assert not suc


def test_updateMessage_2(function):
    function.messages = True
    suc = function.updateMessage('test', 'text')
    assert suc


def test_updateMessage_3(function):
    function.messages = True
    suc = function.updateMessage('test', '[WARNING] should not be shown')
    assert suc


def test_updateMessage_4(function):
    function.messages = True
    suc = function.updateMessage('test', '[ERROR] should not be shown')
    assert suc


def test_updateMessage_5(function):
    function.messages = True
    suc = function.updateMessage('test', 'NOT should not be shown')
    assert suc


def test_updateMessage_6(function):
    function.messages = True
    suc = function.updateMessage('test', '[INFO] should not be shown')
    assert suc


def test_addDiscoveredDevice_1(function):
    device = Device()
    function.indiClass = S(app=App())
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': None}):
        suc = function.addDiscoveredDevice('telescope', 'test')
        assert not suc


def test_addDiscoveredDevice_2(function):
    function.indiClass = S(app=App())
    function.indiClass.client.devices['telescope'] = {}
    suc = function.addDiscoveredDevice('telescope', 'DRIVER_INFO')
    assert not suc


def test_addDiscoveredDevice_3(function):
    device = Device()
    function.indiClass = S(app=App())
    function.client.devices['telescope'] = device
    function.discoverType = None
    with mock.patch.object(device,
                           'getText',
                           return_value={}):
        suc = function.addDiscoveredDevice('telescope', 'DRIVER_INFO')
        assert not suc


def test_addDiscoveredDevice_4(function):
    device = Device()
    function.indiClass = S(app=App())
    function.client.devices['telescope'] = device
    function.discoverType = None
    function.discoverList = list()
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': '0'}):
        suc = function.addDiscoveredDevice('telescope', 'DRIVER_INFO')
        assert not suc


def test_addDiscoveredDevice_5(function):
    device = Device()
    function.indiClass = S(app=App())
    function.client.devices['telescope'] = device
    function.discoverType = 1
    function.discoverList = list()
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': 1}):
        suc = function.addDiscoveredDevice('telescope', 'DRIVER_INFO')
        assert suc


def test_discoverDevices_1(function):
    with mock.patch.object(base.indiClass,
                           'sleepAndEvents'):
        val = function.discoverDevices('dome')
        assert val == []
