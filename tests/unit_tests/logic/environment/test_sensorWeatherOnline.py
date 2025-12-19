############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
import json
import os
import pytest
import requests
from pathlib import Path
import shutil
import unittest.mock as mock
from mw4.base.loggerMW import setupLogging
from mw4.logic.environment.sensorWeatherOnline import SensorWeatherOnline
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.base.signalsDevices import Signals

setupLogging()


class Parent:
    app = App()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    class Test1:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    shutil.copy("tests/testData/openweathermap.data", "tests/work/data/openweathermap.data")
    with mock.patch.object(requests, "get", return_value=Test1()):
        func = SensorWeatherOnline(parent=Parent())
        yield func


def test_startCommunication_(function):
    with mock.patch.object(function, "pollOpenWeatherMapData"):
        function.startCommunication()


def test_stopCommunication_1(function):
    function.running = True
    function.stopCommunication()
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


def test_processOpenWeatherMapData_1(function):
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.processOpenWeatherMapData()


def test_processOpenWeatherMapData_2(function):
    shutil.copy("tests/testData/openweathermap.data", "tests/work/data/openweathermap.data")
    with mock.patch.object(json, "load", return_value={}, side_effect=Exception):
        function.processOpenWeatherMapData()


def test_processOpenWeatherMapData_3(function):
    data = {
        "test": {"temp": 290, "pressure": 1000, "humidity": 50},
        "clouds": {"all": 100},
        "wind": {"speed": 10, "deg": 260},
        "rain": {"3h": 10},
    }
    shutil.copy("tests/testData/openweathermap.data", "tests/work/data/openweathermap.data")
    with mock.patch.object(json, "load", return_value=data):
        function.processOpenWeatherMapData()


def test_processOpenWeatherMapData_4(function):
    data = {
        "main": {"temp": 290, "pressure": 1000, "humidity": 50},
        "clouds": {"all": 100},
        "wind": {"speed": 10, "deg": 260},
        "rain": {"3h": 10},
    }

    shutil.copy("tests/testData/openweathermap.data", "tests/work/data/openweathermap.data")
    with mock.patch.object(json, "load", return_value=data):
        function.processOpenWeatherMapData()


def test_processOpenWeatherMapData_5(function):
    data = {
        "main": {"temp": 290, "pressure": 1000, "humidity": 50},
        "clouds": {"all": 100},
        "wind": {"speed": 10, "deg": 260},
    }

    shutil.copy("tests/testData/openweathermap.data", "tests/work/data/openweathermap.data")
    with mock.patch.object(json, "load", return_value=data):
        function.processOpenWeatherMapData()


def test_workerGetOpenWeatherMapData_1(function):
    class Test:
        status_code = 300

    function.app.onlineMode = False
    with mock.patch.object(requests, "get", return_value=Test()):
        function.workerGetOpenWeatherMapData("http://localhost")


def test_workerGetOpenWeatherMapData_2(function):
    class Test:
        status_code = 300

    function.app.onlineMode = True
    with mock.patch.object(requests, "get", return_value=Test()):
        function.workerGetOpenWeatherMapData("http://localhost")


def test_workerGetOpenWeatherMapData_3(function):
    class Test:
        status_code = 300

    function.app.onlineMode = True
    with mock.patch.object(requests, "get", side_effect=Exception(), return_value=Test()):
        function.workerGetOpenWeatherMapData("http://localhost")


def test_workerGetOpenWeatherMapData_4(function):
    class Test:
        status_code = 300

    function.app.onlineMode = True
    with mock.patch.object(requests, "get", side_effect=TimeoutError(), return_value=Test()):
        function.workerGetOpenWeatherMapData("http://localhost")


def test_workerGetOpenWeatherMapData_5(function):
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    function.app.onlineMode = True
    with mock.patch.object(requests, "get", return_value=Test()):
        function.workerGetOpenWeatherMapData("http://localhost")


def test_sendStatus_1(function):
    function.running = True
    function.sendStatus(False)


def test_sendStatus_2(function):
    function.running = False
    function.sendStatus(True)


def test_getOpenWeatherMapData_1(function):
    with mock.patch.object(function, "loadingFileNeeded", return_value=False):
        with mock.patch.object(function, "processOpenWeatherMapData"):
            with mock.patch.object(function, "sendStatus"):
                with mock.patch.object(function.threadPool, "start"):
                    function.getOpenWeatherMapData("test")


def test_getOpenWeatherMapData_2(function):
    with mock.patch.object(function, "loadingFileNeeded", return_value=True):
        with mock.patch.object(function, "processOpenWeatherMapData"):
            with mock.patch.object(function, "sendStatus"):
                with mock.patch.object(function.threadPool, "start"):
                    function.getOpenWeatherMapData("test")


def test_loadingFileNeeded_1(function):
    with mock.patch.object(Path, "is_file", return_value=False):
        suc = function.loadingFileNeeded("test", 1)
        assert suc


def test_loadingFileNeeded_2(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function.app.mount.obsSite.loader, "days_old", return_value=1):
            suc = function.loadingFileNeeded("test", 1)
            assert suc


def test_loadingFileNeeded_3(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function.app.mount.obsSite.loader, "days_old", return_value=1):
            suc = function.loadingFileNeeded("test", 25)
            assert not suc


def test_pollOpenWeatherMapData_1(function):
    function.apiKey = ""
    function.pollOpenWeatherMapData()


def test_pollOpenWeatherMapData_2(function):
    function.apiKey = "test"
    function.app.onlineMode = False
    function.running = True
    function.pollOpenWeatherMapData()


def test_pollOpenWeatherMapData_3(function):
    function.apiKey = "test"
    function.app.onlineMode = True
    function.pollOpenWeatherMapData()


def test_pollOpenWeatherMapData_4(function):
    function.apiKey = "test"
    function.app.onlineMode = True
    with mock.patch.object(function, "loadingFileNeeded", return_value=False):
        function.pollOpenWeatherMapData()


def test_pollOpenWeatherMapData_5(function):
    function.apiKey = "test"
    function.app.onlineMode = True
    with mock.patch.object(function, "loadingFileNeeded", return_value=True):
        with mock.patch.object(function, "getOpenWeatherMapData"):
            function.pollOpenWeatherMapData()
