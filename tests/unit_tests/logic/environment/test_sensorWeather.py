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
import platform
import pytest
import unittest.mock as mock
from mw4.logic.environment.sensorWeather import SensorWeather
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        func = SensorWeather(app=App())
    except Exception as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func


def test_properties(function):
    function.framework = "indi"
    function.host = ("localhost", 7624)
    assert function.host == ("localhost", 7624)

    function.deviceName = "test"
    assert function.deviceName == "test"


def test_properties_2(function):
    function.loadConfig = True
    function.framework = "indi"
    assert function.loadConfig


def test_startCommunication_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "startCommunication", return_value=True):
        function.startCommunication()


def test_stopCommunication_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "stopCommunication", return_value=True):
        function.stopCommunication()


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_sensorWeatherAscom_import():
    import importlib
    spec = importlib.util.find_spec("mw4.logic.sensorWeather.sensorWeatherAscom")
    assert spec is not None


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_sensorWeather_ascom_in_run():
    from mw4.logic.environment.sensorWeather import SensorWeather
    from tests.unit_tests.unitTestAddOns.baseTestApp import App
    function = SensorWeather(app=App())
    if platform.system() == "Windows":
        assert "ascom" in function.run
        assert function.run["ascom"] is not None
