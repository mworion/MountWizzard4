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


@pytest.fixture(autouse=True, scope="function")
def function():
    func = PegasusUPBAlpaca(parent=Parent())
    yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getAlpacaProperty"):
        function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=15):
        with mock.patch.object(function, "storePropertyToData"):
            function.workerPollData()


def test_workerPollData_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=21):
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
    with mock.patch.object(function, "setAlpacaProperty"):
        function.togglePowerPort("1")


def test_togglePowerPortBoot_1(function):
    function.deviceConnected = False
    function.togglePowerPortBoot("1")


def test_togglePowerPortBoot_2(function):
    function.deviceConnected = True
    function.togglePowerPortBoot("1")


def test_toggleHubUSB_1(function):
    function.deviceConnected = False
    function.toggleHubUSB()


def test_toggleHubUSB_2(function):
    function.deviceConnected = True
    function.toggleHubUSB()


def test_togglePortUSB_1(function):
    function.deviceConnected = False
    function.togglePortUSB("1")


def test_togglePortUSB_2(function):
    function.deviceConnected = True
    function.togglePortUSB("1")


def test_togglePortUSB_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=21):
        with mock.patch.object(function, "setAlpacaProperty"):
            function.togglePortUSB("1")


def test_toggleAutoDew_1(function):
    function.deviceConnected = False
    function.toggleAutoDew()


def test_toggleAutoDew_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=21):
        with mock.patch.object(function, "setAlpacaProperty"):
            function.toggleAutoDew()


def test_toggleAutoDew_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=15):
        with mock.patch.object(function, "setAlpacaProperty"):
            function.toggleAutoDew()


def test_sendDew_1(function):
    function.deviceConnected = False
    function.sendDew("1", 10)


def test_sendDew_2(function):
    function.deviceConnected = True
    function.sendDew("1", 10)


def test_sendDew_3(function):
    function.deviceConnected = True
    function.sendDew("1", 10)


def test_sendDew_4(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=21):
        with mock.patch.object(function, "setAlpacaProperty"):
            function.sendDew("1", 10)


def test_sendAdjustableOutput_1(function):
    function.deviceConnected = False
    function.sendAdjustableOutput(1)


def test_sendAdjustableOutput_2(function):
    function.deviceConnected = True
    function.sendAdjustableOutput(4)


def test_reboot_1(function):
    function.deviceConnected = False
    function.reboot()


def test_reboot_2(function):
    function.deviceConnected = True
    function.reboot()
