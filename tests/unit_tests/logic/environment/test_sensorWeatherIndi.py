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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from indibase.indiBase import Device, Client

# local import
from logic.environment.sensorWeather import SensorWeatherIndi
from logic.environment.sensorWeather import SensorWeatherSignals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
    global app
    app = SensorWeatherIndi(app=Test(), signals=SensorWeatherSignals(), data={})

    yield


def test_setUpdateConfig_1():
    app.name = ''
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2():
    app.name = 'test'
    app.device = None
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = app.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_4():
    app.name = 'test'
    app.device = Device()
    app.UPDATE_RATE = 1
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        suc = app.setUpdateConfig('test')
        assert suc


def test_setUpdateConfig_5():
    app.name = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=False):
            suc = app.setUpdateConfig('test')
            assert not suc


def test_setUpdateConfig_6():
    app.name = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.setUpdateConfig('test')
            assert suc


def test_updateNumber_1():
    app.name = ''
    suc = app.updateNumber('test', 'test')
    assert not suc


def test_updateNumber_2():
    app.name = ''
    app.device = Device()
    suc = app.updateNumber('test', 'test')
    assert not suc


def test_updateNumber_3():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'WEATHER_BAROMETER': 1}):
        suc = app.updateNumber('test', 'WEATHER_BAROMETER')
        assert suc
