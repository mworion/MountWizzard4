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
import queue
import subprocess
import threading
import time
from mw4.base.alpacaAscomCommon import CommandItem
from mw4.base.ascomClass import AscomClass
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)

setupLogging()


class Parent:
    app = App()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="function")
def function():
    func = AscomClass(parent=Parent())
    func.signals = Signals()
    func.device = mock.MagicMock()
    yield func


def test_init(function):
    assert isinstance(function.commandQueue, queue.Queue)
    assert isinstance(function.stopEvent, threading.Event)
    assert function.workerRunnerCoreLoop is None
    assert isinstance(function.propertyExceptions, list)
    assert len(function.propertyExceptions) == 0


def test_getAscomProperty_success(function):
    function.device.Connected = True
    val = function.getDeviceProp("Connected")
    assert val is True


def test_getAscomProperty_exception(function):
    function.device = None
    val = function.getDeviceProp("Connected")
    assert val is None


def test_getAscomProperty_imageArray(function):
    function.device.ImageArray = [[1, 2], [3, 4]]
    val = function.getDeviceProp("ImageArray")
    assert val is not None


def test_getAscomProperty_propertyException(function):
    function.propertyExceptions.append("Connected")
    val = function.getDeviceProp("Connected")
    assert val is None


def test_setAscomProperty_success(function):
    function.setDeviceProp("Connected", True)


def test_setAscomProperty_exception(function):
    function.device = None
    function.setDeviceProp("Connected", True)


def test_setAscomProperty_propertyException(function):
    function.propertyExceptions.append("Connected")
    function.setDeviceProp("Connected", True)


def test_getAndStoreAscomProperty(function):
    with (
        mock.patch.object(function, "getDeviceProp", return_value=42),
        mock.patch.object(function, "storePropertyToData") as m,
    ):
        function.getAndStoreDeviceProp("Name", "KEY")
        m.assert_called_once_with(42, "KEY")


def test_callAscomMethod_success(function):
    function.device.Halt = mock.MagicMock(return_value=99)
    result = function.callDeviceMethod("Halt")
    assert result == 99


def test_callAscomMethod_exception(function):
    function.device = None
    result = function.callDeviceMethod("Halt")
    assert result is None


def test_callAscomMethod_kwargs(function):
    function.device.Move = mock.MagicMock()
    function.callDeviceMethod("Move", Position=100)
    function.device.Move.assert_called_once_with(Position=100)


def test_callAscomMethod_noKwargs(function):
    function.device.OpenShutter = mock.MagicMock()
    function.callDeviceMethod("OpenShutter")
    function.device.OpenShutter.assert_called_once_with()


def test_callAscomMethod_propertyException(function):
    function.propertyExceptions.append("Halt")
    result = function.callDeviceMethod("Halt")
    assert result is None


def test_setAscomPropertyQueued(function):
    function.setDevicePropQueued("Gain", 42)
    cmd = function.commandQueue.get_nowait()
    assert cmd.cmdType == "set"
    assert cmd.valueProp == "Gain"
    assert cmd.value == 42


def test_callAscomMethodQueued(function):
    function.callDeviceMethodQueued("Halt", SwitchIndex=0)
    cmd = function.commandQueue.get_nowait()
    assert cmd.cmdType == "call"
    assert cmd.valueProp == "Halt"
    assert cmd.kwargs == {"SwitchIndex": 0}


def test_callAscomMethodQueued_noKwargs(function):
    function.callDeviceMethodQueued("OpenShutter")
    cmd = function.commandQueue.get_nowait()
    assert cmd.cmdType == "call"
    assert cmd.valueProp == "OpenShutter"
    assert cmd.kwargs == {}


def test_processCommandQueue_empty(function):
    function.processCommandQueue()


def test_processCommandQueue_call(function):
    function.commandQueue.put(CommandItem(cmdType="call", valueProp="OpenShutter"))
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.processCommandQueue()
        m.assert_called_once_with("OpenShutter")


def test_processCommandQueue_callWithKwargs(function):
    function.commandQueue.put(
        CommandItem(
            cmdType="call",
            valueProp="Move",
            kwargs={"Position": 100},
        )
    )
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.processCommandQueue()
        m.assert_called_once_with("Move", Position=100)


def test_processCommandQueue_set(function):
    function.commandQueue.put(CommandItem(cmdType="set", valueProp="Gain", value=10))
    with mock.patch.object(function, "setDeviceProp") as m:
        function.processCommandQueue()
        m.assert_called_once_with("Gain", 10)


def test_processCommandQueue_unknownType(function):
    function.commandQueue.put(CommandItem(cmdType="unknown", valueProp="X"))
    function.processCommandQueue()


def test_processCommandQueue_callException(function):
    function.device = None
    function.commandQueue.put(CommandItem(cmdType="call", valueProp="Halt"))
    function.processCommandQueue()


def test_processCommandQueue_queueEmpty(function):
    with (
        mock.patch.object(function.commandQueue, "empty", return_value=False),
        mock.patch.object(function.commandQueue, "get_nowait", side_effect=queue.Empty),
    ):
        function.processCommandQueue()


def test_connectDevice_allFail(function):
    with (
        mock.patch.object(time, "sleep"),
        mock.patch.object(function, "setDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=False),
    ):
        result = function.connectDevice()
    assert not result
    assert not function.deviceConnected


def test_connectDevice_firstSuccess(function):
    with (
        mock.patch.object(function, "setDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=True),
    ):
        result = function.connectDevice()
    assert result


def test_connectDevice_retriesThenSuccess(function):
    responses = [False, False, True]
    with (
        mock.patch.object(time, "sleep"),
        mock.patch.object(function, "setDeviceProp"),
        mock.patch.object(function, "getDeviceProp", side_effect=responses),
    ):
        result = function.connectDevice()
    assert result


def test_getInitialConfig(function):
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        function.getInitialConfig()
        assert m.call_count == 3


def test_pollData(function):
    function.pollData()


def test_handleDeviceConnect_fail(function):
    with mock.patch.object(function, "connectDevice", return_value=False):
        function.handleDeviceConnect()
    assert not function.deviceConnected
    assert not function.serverConnected


def test_handleDeviceConnect_success(function):
    with (
        mock.patch.object(function, "connectDevice", return_value=True),
        mock.patch.object(function, "getInitialConfig") as m,
    ):
        function.handleDeviceConnect()
    assert function.deviceConnected
    assert function.serverConnected
    m.assert_called_once()


def test_handleDeviceDisconnect(function):
    function.deviceConnected = True
    function.handleDeviceDisconnect()
    assert not function.deviceConnected


def test_runnerCoreLoop_dispatchError(function):
    with (
        mock.patch("mw4.base.ascomClass.CoInitialize") as ci,
        mock.patch("mw4.base.ascomClass.CoUninitialize") as cu,
        mock.patch(
            "mw4.base.ascomClass.client.dynamic.Dispatch", side_effect=Exception("fail")
        ),
    ):
        function.runnerCoreLoop()
    ci.assert_called_once()
    cu.assert_called_once()
    assert function.device is None


def test_runnerCoreLoop_success(function):
    with (
        mock.patch("mw4.base.ascomClass.CoInitialize") as ci,
        mock.patch("mw4.base.ascomClass.CoUninitialize") as cu,
        mock.patch("mw4.base.ascomClass.client.dynamic.Dispatch"),
        mock.patch.object(function, "runnerCommunicationLoop") as m,
    ):
        function.runnerCoreLoop()
    ci.assert_called_once()
    m.assert_called_once()
    cu.assert_called_once()


def test_runnerCoreLoop_cleanup(function):
    with (
        mock.patch("mw4.base.ascomClass.CoInitialize"),
        mock.patch("mw4.base.ascomClass.CoUninitialize") as cu,
        mock.patch("mw4.base.ascomClass.client.dynamic.Dispatch"),
        mock.patch.object(function, "runnerCommunicationLoop"),
        mock.patch.object(function, "setDeviceProp") as ms,
    ):
        function.runnerCoreLoop()
    ms.assert_called_with("Connected", False)
    assert function.device is None
    cu.assert_called_once()


def test_runnerCommunicationLoop_stopImmediately(function):
    function.stopEvent.set()
    with mock.patch.object(function, "handleDeviceConnect") as m:
        function.runnerCommunicationLoop()
    m.assert_not_called()


def test_runnerCommunicationLoop_connectBranch(function):
    call_count = 0

    def fake_connect() -> None:
        nonlocal call_count
        call_count += 1
        function.stopEvent.set()

    function.deviceConnected = False
    with (
        mock.patch.object(function, "handleDeviceConnect", side_effect=fake_connect),
        mock.patch.object(function, "getDeviceProp", return_value=True),
    ):
        function.runnerCommunicationLoop()
    assert call_count == 1


def test_runnerCommunicationLoop_disconnectBranch(function):
    call_count = 0

    def fake_disconnect() -> None:
        nonlocal call_count
        call_count += 1
        function.stopEvent.set()

    function.deviceConnected = True
    with (
        mock.patch.object(function, "getDeviceProp", return_value=False),
        mock.patch.object(function, "handleDeviceDisconnect", side_effect=fake_disconnect),
    ):
        function.runnerCommunicationLoop()
    assert call_count == 1


def test_runnerCommunicationLoop_pollCycle(function):
    call_count = 0

    def fake_poll() -> None:
        nonlocal call_count
        call_count += 1
        function.stopEvent.set()

    function.deviceConnected = True
    with (
        mock.patch.object(function, "getDeviceProp", return_value=True),
        mock.patch.object(function, "pollData", side_effect=fake_poll),
        mock.patch.object(function, "processCommandQueue") as mq,
    ):
        function.runnerCommunicationLoop()
    assert call_count == 1
    mq.assert_called_once()


def test_runnerCommunicationLoop_pollException(function):
    call_count = 0

    def fake_poll() -> None:
        nonlocal call_count
        call_count += 1
        function.stopEvent.set()
        raise RuntimeError("boom")

    function.deviceConnected = True
    with (
        mock.patch.object(function, "getDeviceProp", return_value=True),
        mock.patch.object(function, "pollData", side_effect=fake_poll),
        mock.patch.object(function, "processCommandQueue"),
        pytest.raises(RuntimeError),
    ):
        function.runnerCommunicationLoop()
    assert call_count == 1


def test_startCommunication_noDevice(function):
    function.deviceName = ""
    with mock.patch.object(function.threadPool, "start") as m:
        function.startCommunication()
    m.assert_not_called()


def test_startCommunication_success(function):
    function.deviceName = "test.driver"
    with mock.patch.object(function.threadPool, "start") as m:
        function.startCommunication()
    m.assert_called_once()
    assert not function.stopEvent.is_set()


def test_stopCommunication(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = "test"
    function.stopCommunication()
    assert function.stopEvent.is_set()
    assert not function.deviceConnected
    assert not function.serverConnected


def test_selectAscomDriver_success(function):
    with mock.patch("subprocess.check_output", return_value="ASCOM.Test.Telescope"):
        result = function.selectAscomDriver("old", "Telescope")
    assert result == "ASCOM.Test.Telescope"


def test_selectAscomDriver_error(function):
    with mock.patch(
        "subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, "cmd"),
    ):
        result = function.selectAscomDriver("original", "Telescope")
    assert result == "original"


def test_selectAscomDriver_empty(function):
    with mock.patch("subprocess.check_output", return_value="  "):
        result = function.selectAscomDriver("fallback", "Telescope")
    assert result == "fallback"


def test_selectAscomDriver_uses_json_payload(function):
    """SEC-1: deviceName and deviceType must be passed as a JSON payload, not
    interpolated into the script string."""
    import json as _json

    with mock.patch("subprocess.check_output", return_value="result") as m:
        function.selectAscomDriver("MyDevice", "Camera")

    args, _ = m.call_args
    cmd_list = args[0]
    # script is cmd_list[2]; JSON payload is cmd_list[3]
    script = cmd_list[2]
    payload_str = cmd_list[3]

    # The device name / type must NOT appear literally in the script string
    assert "MyDevice" not in script
    assert "Camera" not in script

    # The payload must be valid JSON containing the correct keys
    payload = _json.loads(payload_str)
    assert payload["deviceName"] == "MyDevice"
    assert payload["deviceType"] == "Camera"


def test_selectAscomDriver_injection_safe(function):
    """SEC-1: A malicious deviceName with Python-injection characters must be
    transmitted safely through the JSON payload, not break the script."""
    import json as _json

    malicious = "'; import os; os.system('rm -rf /')#"
    with mock.patch("subprocess.check_output", return_value="") as m:
        function.selectAscomDriver(malicious, "Telescope")

    args, _ = m.call_args
    cmd_list = args[0]
    script = cmd_list[2]
    payload_str = cmd_list[3]

    # Injection string must not appear raw in the script
    assert malicious not in script
    # But it must survive round-tripping through JSON
    payload = _json.loads(payload_str)
    assert payload["deviceName"] == malicious
