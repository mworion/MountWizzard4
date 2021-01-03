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
# written in python3 , (c) 2019, 2020 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from indibase.indiBase import Client, Device
from indibase import indiXML
from indibase.indiXML import INDIBase
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    function = Client()
    yield function


def test_properties_1(function):
    function.host = 'localhost'
    assert function.host == ('localhost', 7624)


def test_properties_2(function):
    function.host = 12
    assert function.host is None


def test_clearParser(function):
    suc = function.clearParser()
    assert suc


def test_setServer_1(function):
    suc = function.setServer()
    assert not suc
    assert not function.connected


def test_setServer_2(function):
    function.connected = True
    suc = function.setServer('localhost')
    assert suc
    assert not function.connected
    assert function.host == ('localhost', 7624)


def test_watchDevice_1(function):
    with mock.patch.object(indiXML,
                           'clientGetProperties'):
        with mock.patch.object(function,
                               '_sendCmd',
                               return_value=False):
            suc = function.watchDevice('test')
            assert not suc


def test_watchDevice_2(function):
    with mock.patch.object(indiXML,
                           'clientGetProperties'):
        with mock.patch.object(function,
                               '_sendCmd',
                               return_value=True):
            suc = function.watchDevice('')
            assert suc


def test_connectServer_1(function):
    function._host = None
    with mock.patch.object(function.socket,
                           'connectToHost'):
        with mock.patch.object(function.socket,
                               'waitForConnected',
                               return_value=True):
            suc = function.connectServer()
            assert not suc


def test_connectServer_2(function):
    function._host = ('localhost', 7624)
    function.connected = True
    suc = function.connectServer()
    assert suc


def test_connectServer_3(function):
    function._host = ('localhost', 7624)
    function.connected = False
    with mock.patch.object(function.socket,
                           'connectToHost'):
        with mock.patch.object(function.socket,
                               'waitForConnected',
                               return_value=False):
            suc = function.connectServer()
            assert not suc
            assert not function.connected


def test_connectServer_4(function):
    function._host = ('localhost', 7624)
    function.connected = False
    with mock.patch.object(function.socket,
                           'connectToHost'):
        with mock.patch.object(function.socket,
                               'waitForConnected',
                               return_value=True):
            suc = function.connectServer()
            assert suc
            assert function.connected


def test_clearDevices_1(function):
    function.devices = {'test1', 'test2'}
    suc = function.clearDevices()
    assert suc
    assert function.devices == {}


def test_clearDevices_2(function):
    function.devices = {'test1', 'test2'}
    suc = function.clearDevices('test1')
    assert suc
    assert function.devices == {}


def test_disconnectServer(function):
    with mock.patch.object(function,
                           'clearParser'):
        with mock.patch.object(function,
                               'clearDevices'):
            with mock.patch.object(function.socket,
                                   'abort'):
                suc = function.disconnectServer()
                assert suc


def test_handleDisconnected(function):
    function.connected = True
    suc = function.handleDisconnected()
    assert suc
    assert not function.connected


def test_isServerConnected_1(function):
    function.connected = True
    suc = function.isServerConnected()
    assert suc


def test_isServerConnected_2(function):
    function.connected = False
    suc = function.isServerConnected()
    assert not suc


def test_connectDevice_1(function):
    function.connected = False
    suc = function.connectDevice()
    assert not suc


def test_connectDevice_2(function):
    function.connected = True
    suc = function.connectDevice()
    assert not suc


def test_connectDevice_3(function):
    function.connected = True
    suc = function.connectDevice('test')
    assert not suc


def test_connectDevice_4(function):
    function.connected = True
    function.devices = {'test': Device()}
    with mock.patch.object(function.devices['test'],
                           'getSwitch',
                           return_value={'CONNECT': 'On'}):
        suc = function.connectDevice('test')
        assert not suc


def test_connectDevice_5(function):
    function.connected = True
    function.devices = {'test': Device()}
    with mock.patch.object(function.devices['test'],
                           'getSwitch',
                           return_value={'CONNECT': 'Off'}):
        with mock.patch.object(function,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.connectDevice('test')
            assert not suc


def test_connectDevice_6(function):
    function.connected = True
    function.devices = {'test': Device()}
    with mock.patch.object(function.devices['test'],
                           'getSwitch',
                           return_value={'CONNECT': 'Off'}):
        with mock.patch.object(function,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.connectDevice('test')
            assert suc


def test_disconnectDevice_1(function):
    function.connected = False
    suc = function.disconnectDevice()
    assert not suc


def test_disconnectDevice_2(function):
    function.connected = True
    suc = function.disconnectDevice()
    assert not suc


def test_disconnectDevice_3(function):
    function.connected = True
    suc = function.disconnectDevice('test')
    assert not suc


def test_disconnectDevice_4(function):
    function.connected = True
    function.devices = {'test': Device()}
    with mock.patch.object(function.devices['test'],
                           'getSwitch',
                           return_value={'DISCONNECT': 'On'}):
        suc = function.disconnectDevice('test')
        assert not suc


def test_disconnectDevice_5(function):
    function.connected = True
    function.devices = {'test': Device()}
    with mock.patch.object(function.devices['test'],
                           'getSwitch',
                           return_value={'DISCONNECT': 'Off'}):
        with mock.patch.object(function,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.disconnectDevice('test')
            assert not suc


def test_disconnectDevice_6(function):
    function.connected = True
    function.devices = {'test': Device()}
    with mock.patch.object(function.devices['test'],
                           'getSwitch',
                           return_value={'DISCONNECT': 'Off'}):
        with mock.patch.object(function,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.disconnectDevice('test')
            assert suc


def test_getDevice_1(function):
    val = function.getDevice()
    assert val is None


def test_getDevice_2(function):
    function.devices = {'test': 1}
    val = function.getDevice('test')
    assert val == 1


def test_getDevices_1(function):
    val = function.getDevices()
    assert val == []


def test_getDevices_2(function):
    function.devices = {'test': 1}
    with mock.patch.object(function,
                           '_getDriverInterface',
                           return_value=0x0001):
        val = function.getDevices()
        assert val == ['test']


def test_getDevices_3(function):
    function.devices = {'test': 1}
    with mock.patch.object(function,
                           '_getDriverInterface',
                           return_value=0x0003):
        val = function.getDevices(0x00f0)
        assert val == []


def test_setBlobMode_1(function):
    suc = function.setBlobMode()
    assert not suc


def test_setBlobMode_2(function):
    suc = function.setBlobMode(deviceName='test')
    assert not suc


def test_setBlobMode_3(function):
    function.devices = {'test': Device()}
    with mock.patch.object(indiXML,
                           'enableBLOB'):
        with mock.patch.object(function,
                               '_sendCmd',
                               return_value=False):
            suc = function.setBlobMode(deviceName='test')
            assert not suc


def test_setBlobMode_4(function):
    function.devices = {'test': Device()}
    with mock.patch.object(indiXML,
                           'enableBLOB'):
        with mock.patch.object(function,
                               '_sendCmd',
                               return_value=True):
            suc = function.setBlobMode(deviceName='test')
            assert suc


def test_getBlobMode(function):
    function.getBlobMode()


def test_getHost_1(function):
    function._host = None
    val = function.getHost()
    assert val == ''


def test_getHost_2(function):
    function._host = ('localhost', 7624)
    val = function.getHost()
    assert val == 'localhost'


def test_getPort_1(function):
    function._host = None
    val = function.getPort()
    assert val == 0


def test_getPort_2(function):
    function._host = ('localhost', 7624)
    val = function.getPort()
    assert val == 7624


def test_sendNewText_1(function):
    function.devices = {'test': Device()}
    suc = function.sendNewText('')
    assert not suc


def test_sendNewText_2(function):
    function.devices = {'test': Device()}
    suc = function.sendNewText(deviceName='test',
                               propertyName='prop')
    assert not suc


def test_sendNewText_3(function):
    function.devices = {'test': Device()}
    function.devices['test'].prop = None
    suc = function.sendNewText(deviceName='test',
                               propertyName='prop',
                               text='test')
    assert not suc


def test_sendNewText_4(function):
    function.devices = {'test': Device()}
    function.devices['test'].prop = None
    with mock.patch.object(indiXML,
                           'oneText',
                           return_value='test'):
        with mock.patch.object(indiXML,
                               'newTextVector'):
            with mock.patch.object(function,
                                   '_sendCmd',
                                   return_value=False):
                suc = function.sendNewText(deviceName='test',
                                           propertyName='prop',
                                           text='test')
                assert not suc


def test_sendNewText_5(function):
    function.devices = {'test': Device()}
    function.devices['test'].prop = None
    with mock.patch.object(indiXML,
                           'oneText',
                           return_value='test'):
        with mock.patch.object(indiXML,
                               'newTextVector'):
            with mock.patch.object(function,
                                   '_sendCmd',
                                   return_value=True):
                suc = function.sendNewText(deviceName='test',
                                           propertyName='prop',
                                           text='test')
                assert suc


def test_sendNewNumber_1(function):
    function.devices = {'test': Device()}
    suc = function.sendNewNumber('')
    assert not suc


def test_sendNewNumber_2(function):
    function.devices = {'test': Device()}
    suc = function.sendNewNumber(deviceName='test',
                                 propertyName='prop')
    assert not suc


def test_sendNewNumber_3(function):
    function.devices = {'test': Device()}
    function.devices['test'].prop = None
    suc = function.sendNewNumber(deviceName='test',
                                 propertyName='prop',
                                 number=1)
    assert not suc


def test_sendNewNumber_4(function):
    function.devices = {'test': Device()}
    function.devices['test'].prop = None
    with mock.patch.object(indiXML,
                           'oneNumber',
                           return_value='test'):
        with mock.patch.object(indiXML,
                               'newNumberVector'):
            with mock.patch.object(function,
                                   '_sendCmd',
                                   return_value=False):
                suc = function.sendNewNumber(deviceName='test',
                                             propertyName='prop',
                                             number=1)
                assert not suc


def test_sendNewNumber_5(function):
    function.devices = {'test': Device()}
    function.devices['test'].prop = None
    with mock.patch.object(indiXML,
                           'oneNumber',
                           return_value='test'):
        with mock.patch.object(indiXML,
                               'newNumberVector'):
            with mock.patch.object(function,
                                   '_sendCmd',
                                   return_value=True):
                suc = function.sendNewNumber(deviceName='test',
                                             propertyName='prop',
                                             number=1)
                assert suc


def test_sendNewSwitch_1(function):
    function.devices = {'test': Device()}
    suc = function.sendNewSwitch('')
    assert not suc


def test_sendNewSwitch_2(function):
    function.devices = {'test': Device()}
    suc = function.sendNewSwitch(deviceName='test',
                                 propertyName='prop')
    assert not suc


def test_sendNewSwitch_3(function):
    function.devices = {'test': Device()}
    function.devices['test'].prop = None
    suc = function.sendNewSwitch(deviceName='test',
                                 propertyName='prop')
    assert not suc


def test_sendNewSwitch_4(function):
    function.devices = {'test': Device()}
    function.devices['test'].prop = None
    with mock.patch.object(indiXML,
                           'oneSwitch',
                           return_value='test'):
        with mock.patch.object(indiXML,
                               'newSwitchVector'):
            with mock.patch.object(function,
                                   '_sendCmd',
                                   return_value=False):
                suc = function.sendNewSwitch(deviceName='test',
                                             propertyName='prop')
                assert not suc


def test_sendNewSwitch_5(function):
    function.devices = {'test': Device()}
    function.devices['test'].prop = None
    with mock.patch.object(indiXML,
                           'oneSwitch',
                           return_value='test'):
        with mock.patch.object(indiXML,
                               'newSwitchVector'):
            with mock.patch.object(function,
                                   '_sendCmd',
                                   return_value=True):
                suc = function.sendNewSwitch(deviceName='test',
                                             propertyName='prop')
                assert suc


def test_startBlob(function):
    suc = function.startBlob()
    assert suc


def test_sendOneBlob(function):
    suc = function.sendOneBlob()
    assert suc


def test_finishBlob(function):
    suc = function.finishBlob()
    assert suc


def test_setVerbose(function):
    suc = function.setVerbose(True)
    assert suc


def test_isVerbose(function):
    suc = function.isVerbose()
    assert not suc


def test_setConnectionTimeout(function):
    suc = function.setConnectionTimeout()
    assert suc


def test__sendCmd_1(function):
    function.connected = False
    suc = function._sendCmd('')
    assert not suc


def test__sendCmd_2(function):
    function.connected = True
    cmd = INDIBase('<begin><end>'.encode(encoding='UTF-8'), 0, {}, {})
    with mock.patch.object(INDIBase,
                           'toXML',
                           return_value='test'.encode()):
        with mock.patch.object(function.socket,
                               'write',
                               return_value=0):
            with mock.patch.object(function.socket,
                                   'flush'):
                suc = function._sendCmd(cmd)
                assert not suc


def test__sendCmd_3(function):
    function.connected = True
    cmd = INDIBase('<begin><end>'.encode(encoding='UTF-8'), 0, {}, {})
    with mock.patch.object(INDIBase,
                           'toXML',
                           return_value='test'.encode()):
        with mock.patch.object(function.socket,
                               'write',
                               return_value=256):
            with mock.patch.object(function.socket,
                                   'flush'):
                suc = function._sendCmd(cmd)
                assert suc
