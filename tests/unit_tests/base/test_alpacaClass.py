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
import pytest
import queue
import threading
import time
from alpaca.exceptions import NotImplementedException as AlpycaNotImplError
from mw4.base.alpacaClass import AlpacaClass, CommandItem
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
    assert not hasattr(function, "propertyExceptions")
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
    type(function.device).TestProp = mock.PropertyMock(side_effect=Exception("error"))
    result = function.getDeviceProp("TestProp")
    assert result is None


def test_setDeviceProp_1(function):
    result = function.setDeviceProp("Connected", True)
    assert result


def test_setDeviceProp_2(function):
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


def test_setDeviceProp_3(function):
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


def test_callDeviceMethodQueued_1(function):
    function.callDeviceMethodQueued("Halt")
    assert not function.commandQueue.empty()
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "call"
    assert item.name == "Halt"


def test_setDevicePropQueued_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.setDevicePropQueued("Connected", True)
    assert not function.commandQueue.empty()
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.name == "Connected"
    assert item.value is True


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
    with mock.patch.object(alpacaMgmt, "configureddevices", side_effect=Exception()):
        val = function.discoverAlpacaDevices()
        assert val == []


def test_discoverAlpacaDevices_2(function):
    with mock.patch.object(alpacaMgmt, "configureddevices", return_value=[]):
        val = function.discoverAlpacaDevices()
        assert val == []


def test_discoverAlpacaDevices_3(function):
    devices = [{"DeviceName": "cam", "DeviceType": "Camera", "DeviceNumber": 0}]
    with mock.patch.object(alpacaMgmt, "configureddevices", return_value=devices):
        val = function.discoverAlpacaDevices()
        assert val == devices


def test_discoverDevices_1(function):
    devices = [
        {"DeviceName": "test", "DeviceNumber": 1, "DeviceType": "Dome"},
        {"DeviceName": "test1", "DeviceNumber": 3, "DeviceType": "Dome"},
    ]
    with mock.patch.object(function, "discoverAlpacaDevices", return_value=devices):
        val = function.discoverDevices("dome")
        assert val == ["test:dome:1", "test1:dome:3"]


def test_discoverDevices_2(function):
    with mock.patch.object(function, "discoverAlpacaDevices", return_value=[]):
        val = function.discoverDevices("dome")
        assert val == []


def test_connectDevice_1(function):
    with mock.patch.object(time, "sleep"):
        with mock.patch.object(function, "setDeviceProp"):
            with mock.patch.object(function, "getDeviceProp", return_value=False):
                result = function.connectDevice()
                assert not result


def test_connectDevice_2(function):
    with mock.patch.object(time, "sleep"):
        with mock.patch.object(function, "setDeviceProp"):
            with mock.patch.object(function, "getDeviceProp", return_value=True):
                result = function.connectDevice()
                assert result


def test_connectDevice_3(function):
    responses = [False, False, True]
    with mock.patch.object(time, "sleep"):
        with mock.patch.object(function, "setDeviceProp"):
            with mock.patch.object(function, "getDeviceProp", side_effect=responses):
                result = function.connectDevice()
                assert result


def test_getInitialConfig(function):
    with mock.patch.object(function, "getDeviceProp", return_value="val"):
        function.getInitialConfig()
        assert function.data["DRIVER_INFO.DRIVER_NAME"] == "val"
        assert function.data["DRIVER_INFO.DRIVER_VERSION"] == "val"
        assert function.data["DRIVER_INFO.DRIVER_EXEC"] == "val"


def test_pollData(function):
    function.pollData()


def test_processCommandQueue_1(function):
    function.processCommandQueue()


def test_processCommandQueue_2(function):
    function.commandQueue.put(CommandItem(cmdType="call", name="Halt"))
    function.processCommandQueue()
    function.device.Halt.assert_called_once_with()


def test_processCommandQueue_3(function):
    function.commandQueue.put(CommandItem(cmdType="set", name="Connected", value=True))
    with mock.patch.object(function, "setDeviceProp") as m:
        function.processCommandQueue()
        m.assert_called_once_with("Connected", True)


def test_processCommandQueue_4(function):
    function.commandQueue.put(CommandItem(cmdType="unknown", name="Halt"))
    function.processCommandQueue()


def test_processCommandQueue_5(function):
    function.device.Halt.side_effect = Exception("error")
    function.commandQueue.put(CommandItem(cmdType="call", name="Halt"))
    function.processCommandQueue()


def test_processCommandQueue_6(function):
    function.device.Halt.side_effect = AlpycaNotImplError("not implemented")
    function.commandQueue.put(CommandItem(cmdType="call", name="Halt"))
    function.processCommandQueue()


def test_processCommandQueue_7(function):
    with mock.patch.object(
        function.commandQueue,
        "empty",
        return_value=False,
    ):
        with mock.patch.object(
            function.commandQueue,
            "get_nowait",
            side_effect=queue.Empty,
        ):
            function.processCommandQueue()


def test_handleDeviceConnect_1(function):
    with mock.patch.object(function, "connectDevice", return_value=False):
        with mock.patch.object(function, "getInitialConfig") as m_cfg:
            function.handleDeviceConnect()
            assert not function.deviceConnected
            assert not function.serverConnected
            m_cfg.assert_not_called()


def test_handleDeviceConnect_2(function):
    with mock.patch.object(function, "connectDevice", return_value=True):
        with mock.patch.object(function, "getInitialConfig") as m_cfg:
            function.handleDeviceConnect()
            assert function.deviceConnected
            assert function.serverConnected
            m_cfg.assert_called_once()


def test_handleDeviceDisconnect(function):
    function.deviceConnected = True
    function.handleDeviceDisconnect()
    assert not function.deviceConnected


def test_runnerCommunicationLoop_stopImmediately(function):
    function.stopEvent.set()
    function.runnerCommunicationLoop()


def test_runnerCommunicationLoop_pollCycle(function):
    function.deviceConnected = True

    def stop_after_one(*args, **kwargs):
        function.stopEvent.set()

    with mock.patch.object(function, "getDeviceProp", return_value=True):
        with mock.patch.object(function, "pollData") as m_poll:
            with mock.patch.object(function, "processCommandQueue") as m_queue:
                with mock.patch.object(function.stopEvent, "wait", side_effect=stop_after_one):
                    function.runnerCommunicationLoop()
                    m_poll.assert_called_once()
                    m_queue.assert_called_once()


def test_runnerCommunicationLoop_pollDataException(function):
    function.deviceConnected = True

    def stop_after_one(*args, **kwargs):
        function.stopEvent.set()

    with mock.patch.object(function, "getDeviceProp", return_value=True):
        with mock.patch.object(function, "pollData", side_effect=Exception("boom")):
            with mock.patch.object(function.stopEvent, "wait", side_effect=stop_after_one):
                function.runnerCommunicationLoop()


def test_runnerCommunicationLoop_notConnected(function):
    function.deviceConnected = False

    def make_connected() -> None:
        function.deviceConnected = True

    def stop_after_one(*args, **kwargs) -> None:
        function.stopEvent.set()

    with mock.patch.object(function, "handleDeviceConnect", side_effect=make_connected) as m:
        with mock.patch.object(function, "getDeviceProp", return_value=True):
            with mock.patch.object(function, "pollData"):
                with mock.patch.object(function.stopEvent, "wait", side_effect=stop_after_one):
                    function.runnerCommunicationLoop()
                    m.assert_called_once()


def test_runnerCommunicationLoop_deviceLost(function):
    function.deviceConnected = True

    def stop_on_disconnect() -> None:
        function.stopEvent.set()

    with mock.patch.object(function, "getDeviceProp", return_value=False):
        with mock.patch.object(
            function, "handleDeviceDisconnect", side_effect=stop_on_disconnect
        ) as m:
            function.runnerCommunicationLoop()
            m.assert_called_once()


def test_startCommunication_1(function):
    with mock.patch.object(function, "createAlpacaDevice", return_value=False):
        with mock.patch.object(function.threadPool, "start") as m_start:
            function.startCommunication()
            assert function.workerCommunicationLoop is not None
            m_start.assert_not_called()


def test_startCommunication_2(function):
    with mock.patch.object(function, "createAlpacaDevice", return_value=True):
        with mock.patch.object(function.threadPool, "start") as m_start:
            function.startCommunication()
            assert function.workerCommunicationLoop is not None
            assert not function.stopEvent.is_set()
            m_start.assert_called_once()


def test_stopCommunication(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = "test"
    with mock.patch.object(function, "setDeviceProp"):
        function.stopCommunication()
        assert function.stopEvent.is_set()
        assert not function.deviceConnected
        assert not function.serverConnected
