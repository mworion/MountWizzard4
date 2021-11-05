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
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock

# external packages
import pytest
import PyQt5
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtTest import QTest
from indibase.indiBase import Device
from base.indiClass import IndiClass

# local import
from base import indiClass
from base.driverDataClass import Signals

host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = IndiClass()
        app.app = Test()
        yield


def test_class_without_app():
    a = indiClass.IndiClass()


def test_properties():
    app.deviceName = 'test'
    assert app.deviceName == 'test'
    app.host = ('localhost', 7624)
    assert app.host == ('localhost', 7624)
    app.hostaddress = 'localhost'
    assert app.hostaddress == 'localhost'
    app.port = 7624
    assert app.port == 7624


def test_serverConnected_1():
    app.deviceName = ''
    suc = app.serverConnected()
    assert not suc


def test_serverConnected_2():
    app.deviceName = 'test'
    with mock.patch.object(app.client,
                           'watchDevice',
                           return_value=True) as call:
        suc = app.serverConnected()
        assert suc
        call.assert_called_with('test')


def test_serverDisconnected():
    suc = app.serverDisconnected({'test': 'test'})
    assert suc


def test_newDevice_1():
    app.deviceName = 'false'
    with mock.patch.object(app.client,
                           'getDevice',
                           return_value=None):
        suc = app.newDevice('test')
        assert suc
        assert None is app.device


def test_newDevice_2():
    app.deviceName = 'test'
    with mock.patch.object(app.client,
                           'getDevice',
                           return_value=Device()):
        suc = app.newDevice('test')
        assert suc
        assert app.device is not None


def test_removeDevice_1():
    app.deviceName = 'test'
    app.device = Device()
    app.data = {'test': 1}
    suc = app.removeDevice('foo')
    assert not suc


def test_removeDevice_2():
    app.deviceName = 'test'
    app.device = Device()
    app.data = {'test': 1}
    suc = app.removeDevice('test')
    assert suc
    assert app.data == {}
    assert app.device is None


def test_startRetry_1():
    app.deviceName = ''
    suc = app.startRetry()
    assert not suc


def test_startRetry_2():
    app.deviceName = 'test'
    app.device = Device()
    app.data = {}
    suc = app.startRetry()
    assert not suc


def test_startRetry_3():
    app.deviceConnected = False
    app.deviceName = 'test'
    app.device = Device()
    app.data = {}
    with mock.patch.object(app.client,
                           'connectServer',
                           return_value=True):
        suc = app.startRetry()
        assert suc
        assert not app.deviceConnected


def test_startRetry_4():
    app.deviceConnected = False
    app.deviceName = 'test'
    app.device = Device()
    app.data = {'test': 1}
    with mock.patch.object(app.client,
                           'connectServer',
                           return_value=False):
        suc = app.startRetry()
        assert suc
        assert app.deviceConnected


def test_startCommunication_1():
    app.data = {}
    with mock.patch.object(app.client,
                           'startTimers',
                           return_value=False):
        with mock.patch.object(app.client,
                               'connectServer',
                               return_value=False):
            with mock.patch.object(app.timerRetry,
                                   'start'):
                suc = app.startCommunication()
                assert not suc


def test_startCommunication_2():
    app.data = {}
    with mock.patch.object(app.client,
                           'startTimers',
                           return_value=False):
        with mock.patch.object(app.client,
                               'connectServer',
                               return_value=True):
            with mock.patch.object(app.timerRetry,
                                   'start'):
                suc = app.startCommunication()
                assert suc


def test_stopCommunication_1():
    with mock.patch.object(app.client,
                           'stopTimers',
                           return_value=False):
        with mock.patch.object(app.client,
                               'disconnectServer',
                               return_value=False):
            suc = app.stopCommunication()
            assert not suc


def test_stopCommunication_2():
    with mock.patch.object(app.client,
                           'stopTimers',
                           return_value=False):
        with mock.patch.object(app.client,
                               'disconnectServer',
                               return_value=True):
            suc = app.stopCommunication()
            assert suc


def test_connectDevice1():
    with mock.patch.object(app.client,
                           'connectDevice',
                           return_value=False):
        suc = app.connectDevice('test', 'test')
        assert not suc


def test_connectDevice2():
    with mock.patch.object(app.client,
                           'connectDevice',
                           return_value=False):
        suc = app.connectDevice('test', 'CONNECTION')
        assert not suc


def test_connectDevice3():
    app.deviceName = 'test'
    with mock.patch.object(app.client,
                           'connectDevice',
                           return_value=True):
        suc = app.connectDevice('test', 'CONNECTION')
        assert suc


def test_connectDevice4():
    app.deviceName = 'test'
    with mock.patch.object(app.client,
                           'connectDevice',
                           return_value=False):
        suc = app.connectDevice('test', 'CONNECTION')
        assert not suc


def test_loadDefaultConfig_1():
    app.loadIndiConfig = False
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'test': 1}):
        suc = app.loadConfig('test')
        assert not suc


def test_loadDefaultConfig_2():
    app.loadIndiConfig = True
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'test': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.loadConfig('test')
            assert not suc


def test_loadDefaultConfig_3():
    app.loadIndiConfig = True
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'test': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.loadConfig('test')
            assert suc


def test_setUpdateConfig():
    app.setUpdateConfig('test')


def test_convertIndigoProperty_1():
    app.INDIGO = {'test': 'test1'}
    val = app.convertIndigoProperty('test')
    assert val == 'test1'


def test_updateNumber_1():
    suc = app.updateNumber('telescope', 'test')
    assert not suc


def test_updateNumber_2():
    app.device = Device()
    suc = app.updateNumber('telescope', 'test')
    assert not suc


def test_updateNumber_3():
    app.data = {}
    app.device = Device()
    app.deviceName = 'telescope'
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'test': 1}):
        suc = app.updateNumber('telescope', 'test')
        assert suc


def test_updateText_1():
    suc = app.updateText('telescope', 'test')
    assert not suc


def test_updateText_2():
    app.device = Device()
    suc = app.updateText('telescope', 'test')
    assert not suc


def test_updateText_3():
    app.data = {}
    app.device = Device()
    app.deviceName = 'telescope'
    with mock.patch.object(app.device,
                           'getText',
                           return_value={'test': 1}):
        suc = app.updateText('telescope', 'test')
        assert suc


def test_updateSwitch_1():
    suc = app.updateSwitch('telescope', 'test')
    assert not suc


def test_updateSwitch_2():
    app.device = Device()
    suc = app.updateSwitch('telescope', 'test')
    assert not suc


def test_updateSwitch_3():
    app.data = {}
    app.device = Device()
    app.deviceName = 'telescope'
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'test': 1}):
        suc = app.updateSwitch('telescope', 'test')
        assert suc


def test_updateSwitch_4():
    app.data = {}
    app.device = Device()
    app.deviceName = 'telescope'
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'test': 1}):
        suc = app.updateSwitch('telescope', 'PROFILE')
        assert suc


def test_updateLight_1():
    suc = app.updateLight('telescope', 'test')
    assert not suc


def test_updateLight_2():
    app.device = Device()
    suc = app.updateLight('telescope', 'test')
    assert not suc


def test_updateLight_3():
    app.data = {}
    app.device = Device()
    app.deviceName = 'telescope'
    with mock.patch.object(app.device,
                           'getLight',
                           return_value={'test': 1}):
        suc = app.updateLight('telescope', 'test')
        assert suc


def test_updateBLOB_1():
    suc = app.updateBLOB('telescope', 'test')
    assert not suc


def test_updateBLOB_2():
    app.device = Device()
    suc = app.updateBLOB('telescope', 'test')
    assert not suc


def test_updateBLOB_3():
    app.device = Device()
    app.deviceName = 'telescope'
    suc = app.updateBLOB('telescope', 'test')
    assert suc


def test_removePrefix_1():
    value = app.removePrefix('', '')
    assert value == ''


def test_removePrefix_2():
    value = app.removePrefix('NOT should not be shown', 'NOT')
    assert value == 'should not be shown'


def test_updateMessage_1():
    app.showMessages = False
    suc = app.updateMessage('test', 'text')
    assert not suc


def test_updateMessage_2():
    app.showMessages = True
    suc = app.updateMessage('test', 'text')
    assert suc


def test_updateMessage_3():
    app.showMessages = True
    suc = app.updateMessage('test', '[WARNING] should not be shown')
    assert suc


def test_updateMessage_4():
    app.showMessages = True
    suc = app.updateMessage('test', '[ERROR] should not be shown')
    assert suc


def test_updateMessage_5():
    app.showMessages = True
    suc = app.updateMessage('test', 'NOT should not be shown')
    assert suc


def test_addDiscoveredDevice_1(qtbot):
    device = Device()
    app.indiClass = IndiClass()
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': None}):
        suc = app.addDiscoveredDevice('telescope', 'test')
        assert not suc


def test_addDiscoveredDevice_2(qtbot):
    app.indiClass = IndiClass()
    app.indiClass.client.devices['telescope'] = {}
    suc = app.addDiscoveredDevice('telescope', 'DRIVER_INFO')
    assert not suc


def test_addDiscoveredDevice_3(qtbot):
    device = Device()
    app.indiClass = IndiClass()
    app.client.devices['telescope'] = device
    app.discoverType = None
    with mock.patch.object(device,
                           'getText',
                           return_value={}):
        suc = app.addDiscoveredDevice('telescope', 'DRIVER_INFO')
        assert not suc


def test_addDiscoveredDevice_4(qtbot):
    device = Device()
    app.indiClass = IndiClass()
    app.client.devices['telescope'] = device
    app.discoverType = None
    app.discoverList = list()
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': '0'}):
        suc = app.addDiscoveredDevice('telescope', 'DRIVER_INFO')
        assert not suc


def test_addDiscoveredDevice_5(qtbot):
    device = Device()
    app.indiClass = IndiClass()
    app.client.devices['telescope'] = device
    app.discoverType = 1
    app.discoverList = list()
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': 1}):
        suc = app.addDiscoveredDevice('telescope', 'DRIVER_INFO')
        assert suc


def test_discoverDevices_1():
    with mock.patch.object(QTest,
                           'qWait'):
        val = app.discoverDevices('dome')
        assert val == []
