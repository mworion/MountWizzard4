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
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import numpy as np
import pytest
import unittest.mock as mock
from mw4.logic.measure.measure import MeasureData
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    func = MeasureData(app=App())
    yield func


def test_property(function):
    function.framework = "raw"
    function.deviceName = "test"
    assert function.deviceName == "test"


def test_collectDataDevices(function):
    class Drivers:
        drivers = {}

    class MainWindowAddOns:
        addons = {"SettDevice": Drivers()}

    function.app.mainW.mainWindowAddons = MainWindowAddOns()
    function.app.deviceStat = {
        "sensor1Weather": object(),
        "directWeather": object(),
        "skymeter": object(),
        "filterwheel": object(),
        "focuser": object(),
        "power": object(),
        "camera": object(),
        "unknownDevice": object(),
    }
    function.app.mainW.mainWindowAddons.addons = {
        "SettDevice": mock.MagicMock()
    }
    function.app.mainW.mainWindowAddons.addons["SettDevice"].drivers = {
        "sensor1Weather": {"class": object()},
        "camera": {"class": object()},
    }
    function.collectDataDevices()
    assert "sensor1Weather" in function.devices
    assert "camera" in function.devices
    assert "focuser" not in function.devices


def test_clearData_1(function):
    function.devices = {'directWeather': object(),
                        'test': object()}
    function.clearData()


def test_startCommunication_1(function):
    function.framework = "raw"
    with mock.patch.object(function.run[function.framework], "startCommunication"):
        with mock.patch.object(function, "collectDataDevices"):
            with mock.patch.object(function, "clearData"):
                function.startCommunication()


def test_stopCommunication_1(function):
    function.framework = "raw"
    with mock.patch.object(function.run[function.framework], "stopCommunication"):
        function.stopCommunication()


def test_checkStart_1(function):
    function.checkStart()


def test_checkStart_2(function):
    function.shorteningStart = True
    function.checkStart()


def test_checkStart_3(function):
    function.data = {"time": [2, 2, 2]}
    function.shorteningStart = True
    function.checkStart()


def test_checkSize_1(function):
    function.data.clear()
    function.data["time"] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data["directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.MAXSIZE = 20
    function.checkSize()


def test_checkSize_2(function):
    function.data.clear()
    function.data["time"] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data["directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.MAXSIZE = 5
    function.checkSize()


def test_measureTask_1(function):
    function.mutexMeasure.lock()
    function.measureTask()
    function.mutexMeasure.unlock()


def test_measureTask_2(function):
    class Data:
        data = {
            "WEATHER_PARAMETERS.WEATHER_TEMPERATURE": 0,
            "WEATHER_PARAMETERS.WEATHER_PRESSURE": 0,
            "WEATHER_PARAMETERS.WEATHER_DEWPOINT": 0,
            "WEATHER_PARAMETERS.WEATHER_HUMIDITY": 0,
        }
    function.devices = {"directWeather": Data()}
    function.clearData()
    with mock.patch.object(function, "checkStart"):
        with mock.patch.object(function, "checkSize"):
            function.measureTask()
