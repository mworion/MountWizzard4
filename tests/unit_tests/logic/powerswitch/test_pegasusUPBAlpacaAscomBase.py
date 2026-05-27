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
    DEVICE_TYPE = "switch"
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = PegasusUPBAlpaca(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_pollData_UPB(function):
    function.data["MaxSwitch"] = 15
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.pollData()
        assert function.data["FIRMWARE_INFO.VERSION"] == "1.4"


def test_pollData_UPBv2(function):
    function.data["MaxSwitch"] = 21
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.pollData()
        assert function.data["FIRMWARE_INFO.VERSION"] == "2.1"


def test_togglePowerPort(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.togglePowerPort("1")
    assert not function.commandQueue.empty()


def test_togglePowerPortBoot(function):
    function.togglePowerPortBoot("1")


def test_toggleHubUSB(function):
    function.toggleHubUSB()


def test_togglePortUSB_UPB(function):
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.togglePortUSB("1")
        assert function.commandQueue.empty()


def test_togglePortUSB_UPBv2(function):
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.togglePortUSB("1")
        assert not function.commandQueue.empty()


def test_toggleAutoDew_UPBv2(function):
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.toggleAutoDew()
        assert not function.commandQueue.empty()


def test_toggleAutoDew_UPB(function):
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.toggleAutoDew()
        assert not function.commandQueue.empty()


def test_sendDew_UPB(function):
    with mock.patch.object(function, "getDeviceProp", return_value=15):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.sendDew("A", 10)
        assert function.commandQueue.empty()


def test_sendDew_UPBv2(function):
    with mock.patch.object(function, "getDeviceProp", return_value=21):
        while not function.commandQueue.empty():
            function.commandQueue.get_nowait()
        function.sendDew("A", 10)
        assert not function.commandQueue.empty()


def test_sendAdjustableOutput(function):
    function.sendAdjustableOutput(1)


def test_reboot(function):
    function.reboot()
