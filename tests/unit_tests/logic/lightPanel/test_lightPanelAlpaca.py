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
from mw4.logic.lightPanel.lightPanelAlpaca import LightPanelAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    DEVICE_TYPE = "covercalibrator"
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = LightPanelAlpaca(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        function.pollData()
        assert m.call_count == 2
        attrs = [c.args[0] for c in m.call_args_list]
        assert "Brightness" in attrs
        assert "MaxBrightness" in attrs


def test_pollData_2(function):
    function.data["FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"] = 100
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.pollData()
    assert function.data["FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON"] == 1


def test_lightOn_1(function):
    function.app.lightPanel.data = {
        "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX": 254
    }
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.lightOn()
    item = function.commandQueue.get_nowait()
    assert item.valueProp == "CalibratorOn"
    assert item.kwargs == {"BrightnessVal": 127}


def test_lightOff_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.lightOff()
    item = function.commandQueue.get_nowait()
    assert item.valueProp == "CalibratorOff"


def test_lightIntensity_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.lightIntensity(100.5)
    item = function.commandQueue.get_nowait()
    assert item.valueProp == "CalibratorOn"
    assert item.kwargs == {"BrightnessVal": 100.5}


def test_startCommunication_1(function):
    with mock.patch.object(function, "createAlpacaDevice", return_value=False):
        with mock.patch.object(function.threadPool, "start") as m_start:
            function.startCommunication()
            m_start.assert_not_called()


def test_startCommunication_2(function):
    with mock.patch.object(function, "createAlpacaDevice", return_value=True):
        with mock.patch.object(function.threadPool, "start") as m_start:
            function.startCommunication()
            m_start.assert_called_once()

