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
import alpaca.management as alpacaMgmt
import pytest
import queue
import threading
from alpaca.exceptions import NotImplementedException as AlpycaNotImplError
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

setupLogging()


@pytest.fixture(autouse=True, scope="module")
def function():
    class Parent:
        app = App()
        data = {}
        deviceType = ""
        signals = Signals()

    func = AlpacaClass(parent=Parent())
    func.device = mock.MagicMock()
    yield func


@pytest.fixture(autouse=True)
def resetState(function):
    function.device = mock.MagicMock()
    function.data.clear()
    function.deviceConnected = False
    function.serverConnected = False
    function.stopEvent.clear()
    function.commandQueue = queue.Queue()
    function.propertyExceptions.clear()
    function.hostaddress = "localhost"
    function.port = 11111
    function.deviceName = ""
    function.deviceType = ""
    function.number = 0
    function.apiVersion = 1
    function.protocol = "http"
    yield


def test_init(function):
    assert hasattr(function, "commandQueue")
    assert hasattr(function, "stopEvent")
    assert hasattr(function, "workerCommunicationLoop")
    assert isinstance(function.commandQueue, queue.Queue)
    assert isinstance(function.stopEvent, threading.Event)
    assert function.PROTOCOL_NAME == "ALPACA"
    assert not hasattr(function, "cycleDevice")
    assert not hasattr(function, "cycleData")


def test_properties_1(function):
    function.host = ("localhost", 11111)
    function.hostaddress = "localhost"
    function.port = 11111
    function.deviceName = "test"
    function.deviceName = "test:2"
    function.apiVersion = 1
    function.protocol = "1"


def test_properties_2(function):
    assert function.host == ("localhost", 11111)
    assert function.hostaddress == "localhost"
    assert function.port == 11111
    assert function.deviceName == ""
    assert function.apiVersion == 1
    assert function.protocol == "http"


def test_properties_3(function):
    function.deviceName = "test:camera:3"
    assert function.deviceName == "test:camera:3"


def test_createAlpacaDevice_1(function):
    function.number = 0
    suc = function.createAlpacaDevice("camera")
    assert suc
    assert function.device is not None


def test_createAlpacaDevice_2(function):
    suc = function.createAlpacaDevice("unknown")
    assert not suc


def test_createAlpacaDevice_3(function):
    function.number = 0

    class RaisingClass:
        def __init__(self, *args, **kwargs):
            raise Exception("error")

    with mock.patch.dict(AlpacaClass.DEVICE_TYPE_MAP, {"dome": RaisingClass}):
        suc = function.createAlpacaDevice("dome")
        assert not suc


def test_getDeviceProp_propertyException(function):
    function.propertyExceptions.append("Connected")
    result = function.getDeviceProp("Connected")
    assert result is None


def test_getDeviceProp_1(function):
    function.device.Connected = True
    result = function.getDeviceProp("Connected")
    assert result is True


def test_getDeviceProp_2(function):
    type(function.device).TestProp = mock.PropertyMock(
        side_effect=AlpycaNotImplError("not implemented")
    )
    result = function.getDeviceProp("TestProp")
    assert result is None


def test_getDeviceProp_3(function):
    type(function.device).TestProp = mock.PropertyMock(
        side_effect=Exception("error")
    )
    result = function.getDeviceProp("TestProp")
    assert result is None


def test_setDeviceProp_propertyException(function):
    function.propertyExceptions.append("Connected")
    function.setDeviceProp("Connected", True)


def test_setDeviceProp_1(function):
    function.setDeviceProp("Connected", True)


def test_setDeviceProp_2(function):
    class DeviceWithBadProp:
        @property
        def TestProp(self):
            return None

        @TestProp.setter
        def TestProp(self, value):
            raise AlpycaNotImplError("not implemented")

    function.device = DeviceWithBadProp()
    function.setDeviceProp("TestProp", True)
    assert "TestProp" in function.propertyExceptions


def test_setDeviceProp_3(function):
    class DeviceWithErrorProp:
        @property
        def TestProp(self):
            return None

        @TestProp.setter
        def TestProp(self, value):
            raise Exception("error")

    function.device = DeviceWithErrorProp()
    function.setDeviceProp("TestProp", True)
    assert "TestProp" in function.propertyExceptions


def test_callDeviceMethod_propertyException(function):
    function.propertyExceptions.append("Halt")
    result = function.callDeviceMethod("Halt")
    assert result is None


def test_callDeviceMethod_1(function):
    function.device.Halt.return_value = "ok"
    result = function.callDeviceMethod("Halt")
    assert result == "ok"


def test_callDeviceMethod_2(function):
    function.device.Move.side_effect = AlpycaNotImplError("not implemented")
    result = function.callDeviceMethod("Move", Position=100)
    assert result is None


def test_callDeviceMethod_3(function):
    function.device.Move.side_effect = Exception("error")
    result = function.callDeviceMethod("Move", Position=100)
    assert result is None


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
    with mock.patch.object(alpacaMgmt, "configureddevices", return_value=[]):
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
    with mock.patch.object(
        function, "discoverAlpacaDevices", return_value=[]
    ):
        val = function.discoverDevices("dome")
        assert val == []


def test_startCommunication_1(function):
    with mock.patch.object(function.threadPool, "start") as m_start:
        function.startCommunication()
        assert function.workerCommunicationLoop is not None
        m_start.assert_called_once()


def test_startCommunication_2(function):
    with mock.patch.object(function.threadPool, "start") as m_start:
        function.startCommunication()
        assert not function.deviceConnected
        assert not function.serverConnected
        assert not function.stopEvent.is_set()
        m_start.assert_called_once()
