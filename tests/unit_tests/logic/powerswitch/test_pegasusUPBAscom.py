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
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from mw4.logic.powerswitch.pegasusUPBAscom import PegasusUPBAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = PegasusUPBAscom(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_pollData_UPB(function):
    function.data["MaxSwitch"] = 15
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        function.pollData()
    assert function.data["FIRMWARE_INFO.VERSION"] == "1.4"


def test_pollData_UPBv2(function):
    function.data["MaxSwitch"] = 21
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        function.pollData()
    assert function.data["FIRMWARE_INFO.VERSION"] == "2.1"


def test_togglePowerPort(function):
    function.data["MaxSwitch"] = 15
    function.data["POWER_CONTROL.POWER_CONTROL_1"] = True
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.togglePowerPort("1")
    m.assert_called_once_with("SetSwitch", Id=0, State=False)


def test_togglePowerPortBoot(function):
    function.togglePowerPortBoot("1")


def test_toggleHubUSB(function):
    function.toggleHubUSB()


def test_togglePortUSB_UPB(function):
    function.data["MaxSwitch"] = 15
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.togglePortUSB("1")
    m.assert_not_called()


def test_togglePortUSB_UPBv2(function):
    function.data["MaxSwitch"] = 21
    function.data["USB_PORT_CONTROL.PORT_1"] = True
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.togglePortUSB("1")
    m.assert_called_once_with("SetSwitch", Id=7, State=False)


def test_toggleAutoDew_UPB(function):
    function.data["MaxSwitch"] = 15
    function.data["AUTO_DEW.INDI_ENABLED"] = False
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.toggleAutoDew()
    m.assert_called_once_with("SetSwitch", Id=7, State=True)


def test_toggleAutoDew_UPBv2(function):
    function.data["MaxSwitch"] = 21
    function.data["AUTO_DEW.DEW_A"] = False
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.toggleAutoDew()
    m.assert_called_once_with("SetSwitch", Id=13, State=True)


def test_sendDew_UPB(function):
    function.data["MaxSwitch"] = 15
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.sendDew("A", 50.0)
    m.assert_not_called()


def test_sendDew_UPBv2(function):
    function.data["MaxSwitch"] = 21
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.sendDew("A", 50.0)
    m.assert_called_once_with("SetSwitchValue", Id=4, Value=127)


def test_sendAdjustableOutput(function):
    function.sendAdjustableOutput(1.0)


def test_reboot(function):
    function.reboot()
