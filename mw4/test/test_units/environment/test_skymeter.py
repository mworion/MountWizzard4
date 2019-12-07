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
import datetime
# external packages
import indibase
# local import
from mw4.test.test_units.setupQt import setupQt

host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_name():
    name = 'MBox'
    app.skymeter.name = name
    assert name == app.skymeter.name


def test_newDevice_1():
    with mock.patch.object(app.skymeter.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.skymeter.client,
                               'getDevice',
                               return_value=1):
            suc = app.skymeter.newDevice('test')
            assert suc
            assert app.skymeter.device is None


def test_newDevice_2():
    app.skymeter.name = 'Test'
    with mock.patch.object(app.skymeter.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.skymeter.client,
                               'getDevice',
                               return_value=1):
            suc = app.skymeter.newDevice('Test')
            assert suc
            assert app.skymeter.device == 1


def test_removeDevice_1():
    app.skymeter.name = 'Test'
    with mock.patch.object(app.skymeter.client,
                           'isServerConnected',
                           return_value=True):
        suc = app.skymeter.removeDevice('Test')
        assert suc
        assert app.skymeter.device is None
        assert app.skymeter.data == {}


def test_startCommunication_1():
    app.skymeter.name = ''
    with mock.patch.object(app.skymeter.client,
                           'connectServer',
                           return_value=False):
        suc = app.skymeter.startCommunication()
        assert not suc


def test_setUpdateRate_1():
    app.skymeter.name = 'test'
    suc = app.skymeter.setUpdateConfig('false')
    assert not suc


def test_setUpdateRate_2():
    app.skymeter.name = 'test'
    app.skymeter.device = None
    suc = app.skymeter.setUpdateConfig('test')
    assert not suc


def test_setUpdateRate_3():
    class Test:
        @staticmethod
        def getNumber(test):
            return {}
    app.skymeter.name = 'test'
    app.skymeter.device = Test()
    suc = app.skymeter.setUpdateConfig('test')
    assert not suc


def test_setUpdateRate_4():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 1}
    app.skymeter.name = 'test'
    app.skymeter.device = Test()
    suc = app.skymeter.setUpdateConfig('test')
    assert suc


def test_setUpdateRate_5():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.skymeter.name = 'test'
    app.skymeter.device = Test()
    with mock.patch.object(app.skymeter.client,
                           'sendNewNumber',
                           return_value=False):
        suc = app.skymeter.setUpdateConfig('test')
        assert not suc


def test_setUpdateRate_6():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.skymeter.name = 'test'
    app.skymeter.device = Test()
    with mock.patch.object(app.skymeter.client,
                           'sendNewNumber',
                           return_value=True):
        suc = app.skymeter.setUpdateConfig('test')
        assert suc
