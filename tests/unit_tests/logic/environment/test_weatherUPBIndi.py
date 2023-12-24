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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from indibase.indiBase import Device, Client

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.environment.weatherUPBIndi import WeatherUPBIndi
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def function():
    func = WeatherUPBIndi(app=App(), signals=Signals(), data={})
    yield func


def test_setUpdateConfig_1(function):
    function.deviceName = ''
    function.loadConfig = True
    function.updateRate = 1000
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2(function):
    function.deviceName = 'test'
    function.device = None
    function.loadConfig = True
    function.updateRate = 1000
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_4(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=False):
            suc = function.setUpdateConfig('test')
            assert not suc


def test_setUpdateConfig_5(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.setUpdateConfig('test')
            assert suc


def test_updateNumber_1(function):
    function.deviceName = ''
    function.device = None
    suc = function.updateNumber('test', {})
    assert suc
    assert function.data == {}


def test_updateNumber_2(function):
    function.deviceName = ''
    function.device = None
    elements = {'VALUE': 1}
    suc = function.updateNumber('SENSORS.AbsolutePressure', elements)
    assert suc
    assert function.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] == 1


def test_updateNumber_3(function):
    function.deviceName = ''
    function.device = None
    elements = {'VALUE': 1}
    suc = function.updateNumber('SENSORS.DewPoint', elements)
    assert suc
    assert function.data['WEATHER_PARAMETERS.WEATHER_DEWPOINT'] == 1

