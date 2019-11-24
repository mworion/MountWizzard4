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
# Python  v3.7.5
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
from mw4.test.test_units.setupQt import setupQt

host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_name():
    name = 'PegasusUPB'
    app.power.name = name
    assert name == app.power.name


def test_newDevice_1():
    with mock.patch.object(app.power.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.power.client,
                               'getDevice',
                               return_value=1):
            suc = app.power.newDevice('test')
            assert suc
            assert app.power.device is None


def test_newDevice_2():
    app.power.name = 'Test'
    with mock.patch.object(app.power.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.power.client,
                               'getDevice',
                               return_value=1):
            suc = app.power.newDevice('Test')
            assert suc
            assert app.power.device == 1


def test_removeDevice_1():
    app.power.name = 'Test'
    with mock.patch.object(app.power.client,
                           'isServerConnected',
                           return_value=True):
        suc = app.power.removeDevice('Test')
        assert suc
        assert app.power.device is None
        assert app.power.data == {}


def test_startCommunication_1():
    app.power.name = ''
    with mock.patch.object(app.power.client,
                           'connectServer',
                           return_value=False):
        suc = app.power.startCommunication()
        assert not suc


def test_setUpdateConfig_1():
    app.power.name = 'test'
    suc = app.power.setUpdateConfig('false')
    assert not suc


def test_setUpdateConfig_2():
    app.power.name = 'test'
    app.power.device = None
    suc = app.power.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3():
    class Test:
        @staticmethod
        def getNumber(test):
            return {}
    app.power.name = 'test'
    app.power.device = Test()
    suc = app.power.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_4():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 1}
    app.power.name = 'test'
    app.power.device = Test()
    suc = app.power.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_5():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.power.name = 'test'
    app.power.device = Test()
    with mock.patch.object(app.power.client,
                           'sendNewNumber',
                           return_value=False):
        suc = app.power.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_6():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.power.name = 'test'
    app.power.device = Test()
    with mock.patch.object(app.power.client,
                           'sendNewNumber',
                           return_value=True):
        suc = app.power.setUpdateConfig('test')
        assert suc


