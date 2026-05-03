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
import PySide6
import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.lightPanel.lightPanelAlpaca import LightPanelAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        func = LightPanelAlpaca(parent=Parent())
        yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=128):
        with mock.patch.object(function, "storePropertyToData"):
            function.workerPollData()


def test_lightOn_1(function):
    function.deviceConnected = False
    function.lightOn()


def test_lightOn_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.lightOn()
        m.assert_called_once_with("CalibratorOn", Brightness=127)


def test_lightOff_1(function):
    function.deviceConnected = False
    function.lightOff()


def test_lightOff_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.lightOff()
        m.assert_called_once_with("CalibratorOff")


def test_lightIntensity_1(function):
    function.deviceConnected = False
    function.lightIntensity(0)


def test_lightIntensity_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.lightIntensity(100.5)
        m.assert_called_once_with("CalibratorOn", Brightness=100)
