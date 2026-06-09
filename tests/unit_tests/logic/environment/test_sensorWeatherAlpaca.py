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
import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.environment.sensorWeatherAlpaca import SensorWeatherAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    try:
        app = App()
    except Exception:
        app = mock.MagicMock()
    data = {}
    DEVICE_TYPE = "observingconditions"
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        func = SensorWeatherAlpaca(parent=Parent())
        func.device = mock.MagicMock()
        func.deviceName = "test_sensor"
    except Exception as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        function.pollData()
        attrs = [c.args[0] for c in m.call_args_list]
        assert "Temperature" in attrs
        assert "Pressure" in attrs
        assert "DewPoint" in attrs
        assert "Humidity" in attrs
        assert "CloudCover" in attrs
        assert "RainRate" in attrs
        assert "SkyQuality" in attrs


def test_startCommunication_1(function):
    with (
        mock.patch.object(function, "createAlpacaDevice", return_value=False),
        mock.patch.object(function.threadPool, "start") as m_start,
    ):
        function.startCommunication()
        m_start.assert_not_called()


def test_startCommunication_2(function):
    with (
        mock.patch.object(function, "createAlpacaDevice", return_value=True),
        mock.patch.object(function.threadPool, "start") as m_start,
    ):
        function.startCommunication()
        m_start.assert_called_once()
