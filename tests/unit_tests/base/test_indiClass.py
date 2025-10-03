############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock

import base.indiClass
import pytest
from base.indiClass import IndiClass
from base.signalsDevices import Signals
from indibase.indiDevice import Device

# external packages
# local import
from PySide6.QtCore import QTimer

from tests.unit_tests.unitTestAddOns.baseTestApp import App

host_ip = "127.0.0.1"


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    with mock.patch.object(QTimer, "start"):
        func = IndiClass(parent=Parent())
        yield func


def test_properties(function):
    function.deviceName = "test"
    assert function.deviceName == "test"
    function.host = ("localhost", 7624)
    assert function.host == ("localhost", 7624)
    function.hostaddress = "localhost"
    assert function.hostaddress == "localhost"
    function.port = 7624
    assert function.port == 7624


def test_serverConnected_1(function):
    function.deviceName = ""
    function.serverConnected()


def test_serverConnected_2(function):
    function.deviceName = "test"
    with mock.patch.object(function.client, "watchDevice", return_value=True) as call:
        function.serverConnected()
        call.assert_called_with("test")


def test_serverDisconnected(function):
    function.serverDisconnected({"test": "test"})


def test_newDevice_1(function):
    function.deviceName = "false"
    with mock.patch.object(function.client, "getDevice", return_value=None):
        function.newDevice("test")
        assert None is function.device


def test_newDevice_2(function):
    function.deviceName = "test"
    with mock.patch.object(function.client, "getDevice", return_value=Device()):
        function.newDevice("test")
        assert function.device is not None


def test_removeDevice_1(function):
    function.deviceName = "test"
    function.device = Device()
    function.data = {"test": 1}
    function.removeDevice("foo")


def test_removeDevice_2(function):
    function.deviceName = "test"
    function.device = Device()
    function.data = {"test": 1}
    function.removeDevice("test")
    assert function.data == {}
    assert function.device is None


def test_startRetry_1(function):
    function.deviceName = ""
    function.startRetry()


def test_startRetry_2(function):
    function.deviceName = "test"
    function.device = Device()
    function.client.connected = True
    with mock.patch.object(function.client, "connectServer", return_value=True):
        function.startRetry()


def test_startRetry_3(function):
    function.deviceName = "test"
    function.device = Device()
    function.client.connected = False
    with mock.patch.object(function.client, "connectServer", return_value=True):
        function.startRetry()


def test_startCommunication_1(function):
    function.data = {}
    with mock.patch.object(function.client, "connectServer", return_value=False):
        with mock.patch.object(function.timerRetry, "start"):
            function.startCommunication()


def test_startCommunication_2(function):
    function.data = {}
    with mock.patch.object(function.client, "connectServer", return_value=True):
        with mock.patch.object(function.timerRetry, "start"):
            function.startCommunication()


def test_stopCommunication_1(function):
    with mock.patch.object(function.client, "disconnectServer", return_value=False):
        function.stopCommunication()


def test_stopCommunication_2(function):
    with mock.patch.object(function.client, "disconnectServer", return_value=True):
        function.stopCommunication()


def test_connectDevice1(function):
    with mock.patch.object(function.client, "connectDevice", return_value=False):
        function.connectDevice("test", "test")


def test_connectDevice2(function):
    with mock.patch.object(function.client, "connectDevice", return_value=False):
        function.connectDevice("test", "CONNECTION")


def test_connectDevice3(function):
    function.deviceName = "test"
    with mock.patch.object(function.client, "connectDevice", return_value=True):
        function.connectDevice("test", "CONNECTION")


def test_connectDevice4(function):
    function.deviceName = "test"
    with mock.patch.object(function.client, "connectDevice", return_value=False):
        function.connectDevice("test", "CONNECTION")


def test_loadDefaultConfig_1(function):
    function.loadIndiConfigFlag = False
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"test": 1}):
        function.loadIndiConfig("test")


def test_loadDefaultConfig_2(function):
    function.loadIndiConfigFlag = True
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"test": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.loadIndiConfig("test")


def test_loadDefaultConfig_3(function):
    function.loadIndiConfigFlag = True
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"test": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.loadIndiConfig("test")


def test_setUpdateConfig_1(function):
    function.deviceName = ""
    function.loadConfig = True
    with mock.patch.object(function, "loadIndiConfig"):
        function.setUpdateConfig("test")


def test_setUpdateConfig_2(function):
    function.deviceName = "test"
    function.loadConfig = True
    with mock.patch.object(function, "loadIndiConfig"):
        function.setUpdateConfig("test")


def test_setUpdateConfig_3(function):
    function.deviceName = "test"
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    with mock.patch.object(function, "loadIndiConfig"):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.setUpdateConfig("test")


def test_convertIndigoProperty_1(function):
    function.INDIGO = {"test": "test1"}
    val = function.convertIndigoProperty("test")
    assert val == "test1"


def test_updateNumber_1(function):
    function.updateNumber("telescope", "test")


def test_updateNumber_2(function):
    function.device = Device()
    function.updateNumber("telescope", "test")


def test_updateNumber_3(function):
    function.data = {}
    function.device = Device()
    function.deviceName = "telescope"
    with mock.patch.object(function.device, "getNumber", return_value={"test": 1}):
        function.updateNumber("telescope", "test")


def test_updateText_1(function):
    function.updateText("telescope", "test")


def test_updateText_2(function):
    function.device = Device()
    function.updateText("telescope", "test")


def test_updateText_3(function):
    function.data = {}
    function.device = Device()
    function.deviceName = "telescope"
    with mock.patch.object(function.device, "getText", return_value={"test": 1}):
        function.updateText("telescope", "test")


def test_updateSwitch_1(function):
    function.updateSwitch("telescope", "test")


def test_updateSwitch_2(function):
    function.device = Device()
    function.updateSwitch("telescope", "test")


def test_updateSwitch_3(function):
    function.data = {}
    function.device = Device()
    function.deviceName = "telescope"
    with mock.patch.object(function.device, "getSwitch", return_value={"test": 1}):
        function.updateSwitch("telescope", "test")


def test_updateSwitch_4(function):
    function.data = {}
    function.device = Device()
    function.deviceName = "telescope"
    with mock.patch.object(function.device, "getSwitch", return_value={"test": 1}):
        function.updateSwitch("telescope", "PROFILE")


def test_updateLight_1(function):
    function.updateLight("telescope", "test")


def test_updateLight_2(function):
    function.device = Device()
    function.updateLight("telescope", "test")


def test_updateLight_3(function):
    function.data = {}
    function.device = Device()
    function.deviceName = "telescope"
    with mock.patch.object(function.device, "getLight", return_value={"test": 1}):
        function.updateLight("telescope", "test")


def test_updateBLOB_1(function):
    function.updateBLOB("telescope", "test")


def test_updateBLOB_2(function):
    function.device = Device()
    function.updateBLOB("telescope", "test")


def test_updateBLOB_3(function):
    function.device = Device()
    function.deviceName = "telescope"
    function.updateBLOB("telescope", "test")


def test_removePrefix_1(function):
    value = function.removePrefix("", "")
    assert value == ""


def test_removePrefix_2(function):
    value = function.removePrefix("NOT should not be shown", "NOT")
    assert value == "should not be shown"


def test_updateMessage_1(function):
    function.messages = False
    function.updateMessage("test", "text")


def test_updateMessage_2(function):
    function.messages = True
    function.updateMessage("test", "text")


def test_updateMessage_3(function):
    function.messages = True
    function.updateMessage("test", "[WARNING] should not be shown")


def test_updateMessage_4(function):
    function.messages = True
    function.updateMessage("test", "[ERROR] should not be shown")


def test_updateMessage_5(function):
    function.messages = True
    function.updateMessage("test", "NOT should not be shown")


def test_updateMessage_6(function):
    function.messages = True
    function.updateMessage("test", "[INFO] should not be shown")


def test_addDiscoveredDevice_1(function):
    device = Device()
    function.indiClass = IndiClass(parent=Parent())
    with mock.patch.object(device, "getText", return_value={"DRIVER_INTERFACE": None}):
        function.addDiscoveredDevice("telescope", "test")


def test_addDiscoveredDevice_2(function):
    function.indiClass = IndiClass(parent=Parent())
    function.indiClass.client.devices["telescope"] = {}
    function.addDiscoveredDevice("telescope", "DRIVER_INFO")


def test_addDiscoveredDevice_3(function):
    device = Device()
    function.indiClass = IndiClass(parent=Parent())
    function.client.devices["telescope"] = device
    function.discoverType = None
    with mock.patch.object(device, "getText", return_value={}):
        function.addDiscoveredDevice("telescope", "DRIVER_INFO")


def test_addDiscoveredDevice_4(function):
    device = Device()
    function.indiClass = IndiClass(parent=Parent())
    function.client.devices["telescope"] = device
    function.discoverType = None
    function.discoverList = list()
    with mock.patch.object(device, "getText", return_value={"DRIVER_INTERFACE": "0"}):
        function.addDiscoveredDevice("telescope", "DRIVER_INFO")


def test_addDiscoveredDevice_5(function):
    device = Device()
    function.indiClass = IndiClass(parent=Parent())
    function.client.devices["telescope"] = device
    function.discoverType = 1
    function.discoverList = list()
    with mock.patch.object(device, "getText", return_value={"DRIVER_INTERFACE": 1}):
        function.addDiscoveredDevice("telescope", "DRIVER_INFO")


def test_discoverDevices_1(function):
    with mock.patch.object(base.indiClass, "sleepAndEvents"):
        val = function.discoverDevices("dome")
        assert val == []
