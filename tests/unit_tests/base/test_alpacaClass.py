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
import alpaca.management as alpacaMgmt
import PySide6
import pytest
import time
from alpaca.exceptions import NotImplementedException as AlpycaNotImplError
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from PySide6.QtCore import QTimer
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

setupLogging()


@pytest.fixture(autouse=True, scope="function")
def function():
    class Parent:
        app = App()
        data = {}
        signals = Signals()

    with mock.patch.object(QTimer, "start"):
        func = AlpacaClass(parent=Parent())
        yield func


def test_properties_1(function):
    function.host = ("localhost", 11111)
    function.hostaddress = "localhost"
    function.port = 11111
    function.deviceName = "test"
    function.deviceName = "test:2"
    function.apiVersion = 1
    function.protocol = "1"


def test_properties_2(function):
    host = function.host
    assert host == ("localhost", 11111)
    assert function.hostaddress == "localhost"
    assert function.port == 11111
    assert function.deviceName == ""
    assert function.apiVersion == 1
    assert function.protocol == "http"


def test_properties_3(function):
    function.deviceName = "test:camera:3"
    assert function.deviceName == "test:camera:3"
    assert function.deviceType == "camera"
    assert function.number == 3


def test_createAlpacaDevice_1(function):
    function.deviceType = "camera"
    function.number = 0
    suc = function.createAlpacaDevice()
    assert suc
    assert function.device is not None


def test_createAlpacaDevice_2(function):
    function.deviceType = "unknown"
    suc = function.createAlpacaDevice()
    assert not suc


def test_createAlpacaDevice_3(function):
    function.deviceType = "dome"
    function.number = 0

    class RaisingClass:
        def __init__(self, *args, **kwargs):
            raise Exception("error")

    with mock.patch.dict(AlpacaClass.DEVICE_TYPE_MAP, {"dome": RaisingClass}):
        suc = function.createAlpacaDevice()
        assert not suc


def test_getDeviceProp_1(function):
    function.device = None
    result = function.getDeviceProp("Connected")
    assert result is None


def test_getDeviceProp_2(function):
    function.propertyExceptions = ["Connected"]
    function.device = mock.MagicMock()
    result = function.getDeviceProp("Connected")
    assert result is None


def test_getDeviceProp_3(function):
    function.propertyExceptions = []
    function.device = mock.MagicMock()
    function.device.Connected = True
    result = function.getDeviceProp("Connected")
    assert result is True


def test_getDeviceProp_4(function):
    function.propertyExceptions = []
    function.device = mock.MagicMock()
    type(function.device).TestProp = mock.PropertyMock(
        side_effect=AlpycaNotImplError("not implemented")
    )
    result = function.getDeviceProp("TestProp")
    assert result is None
    assert "TestProp" in function.propertyExceptions


def test_getDeviceProp_5(function):
    function.propertyExceptions = []
    function.device = mock.MagicMock()
    type(function.device).TestProp = mock.PropertyMock(
        side_effect=Exception("error")
    )
    result = function.getDeviceProp("TestProp")
    assert result is None


def test_setDeviceProp_1(function):
    function.device = None
    result = function.setDeviceProp("Connected", True)
    assert not result


def test_setDeviceProp_2(function):
    function.propertyExceptions = ["Connected"]
    function.device = mock.MagicMock()
    result = function.setDeviceProp("Connected", True)
    assert not result


def test_setDeviceProp_3(function):
    function.propertyExceptions = []
    function.device = mock.MagicMock()
    result = function.setDeviceProp("Connected", True)
    assert result


def test_setDeviceProp_4(function):
    function.propertyExceptions = []

    class DeviceWithBadProp:
        @property
        def TestProp(self):
            return None

        @TestProp.setter
        def TestProp(self, value):
            raise AlpycaNotImplError("not implemented")

    function.device = DeviceWithBadProp()
    result = function.setDeviceProp("TestProp", True)
    assert not result
    assert "TestProp" in function.propertyExceptions


def test_setDeviceProp_5(function):
    function.propertyExceptions = []

    class DeviceWithErrorProp:
        @property
        def TestProp(self):
            return None

        @TestProp.setter
        def TestProp(self, value):
            raise Exception("error")

    function.device = DeviceWithErrorProp()
    result = function.setDeviceProp("TestProp", True)
    assert not result


def test_callDeviceMethod_1(function):
    function.deviceConnected = False
    function.device = mock.MagicMock()
    result = function.callDeviceMethod("Halt")
    assert result is None


def test_callDeviceMethod_2(function):
    function.deviceConnected = True
    function.device = None
    result = function.callDeviceMethod("Halt")
    assert result is None


def test_callDeviceMethod_3(function):
    function.deviceConnected = True
    function.propertyExceptions = ["Halt"]
    function.device = mock.MagicMock()
    result = function.callDeviceMethod("Halt")
    assert result is None


def test_callDeviceMethod_4(function):
    function.deviceConnected = True
    function.propertyExceptions = []
    function.device = mock.MagicMock()
    function.device.Halt.return_value = None
    function.callDeviceMethod("Halt")
    function.device.Halt.assert_called_once_with()


def test_callDeviceMethod_5(function):
    function.deviceConnected = True
    function.propertyExceptions = []
    function.device = mock.MagicMock()
    function.device.Move.side_effect = AlpycaNotImplError("not implemented")
    result = function.callDeviceMethod("Move", Position=100)
    assert result is None
    assert "Move" in function.propertyExceptions


def test_callDeviceMethod_6(function):
    function.deviceConnected = True
    function.propertyExceptions = []
    function.device = mock.MagicMock()
    function.device.Move.side_effect = Exception("error")
    result = function.callDeviceMethod("Move", Position=100)
    assert result is None


def test_getAndStoreDeviceProp(function):
    with mock.patch.object(function, "getDeviceProp", return_value="test"):
        with mock.patch.object(function, "storePropertyToData") as m:
            function.getAndStoreDeviceProp("Name", "KEY")
            m.assert_called_once_with("test", "KEY")


def test_discoverAPIVersion_1(function):
    with mock.patch.object(alpacaMgmt, "apiversions", side_effect=Exception()):
        val = function.discoverAPIVersion()
        assert val == 0


def test_discoverAPIVersion_2(function):
    with mock.patch.object(alpacaMgmt, "apiversions", return_value=[]):
        val = function.discoverAPIVersion()
        assert val == 0


def test_discoverAPIVersion_3(function):
    with mock.patch.object(alpacaMgmt, "apiversions", return_value=[1, 2]):
        val = function.discoverAPIVersion()
        assert val == 2


def test_discoverAlpacaDevices_1(function):
    with mock.patch.object(
        alpacaMgmt, "configureddevices", side_effect=Exception()
    ):
        val = function.discoverAlpacaDevices()
        assert val == []


def test_discoverAlpacaDevices_2(function):
    with mock.patch.object(
        alpacaMgmt, "configureddevices", return_value=[]
    ):
        val = function.discoverAlpacaDevices()
        assert val == []


def test_discoverAlpacaDevices_3(function):
    devices = [
        {"DeviceName": "cam", "DeviceType": "Camera", "DeviceNumber": 0}
    ]
    with mock.patch.object(
        alpacaMgmt, "configureddevices", return_value=devices
    ):
        val = function.discoverAlpacaDevices()
        assert val == devices


def test_workerConnectDevice_1(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(function, "createAlpacaDevice", return_value=False):
        function.workerConnectDevice()
        assert not function.serverConnected
        assert not function.deviceConnected


def test_workerConnectDevice_2(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(time, "sleep"):
        with mock.patch.object(
            function, "createAlpacaDevice", return_value=True
        ):
            with mock.patch.object(
                function, "setDeviceProp"
            ):
                with mock.patch.object(
                    function, "getDeviceProp", return_value=False
                ):
                    function.workerConnectDevice()
                    assert not function.serverConnected
                    assert not function.deviceConnected


def test_workerConnectDevice_3(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(time, "sleep"):
        with mock.patch.object(
            function, "createAlpacaDevice", return_value=True
        ):
            with mock.patch.object(function, "setDeviceProp"):
                with mock.patch.object(
                    function, "getDeviceProp", return_value=True
                ):
                    function.workerConnectDevice()
                    assert function.serverConnected
                    assert function.deviceConnected


def test_startTimer(function):
    function.startAlpacaTimer()


def test_stopTimer(function):
    with mock.patch.object(PySide6.QtCore.QTimer, "stop"):
        function.stopAlpacaTimer()


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(function, "getDeviceProp", return_value="test"):
        function.workerGetInitialConfig()
        assert function.data["DRIVER_INFO.DRIVER_NAME"] == "test"
        assert function.data["DRIVER_INFO.DRIVER_VERSION"] == "test"
        assert function.data["DRIVER_INFO.DRIVER_EXEC"] == "test"


def test_workerPollStatus_1(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=False):
        function.workerPollStatus()
        assert not function.deviceConnected


def test_workerPollStatus_2(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getDeviceProp", return_value=True):
        function.workerPollStatus()
        assert function.deviceConnected


def test_processPolledData(function):
    function.processPolledData()


def test_workerPollData(function):
    function.workerPollData()


def test_pollData_1(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool, "start"):
        function.pollData()


def test_pollData_2(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool, "start"):
        function.pollData()


def test_pollStatus_1(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool, "start"):
        function.pollStatus()


def test_pollStatus_2(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool, "start"):
        function.pollStatus()


def test_getInitialConfig_1(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool, "start"):
        function.getInitialConfig()


def test_getInitialConfig_2(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool, "start"):
        function.getInitialConfig()


def test_startCommunication(function):
    with mock.patch.object(function.threadPool, "start"):
        function.startCommunication()


def test_stopCommunication_1(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = "test"
    function.device = mock.MagicMock()
    with mock.patch.object(function, "stopAlpacaTimer"):
        with mock.patch.object(function, "setDeviceProp"):
            function.stopCommunication()
            assert not function.serverConnected
            assert not function.deviceConnected


def test_discoverDevices_1(function):
    devices = [
        {"DeviceName": "test", "DeviceNumber": 1, "DeviceType": "Dome"},
        {"DeviceName": "test1", "DeviceNumber": 3, "DeviceType": "Dome"},
    ]
    with mock.patch.object(
        function, "discoverAlpacaDevices", return_value=devices
    ):
        val = function.discoverDevices("dome")
        assert val == ["test:dome:1", "test1:dome:3"]


def test_discoverDevices_2(function):
    with mock.patch.object(function, "discoverAlpacaDevices", return_value=[]):
        val = function.discoverDevices("dome")
        assert val == []
