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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
# external packages
import PyQt5
from indibase.indiBase import Device
# local import
from mw4.base import indiClass

host_ip = 'astro-mount.fritz.box'


class Signal(PyQt5.QtCore.QObject):
    message = PyQt5.QtCore.pyqtSignal(str, int)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app, message
    m = Signal()
    app = indiClass.IndiClass(host_ip, message=m.message)
    yield
    app = None


def test_name():
    app.name = 'test'
    assert app.name == 'test'


def test_serverConnected_1():
    app.name = ''
    suc = app.serverConnected()
    assert not suc


def test_serverConnected_2():
    app.name = 'test'
    with mock.patch.object(app.client,
                           'watchDevice',
                           return_value=True) as call:
        suc = app.serverConnected()
        assert suc
        call.assert_called_with('test')


def test_serverDisconnected():
    suc = app.serverDisconnected(None)
    assert suc


def test_newDevice_1():
    app.name = 'false'
    with mock.patch.object(app.client,
                           'getDevice',
                           return_value=None):
        suc = app.newDevice('test')
        assert suc
        assert None is app.device


def test_newDevice_2():
    app.name = 'test'
    with mock.patch.object(app.client,
                           'getDevice',
                           return_value=Device()):
        suc = app.newDevice('test')
        assert suc
        assert app.device is not None


def test_removeDevice_1():
    app.name = 'test'
    app.device = Device()
    app.data = {'test': 1}
    suc = app.removeDevice('foo')
    assert not suc


def test_removeDevice_2():
    app.name = 'test'
    app.device = Device()
    app.data = {'test': 1}
    suc = app.removeDevice('test')
    assert suc
    assert app.data == {}
    assert app.device is None


def test_startRetry_1():
    app.name = ''
    suc = app.startRetry()
    assert not suc


def test_startRetry_2():
    app.name = 'test'
    app.device = Device()
    app.data = {}
    suc = app.startRetry()
    assert suc


def test_startRetry_3():
    app.name = 'test'
    app.device = Device()
    app.data = {'test': 1}
    suc = app.startRetry()
    assert suc


def test_startCommunication_1():
    with mock.patch.object(app.client,
                           'startTimers',
                           return_value=False):
        with mock.patch.object(app.client,
                               'connectServer',
                               return_value=False):
            suc = app.startCommunication()
            assert not suc


def test_startCommunication_2():
    with mock.patch.object(app.client,
                           'startTimers',
                           return_value=False):
        with mock.patch.object(app.client,
                               'connectServer',
                               return_value=True):
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
    app.name = 'test'
    with mock.patch.object(app.client,
                           'connectDevice',
                           return_value=True):
        suc = app.connectDevice('test', 'CONNECTION')
        assert suc


def test_connectDevice4():
    app.name = 'test'
    with mock.patch.object(app.client,
                           'connectDevice',
                           return_value=False):
        suc = app.connectDevice('test', 'CONNECTION')
        assert not suc


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
