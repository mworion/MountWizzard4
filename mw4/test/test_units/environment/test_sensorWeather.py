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
import datetime
# external packages
import indibase
# local import
from mw4.test.test_units.setupQt import setupQt

host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_name():
    name = 'MBox'
    app.sensorWeather.name = name
    assert name == app.sensorWeather.name


def test_newDevice_1():
    with mock.patch.object(app.sensorWeather.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.sensorWeather.client,
                               'getDevice',
                               return_value=1):
            suc = app.sensorWeather.newDevice('test')
            assert suc
            assert app.sensorWeather.device is None


def test_newDevice_2():
    app.sensorWeather.name = 'Test'
    with mock.patch.object(app.sensorWeather.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.sensorWeather.client,
                               'getDevice',
                               return_value=1):
            suc = app.sensorWeather.newDevice('Test')
            assert suc
            assert app.sensorWeather.device == 1


def test_removeDevice_1():
    app.sensorWeather.name = 'Test'
    with mock.patch.object(app.sensorWeather.client,
                           'isServerConnected',
                           return_value=True):
        suc = app.sensorWeather.removeDevice('Test')
        assert suc
        assert app.sensorWeather.device is None
        assert app.sensorWeather.data == {}


def test_startCommunication_1():
    app.sensorWeather.name = ''
    with mock.patch.object(app.sensorWeather.client,
                           'connectServer',
                           return_value=False):
        suc = app.sensorWeather.startCommunication()
        assert not suc


def test_setUpdateConfig_1():
    app.sensorWeather.name = 'test'
    suc = app.sensorWeather.setUpdateConfig('false')
    assert not suc


def test_setUpdateConfig_2():
    app.sensorWeather.name = 'test'
    app.sensorWeather.device = None
    suc = app.sensorWeather.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3():
    class Test:
        @staticmethod
        def getNumber(test):
            return {}
    app.sensorWeather.name = 'test'
    app.sensorWeather.device = Test()
    suc = app.sensorWeather.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_4():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 1}
    app.sensorWeather.name = 'test'
    app.sensorWeather.device = Test()
    suc = app.sensorWeather.setUpdateConfig('test')
    assert suc


def test_setUpdateConfig_5():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.sensorWeather.name = 'test'
    app.sensorWeather.device = Test()
    with mock.patch.object(app.sensorWeather.client,
                           'sendNewNumber',
                           return_value=False):
        suc = app.sensorWeather.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_6():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.sensorWeather.name = 'test'
    app.sensorWeather.device = Test()
    with mock.patch.object(app.sensorWeather.client,
                           'sendNewNumber',
                           return_value=True):
        suc = app.sensorWeather.setUpdateConfig('test')
        assert suc


def test_updateNumber_1():
    app.sensorWeather.device = None
    app.sensorWeather.name = 'test'
    suc = app.sensorWeather.updateNumber('false', 'WEATHER_HUMIDITY')
    assert not suc


def test_updateNumber_2():
    app.sensorWeather.device = 1
    app.sensorWeather.name = 'test'
    suc = app.sensorWeather.updateNumber('false', 'WEATHER_HUMIDITY')
    assert not suc


def test_updateNumber_3():
    app.sensorWeather.device = indibase.indiBase.Device()
    app.sensorWeather.name = 'test'
    values = {'WEATHER_DEWPOINT': 5,
              'WEATHER_TEMPERATURE': 10,
              'WEATHER_HUMIDITY': 50,
              }
    with mock.patch.object(app.sensorWeather.device,
                           'getNumber',
                           return_value=values):
        suc = app.sensorWeather.updateNumber('test', 'WEATHER_PARAMETERS')
        assert suc
        assert app.sensorWeather.data['WEATHER_DEWPOINT'] == 5
        assert app.sensorWeather.data['WEATHER_TEMPERATURE'] == 10
        assert app.sensorWeather.data['WEATHER_HUMIDITY'] == 50


def test_updateNumber_4():
    app.sensorWeather.device = indibase.indiBase.Device()
    app.sensorWeather.name = 'test'
    values = {'WEATHER_DEWPOINT': 5,
              }
    with mock.patch.object(app.sensorWeather.device,
                           'getNumber',
                           return_value=values):
        suc = app.sensorWeather.updateNumber('test', 'WEATHER_PARAMETERS')
        assert suc


def test_updateNumber_5():
    app.sensorWeather.device = indibase.indiBase.Device()
    app.sensorWeather.name = 'test'
    values = {'WEATHER_HUMIDITY': 50,
              }
    with mock.patch.object(app.sensorWeather.device,
                           'getNumber',
                           return_value=values):
        suc = app.sensorWeather.updateNumber('test', 'WEATHER_PARAMETERS')
        assert suc


def test_updateNumber_6():
    app.sensorWeather.device = indibase.indiBase.Device()
    app.sensorWeather.name = 'test'
    values = {'WEATHER_TEMPERATURE': 10,
              }
    with mock.patch.object(app.sensorWeather.device,
                           'getNumber',
                           return_value=values):
        suc = app.sensorWeather.updateNumber('test', 'WEATHER_PARAMETERS')
        assert suc
