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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import datetime
# external packages
import PyQt5.QtWidgets
import indibase
# local import
from mw4.environment import weather
import mw4.test.test_setupQt

host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = weather.Weather(host=host_ip)
    yield
    app = None


def test_name():
    name = 'MBox'
    app.name = name
    assert name == app.name


def test_newDevice_1():
    with mock.patch.object(app.client,
                           'isServerConnected',
                           return_value=True):
        with mock.patch.object(app.client,
                               'getDevice',
                               return_value=1):
            suc = app.newDevice('test')
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


def test_setUpdateRate_1():
    app.name = 'test'
    suc = app._setUpdateRate('false')
    assert not suc


def test_setUpdateRate_2():
    app.name = 'test'
    app.device = None
    suc = app._setUpdateRate('test')
    assert not suc


def test_setUpdateRate_3():
    class Test:
        @staticmethod
        def getNumber(test):
            return {}
    app.name = 'test'
    app.device = Test()
    suc = app._setUpdateRate('test')
    assert not suc


def test_setUpdateRate_4():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 1}
    app.name = 'test'
    app.device = Test()
    suc = app._setUpdateRate('test')
    assert suc


def test_setUpdateRate_5():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.name = 'test'
    app.device = Test()
    with mock.patch.object(app.client,
                           'sendNewNumber',
                           return_value=False):
        suc = app._setUpdateRate('test')
        assert not suc


def test_setUpdateRate_6():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.name = 'test'
    app.device = Test()
    with mock.patch.object(app.client,
                           'sendNewNumber',
                           return_value=True):
        suc = app._setUpdateRate('test')
        assert suc


def test_getDewPoint():
    temp = 20
    hum = 50
    value = app._getDewPoint(temp, hum)
    assert value == 9.254294282076941


def test_updateData_1():
    app.device = None
    app.name = 'test'
    suc = app.updateData('false', 'WEATHER_HUMIDITY')
    assert not suc


def test_updateData_2():
    app.device = 1
    app.name = 'test'
    suc = app.updateData('false', 'WEATHER_HUMIDITY')
    assert not suc


def test_updateData_3():
    app.device = indibase.indiBase.Device()
    app.name = 'test'
    values = {'WEATHER_DEWPOINT': 5,
              'WEATHER_TEMPERATURE': 10,
              'WEATHER_HUMIDITY': 50,
              }
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value=values):
        suc = app.updateData('test', 'WEATHER_PARAMETERS')
        assert suc
        assert app.data['WEATHER_DEWPOINT'] == 5
        assert app.data['WEATHER_TEMPERATURE'] == 10
        assert app.data['WEATHER_HUMIDITY'] == 50


def test_updateData_4():
    app.device = indibase.indiBase.Device()
    app.name = 'test'
    values = {'WEATHER_DEWPOINT': 5,
              }
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value=values):
        suc = app.updateData('test', 'WEATHER_PARAMETERS')
        assert suc


def test_updateData_5():
    app.device = indibase.indiBase.Device()
    app.name = 'test'
    values = {'WEATHER_HUMIDITY': 50,
              }
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value=values):
        suc = app.updateData('test', 'WEATHER_PARAMETERS')
        assert suc


def test_updateData_6():
    app.device = indibase.indiBase.Device()
    app.name = 'test'
    values = {'WEATHER_TEMPERATURE': 10,
              }
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value=values):
        suc = app.updateData('test', 'WEATHER_PARAMETERS')
        assert suc


def test_updateData_7():
    app.device = indibase.indiBase.Device()
    app.name = 'test'
    values = {'WEATHER_TEMPERATURE': 20,
              'WEATHER_HUMIDITY': 50,
              }
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value=values):
        suc = app.updateData('test', 'WEATHER_PARAMETERS')
        assert suc


def test_updateData_8():
    app.device = indibase.indiBase.Device()
    app.name = 'test'
    t = datetime.datetime.utcnow()
    values = {'WEATHER_TEMPERATURE': 10,
              'WEATHER_HUMIDITY': 50,
              }
    app.data = {'WEATHER_TEMPERATURE': 10,
                'WEATHER_HUMIDITY': 50,
                }
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value=values):
        suc = app.updateData('test', 'WEATHER_PARAMETERS')
        assert suc
