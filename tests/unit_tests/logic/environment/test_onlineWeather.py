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
import os
import json
import shutil

# external packages
import requests

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.environment.onlineWeather import OnlineWeather
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    shutil.copy('tests/testData/openweathermap.data',
                'tests/workDir/data/openweathermap.data')
    with mock.patch.object(requests,
                           'get',
                           return_value=Test1()):
        func = OnlineWeather(app=App())
        yield func


def test_properties(function):
    with mock.patch.object(function,
                           'pollOpenWeatherMapData'):
        function.keyAPI = 'test'
        assert function.keyAPI == 'test'
        function.online = True
        assert function.online


def test_startCommunication_(function):
    function.enabled = False
    with mock.patch.object(function,
                           'pollOpenWeatherMapData'):
        suc = function.startCommunication()
        assert suc
        assert function.enabled


def test_stopCommunication_1(function):
    function.running = True
    function.enabled = True
    suc = function.stopCommunication()
    assert suc
    assert not function.running
    assert not function.enabled


def test_getDewPoint_1(function):
    val = function.getDewPoint(-100, 10)
    assert not val


def test_getDewPoint_2(function):
    val = function.getDewPoint(100, 10)
    assert not val


def test_getDewPoint_3(function):
    val = function.getDewPoint(10, -10)
    assert not val


def test_getDewPoint_4(function):
    val = function.getDewPoint(10, 110)
    assert not val


def test_getDewPoint_5(function):
    val = function.getDewPoint(10, 10)
    assert val == -20.216642415771897


def test_processOpenWeatherMapData_1(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        suc = function.processOpenWeatherMapData()
        assert not suc


def test_processOpenWeatherMapData_2(function):
    with mock.patch.object(json,
                           'load',
                           return_value={},
                           side_effect=Exception):
        suc = function.processOpenWeatherMapData()
        assert not suc


def test_processOpenWeatherMapData_2a(function):
    data = {'test': {'temp': 290,
                     'pressure': 1000,
                     'humidity': 50},
            'clouds': {'all': 100},
            'wind': {'speed': 10,
                     'deg': 260},
            'rain': {'3h': 10}
            }

    with mock.patch.object(json,
                           'load',
                           return_value=data):
        suc = function.processOpenWeatherMapData()
        assert not suc


def test_processOpenWeatherMapData_3(function):
    data = {'main': {'temp': 290,
                     'pressure': 1000,
                     'humidity': 50},
            'clouds': {'all': 100},
            'wind': {'speed': 10,
                     'deg': 260},
            'rain': {'3h': 10}
            }

    with mock.patch.object(json,
                           'load',
                           return_value=data):
        suc = function.processOpenWeatherMapData()
        assert suc


def test_processOpenWeatherMapData_4(function):
    data = {'main': {'temp': 290,
                     'pressure': 1000,
                     'humidity': 50},
            'clouds': {'all': 100},
            'wind': {'speed': 10,
                     'deg': 260},
            }

    with mock.patch.object(json,
                           'load',
                           return_value=data):
        suc = function.processOpenWeatherMapData()
        assert suc


def test_workerGetOpenWeatherMapData_1(function):
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = function.workerGetOpenWeatherMapData('http://localhost')
        assert not suc


def test_workerGetOpenWeatherMapData_3(function):
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception(),
                           return_value=Test()):
        suc = function.workerGetOpenWeatherMapData('http://localhost')
        assert not suc


def test_workerGetOpenWeatherMapData_4(function):
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           side_effect=TimeoutError(),
                           return_value=Test()):
        suc = function.workerGetOpenWeatherMapData('http://localhost')
        assert not suc


def test_workerGetOpenWeatherMapData_5(function):
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = function.workerGetOpenWeatherMapData('http://localhost')
        assert suc


def test_sendStatus_1(function):
    function.running = True
    suc = function.sendStatus(False)
    assert suc


def test_sendStatus_2(function):
    function.running = False
    suc = function.sendStatus(True)
    assert suc


def test_getOpenWeatherMapData(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.getOpenWeatherMapData('test')
        assert suc


def test_loadingFileNeeded_1(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        suc = function.loadingFileNeeded('test', 1)
        assert suc


def test_loadingFileNeeded_2(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite.loader,
                               'days_old',
                               return_value=1):
            suc = function.loadingFileNeeded('test', 1)
            assert suc


def test_loadingFileNeeded_3(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite.loader,
                               'days_old',
                               return_value=1):
            suc = function.loadingFileNeeded('test', 25)
            assert not suc


def test_pollOpenWeatherMapData_1(function):
    function.enabled = False
    function.running = False
    function.online = False
    function.apiKey = ''
    suc = function.pollOpenWeatherMapData()
    assert not suc


def test_pollOpenWeatherMapData_2(function):
    function.enabled = True
    function.online = False
    function.running = False
    function.apiKey = ''
    suc = function.pollOpenWeatherMapData()
    assert not suc


def test_pollOpenWeatherMapData_3(function):
    function.enabled = True
    function.online = False
    function.running = True
    function.apiKey = 'test'
    suc = function.pollOpenWeatherMapData()
    assert not suc
    assert not function.running


def test_pollOpenWeatherMapData_4(function):
    function.enabled = True
    function.online = True
    function.running = False
    function.apiKey = 'test'
    with mock.patch.object(function,
                           'loadingFileNeeded',
                           return_value=False):
        suc = function.pollOpenWeatherMapData()
        assert suc


def test_pollOpenWeatherMapData_5(function):
    function.enabled = True
    function.online = True
    function.running = True
    function.apiKey = 'test'
    with mock.patch.object(function,
                           'loadingFileNeeded',
                           return_value=True):
        with mock.patch.object(function,
                               'getOpenWeatherMapData'):
            suc = function.pollOpenWeatherMapData()
            assert suc
