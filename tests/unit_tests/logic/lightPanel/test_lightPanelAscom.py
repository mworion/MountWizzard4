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
from mw4.base.signalsDevices import Signals
from mw4.logic.lightPanel.lightPanelAscom import LightPanelAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    signals = Signals()
    deviceType = ""
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = LightPanelAscom(parent=Parent())
    func.device = mock.MagicMock()
    func.device.Brightness = 100
    func.device.MaxBrightness = 255
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.pollData()


def test_lightOn(function):
    function.app.dReg.drivers["lightPanel"]["class"].data = {"FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX": 200}
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.lightOn()
    m.assert_called_once_with("CalibratorOn", BrightnessVal=100)


def test_lightOff(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.lightOff()
    m.assert_called_once_with("CalibratorOff")


def test_lightIntensity(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.lightIntensity(128.0)
    m.assert_called_once_with("CalibratorOn", BrightnessVal=128.0)
