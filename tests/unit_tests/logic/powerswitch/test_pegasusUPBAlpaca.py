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
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.powerswitch.pegasusUPBAlpaca import PegasusUPBAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = PegasusUPBAlpaca(parent=Parent())
    yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "callDeviceMethod"):
        function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        with mock.patch.object(function, "callDeviceMethod", return_value=True):
            with mock.patch.object(function, "storePropertyToData"):
                function.workerPollData()


def test_workerPollData_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        with mock.patch.object(
            function, "callDeviceMethod", return_value=1.0
        ):
            with mock.patch.object(function, "storePropertyToData"):
                function.workerPollData()


def test_togglePowerPort_1(function):
    function.deviceConnected = False
    function.togglePowerPort("1")


def test_togglePowerPort_2(function):
    function.deviceConnected = True
    function.togglePowerPort("1")


def test_togglePowerPort_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callDeviceMethod"):
        function.togglePowerPort("1")


def test_togglePowerPortBoot_1(function):
    function.togglePowerPortBoot("1")


def test_toggleHubUSB_1(function):
    function.toggleHubUSB()


def test_togglePortUSB_1(function):
    function.deviceConnected = False
    function.togglePortUSB("1")


def test_togglePortUSB_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        function.togglePortUSB("1")


def test_togglePortUSB_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        with mock.patch.object(function, "callDeviceMethod"):
            function.togglePortUSB("1")


def test_toggleAutoDew_1(function):
    function.deviceConnected = False
    function.toggleAutoDew()


def test_toggleAutoDew_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        with mock.patch.object(function, "callDeviceMethod"):
            function.toggleAutoDew()


def test_toggleAutoDew_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        with mock.patch.object(function, "callDeviceMethod"):
            function.toggleAutoDew()


def test_sendDew_1(function):
    function.deviceConnected = False
    function.sendDew("A", 10)


def test_sendDew_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        function.sendDew("A", 10)


def test_sendDew_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        with mock.patch.object(function, "callDeviceMethod"):
            function.sendDew("A", 10)


def test_sendAdjustableOutput_1(function):
    function.sendAdjustableOutput(1)


def test_reboot_1(function):
    function.reboot()
