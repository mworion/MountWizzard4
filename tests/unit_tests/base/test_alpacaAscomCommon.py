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
import queue
import threading
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon, CommandItem
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from typing import Any
from unittest import mock

setupLogging()


class Parent:
    app = App()
    data = {}
    deviceType = "test"
    signals = Signals()
    loadConfig = True


class ConcreteDevice(AlpacaAscomCommon):
    """Concrete test double that implements the abstract template methods."""

    PROTOCOL_NAME: str = "TEST"

    def getDeviceProp(self, valueProp: str) -> Any:
        if self.device is None:
            return None
        return getattr(self.device, valueProp, None)

    def setDeviceProp(self, valueProp: str, value: Any) -> None:
        if self.device is None:
            return
        setattr(self.device, valueProp, value)

    def callDeviceMethod(self, valueProp: str, **kwargs: Any) -> Any:
        if self.device is None:
            return None
        return getattr(self.device, valueProp)(**kwargs)


@pytest.fixture(autouse=True, scope="function")
def function():
    parent = Parent()
    func = ConcreteDevice(parent=parent)
    func.signals = mock.MagicMock()
    func.device = mock.MagicMock()
    yield func


def test_commandItem():
    # arrange / act
    item = CommandItem(cmdType="call", valueProp="Test")
    # assert
    assert item.cmdType == "call"
    assert item.valueProp == "Test"
    assert item.kwargs == {}
    assert item.value is None


def test_commandItemWithValue():
    # arrange / act
    item = CommandItem(cmdType="set", valueProp="Prop", value=42)
    # assert
    assert item.value == 42


def test_init(function):
    # assert
    assert isinstance(function.commandQueue, queue.Queue)
    assert isinstance(function.stopEvent, threading.Event)
    assert isinstance(function.propertyExceptions, list)
    assert len(function.propertyExceptions) == 0
    assert function.deviceConnected is False
    assert function.serverConnected is False
    assert function.loadConfig is False
    assert function.device is not None
    assert function.deviceName == ""


def test_protocolName(function):
    assert function.PROTOCOL_NAME == "TEST"


def test_setDevicePropQueued(function):
    # act
    function.setDevicePropQueued("Gain", 100)
    # assert
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "Gain"
    assert item.value == 100


def test_callDeviceMethodQueued(function):
    # act
    function.callDeviceMethodQueued("Move", Position=500)
    # assert
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "call"
    assert item.valueProp == "Move"
    assert item.kwargs == {"Position": 500}


def test_callDeviceMethodQueued_noKwargs(function):
    # act
    function.callDeviceMethodQueued("Halt")
    # assert
    item = function.commandQueue.get_nowait()
    assert item.kwargs == {}


def test_getAndStoreDeviceProp(function):
    # arrange
    function.device.Name = "TestDevice"
    # act
    function.getAndStoreDeviceProp("Name", "DRIVER_INFO.DRIVER_NAME")
    # assert
    assert function.data["DRIVER_INFO.DRIVER_NAME"] == "TestDevice"


def test_connectDevice_successFirst(function):
    # arrange
    function.device.Connected = True
    # act
    suc = function.connectDevice()
    # assert
    assert suc is True


def test_connectDevice_successAfterRetry(function):
    # arrange — fail twice then succeed
    call_count = {"n": 0}

    def fake_get(prop: str) -> Any:
        if prop == "Connected":
            call_count["n"] += 1
            return call_count["n"] >= 3
        return None

    function.getDeviceProp = fake_get
    function.setDeviceProp = mock.MagicMock()
    with mock.patch("time.sleep"):
        suc = function.connectDevice()
    assert suc is True


def test_connectDevice_allFail(function):
    # arrange
    function.getDeviceProp = mock.MagicMock(return_value=False)
    function.setDeviceProp = mock.MagicMock()
    with mock.patch("time.sleep"):
        suc = function.connectDevice()
    # assert
    assert suc is False


def test_getInitialConfig(function):
    # arrange
    function.device.Name = "MySensor"
    function.device.DriverVersion = "1.0"
    # act
    function.getInitialConfig()
    # assert
    assert function.data["DRIVER_INFO.DRIVER_NAME"] == "MySensor"
    assert function.data["DRIVER_INFO.DRIVER_VERSION"] == "1.0"


def test_pollData(function):
    # act / assert — must be a no-op
    function.pollData()


def test_processCommandQueue_empty(function):
    # act / assert — must complete without error
    function.processCommandQueue()


def test_processCommandQueue_call(function):
    # arrange
    function.callDeviceMethodQueued("Halt")
    # act
    function.processCommandQueue()
    # assert
    function.device.Halt.assert_called_once_with()


def test_processCommandQueue_callWithKwargs(function):
    # arrange
    function.callDeviceMethodQueued("Move", Position=100)
    # act
    function.processCommandQueue()
    # assert
    function.device.Move.assert_called_once_with(Position=100)


def test_processCommandQueue_set(function):
    # arrange
    function.setDevicePropQueued("Gain", 50)
    # act
    function.processCommandQueue()
    # assert
    assert function.device.Gain == 50


def test_processCommandQueue_unknownType(function):
    # arrange
    function.commandQueue.put(CommandItem(cmdType="unknown", valueProp="X"))
    # act / assert — must not raise
    function.processCommandQueue()


def test_processCommandQueue_queueEmpty(function):
    # arrange — put an item that raises queue.Empty on get_nowait
    with mock.patch.object(function.commandQueue, "get_nowait", side_effect=queue.Empty):
        # act / assert — must not raise
        function.commandQueue._mock_empty = False
        with mock.patch.object(function.commandQueue, "empty", return_value=False):
            function.processCommandQueue()


def test_handleDeviceConnect_fail(function):
    # arrange
    function.getDeviceProp = mock.MagicMock(return_value=False)
    function.setDeviceProp = mock.MagicMock()
    with mock.patch("time.sleep"):
        function.handleDeviceConnect()
    # assert — signals must NOT have been emitted
    function.signals.serverConnected.emit.assert_not_called()
    function.signals.deviceConnected.emit.assert_not_called()
    assert function.serverConnected is False
    assert function.deviceConnected is False


def test_handleDeviceConnect_success(function):
    # arrange
    function.device.Connected = True
    function.handleDeviceConnect()
    # assert
    function.signals.serverConnected.emit.assert_called_once()
    function.signals.deviceConnected.emit.assert_called_once_with(function.deviceName)
    assert function.serverConnected is True
    assert function.deviceConnected is True


def test_handleDeviceDisconnect(function):
    # arrange
    function.deviceConnected = True
    function.handleDeviceDisconnect()
    # assert
    assert function.deviceConnected is False
    function.signals.deviceDisconnected.emit.assert_called_once_with(function.deviceName)


def test_runnerCommunicationLoop_stopImmediate(function):
    # arrange — set stop event before starting
    function.stopEvent.set()
    # act / assert — must return immediately
    function.runnerCommunicationLoop()


def test_runnerCommunicationLoop_connectBranch(function):
    # arrange
    function.deviceConnected = False
    call_count = {"n": 0}

    def fake_connect() -> None:
        call_count["n"] += 1
        function.stopEvent.set()

    function.handleDeviceConnect = fake_connect
    function.getDeviceProp = mock.MagicMock(return_value=True)
    # act
    function.runnerCommunicationLoop()
    # assert
    assert call_count["n"] == 1


def test_runnerCommunicationLoop_disconnectBranch(function):
    # arrange
    function.deviceConnected = True
    call_count = {"n": 0}

    def fake_disconnect() -> None:
        call_count["n"] += 1
        function.stopEvent.set()

    function.handleDeviceDisconnect = fake_disconnect
    function.getDeviceProp = mock.MagicMock(return_value=False)
    # act
    function.runnerCommunicationLoop()
    # assert
    assert call_count["n"] == 1


def test_runnerCommunicationLoop_pollCycle(function):
    # arrange
    function.deviceConnected = True
    poll_count = {"n": 0}

    def fake_poll() -> None:
        poll_count["n"] += 1
        function.stopEvent.set()

    function.pollData = fake_poll
    function.getDeviceProp = mock.MagicMock(return_value=True)
    # act
    function.runnerCommunicationLoop()
    # assert
    assert poll_count["n"] == 1


def test_stopCommunication(function):
    # arrange
    function.deviceConnected = True
    function.serverConnected = True
    function.stopCommunication()
    # assert
    assert function.stopEvent.is_set()
    assert function.deviceConnected is False
    assert function.serverConnected is False
    function.signals.deviceDisconnected.emit.assert_called_once_with(function.deviceName)
    function.signals.serverDisconnected.emit.assert_called_once()
    # "Connected" must be queued
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "Connected"
    assert item.value is False


def test_getDeviceProp_noDevice():
    # arrange — use base class directly, device is None
    parent = Parent()
    base = AlpacaAscomCommon(parent=parent)
    # act
    result = base.getDeviceProp("Test")
    # assert — exception is caught, prop added to exceptions, None returned
    assert result is None
    assert "Test" in base.propertyExceptions


def test_getDeviceProp_inPropertyExceptions():
    # arrange
    parent = Parent()
    base = AlpacaAscomCommon(parent=parent)
    base.propertyExceptions.append("Test")
    # act
    result = base.getDeviceProp("Test")
    # assert — early return
    assert result is None


def test_getDeviceProp_withLoggingTrace():
    # arrange
    parent = Parent()
    base = AlpacaAscomCommon(parent=parent)
    base.device = mock.MagicMock()
    base.device.Name = "TracedDevice"
    base.loggingTrace = True
    # act
    result = base.getDeviceProp("Name")
    # assert
    assert result == "TracedDevice"


def test_setDeviceProp_noDevice():
    parent = Parent()
    base = AlpacaAscomCommon(parent=parent)
    base.setDeviceProp("Test", True)
    assert "Test" in base.propertyExceptions


def test_setDeviceProp_inPropertyExceptions():
    # arrange
    parent = Parent()
    base = AlpacaAscomCommon(parent=parent)
    base.propertyExceptions.append("Test")
    # act — must not raise and must not add a second entry
    base.setDeviceProp("Test", True)
    # assert
    assert base.propertyExceptions.count("Test") == 1


def test_setDeviceProp_withLoggingTrace():
    # arrange
    parent = Parent()
    base = AlpacaAscomCommon(parent=parent)
    base.device = mock.MagicMock()
    base.loggingTrace = True
    # act
    base.setDeviceProp("Gain", 42)
    # assert
    assert base.device.Gain == 42


def test_callDeviceMethod_noDevice():
    parent = Parent()
    base = AlpacaAscomCommon(parent=parent)
    result = base.callDeviceMethod("Test")
    assert result is None
    assert "Test" in base.propertyExceptions


def test_callDeviceMethod_inPropertyExceptions():
    # arrange
    parent = Parent()
    base = AlpacaAscomCommon(parent=parent)
    base.propertyExceptions.append("Test")
    # act
    result = base.callDeviceMethod("Test")
    # assert — early return
    assert result is None


def test_callDeviceMethod_withLoggingTrace():
    # arrange
    parent = Parent()
    base = AlpacaAscomCommon(parent=parent)
    base.device = mock.MagicMock()
    base.device.Halt.return_value = "ok"
    base.loggingTrace = True
    # act
    result = base.callDeviceMethod("Halt")
    # assert
    base.device.Halt.assert_called_once_with()
    assert result == "ok"
