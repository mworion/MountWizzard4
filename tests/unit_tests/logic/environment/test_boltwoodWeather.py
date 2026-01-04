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
import pytest
import shutil
import unittest.mock as mock
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from mw4.logic.environment.sensorWeatherBoltwood import SensorWeatherBoltwood
from pathlib import Path
from tests.unit_tests.unitTestAddOns.baseTestApp import App

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
    shutil.copy("tests/testData/boltwood_test.txt", "tests/work/data/boltwood_test.txt")

    func = SensorWeatherBoltwood(parent=Parent())
    yield func


def test_startCommunication_1(function):
    function.enabled = False
    function.startCommunication()
    assert function.enabled  # as there is no real device


def test_stopCommunication_1(function):
    function.data = {"test": 1}
    function.enabled = True
    function.deviceConnected = True
    function.stopCommunication()
    assert not function.deviceConnected
    assert not function.enabled
    assert function.data == {}


def test_convert_knots2kmh_1(function):
    speedKmh = function.convert_knots2kmh(10)
    assert round(speedKmh, 3) == 18.52


def test_convert_knots2kmh_2(function):
    speedKmh = function.convert_knots2kmh(0)
    assert round(speedKmh, 3) == 0.0


def test_convert_mph2kmh_1(function):
    speedKmh = function.convert_mph2kmh(10)
    assert round(speedKmh, 3) == 16.093


def test_convert_mph2kmh_2(function):
    speedKmh = function.convert_mph2kmh(0)
    assert round(speedKmh, 3) == 0.0


def test_convertFtoC_1(function):
    tempC = function.convertFtoC(32)
    assert tempC == 0.0


def test_convertFtoC_2(function):
    tempC = function.convertFtoC(212)
    assert tempC == 100.0


def test_parseAndWriteBoltwoodData_1(function):
    rawData = "2018-01-17 14:51:45.00 F M 35.9   78.1  78     10      45  56.1   000 0 0 00020 043117.61927 1 1 1 3 0 0"
    assert function.parseAndWriteBoltwoodData(rawData)
    assert round(function.data["SKY_QUALITY.SKY_BRIGHTNESS"], 3) == 2.167
    assert round(function.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"], 3) == 25.611
    assert round(function.data["WEATHER_PARAMETERS.WEATHER_HUMIDITY"], 3) == 45.0
    assert round(function.data["WEATHER_PARAMETERS.WEATHER_DEWPOINT"], 3) == 13.389
    assert round(function.data["WEATHER_PARAMETERS.WIND_SPEED"], 3) == 16.093


def test_parseAndWriteBoltwoodData_2(function):
    rawData = "2018-01-17 14:51:45.00 C K 35.9   78.1  78     10      45  56.1   000 0 0 00020 043117.61927 1 1 1 3 0 0"
    assert function.parseAndWriteBoltwoodData(rawData)
    assert round(function.data["SKY_QUALITY.SKY_BRIGHTNESS"], 3) == 35.9
    assert round(function.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"], 3) == 78.1
    assert round(function.data["WEATHER_PARAMETERS.WEATHER_HUMIDITY"], 3) == 45.0
    assert round(function.data["WEATHER_PARAMETERS.WEATHER_DEWPOINT"], 3) == 56.1
    assert round(function.data["WEATHER_PARAMETERS.WIND_SPEED"], 3) == 18.52


def test_parseAndWriteBoltwoodData_3(function):
    rawData = "2018-01-17 14:51:45.00"
    assert not function.parseAndWriteBoltwoodData(rawData)


def test_processBoltwoodData_1(function):
    with mock.patch.object(Path, "is_file", return_value=False):
        assert not function.processBoltwoodData(Path())


def test_processBoltwoodData_2(function):
    filePath = Path("tests/work/data/boltwood_test.txt")
    with mock.patch.object(function, "parseAndWriteBoltwoodData", return_value=False):
        assert not function.processBoltwoodData(filePath)


def test_processBoltwoodData_3(function):
    filePath = Path("tests/work/data/boltwood_test.txt")
    with mock.patch.object(function, "parseAndWriteBoltwoodData", return_value=True):
        assert function.processBoltwoodData(filePath)


def test_pollBoltwoodData_1(function):
    function.enabled = False
    function.deviceConnected = False
    function.pollBoltwoodData()


def test_pollBoltwoodData_2(function):
    function.deviceConnected = True
    function.enabled = True
    function.filePath = "tests/work/data/boltwood_testwrong.txt"
    with mock.patch.object(function, "processBoltwoodData", return_value=False):
        function.pollBoltwoodData()
        assert not function.deviceConnected
        assert not function.enabled


def test_pollBoltwoodData_3(function):
    function.deviceConnected = False
    function.enabled = True
    function.filePath = "tests/work/data/boltwood_testwrong.txt"
    with mock.patch.object(function, "processBoltwoodData", return_value=True):
        function.pollBoltwoodData()
        assert function.deviceConnected
        assert function.enabled
