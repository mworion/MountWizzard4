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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

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


def test_startCommunication_1(function):
    function.running = False
    with mock.patch.object(function,
                           'pollOpenWeatherMapData'):
        suc = function.startCommunication()
        assert not suc
        assert not function.running


def test_startCommunication_2(function):
    function.running = False
    function.apiKey = 'test'
    with mock.patch.object(function,
                           'pollOpenWeatherMapData'):
        suc = function.startCommunication()
        assert suc
        assert function.running


def test_stopCommunication_1(function):
    function.running = True
    suc = function.stopCommunication()
    assert suc
    assert not function.running


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


def test_updateOpenWeatherMapDataWorker_1(function):
    suc = function.processOpenWeatherMapData()
    assert not suc


def test_updateOpenWeatherMapDataWorker_2(function):
    data = {'test': {}}
    suc = function.processOpenWeatherMapData(data=data)
    assert not suc


def test_updateOpenWeatherMapDataWorker_3(function):
    entry = {'main': {'temp': 290,
                      'grnd_level': 1000,
                      'humidity': 50},
             'clouds': {'all': 100},
             'wind': {'speed': 10,
                      'deg': 260},
             'rain': {'3h': 10}
             }
    data = {'list': [entry]}
    suc = function.processOpenWeatherMapData(data=data)
    assert suc


def test_updateOpenWeatherMapDataWorker_4(function):
    data = {'list': []}
    suc = function.processOpenWeatherMapData(data=data)
    assert not suc


def test_getOpenWeatherMapDataWorker_1(function):
    val = function.workerGetOpenWeatherMapData()
    assert val is None


def test_getOpenWeatherMapDataWorker_2(function):
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.workerGetOpenWeatherMapData('http://localhost')
        assert val is None


def test_getOpenWeatherMapDataWorker_3(function):
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception(),
                           return_value=Test()):
        val = function.workerGetOpenWeatherMapData('http://localhost')
        assert val is None


def test_getOpenWeatherMapDataWorker_4(function):
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           side_effect=TimeoutError(),
                           return_value=Test()):
        val = function.workerGetOpenWeatherMapData('http://localhost')
        assert val is None


def test_getOpenWeatherMapDataWorker_5(function):
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.workerGetOpenWeatherMapData('http://localhost')
        assert val == 'test'


def test_updateOpenWeatherMapData_1(function):
    suc = function.pollOpenWeatherMapData()
    assert not suc


def test_updateOpenWeatherMapData_2(function):
    function.online = True
    suc = function.pollOpenWeatherMapData()
    assert not suc


def test_updateOpenWeatherMapData_3(function):
    function.online = True
    function.running = True
    suc = function.pollOpenWeatherMapData()
    assert suc


def test_updateOpenWeatherMapData_4(function):
    function.online = False
    function.running = True
    with mock.patch.object(function,
                           'stopCommunication'):
        suc = function.pollOpenWeatherMapData()
        assert not suc

