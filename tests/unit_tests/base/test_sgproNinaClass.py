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
import requests
import threading
from mw4.base.loggerMW import setupLogging
from mw4.base.sgproNinaClass import SgproNinaCommon
from mw4.base.signalsDevices import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

setupLogging()


class ConcreteSgproNina(SgproNinaCommon):
    PROTOCOL_NAME = "TEST"


@pytest.fixture(autouse=True, scope="function")
def function():
    class Parent:
        app = App()
        data = {}
        signals = Signals()

    func = ConcreteSgproNina(parent=Parent())
    func.signals = mock.MagicMock()
    yield func


def test_init(function):
    assert isinstance(function.commandQueue, queue.Queue)
    assert isinstance(function.stopEvent, threading.Event)
    assert function.deviceConnected is False
    assert function.serverConnected is False
    assert function.loadConfig is False
    assert function.PROTOCOL_NAME == "TEST"


def test_properties_1(function):
    function.deviceName = "test"
    assert function.deviceName == "test"
    function.deviceName = "test:2"
    assert function.deviceName == "test:2"


def test_requestProperty_1(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(requests, "post", return_value=Response()):
        val = function.requestProperty("test", {"test": 1})
        assert val == "test"


def test_requestProperty_2(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(requests, "get", return_value=Response()):
        val = function.requestProperty("test")
        assert val == "test"


def test_requestProperty_3(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(
        requests,
        "get",
        side_effect=requests.exceptions.Timeout,
        return_value=Response(),
    ):
        val = function.requestProperty("test")
        assert not val


def test_requestProperty_4(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(
        requests,
        "get",
        side_effect=requests.exceptions.ConnectionError,
        return_value=Response(),
    ):
        val = function.requestProperty("test")
        assert not val


def test_requestProperty_5(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(requests, "get", side_effect=Exception, return_value=Response()):
        val = function.requestProperty("test")
        assert not val


def test_requestProperty_6(function):
    function.deviceName = "test"

    class Response:
        status_code = 400

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(requests, "get", return_value=Response()):
        val = function.requestProperty("test")
        assert not val


def test_requestPropertyQueued_noParams(function):
    # arrange / act
    function.requestPropertyQueued("abortimage")
    # assert
    valueProp, params = function.commandQueue.get_nowait()
    assert valueProp == "abortimage"
    assert params is None


def test_requestPropertyQueued_withParams(function):
    # arrange / act
    function.requestPropertyQueued("image", {"key": "val"})
    # assert
    valueProp, params = function.commandQueue.get_nowait()
    assert valueProp == "image"
    assert params == {"key": "val"}


def test_connectDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.connectDevice()
        assert not suc


def test_connectDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
        suc = function.connectDevice()
        assert suc


def test_disconnectDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.disconnectDevice()
        assert not suc


def test_disconnectDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
        suc = function.disconnectDevice()
        assert suc


def test_enumerateDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.enumerateDevice()
        assert not suc


def test_enumerateDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={"Devices": True}):
        suc = function.enumerateDevice()
        assert suc


def test_workerGetInitialConfig_1(function):
    function.workerGetInitialConfig()


def test_getInitialConfig_1(function):
    with mock.patch.object(function, "workerGetInitialConfig") as m:
        function.getInitialConfig()
    m.assert_called_once()


def test_pollData_emptyResponse(function):
    # requestProperty returns {} -> returns False
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        result = function.pollData()
    assert result is False


def test_pollData_connected(function):
    # state == "CONNECTED" -> returns True
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(
        function,
        "requestProperty",
        return_value={"State": "CONNECTED", "Message": "ok"},
    ):
        result = function.pollData()
    assert result is True
    assert function.data["Device.Status"] == "CONNECTED"
    assert function.data["Device.Message"] == "ok"


def test_pollData_disconnected(function):
    # state == "DISCONNECTED" -> returns False
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(
        function,
        "requestProperty",
        return_value={"State": "DISCONNECTED", "Message": "off"},
    ):
        result = function.pollData()
    assert result is False


def test_processCommandQueue_empty(function):
    # act / assert — must complete without error on empty queue
    function.processCommandQueue()


def test_processCommandQueue_withItem(function):
    # arrange
    function.commandQueue.put(("abortimage", None))
    # act
    with mock.patch.object(function, "requestProperty") as m:
        function.processCommandQueue()
    m.assert_called_once_with("abortimage", None)


def test_processCommandQueue_withParams(function):
    # arrange
    function.commandQueue.put(("image", {"key": "val"}))
    # act
    with mock.patch.object(function, "requestProperty") as m:
        function.processCommandQueue()
    m.assert_called_once_with("image", {"key": "val"})


def test_processCommandQueue_queueEmpty(function):
    # arrange — simulate queue.Empty on get_nowait
    with mock.patch.object(function.commandQueue, "empty", return_value=False):
        with mock.patch.object(
            function.commandQueue,
            "get_nowait",
            side_effect=queue.Empty,
        ):
            function.processCommandQueue()


def test_handleDeviceConnect_fail(function):
    # connectDevice returns False -> no signals, state unchanged
    with mock.patch.object(function, "connectDevice", return_value=False):
        function.handleDeviceConnect()
    function.signals.serverConnected.emit.assert_not_called()
    function.signals.deviceConnected.emit.assert_not_called()
    assert function.serverConnected is False
    assert function.deviceConnected is False


def test_handleDeviceConnect_success(function):
    # connectDevice returns True -> signals emitted, getInitialConfig called
    with mock.patch.object(function, "connectDevice", return_value=True):
        with mock.patch.object(function, "getInitialConfig") as mi:
            function.handleDeviceConnect()
    function.signals.serverConnected.emit.assert_called_once()
    function.signals.deviceConnected.emit.assert_called_once_with(function.deviceName)
    assert function.serverConnected is True
    assert function.deviceConnected is True
    mi.assert_called_once()


def test_handleDeviceDisconnect(function):
    # arrange
    function.deviceConnected = True
    # act
    function.handleDeviceDisconnect()
    # assert
    assert function.deviceConnected is False
    function.signals.deviceDisconnected.emit.assert_called_once_with(function.deviceName)


def test_runnerCommunicationLoop_stopImmediate(function):
    # stopEvent pre-set -> loop body never executes
    function.stopEvent.set()
    function.runnerCommunicationLoop()


def test_runnerCommunicationLoop_connectBranch(function):
    # deviceConnected=False -> handleDeviceConnect called once then stop
    function.deviceConnected = False
    call_count = {"n": 0}

    def fake_connect() -> None:
        call_count["n"] += 1
        function.stopEvent.set()

    function.handleDeviceConnect = fake_connect
    function.runnerCommunicationLoop()
    assert call_count["n"] == 1


def test_runnerCommunicationLoop_pollConnected(function):
    # deviceConnected=True, pollData=True -> processCommandQueue called
    function.deviceConnected = True
    poll_count = {"n": 0}

    def fake_poll() -> bool:
        poll_count["n"] += 1
        function.stopEvent.set()
        return True

    function.pollData = fake_poll
    with mock.patch.object(function, "processCommandQueue") as mq:
        function.runnerCommunicationLoop()
    assert poll_count["n"] == 1
    mq.assert_called_once()


def test_runnerCommunicationLoop_pollDisconnected(function):
    # deviceConnected=True, pollData=False -> handleDeviceDisconnect called
    function.deviceConnected = True
    call_count = {"n": 0}

    def fake_poll() -> bool:
        return False

    def fake_disconnect() -> None:
        call_count["n"] += 1
        function.stopEvent.set()

    function.pollData = fake_poll
    function.handleDeviceDisconnect = fake_disconnect
    function.runnerCommunicationLoop()
    assert call_count["n"] == 1


def test_startCommunication(function):
    # arrange
    function.stopEvent.set()
    function.data["test"] = 1
    # act
    with mock.patch.object(function.threadPool, "start") as ms:
        function.startCommunication()
    # assert: data cleared, stopEvent cleared, worker started
    assert not function.data
    assert not function.stopEvent.is_set()
    ms.assert_called_once()


def test_stopCommunication_1(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = "test"
    function.stopCommunication()
    assert function.stopEvent.is_set()
    assert not function.serverConnected
    assert not function.deviceConnected
    function.signals.deviceDisconnected.emit.assert_called_once()
    function.signals.serverDisconnected.emit.assert_called_once()


def test_discoverDevices_1(function):
    with mock.patch.object(function, "enumerateDevice", return_value=[]):
        val = function.discoverDevices("Camera")
        assert val == []


def test_discoverDevices_2(function):
    with mock.patch.object(function, "enumerateDevice", return_value=["test"]):
        val = function.discoverDevices("Camera")
        assert val == ["test"]


def test_isConnectedState_1(function):
    assert function.isConnectedState("test")


def test_isConnectedState_2(function):
    assert not function.isConnectedState("DISCONNECTED")
