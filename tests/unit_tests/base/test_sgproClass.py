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
import contextlib
import pytest
import queue
import threading
from mw4.base.sgproClass import CommandItem, DeviceConfigSGPro, SGProClass
from mw4.base.signalsDevices import Signals
from pathlib import Path
from PySide6.QtCore import QThreadPool
from unittest import mock


class Parent:
    """Minimal parent class for SGProClass testing."""

    def __init__(self) -> None:
        self.data: dict = {}
        self.signals = Signals()
        self.app = mock.MagicMock()
        self.app.msg = mock.MagicMock()
        self.app.threadPool = QThreadPool()
        self.app.mwGlob = {"logDir": Path("/tmp")}


@pytest.fixture(autouse=True, scope="module")
def function():
    func = SGProClass(parent=Parent())
    func.UPDATE_RATE = 0.25
    yield func


# ─── Initialization and Configuration ───────────────────────────────────────


def test_init_default_values():
    """Test that SGProClass initializes with correct default values."""
    function = SGProClass(parent=Parent())
    assert function.deviceConnected is False
    assert isinstance(function.commandQueue, queue.Queue)
    assert isinstance(function.stopEvent, threading.Event)
    assert function.loggingTrace is False
    assert function.workerCommunicationLoop is None
    assert function.SGPRO_TIMEOUT == 3
    assert function.DEVICE_TYPE == "Camera"


def test_init_config():
    """Test that config is properly initialized."""
    function = SGProClass(parent=Parent())
    assert function.config.deviceName == ""
    assert function.config.hostAddress == "127.0.0.1"
    assert function.config.port == 59590
    assert function.config.UPDATE_RATE == 0.25
    assert function.config.PROTOCOL_NAME == "SGPro"


def test_config_deviceConfigSGPro():
    """Test DeviceConfigSGPro dataclass."""
    config = DeviceConfigSGPro()
    assert config.deviceName == ""
    assert config.hostAddress == "127.0.0.1"
    assert config.port == 59590
    assert config.UPDATE_RATE == 0.25
    assert config.PROTOCOL_NAME == "SGPro"


def test_config_deviceConfigSGPro_custom():
    """Test DeviceConfigSGPro with custom values."""
    config = DeviceConfigSGPro(deviceName="MyCamera", hostAddress="192.168.1.100", port=8080)
    assert config.deviceName == "MyCamera"
    assert config.hostAddress == "192.168.1.100"
    assert config.port == 8080


def test_command_item_creation():
    """Test CommandItem dataclass creation."""
    item = CommandItem(cmdType="call", valueProp="testProp")
    assert item.cmdType == "call"
    assert item.valueProp == "testProp"
    assert item.kwargs == {}
    assert item.value is None


def test_command_item_with_kwargs():
    """Test CommandItem with kwargs."""
    kwargs = {"key": "value"}
    item = CommandItem(cmdType="call", valueProp="testProp", kwargs=kwargs)
    assert item.kwargs == kwargs


# ─── Request Property ────────────────────────────────────────────────────────


def test_requestProperty_get_success(function):
    """Test successful GET request."""
    function.config.hostAddress = "localhost"
    function.config.port = 59590
    response_data = {"Success": True, "Data": "test"}
    with mock.patch("mw4.base.sgproClass.requests.get") as mock_get:
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_get.return_value = mock_response
        result = function.requestProperty("testProp")
        assert result == response_data
        mock_get.assert_called_once_with(
            "http://localhost:59590/testProp?format=json", timeout=3
        )


def test_requestProperty_post_with_params(function):
    """Test successful POST request with params."""
    function.config.hostAddress = "localhost"
    function.config.port = 59590
    response_data = {"Success": True}
    params = {"param1": "value1"}
    with mock.patch("mw4.base.sgproClass.requests.post") as mock_post:
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_post.return_value = mock_response
        result = function.requestProperty("testProp", params)
        assert result == response_data
        mock_post.assert_called_once_with(
            "http://localhost:59590/testProp?format=json", json=params, timeout=3
        )


def test_requestProperty_timeout_exception(function):
    """Test timeout exception handling."""
    function.config.hostAddress = "localhost"
    function.config.port = 59590
    with mock.patch("mw4.base.sgproClass.requests.get") as mock_get:
        mock_get.side_effect = Exception("Timeout")
        result = function.requestProperty("testProp")
        assert result == {}


def test_requestProperty_connection_error(function):
    """Test connection error handling."""
    function.config.hostAddress = "localhost"
    function.config.port = 59590
    with mock.patch("mw4.base.sgproClass.requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection refused")
        result = function.requestProperty("testProp")
        assert result == {}


def test_requestProperty_invalid_status_code(function):
    """Test handling of invalid HTTP status code."""
    function.config.hostAddress = "localhost"
    function.config.port = 59590
    with mock.patch("mw4.base.sgproClass.requests.get") as mock_get:
        mock_response = mock.MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        result = function.requestProperty("testProp")
        assert result == {}


# ─── Device Connection ──────────────────────────────────────────────────────


def test_sgConnectDevice_success(function):
    """Test successful device connection."""
    function.config.deviceName = "TestCamera"
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True}
        result = function.sgConnectDevice()
        assert result is True
        mock_request.assert_called_once_with("connectdevice/Camera/TestCamera")


def test_sgConnectDevice_failure(function):
    """Test failed device connection."""
    function.config.deviceName = "TestCamera"
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": False}
        result = function.sgConnectDevice()
        assert result is False


def test_sgConnectDevice_empty_response(function):
    """Test device connection with empty response."""
    function.config.deviceName = "TestCamera"
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {}
        result = function.sgConnectDevice()
        assert result is False


def test_sgConnectDevice_with_spaces(function):
    """Test device connection with device name containing spaces."""
    function.config.deviceName = "Test Camera"
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True}
        result = function.sgConnectDevice()
        assert result is True
        mock_request.assert_called_once_with("connectdevice/Camera/Test%20Camera")


# ─── Device Enumeration ─────────────────────────────────────────────────────


def test_sgEnumerateDevice_success(function):
    """Test successful device enumeration."""
    devices = ["Camera1", "Camera2"]
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Devices": devices}
        result = function.sgEnumerateDevice()
        assert result == devices
        mock_request.assert_called_once_with("enumdevices/Camera")


def test_sgEnumerateDevice_no_devices(function):
    """Test enumeration with no devices."""
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Devices": []}
        result = function.sgEnumerateDevice()
        assert result == []


def test_sgEnumerateDevice_empty_response(function):
    """Test enumeration with empty response."""
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {}
        result = function.sgEnumerateDevice()
        assert result == []


# ─── Poll Status ────────────────────────────────────────────────────────────


def test_workerPollStatus_connected_to_disconnected(function):
    """Test transitioning from connected to disconnected state."""
    function.config.deviceName = "TestCamera"
    function.deviceConnected = True
    response = {"State": "DISCONNECTED", "Message": "Device disconnected"}
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = response
        function.workerPollStatus()
        assert function.deviceConnected is False


def test_workerPollStatus_disconnected_to_connected(function):
    """Test transitioning from disconnected to connected state."""
    function.config.deviceName = "TestCamera"
    function.deviceConnected = False
    response = {"State": "CONNECTED", "Message": "Device ready"}
    with (
        mock.patch.object(function, "getInitialConfig"),
        mock.patch.object(function, "requestProperty") as mock_request,
    ):
        mock_request.return_value = response
        function.workerPollStatus()
        assert function.deviceConnected is True


def test_workerPollStatus_already_connected(function):
    """Test poll status when already connected."""
    function.config.deviceName = "TestCamera"
    function.deviceConnected = True
    response = {"State": "CONNECTED", "Message": "Device ready"}
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = response
        function.workerPollStatus()
        assert function.deviceConnected is True


def test_workerPollStatus_none_response(function):
    """Test poll status with None response."""
    function.config.deviceName = "TestCamera"
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = None
        function.workerPollStatus()


# ─── Command Queuing ────────────────────────────────────────────────────────


def test_callDeviceMethodQueued_single_call(function):
    """Test queuing a single device method call."""
    function.commandQueue = queue.Queue()
    function.callDeviceMethodQueued("focus", value=100)
    assert not function.commandQueue.empty()
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "call"
    assert item.valueProp == "focus"
    assert item.kwargs == {"value": 100}


def test_callDeviceMethodQueued_multiple_calls(function):
    """Test queuing multiple device method calls."""
    function.commandQueue = queue.Queue()
    function.callDeviceMethodQueued("focus", value=100)
    function.callDeviceMethodQueued("expose", duration=10)
    assert function.commandQueue.qsize() == 2


# ─── Connect Device with Retries ────────────────────────────────────────────


def test_connectDevice_success_first_try(function):
    """Test immediate connection success."""
    function.config.deviceName = "TestCamera"
    with mock.patch.object(function, "sgConnectDevice") as mock_connect:
        mock_connect.return_value = True
        result = function.connectDevice()
        assert result is True
        mock_connect.assert_called_once()


def test_connectDevice_success_after_retries(function):
    """Test connection success after multiple retries."""
    function.config.deviceName = "TestCamera"
    with mock.patch.object(function, "sgConnectDevice") as mock_connect:
        mock_connect.side_effect = [False, False, True]
        with mock.patch("mw4.base.sgproClass.time.sleep"):
            result = function.connectDevice()
            assert result is True
            assert mock_connect.call_count == 3


def test_connectDevice_failure_all_retries(function):
    """Test connection failure after all retries exhausted."""
    function.config.deviceName = "TestCamera"
    with (
        mock.patch.object(function, "sgConnectDevice") as mock_connect,
        mock.patch("mw4.base.sgproClass.time.sleep"),
    ):
        mock_connect.return_value = False
        result = function.connectDevice()
        assert result is False
        assert mock_connect.call_count == 25


def test_connectDevice_emits_error_on_failure(function):
    """Test that error message is emitted on connection failure."""
    function.config.deviceName = "TestCamera"
    function.config.PROTOCOL_NAME = "SGPro"
    with (
        mock.patch.object(function, "sgConnectDevice") as mock_connect,
        mock.patch("mw4.base.sgproClass.time.sleep"),
    ):
        mock_connect.return_value = False
        function.connectDevice()
        function.msg.emit.assert_called_with(2, "SGPro", "Connect error", "TestCamera")


# ─── Process Command Queue ──────────────────────────────────────────────────


def test_processCommandQueue_empty(function):
    """Test processing empty command queue."""
    function.commandQueue = queue.Queue()
    function.processCommandQueue()


def test_processCommandQueue_single_command(function):
    """Test processing single command from queue."""
    function.commandQueue = queue.Queue()
    with mock.patch.object(type(function), "callDeviceMethod", create=True) as mock_call:
        function.commandQueue.put(
            CommandItem(cmdType="call", valueProp="focus", kwargs={"value": 100})
        )
        function.processCommandQueue()
        mock_call.assert_called_once_with("focus", value=100)


def test_processCommandQueue_multiple_commands(function):
    """Test processing multiple commands from queue."""
    function.commandQueue = queue.Queue()
    with mock.patch.object(type(function), "callDeviceMethod", create=True) as mock_call:
        function.commandQueue.put(
            CommandItem(cmdType="call", valueProp="focus", kwargs={"value": 100})
        )
        function.commandQueue.put(
            CommandItem(cmdType="call", valueProp="expose", kwargs={"duration": 10})
        )
        function.processCommandQueue()
        assert mock_call.call_count == 2


def test_processCommandQueue_unknown_cmdtype(function):
    """Test processing unknown command type."""
    function.config.deviceName = "TestCamera"
    function.commandQueue = queue.Queue()
    function.commandQueue.put(CommandItem(cmdType="unknown", valueProp="test"))
    function.processCommandQueue()


# ─── Handle Device Connect/Disconnect ────────────────────────────────────────


def test_handleDeviceConnect_success(function):
    """Test successful device connection handling."""
    function.config.deviceName = "TestCamera"
    function.config.PROTOCOL_NAME = "SGPro"
    function.PROTOCOL_NAME = "SGPro"
    function.deviceConnected = False
    with (
        mock.patch.object(function, "connectDevice") as mock_connect,
        mock.patch.object(function, "getInitialConfig"),
        mock.patch.object(function.msg, "emit"),
    ):
        mock_connect.return_value = True
        function.handleDeviceConnect()
        assert function.deviceConnected is True


def test_handleDeviceConnect_failure(function):
    """Test failed device connection handling."""
    function.config.deviceName = "TestCamera"
    function.deviceConnected = False
    with mock.patch.object(function, "connectDevice") as mock_connect:
        mock_connect.return_value = False
        function.handleDeviceConnect()
        assert function.deviceConnected is False


def test_handleDeviceDisconnect(function):
    """Test device disconnection handling."""
    function.config.deviceName = "TestCamera"
    function.config.PROTOCOL_NAME = "SGPro"
    function.PROTOCOL_NAME = "SGPro"
    function.deviceConnected = True
    with mock.patch.object(function.msg, "emit"):
        function.handleDeviceDisconnect()
    assert function.deviceConnected is False


# ─── Communication Loop ──────────────────────────────────────────────────────


def test_runnerCommunicationLoop_disconnected_state(function):
    """Test communication loop when device is disconnected."""
    function.stopEvent.clear()
    function.deviceConnected = False
    function.UPDATE_RATE = 0.25
    with (
        mock.patch.object(function, "handleDeviceConnect"),
        mock.patch.object(function.stopEvent, "wait") as mock_wait,
    ):
        mock_wait.side_effect = [None, KeyboardInterrupt()]
        with contextlib.suppress(KeyboardInterrupt):
            function.runnerCommunicationLoop()


def test_runnerCommunicationLoop_connected_state(function):
    """Test communication loop when device is connected."""
    function.stopEvent.clear()
    function.deviceConnected = True
    function.UPDATE_RATE = 0.25
    with (
        mock.patch.object(function, "getDeviceProp", create=True) as mock_get_prop,
        mock.patch.object(function, "handleDeviceDisconnect"),
        mock.patch.object(function, "pollData"),
        mock.patch.object(function, "processCommandQueue"),
        mock.patch.object(function.stopEvent, "wait") as mock_wait,
    ):
        mock_get_prop.return_value = True
        mock_wait.side_effect = [None, KeyboardInterrupt()]
        with contextlib.suppress(KeyboardInterrupt):
            function.runnerCommunicationLoop()


def test_runnerCommunicationLoop_stop_event_set(function):
    """Test communication loop stops when stopEvent is set."""
    function.stopEvent.set()
    function.deviceConnected = False
    function.runnerCommunicationLoop()


# ─── Start and Stop Communication ───────────────────────────────────────────


def test_startCommunication_clears_data(function):
    """Test that startCommunication clears data."""
    function.data = {"key": "value"}
    function.stopEvent.set()
    with mock.patch.object(function.threadPool, "start"):
        function.startCommunication()
        assert function.data == {}


def test_startCommunication_initializes_state(function):
    """Test that startCommunication initializes state correctly."""
    function.stopEvent.set()
    function.deviceConnected = True
    with mock.patch.object(function.threadPool, "start"):
        function.startCommunication()
        assert function.deviceConnected is False
        assert not function.stopEvent.is_set()


def test_startCommunication_creates_worker(function):
    """Test that startCommunication creates a worker."""
    function.stopEvent.set()
    with mock.patch.object(function.threadPool, "start"):
        function.startCommunication()
        assert function.workerCommunicationLoop is not None


def test_stopCommunication_sets_stop_event(function):
    """Test that stopCommunication sets the stop event."""
    function.stopEvent.clear()
    function.deviceConnected = True
    function.config.deviceName = "TestCamera"
    function.config.PROTOCOL_NAME = "SGPro"
    function.PROTOCOL_NAME = "SGPro"
    with mock.patch.object(function.msg, "emit"):
        function.stopCommunication()
    assert function.stopEvent.is_set()
    assert function.deviceConnected is False


def test_stopCommunication_emits_message(function):
    """Test that stopCommunication emits removal message."""
    function.stopEvent.clear()
    function.deviceConnected = True
    function.config.deviceName = "TestCamera"
    function.config.PROTOCOL_NAME = "SGPro"
    function.PROTOCOL_NAME = "SGPro"
    with mock.patch.object(function.msg, "emit") as mock_emit:
        function.stopCommunication()
    mock_emit.assert_called()


# ─── Discover Devices ────────────────────────────────────────────────────────


def test_discoverDevices_camera(function):
    """Test device discovery for camera type."""
    devices = ["Camera1", "Camera2"]
    with mock.patch.object(function, "sgEnumerateDevice") as mock_enum:
        mock_enum.return_value = devices
        result = function.discoverDevices("Camera")
        assert result == devices


def test_discoverDevices_empty_result(function):
    """Test device discovery with no devices found."""
    with mock.patch.object(function, "sgEnumerateDevice") as mock_enum:
        mock_enum.return_value = []
        result = function.discoverDevices("Camera")
        assert result == []


# ─── Base Methods (inherited from DriverData) ───────────────────────────────


def test_getInitialConfig_override(function):
    """Test that getInitialConfig is overrideable."""
    function.getInitialConfig()


def test_pollData_override(function):
    """Test that pollData is overrideable."""
    function.pollData()


# ─── Edge Cases and Integration ──────────────────────────────────────────────


def test_multiple_queue_operations(function):
    """Test multiple queue operations in sequence."""
    function.commandQueue = queue.Queue()
    function.callDeviceMethodQueued("focus", value=50)
    function.callDeviceMethodQueued("expose", duration=5)
    function.callDeviceMethodQueued("save", path="/tmp")
    assert function.commandQueue.qsize() == 3


def test_requestProperty_url_construction(function):
    """Test correct URL construction for requestProperty."""
    function.config.hostAddress = "192.168.1.1"
    function.config.port = 8080
    with mock.patch("mw4.base.sgproClass.requests.get") as mock_get:
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        function.requestProperty("testProp")
        called_url = mock_get.call_args[0][0]
        assert called_url == "http://192.168.1.1:8080/testProp?format=json"


def test_sgConnectDevice_url_encoding(function):
    """Test proper URL encoding of device names with spaces."""
    function.config.deviceName = "My Test Camera Device"
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True}
        function.sgConnectDevice()
        called_prop = mock_request.call_args[0][0]
        assert "My%20Test%20Camera%20Device" in called_prop


def test_connect_retry_timing(function):
    """Test that retry uses correct timing."""
    function.config.deviceName = "TestCamera"
    with (
        mock.patch.object(function, "sgConnectDevice") as mock_connect,
        mock.patch("mw4.base.sgproClass.time.sleep") as mock_sleep,
    ):
        mock_connect.return_value = False
        function.connectDevice()
        assert mock_sleep.call_count == 25


def test_device_state_persistence(function):
    """Test that device state persists correctly."""
    function.config.deviceName = "TestCamera"
    function.deviceConnected = False
    response = {"State": "CONNECTED", "Message": "Ready"}
    with (
        mock.patch.object(function, "getInitialConfig"),
        mock.patch.object(function, "requestProperty") as mock_request,
    ):
        mock_request.return_value = response
        function.workerPollStatus()
        assert function.deviceConnected is True
        function.workerPollStatus()
        assert function.deviceConnected is True


def test_processCommandQueue_queue_empty_during_iteration(function):
    """Test processing command queue race condition when it becomes empty."""
    function.commandQueue = queue.Queue()
    function.commandQueue.put(CommandItem(cmdType="call", valueProp="focus", kwargs={}))
    call_count = 0

    def mock_empty():
        nonlocal call_count
        call_count += 1
        return call_count != 1

    with (
        mock.patch.object(function.commandQueue, "empty", side_effect=mock_empty),
        mock.patch.object(function.commandQueue, "get_nowait") as mock_get,
    ):
        mock_get.side_effect = queue.Empty()
        function.processCommandQueue()


def test_runnerCommunicationLoop_device_disconnection_during_polling(function):
    """Test communication loop handles device disconnection during polling."""
    function.stopEvent.clear()
    function.deviceConnected = True
    function.UPDATE_RATE = 0.25
    function.config.deviceName = "TestCamera"
    function.config.PROTOCOL_NAME = "SGPro"
    function.PROTOCOL_NAME = "SGPro"

    with (
        mock.patch.object(function, "getDeviceProp", create=True) as mock_get_prop,
        mock.patch.object(function, "handleDeviceDisconnect") as mock_disconnect,
        mock.patch.object(function.msg, "emit"),
        mock.patch.object(function.stopEvent, "wait") as mock_wait,
    ):
        mock_get_prop.return_value = False
        mock_wait.side_effect = [None, KeyboardInterrupt()]
        with contextlib.suppress(KeyboardInterrupt):
            function.runnerCommunicationLoop()
        mock_disconnect.assert_called()
