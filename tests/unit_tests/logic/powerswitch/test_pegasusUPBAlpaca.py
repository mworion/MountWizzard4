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
from mw4.logic.powerswitch.pegasusUPBAlpaca import PegasusUPBAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    deviceType = "switch"
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = PegasusUPBAlpaca(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        with mock.patch.object(function, "callDeviceMethod", return_value=True):
            with mock.patch.object(function, "storePropertyToData"):
                function.pollData()


def test_pollData_2(function):
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        with mock.patch.object(function, "callDeviceMethod", return_value=1.0):
            with mock.patch.object(function, "storePropertyToData"):
                function.pollData()


def test_togglePowerPort_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.togglePowerPort("1")
    assert not function.commandQueue.empty()


def test_togglePowerPortBoot_1(function):
    function.togglePowerPortBoot("1")


def test_toggleHubUSB_1(function):
    function.toggleHubUSB()


def test_togglePortUSB_1(function):
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.togglePortUSB("1")
        assert function.commandQueue.empty()


def test_togglePortUSB_2(function):
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.togglePortUSB("1")
        assert not function.commandQueue.empty()


def test_toggleAutoDew_1(function):
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.toggleAutoDew()
        assert not function.commandQueue.empty()


def test_toggleAutoDew_2(function):
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.toggleAutoDew()
        assert not function.commandQueue.empty()


def test_sendDew_1(function):
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.sendDew("A", 10)
        assert function.commandQueue.empty()


def test_sendDew_2(function):
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.sendDew("A", 10)
        assert not function.commandQueue.empty()


def test_sendAdjustableOutput_1(function):
    function.sendAdjustableOutput(1)


def test_reboot_1(function):
    function.reboot()
