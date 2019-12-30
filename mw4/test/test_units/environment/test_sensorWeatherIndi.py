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


def test_setUpdateConfig_1():
    app.sensorWeather.name = 'test'
    suc = app.sensorWeather.run['indi'].setUpdateConfig('false')
    assert not suc


def test_setUpdateConfig_2():
    app.sensorWeather.name = 'test'
    app.sensorWeather.run['indi'].device = None
    suc = app.sensorWeather.run['indi'].setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3():
    class Test:
        @staticmethod
        def getNumber(test):
            return {}
    app.sensorWeather.name = 'test'
    app.sensorWeather.run['indi'].device = Test()
    suc = app.sensorWeather.run['indi'].setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_4():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 1}
    app.sensorWeather.run['indi'].name = 'test'
    app.sensorWeather.run['indi'].device = Test()
    suc = app.sensorWeather.run['indi'].setUpdateConfig('test')
    assert suc


def test_setUpdateConfig_5():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.sensorWeather.run['indi'].name = 'test'
    app.sensorWeather.run['indi'].device = Test()
    with mock.patch.object(app.sensorWeather.run['indi'].client,
                           'sendNewNumber',
                           return_value=False):
        suc = app.sensorWeather.run['indi'].setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_6():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.sensorWeather.run['indi'].name = 'test'
    app.sensorWeather.run['indi'].device = Test()
    with mock.patch.object(app.sensorWeather.run['indi'].client,
                           'sendNewNumber',
                           return_value=True):
        suc = app.sensorWeather.run['indi'].setUpdateConfig('test')
        assert suc


def test_updateNumber_1():
    app.sensorWeather.run['indi'].device = None
    app.sensorWeather.run['indi'].name = 'test'
    suc = app.sensorWeather.run['indi'].updateNumber('false', 'WEATHER_PARAMETERS.WEATHER_HUMIDITY')
    assert not suc


def test_updateNumber_2():
    app.sensorWeather.run['indi'].device = 1
    app.sensorWeather.run['indi'].name = 'test'
    suc = app.sensorWeather.run['indi'].updateNumber('false', 'WEATHER_PARAMETERS.WEATHER_HUMIDITY')
    assert not suc


def test_updateNumber_3():
    app.sensorWeather.run['indi'].device = indibase.indiBase.Device()
    app.sensorWeather.run['indi'].name = 'test'
    values = {'WEATHER_DEWPOINT': 5,
              'WEATHER_TEMPERATURE': 10,
              'WEATHER_HUMIDITY': 50,
              }
    with mock.patch.object(app.sensorWeather.run['indi'].device,
                           'getNumber',
                           return_value=values):
        suc = app.sensorWeather.run['indi'].updateNumber('test', 'WEATHER_PARAMETERS')
        assert suc
        assert app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_DEWPOINT'] == 5
        assert app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] == 10
        assert app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_HUMIDITY'] == 50


def test_updateNumber_4():
    app.sensorWeather.run['indi'].device = indibase.indiBase.Device()
    app.sensorWeather.run['indi'].name = 'test'
    values = {'WEATHER_DEWPOINT': 5,
              }
    with mock.patch.object(app.sensorWeather.run['indi'].device,
                           'getNumber',
                           return_value=values):
        suc = app.sensorWeather.run['indi'].updateNumber('test', 'WEATHER_PARAMETERS')
        assert suc


def test_updateNumber_5():
    app.sensorWeather.run['indi'].device = indibase.indiBase.Device()
    app.sensorWeather.run['indi'].name = 'test'
    values = {'WEATHER_PARAMETERS.WEATHER_HUMIDITY': 50,
              }
    with mock.patch.object(app.sensorWeather.run['indi'].device,
                           'getNumber',
                           return_value=values):
        suc = app.sensorWeather.run['indi'].updateNumber('test', 'WEATHER_PARAMETERS')
        assert suc


def test_updateNumber_6():
    app.sensorWeather.run['indi'].device = indibase.indiBase.Device()
    app.sensorWeather.run['indi'].name = 'test'
    values = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
              }
    with mock.patch.object(app.sensorWeather.run['indi'].device,
                           'getNumber',
                           return_value=values):
        suc = app.sensorWeather.run['indi'].updateNumber('test', 'WEATHER_PARAMETERS')
        assert suc
