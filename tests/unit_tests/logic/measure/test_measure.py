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
# License APL2.0
#
###########################################################
import numpy as np
import pytest
import unittest.mock as mock
from mw4.logic.measure.measure import MeasureData
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Data:
    def __init__(self, data):
        self.data = data


@pytest.fixture(autouse=True, scope="module")
def function():
    func = MeasureData(app=App())
    yield func


def test_property(function):
    function.framework = "raw"
    function.deviceName = "test"
    assert function.deviceName == "test"


def test_collectDataDevices(function):
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
    activeDrivers = {
        "sensor1Weather": {"class": object()},
        "camera": {"class": object()},
    }
    with mock.patch.object(function.app, "getActiveDrivers", return_value=activeDrivers):
        function.collectDataDevices()
        assert "camera" in function.devices
        assert "focuser" in function.devices
        assert "directWeather" in function.devices


def test_collectDataDevices_unknownActiveDriver(function):
    function.app.deviceStat = {
        "sensor1Weather": object(),
        "unknownDevice": object(),
    }
    activeDrivers = {
        "sensor1Weather": {"class": object()},
        "unknownDevice": {"class": object()},
    }
    with mock.patch.object(function.app, "getActiveDrivers", return_value=activeDrivers):
        function.collectDataDevices()
        assert "sensor1Weather" in function.devices
        assert "unknownDevice" not in function.devices


def test_collectDataDevices_driverClassNone(function):
    # Since collectDataDevices now uses app.dReg.drivers directly (not activeDrivers),
    # all devices that are in measure dict and have a class will be included
    function.collectDataDevices()
    assert "camera" in function.devices
    assert "focuser" in function.devices
    assert "directWeather" in function.devices


def test_clearData_1(function):
    function.devices = {"directWeather": object(), "test": object()}
    function.clearData()


def test_startCommunication_1(function):
    function.framework = "raw"
    with (
        mock.patch.object(function.run[function.framework], "startCommunication"),
        mock.patch.object(function, "collectDataDevices"),
        mock.patch.object(function, "clearData"),
    ):
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
    function.data["directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0]
    )
    function.MAXSIZE = 20
    function.checkSize()


def test_checkSize_2(function):
    function.data.clear()
    function.data["time"] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data["directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0]
    )
    function.MAXSIZE = 5
    function.checkSize()


def test_measureTask_1(function):
    function.mutexMeasure.lock()
    function.measureTask()
    function.mutexMeasure.unlock()


def test_measureTask_2(function):
    data = {
        "WEATHER_PARAMETERS.WEATHER_TEMPERATURE": 0,
        "WEATHER_PARAMETERS.WEATHER_PRESSURE": 0,
        "WEATHER_PARAMETERS.WEATHER_DEWPOINT": 0,
        "WEATHER_PARAMETERS.WEATHER_HUMIDITY": 0,
    }

    function.devices = {"directWeather": Data(data=data)}
    function.clearData()
    with (
        mock.patch.object(function, "checkStart"),
        mock.patch.object(function, "checkSize"),
    ):
        function.measureTask()
