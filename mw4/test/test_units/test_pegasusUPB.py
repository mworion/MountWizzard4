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
# Python  v3.7.3
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
# local import
from mw4.powerswitch import pegasusUPB

host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = pegasusUPB.PegasusUPB(host=host_ip)
    yield
    app = None


def test_name():
    name = 'PegasusUPB'
    app.name = name
    assert name == app.name


def test_newDevice_1():
    with mock.patch.object(app.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.client,
                               'getDevice',
                               return_value=1):
            suc = app.newDevice('test_mountwizzard')
            assert suc
            assert app.device is None


def test_newDevice_2():
    app.name = 'Test'
    with mock.patch.object(app.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.client,
                               'getDevice',
                               return_value=1):
            suc = app.newDevice('Test')
            assert suc
            assert app.device == 1


def test_removeDevice_1():
    app.name = 'Test'
    with mock.patch.object(app.client,
                           'isServerConnected',
                           return_value=True):
        suc = app.removeDevice('Test')
        assert suc
        assert app.device is None
        assert app.data == {}


def test_startCommunication_1():
    app.name = ''
    with mock.patch.object(app.client,
                           'connectServer',
                           return_value=False):
        suc = app.startCommunication()
        assert not suc


def test_setUpdateConfig_1():
    app.name = 'test_mountwizzard'
    suc = app.setUpdateConfig('false')
    assert not suc


def test_setUpdateConfig_2():
    app.name = 'test_mountwizzard'
    app.device = None
    suc = app.setUpdateConfig('test_mountwizzard')
    assert not suc


def test_setUpdateConfig_3():
    class Test:
        @staticmethod
        def getNumber(test):
            return {}
    app.name = 'test_mountwizzard'
    app.device = Test()
    suc = app.setUpdateConfig('test_mountwizzard')
    assert not suc


def test_setUpdateConfig_4():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 1}
    app.name = 'test_mountwizzard'
    app.device = Test()
    suc = app.setUpdateConfig('test_mountwizzard')
    assert not suc


def test_setUpdateConfig_5():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.name = 'test_mountwizzard'
    app.device = Test()
    with mock.patch.object(app.client,
                           'sendNewNumber',
                           return_value=False):
        suc = app.setUpdateConfig('test_mountwizzard')
        assert not suc


def test_setUpdateConfig_6():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.name = 'test_mountwizzard'
    app.device = Test()
    with mock.patch.object(app.client,
                           'sendNewNumber',
                           return_value=True):
        suc = app.setUpdateConfig('test_mountwizzard')
        assert suc


