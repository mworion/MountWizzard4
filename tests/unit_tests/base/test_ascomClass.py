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
from unittest import mock

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)

from mw4.base.ascomClass import AscomClass, CommandItem
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


class Parent:
    app = App()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    func = AscomClass(parent=Parent())
    func.signals = Signals()
    func.client = mock.MagicMock()
    yield func


def test_init(function):
    assert isinstance(function.commandQueue, queue.Queue)
    assert isinstance(function.stopEvent, threading.Event)
    assert function.workerCommunicationLoop is None
    assert not hasattr(function, "propertyExceptions")
    assert not hasattr(function, "tM")
    assert not hasattr(function, "cyclePollData")
    assert not hasattr(function, "cyclePollStatus")


def test_getAscomProperty_success(function):
    function.client.Connected = True
    val = function.getAscomProperty("Connected")
    assert val is True


def test_getAscomProperty_exception(function):
    function.client = None
    val = function.getAscomProperty("Connected")
    assert val is None


def test_getAscomProperty_imageArray(function):
    function.client.ImageArray = [[1, 2], [3, 4]]
    val = function.getAscomProperty("ImageArray")
    assert val is not None


def test_setAscomProperty_success(function):
    function.setAscomProperty("Connected", True)


def test_setAscomProperty_exception(function):
    function.client = None
    function.setAscomProperty("Connected", True)


def test_getAndStoreAscomProperty(function):
    with mock.patch.object(function, "getAscomProperty", return_value=42):
        with mock.patch.object(function, "storePropertyToData") as m:
            function.getAndStoreAscomProperty("Name", "KEY")
            m.assert_called_once_with(42, "KEY")


def test_callAscomMethod_success(function):
    function.client.Halt = mock.MagicMock(return_value=99)
    result = function.callAscomMethod("Halt", ())
    assert result == 99


def test_callAscomMethod_exception(function):
    function.client = None
    result = function.callAscomMethod("Halt", ())
    assert result is None


def test_callAscomMethod_tuple(function):
    function.client.setswitch = mock.MagicMock()
    function.callAscomMethod("setswitch", (0, True))
    function.client.setswitch.assert_called_once_with(0, True)


def test_callAscomMethod_scalar(function):
    function.client.move = mock.MagicMock()
    function.callAscomMethod("move", 100)
    function.client.move.assert_called_once_with(100)


def test_setAscomPropertyQueued(function):
    function.setAscomPropertyQueued("Gain", 42)
    cmd = function.commandQueue.get_nowait()
    assert cmd.cmdType == "set"
    assert cmd.name == "Gain"
    assert cmd.value == 42


def test_callAscomMethodQueued_scalar(function):
    function.callAscomMethodQueued("Halt", 0)
    cmd = function.commandQueue.get_nowait()
    assert cmd.cmdType == "call"
    assert cmd.name == "Halt"
    assert cmd.args == (0,)


def test_callAscomMethodQueued_tuple(function):
    function.callAscomMethodQueued("setswitch", (2, True))
    cmd = function.commandQueue.get_nowait()
    assert cmd.cmdType == "call"
    assert cmd.name == "setswitch"
    assert cmd.args == (2, True)


def test_processCommandQueue_empty(function):
    function.processCommandQueue()


def test_processCommandQueue_call(function):
    function.commandQueue.put(CommandItem(cmdType="call", name="OpenShutter", args=()))
    with mock.patch.object(function, "callAscomMethod") as m:
        function.processCommandQueue()
        m.assert_called_once_with("OpenShutter", ())


def test_processCommandQueue_set(function):
    function.commandQueue.put(CommandItem(cmdType="set", name="Gain", value=10))
    with mock.patch.object(function, "setAscomProperty") as m:
        function.processCommandQueue()
        m.assert_called_once_with("Gain", 10)


def test_processCommandQueue_unknownType(function):
    function.commandQueue.put(CommandItem(cmdType="unknown", name="X"))
    function.processCommandQueue()


def test_processCommandQueue_callException(function):
    function.client = None
    function.commandQueue.put(CommandItem(cmdType="call", name="Halt", args=()))
    function.processCommandQueue()


def test_connectDevice_allFail(function):
    with mock.patch.object(time, "sleep"):
        with mock.patch.object(function, "setAscomProperty"):
            with mock.patch.object(function, "getAscomProperty", return_value=False):
                result = function.connectDevice()
    assert not result
    assert not function.deviceConnected


def test_connectDevice_firstSuccess(function):
    with mock.patch.object(function, "setAscomProperty"):
        with mock.patch.object(function, "getAscomProperty", return_value=True):
            result = function.connectDevice()
    assert result


def test_connectDevice_retriesThenSuccess(function):
    responses = [False, False, True]
    with mock.patch.object(time, "sleep"):
        with mock.patch.object(function, "setAscomProperty"):
            with mock.patch.object(function, "getAscomProperty", side_effect=responses):
                result = function.connectDevice()
    assert result


def test_getInitialConfig(function):
    with mock.patch.object(function, "getAndStoreAscomProperty") as m:
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
    with mock.patch.object(function, "connectDevice", return_value=True):
        with mock.patch.object(function, "getInitialConfig") as m:
            function.handleDeviceConnect()
    assert function.deviceConnected
    assert function.serverConnected
    m.assert_called_once()


def test_handleDeviceDisconnect(function):
    function.deviceConnected = True
    function.handleDeviceDisconnect()
    assert not function.deviceConnected


def test_runnerCommunicationLoop_dispatchError(function):
    function.stopEvent.set()
    with mock.patch("mw4.base.ascomClass.CoInitialize") as ci:
        with mock.patch("mw4.base.ascomClass.CoUninitialize") as cu:
            with mock.patch(
                "mw4.base.ascomClass.client.dynamic.Dispatch",
                side_effect=Exception("fail"),
            ):
                function.runnerCommunicationLoop()
    ci.assert_called_once()
    cu.assert_called_once()
    assert function.client is None


def test_runnerCommunicationLoop_stopImmediately(function):
    function.stopEvent.set()
    with mock.patch("mw4.base.ascomClass.CoInitialize"):
        with mock.patch("mw4.base.ascomClass.CoUninitialize"):
            with mock.patch("mw4.base.ascomClass.client.dynamic.Dispatch"):
                with mock.patch.object(function, "handleDeviceConnect") as m:
                    function.runnerCommunicationLoop()
    m.assert_not_called()


def test_runnerCommunicationLoop_connectBranch(function):
    call_count = 0

    def fake_connect():
        nonlocal call_count
        call_count += 1
        function.stopEvent.set()

    function.deviceConnected = False
    with mock.patch("mw4.base.ascomClass.CoInitialize"):
        with mock.patch("mw4.base.ascomClass.CoUninitialize"):
            with mock.patch("mw4.base.ascomClass.client.dynamic.Dispatch"):
                with mock.patch.object(
                    function,
                    "handleDeviceConnect",
                    side_effect=fake_connect,
                ):
                    function.runnerCommunicationLoop()
    assert call_count == 1


def test_runnerCommunicationLoop_disconnectBranch(function):
    call_count = 0

    def fake_disconnect():
        nonlocal call_count
        call_count += 1
        function.stopEvent.set()

    function.deviceConnected = True
    with mock.patch("mw4.base.ascomClass.CoInitialize"):
        with mock.patch("mw4.base.ascomClass.CoUninitialize"):
            with mock.patch("mw4.base.ascomClass.client.dynamic.Dispatch"):
                with mock.patch.object(function, "getAscomProperty", return_value=False):
                    with mock.patch.object(
                        function,
                        "handleDeviceDisconnect",
                        side_effect=fake_disconnect,
                    ):
                        function.runnerCommunicationLoop()
    assert call_count == 1


def test_runnerCommunicationLoop_pollCycle(function):
    call_count = 0

    def fake_poll():
        nonlocal call_count
        call_count += 1
        function.stopEvent.set()

    function.deviceConnected = True
    with mock.patch("mw4.base.ascomClass.CoInitialize"):
        with mock.patch("mw4.base.ascomClass.CoUninitialize"):
            with mock.patch("mw4.base.ascomClass.client.dynamic.Dispatch"):
                with mock.patch.object(function, "getAscomProperty", return_value=True):
                    with mock.patch.object(function, "pollData", side_effect=fake_poll):
                        with mock.patch.object(function, "processCommandQueue") as mq:
                            function.runnerCommunicationLoop()
    assert call_count == 1
    mq.assert_called_once()


def test_runnerCommunicationLoop_pollException(function):
    call_count = 0

    def fake_poll():
        nonlocal call_count
        call_count += 1
        function.stopEvent.set()
        raise RuntimeError("boom")

    function.deviceConnected = True
    with mock.patch("mw4.base.ascomClass.CoInitialize"):
        with mock.patch("mw4.base.ascomClass.CoUninitialize"):
            with mock.patch("mw4.base.ascomClass.client.dynamic.Dispatch"):
                with mock.patch.object(function, "getAscomProperty", return_value=True):
                    with mock.patch.object(function, "pollData", side_effect=fake_poll):
                        with mock.patch.object(function, "processCommandQueue"):
                            function.runnerCommunicationLoop()
    assert call_count == 1


def test_runnerCommunicationLoop_cleanup(function):
    function.stopEvent.set()
    function.client = mock.MagicMock()
    with mock.patch("mw4.base.ascomClass.CoInitialize"):
        with mock.patch("mw4.base.ascomClass.CoUninitialize") as cu:
            with mock.patch("mw4.base.ascomClass.client.dynamic.Dispatch"):
                with mock.patch.object(function, "setAscomProperty") as ms:
                    function.runnerCommunicationLoop()
    ms.assert_called_with("Connected", False)
    assert function.client is None
    cu.assert_called_once()


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
        result = function.selectAscomDriver("old")
    assert result == "ASCOM.Test.Telescope"


def test_selectAscomDriver_error(function):
    with mock.patch(
        "subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, "cmd"),
    ):
        result = function.selectAscomDriver("original")
    assert result == "original"


def test_selectAscomDriver_empty(function):
    with mock.patch("subprocess.check_output", return_value="  "):
        result = function.selectAscomDriver("fallback")
    assert result == "fallback"
