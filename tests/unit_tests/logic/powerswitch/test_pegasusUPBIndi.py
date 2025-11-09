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
# standard libraries
import unittest.mock as mock

import pytest

from mw4.base.indiClass import IndiClass
from mw4.base.signalsDevices import Signals
from mw4.indibase.indiClient import Client

# external packages
from mw4.indibase.indiDevice import Device
from mw4.logic.powerswitch.pegasusUPBIndi import PegasusUPBIndi

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    func = PegasusUPBIndi(parent=Parent())
    yield func


def test_setUpdateConfig_3(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"Test": 1}):
        function.setUpdateConfig("test")


def test_setUpdateConfig_4(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=False):
            function.setUpdateConfig("test")


def test_setUpdateConfig_5(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.setUpdateConfig("test")


def test_updateText_1(function):
    function.updateText("test", "test")


def test_updateText_2(function):
    function.data = {"AUTO_DEW.DEW_C": 1, "VERSION.UPB": 1}
    with mock.patch.object(IndiClass, "updateText", return_value=True):
        function.updateText("test", "test")


def test_updateText_3(function):
    function.data = {"DRIVER_INFO.DEVICE_MODEL": "UPB", "FIRMWARE_INFO.VERSION": "1.4"}

    with mock.patch.object(IndiClass, "updateText", return_value=True):
        function.updateText("test", "DRIVER_INFO")


def test_updateText_4(function):
    function.data = {
        "DRIVER_INFO.DEVICE_MODEL": "UPBv2",
        "FIRMWARE_INFO.VERSION": "1.5",
    }

    with mock.patch.object(IndiClass, "updateText", return_value=True):
        function.updateText("test", "DRIVER_INFO")


def test_updateText_5(function):
    function.data = {
        "DRIVER_INFO.DEVICE_MODEL": "UPBv2",
        "FIRMWARE_INFO.VERSION": "1.4",
    }
    with mock.patch.object(IndiClass, "updateText", return_value=True):
        function.updateText("test", "DRIVER_INFO")


def test_updateText_6(function):
    function.data = {"DRIVER_INFO.DEVICE_MODEL": "UPB", "FIRMWARE_INFO.VERSION": "1.5"}
    with mock.patch.object(IndiClass, "updateText", return_value=True):
        function.updateText("test", "DRIVER_INFO")


def test_updateNumber_1(function):
    function.updateNumber("test", "test")


def test_updateNumber_2(function):
    function.data = {"AUTO_DEW.DEW_C": 1, "VERSION.UPB": 1}
    with mock.patch.object(IndiClass, "updateNumber", return_value=True):
        function.updateNumber("test", "test")


def test_updateSwitch_1(function):
    function.updateSwitch("test", "test")


def test_updateSwitch_2(function):
    function.data = {"AUTO_DEW.AUTO_DEW_ENABLED": 1, "VERSION.UPB": 2}
    with mock.patch.object(IndiClass, "updateSwitch", return_value=True):
        function.updateSwitch("test", "test")


def test_togglePowerPort_2(function):
    function.device = None
    function.togglePowerPort(port=1)


def test_togglePowerPort_3(function):
    function.device = Device()
    with mock.patch.object(
        function.device, "getSwitch", return_value={"POWER_CONTROL_0": "On"}
    ):
        function.togglePowerPort(port=1)


def test_togglePowerPort_4(function):
    function.device = Device()
    with mock.patch.object(
        function.device, "getSwitch", return_value={"POWER_CONTROL_1": "On"}
    ):
        function.togglePowerPort(port=1)


def test_togglePowerPort_5(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device, "getSwitch", return_value={"OUTLET_1": "On"}):
        function.togglePowerPort(port=1)


def test_togglePowerPort_6(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device, "getSwitch", return_value={"OUTLET_1": "Off"}):
        function.togglePowerPort(port=1)


def test_togglePowerPortBoot_2(function):
    function.device = None
    function.togglePowerPortBoot(port=1)


def test_togglePowerPortBoot_3(function):
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"POWER_PORT_0": "On"}):
        function.togglePowerPortBoot(port=1)


def test_togglePowerPortBoot_4(function):
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"POWER_PORT_1": "On"}):
        function.togglePowerPortBoot(port=1)


def test_togglePowerPortBoot_5(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device, "getSwitch", return_value={"POWER_PORT_1": "On"}):
        function.togglePowerPortBoot(port=1)


def test_togglePowerPortBoot_6(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device, "getSwitch", return_value={"POWER_PORT_1": "Off"}):
        function.togglePowerPortBoot(port=1)


def test_togglePowerPortBoot_7(function):
    function.device = Device()
    function.isINDIGO = False
    with mock.patch.object(function.device, "getSwitch", return_value={"POWER_PORT_1": "Off"}):
        function.togglePowerPortBoot(port=1)


def test_toggleHubUSB_1(function):
    function.toggleHubUSB()


def test_toggleHubUSB_2(function):
    function.toggleHubUSB()


def test_toggleHubUSB_3(function):
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"test": "On"}):
        function.toggleHubUSB()


def test_toggleHubUSB_4(function):
    function.device = Device()
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={"INDI_ENABLED": "On", "INDI_DISABLED": "Off"},
    ):
        function.toggleHubUSB()


def test_toggleHubUSB_5(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={"INDI_ENABLED": "On", "INDI_DISABLED": "Off"},
    ):
        function.toggleHubUSB()


def test_toggleHubUSB_6(function):
    function.device = Device()
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={"INDI_ENABLED": "Off", "INDI_DISABLED": "On"},
    ):
        function.toggleHubUSB()


def test_togglePortUSB_2(function):
    function.device = None
    function.togglePortUSB(port="1")


def test_togglePortUSB_3(function):
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"PORT_1": "On"}):
        function.togglePortUSB(port="1")


def test_togglePortUSB_4(function):
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"PORT_1": "On"}):
        function.togglePortUSB(port="0")


def test_togglePortUSB_5(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device, "getSwitch", return_value={"PORT_1": "On"}):
        function.togglePortUSB(port="0")


def test_togglePortUSB_6(function):
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"PORT_0": "Off"}):
        function.togglePortUSB(port="0")


def test_toggleAutoDew_1(function):
    function.toggleAutoDew()


def test_toggleAutoDew_2(function):
    function.device = Device()
    function.modelVersion = 1
    function.toggleAutoDew()


def test_toggleAutoDew_2b(function):
    function.device = Device()
    function.modelVersion = 0
    function.toggleAutoDew()


def test_toggleAutoDew_3(function):
    function.device = Device()
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={
            "INDI_ENABLED": "On",
            "INDI_DISABLED": "On",
            "DEW_A": "On",
            "DEW_B": "On",
            "DEW_C": "On",
        },
    ):
        function.toggleAutoDew()


def test_toggleAutoDew_4(function):
    function.device = Device()
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={
            "INDI_ENABLED": "On",
            "INDI_DISABLED": "On",
            "DEW_A": "On",
            "DEW_B": "On",
            "DEW_C": "On",
        },
    ):
        function.toggleAutoDew()


def test_toggleAutoDew_5(function):
    function.device = Device()
    function.modelVersion = 1
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={
            "INDI_ENABLED": "On",
            "INDI_DISABLED": "On",
            "DEW_A": "Off",
            "DEW_B": "On",
            "DEW_C": "On",
        },
    ):
        function.toggleAutoDew()


def test_toggleAutoDew_6(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={
            "MANUAL": "On",
            "AUTOMATIC": "Off",
            "DEW_A": "On",
            "DEW_B": "On",
            "DEW_C": "On",
        },
    ):
        function.toggleAutoDew()


def test_toggleAutoDew_7(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={
            "MANUAL": "Off",
            "AUTOMATIC": "Off",
            "DEW_A": "Off",
            "DEW_B": "On",
            "DEW_C": "On",
        },
    ):
        function.toggleAutoDew()


def test_toggleAutoDew_8(function):
    function.device = Device()
    function.modelVersion = 1
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={
            "INDI_ENABLED": "Off",
            "INDI_DISABLED": "On",
            "DEW_A": "On",
            "DEW_B": "On",
            "DEW_C": "On",
        },
    ):
        function.toggleAutoDew()


def test_toggleAutoDew_9(function):
    function.device = Device()
    function.modelVersion = 2
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={
            "INDI_ENABLED": "On",
            "INDI_DISABLED": "On",
            "DEW_A": "Off",
            "DEW_B": "On",
            "DEW_C": "On",
        },
    ):
        function.toggleAutoDew()


def test_sendDew_3(function):
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"DEW_1": 50}):
        function.sendDew(port=1)


def test_sendDew_4(function):
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"DEW_1": 50}):
        function.sendDew(port="A")


def test_sendDew_5(function):
    function.device = Device()
    function.isINDIGO = "On"
    with mock.patch.object(function.device, "getNumber", return_value={"OUTLET_1": 50}):
        function.sendDew(port="A")


def test_sendAdjustableOutput_2(function):
    function.device = None
    function.sendAdjustableOutput(10)


def test_sendAdjustableOutput_3(function):
    function.device = Device()
    with mock.patch.object(
        function.device, "getNumber", return_value={"ADJUSTABLE_VOLTAGE": 12}
    ):
        function.sendAdjustableOutput(10)


def test_sendAdjustableOutput_4(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(
        function.device, "getNumber", return_value={"ADJUSTABLE_VOLTAGE": 12}
    ):
        function.sendAdjustableOutput(10)


def test_reboot_1(function):
    function.reboot()


def test_reboot_2(function):
    function.device = Device()
    function.reboot()


def test_reboot_3(function):
    function.device = Device()
    function.isINDIGO = True
    function.reboot()


def test_reboot_4(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device, "getSwitch", return_value={"REBOOT": "On"}):
        function.reboot()
