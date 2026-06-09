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
import time
from mw4.base.indiClass import IndiClass
from mw4.base.signalsDevices import Signals
from pathlib import Path
from PySide6.QtCore import QThreadPool
from unittest import mock


class Parent:
    """Minimal parent class for IndiClass testing."""

    def __init__(self) -> None:
        self.data: dict = {}
        self.signals = Signals()
        self.app = mock.MagicMock()
        self.app.msg = mock.MagicMock()
        self.app.threadPool = QThreadPool()
        self.app.mwGlob = {"tempDir": Path("/tmp")}
        self.DEVICE_TYPE = "TEST"


@pytest.fixture(autouse=True, scope="module")
def function():
    func = IndiClass(parent=Parent())
    yield func


# ─── Config access ───────────────────────────────────────────────────────────


def test_config_deviceName(function):
    function.config.deviceName = "TestDevice"
    assert function.config.deviceName == "TestDevice"


def test_config_hostAddress(function):
    function.config.hostAddress = "192.168.1.1"
    assert function.config.hostAddress == "192.168.1.1"


def test_config_port(function):
    function.config.port = 8080
    assert function.config.port == 8080


def test_config_loadConfig(function):
    function.config.loadConfig = True
    assert function.config.loadConfig is True


def test_config_showMessage(function):
    function.config.showMessage = True
    assert function.config.showMessage is True


# ─── updateMessage ───────────────────────────────────────────────────────────


def test_updateMessage_messagesDisabled(function):
    """showMessage == False → early return, msg.emit never called."""
    function.config.showMessage = False
    function.config.deviceName = "MyDevice"
    mock_msg = mock.MagicMock()
    original_msg, function.msg = function.msg, mock_msg
    try:
        function.updateMessage(mock.MagicMock())
    finally:
        function.msg = original_msg
    mock_msg.emit.assert_not_called()


def test_updateMessage_noMessageInSnapshot(function):
    """showMessage == True but snapshot contains no messages → early return."""
    function.config.showMessage = True
    function.config.deviceName = "MyDevice"

    snap_device = mock.MagicMock()
    snap_device.dictdump.return_value = {}  # no "messages" key
    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_device}

    mock_msg = mock.MagicMock()
    original_msg, function.msg = function.msg, mock_msg
    try:
        function.updateMessage(item)
    finally:
        function.msg = original_msg
    mock_msg.emit.assert_not_called()


def test_updateMessage_emitsMessage(function):
    """showMessage == True and snapshot contains a message → msg.emit called."""
    function.config.showMessage = True
    function.config.deviceName = "MyDevice"

    snap_device = mock.MagicMock()
    snap_device.dictdump.return_value = {"messages": [("2024-01-01", "Hello INDI")]}
    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_device}

    mock_msg = mock.MagicMock()
    original_msg, function.msg = function.msg, mock_msg
    try:
        function.updateMessage(item)
    finally:
        function.msg = original_msg
    mock_msg.emit.assert_called_once_with(
        0, "INDI", "Device message", f"{'MyDevice':15s} Hello INDI"
    )


# ─── setStatusDeviceConnected ─────────────────────────────────────────────────


def _make_item(deviceName: str, connect_value: str) -> mock.MagicMock:
    """Build an EventItem mock whose snapshot reports the given CONNECT value."""
    conn = mock.MagicMock()
    conn.get.side_effect = lambda k: connect_value if k == "CONNECT" else None
    snap_device = mock.MagicMock()
    snap_device.__getitem__.return_value = conn
    item = mock.MagicMock()
    item.snapshot = {deviceName: snap_device}
    return item


def test_setStatusDeviceConnected_becomeConnected(function):
    function.deviceConnected = False
    function.config.deviceName = "telescope"
    received = []

    def handler(name: str) -> None:
        received.append(name)

    function.signals.deviceConnected.connect(handler)
    function.setStatusDeviceConnected(_make_item("telescope", "On"))
    assert received == ["telescope"]
    assert function.deviceConnected is True


def test_setStatusDeviceConnected_becomeDisconnected(function):
    function.deviceConnected = True
    function.config.deviceName = "telescope"
    received = []

    def handler(name: str) -> None:
        received.append(name)

    function.signals.deviceDisconnected.connect(handler)
    function.setStatusDeviceConnected(_make_item("telescope", "Off"))
    assert received == ["telescope"]
    assert function.deviceConnected is False


def test_setStatusDeviceConnected_stayConnected(function):
    function.deviceConnected = True
    function.config.deviceName = "telescope"
    received = []
    function.signals.deviceConnected.connect(lambda name: received.append(name))
    function.setStatusDeviceConnected(_make_item("telescope", "On"))
    assert received == []
    assert function.deviceConnected is True


def test_setStatusDeviceConnected_stayDisconnected(function):
    function.deviceConnected = False
    function.config.deviceName = "telescope"
    received = []
    function.signals.deviceDisconnected.connect(lambda name: received.append(name))
    function.setStatusDeviceConnected(_make_item("telescope", "Off"))
    assert received == []
    assert function.deviceConnected is False


# ─── writeVectorsToData ───────────────────────────────────────────────────────


def test_writeVectorsToData_value(function):
    function.isINDIGO = False
    function.data = {}
    vectors = {
        "v1": {
            "name": "TEST_VECTOR",
            "members": {"MEMBER": {"value": "hello"}},
        }
    }
    function.writeVectorsToData(mock.MagicMock(), vectors)
    assert function.data["TEST_VECTOR.MEMBER"] == "hello"


def test_writeVectorsToData_valueOn(function):
    function.isINDIGO = False
    function.data = {}
    vectors = {
        "v1": {
            "name": "TEST_VECTOR",
            "members": {"MEMBER": {"value": "On"}},
        }
    }
    function.writeVectorsToData(mock.MagicMock(), vectors)
    assert function.data["TEST_VECTOR.MEMBER"] is True


def test_writeVectorsToData_valueOff(function):
    function.isINDIGO = False
    function.data = {}
    vectors = {
        "v1": {
            "name": "TEST_VECTOR",
            "members": {"MEMBER": {"value": "Off"}},
        }
    }
    function.writeVectorsToData(mock.MagicMock(), vectors)
    assert function.data["TEST_VECTOR.MEMBER"] is False


def test_writeVectorsToData_floatvalue(function):
    function.isINDIGO = False
    function.data = {}
    vectors = {
        "v1": {
            "name": "TEST_VECTOR",
            "members": {"MEMBER": {"floatvalue": 3.14, "value": "ignored"}},
        }
    }
    function.writeVectorsToData(mock.MagicMock(), vectors)
    assert function.data["TEST_VECTOR.MEMBER"] == 3.14


def test_writeVectorsToData_indigoConversion(function):
    function.isINDIGO = True
    function.data = {}
    vectors = {
        "v1": {
            "name": "SENSORS",
            "members": {"AbsolutePressure": {"value": 1013.0}},
        }
    }
    function.writeVectorsToData(mock.MagicMock(), vectors)
    assert function.data.get("WEATHER_PARAMETERS.WEATHER_PRESSURE") == 1013.0


def test_writeVectorsToData_indigoNoConversion(function):
    function.isINDIGO = True
    function.data = {}
    vectors = {
        "v1": {
            "name": "UNKNOWN_VECTOR",
            "members": {"MEMBER": {"value": 42}},
        }
    }
    function.writeVectorsToData(mock.MagicMock(), vectors)
    assert function.data["UNKNOWN_VECTOR.MEMBER"] == 42


# ─── processRxQueue ──────────────────────────────────────────────────────────


def _make_snap_val(connection=None, vectors=None):
    """Build a mock snapshot device value with optional CONNECTION and vectors."""
    snap_val = mock.MagicMock()
    snap_val.get.side_effect = lambda k: connection if k == "CONNECTION" else None
    if connection is not None:
        snap_val.__getitem__.return_value = connection
    snap_val.dictdump.return_value = {"vectors": vectors}
    return snap_val


def test_processRxQueue_commandNotRunning(function):
    function.commandRunning = False
    function.processRxQueue()


def test_processRxQueue_emptyQueueThenStop(function):
    function.commandRunning = True

    def stopper():
        time.sleep(0.01)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()


def test_processRxQueue_deviceNotInSnapshot(function):
    function.commandRunning = True
    function.config.deviceName = "MyDevice"

    item = mock.MagicMock()
    item.snapshot = {}  # deviceName not present → .get() returns None → continue
    function.rxQ.put(item)

    def stopper():
        time.sleep(0.01)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()


def test_processRxQueue_connectionOn(function):
    function.commandRunning = True
    function.config.deviceName = "MyDevice"
    function.deviceConnected = False

    conn_data = mock.MagicMock()
    conn_data.get.return_value = "On"
    snap_val = _make_snap_val(connection=conn_data, vectors=None)

    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_val}
    item.devicename = "MyDevice"
    function.rxQ.put(item)

    def stopper():
        time.sleep(0.01)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()
    assert function.deviceConnected is True


def test_processRxQueue_connectionOff(function):
    function.commandRunning = True
    function.config.deviceName = "MyDevice"
    function.deviceConnected = True

    conn_data = mock.MagicMock()
    conn_data.get.return_value = "Off"
    snap_val = _make_snap_val(connection=conn_data, vectors=None)

    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_val}
    item.devicename = "MyDevice"
    function.rxQ.put(item)

    def stopper():
        time.sleep(0.01)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()
    assert function.deviceConnected is False


def test_processRxQueue_devicenameMismatch(function):
    """item.devicename != deviceName → continue before vector processing."""
    function.commandRunning = True
    function.config.deviceName = "MyDevice"

    snap_val = _make_snap_val(connection=None, vectors=None)
    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_val}
    item.devicename = "OtherDevice"
    function.rxQ.put(item)

    def stopper():
        time.sleep(0.01)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()


def test_processRxQueue_withVectors(function):
    function.commandRunning = True
    function.config.deviceName = "MyDevice"
    function.data = {}

    vectors = {
        "v1": {
            "name": "TEST_VECTOR",
            "members": {"M1": {"value": 99}},
        }
    }
    snap_val = _make_snap_val(connection=None, vectors=vectors)

    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_val}
    item.devicename = "MyDevice"
    function.rxQ.put(item)

    def stopper():
        time.sleep(0.01)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()
    assert function.data["TEST_VECTOR.M1"] == 99


def test_processRxQueue_noVectors(function):
    """vectors is falsy → writeVectorsToData is NOT called."""
    function.commandRunning = True
    function.config.deviceName = "MyDevice"
    function.data = {}

    snap_val = _make_snap_val(connection=None, vectors=None)

    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_val}
    item.devicename = "MyDevice"
    function.rxQ.put(item)

    def stopper():
        time.sleep(0.01)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()
    assert function.data == {}


def test_processRxQueue_messageEvent(function):
    """eventtype == 'Message' → updateMessage is called."""
    function.commandRunning = True
    function.config.deviceName = "MyDevice"
    function.config.showMessage = True

    snap_device = mock.MagicMock()
    snap_device.get.return_value = None  # no CONNECTION key
    snap_device.dictdump.return_value = {"messages": [("2024-01-01", "test msg")]}

    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_device}
    item.devicename = "MyDevice"
    item.eventtype = "Message"
    function.rxQ.put(item)

    mock_msg = mock.MagicMock()
    original_msg, function.msg = function.msg, mock_msg

    def stopper():
        time.sleep(0.01)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    try:
        function.processRxQueue()
    finally:
        function.msg = original_msg
    t.join()
    mock_msg.emit.assert_called_once_with(
        0, "INDI", "Device message", f"{'MyDevice':15s} test msg"
    )


# ─── cleanupStop ─────────────────────────────────────────────────────────────


def test_cleanupStop(function):
    function.clientMutex.lock()
    function.cleanupStop()
    # Verify mutex was unlocked by successfully locking it again
    assert function.clientMutex.tryLock() is True
    function.clientMutex.unlock()


# ─── runQueueClient ──────────────────────────────────────────────────────────


def test_runQueueClient_loggingTraceOff(function):
    """runQueueClient creates QueClient, calls debug_verbosity(0) and runs asyncrun."""
    function.config.hostAddress = "localhost"
    function.config.port = 7624
    function.loggingTrace = False
    mock_client = mock.MagicMock()
    with (
        mock.patch("mw4.base.indiClass.QueClient", return_value=mock_client) as mock_qc,
        mock.patch("mw4.base.indiClass.asyncio.run") as mock_asyncio_run,
    ):
        function.runQueueClient()
    mock_qc.assert_called_once_with(
        function.txQ,
        function.rxQ,
        indihost="localhost",
        indiport=7624,
        blobfolder=mock.ANY,
    )
    mock_client.debug_verbosity.assert_called_once_with(0)
    mock_asyncio_run.assert_called_once_with(mock_client.asyncrun())
    function.queueClient = None


def test_runQueueClient_loggingTraceOn(function):
    """runQueueClient calls debug_verbosity(3) when loggingTrace is True."""
    function.loggingTrace = True
    mock_client = mock.MagicMock()
    with (
        mock.patch("mw4.base.indiClass.QueClient", return_value=mock_client),
        mock.patch("mw4.base.indiClass.asyncio.run"),
    ):
        function.runQueueClient()
    mock_client.debug_verbosity.assert_called_once_with(3)
    function.queueClient = None
    function.loggingTrace = False


# ─── startCommunication ──────────────────────────────────────────────────────


def test_startCommunication_mutexAlreadyLocked(function):
    function.clientMutex.lock()
    function.startCommunication()
    assert function.commandRunning is False
    function.clientMutex.unlock()


def test_startCommunication_success(function):
    with mock.patch("mw4.base.indiClass.Worker") as mock_worker_cls:
        mock_worker_instance = mock.MagicMock()
        mock_worker_cls.return_value = mock_worker_instance
        with mock.patch.object(function.threadPool, "start"):
            function.startCommunication()
    assert function.commandRunning is True
    assert function.workerIndiQueueClient is mock_worker_instance
    assert function.workerProcessRxQueue is mock_worker_instance
    function.clientMutex.unlock()


# ─── stopCommunication ───────────────────────────────────────────────────────


def test_stopCommunication(function):
    function.config.deviceName = "telescope"
    function.deviceConnected = True
    function.commandRunning = True
    received = []

    def handler(name: str) -> None:
        received.append(name)

    function.signals.deviceDisconnected.connect(handler)
    function.stopCommunication()
    # config.deviceName should remain unchanged
    assert function.config.deviceName == "telescope"
    assert function.deviceConnected is False
    assert function.commandRunning is False
    assert received == ["telescope"]
    # None must be queued to signal stop
    assert function.txQ.get_nowait() is None


# ─── loadIndiConfig ──────────────────────────────────────────────────────────


def test_loadIndiConfig(function):
    # Clear any leftover items in the queue from previous tests
    while not function.txQ.empty():
        try:
            function.txQ.get_nowait()
        except queue.Empty:
            break

    function.config.deviceName = "TestDevice"
    function.loadIndiConfig("TestDevice")
    item = function.txQ.get_nowait()
    assert item == ("TestDevice", "CONFIG_PROCESS", {"CONFIG_PROCESS": True})


def test_discoverDevices_mutexLocked(function):
    function.discoverMutex.lock()
    result = function.discoverDevices("dome", "localhost", 7624)
    assert result == []
    function.discoverMutex.unlock()


def test_discoverDevices_emptyQueue(function, monkeypatch):
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    with (
        mock.patch("mw4.base.indiClass.Worker"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls,
    ):
        mock_txQ = mock.MagicMock()
        mock_rxQ = mock.MagicMock()
        mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]
        mock_rxQ.get.side_effect = queue.Empty()

        result = function.discoverDevices("dome", "localhost", 7624)

    assert result == []
    mock_txQ.put.assert_called_once_with(None)


def test_discoverDevices_noneItem(function, monkeypatch):
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    with (
        mock.patch("mw4.base.indiClass.Worker"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls,
    ):
        mock_txQ = mock.MagicMock()
        mock_rxQ = mock.MagicMock()
        mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]
        mock_rxQ.get.side_effect = [None, queue.Empty()]

        result = function.discoverDevices("dome", "localhost", 7624)

    assert result == []
    mock_txQ.put.assert_called_once_with(None)


def test_discoverDevices_withoutDeviceName(function, monkeypatch):
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    item = mock.MagicMock()
    item.devicename = ""

    with (
        mock.patch("mw4.base.indiClass.Worker"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls,
    ):
        mock_txQ = mock.MagicMock()
        mock_rxQ = mock.MagicMock()
        mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]
        mock_rxQ.get.side_effect = [item, queue.Empty()]

        result = function.discoverDevices("dome", "localhost", 7624)

    assert result == []
    mock_rxQ.task_done.assert_called_once()


def test_discoverDevices_driverMatchingType(function, monkeypatch):
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    driver_info = {"DRIVER_INTERFACE": str(1 << 5)}
    snapshot_value = mock.MagicMock()
    snapshot_value.get.return_value = driver_info
    item = mock.MagicMock()
    item.devicename = "TestDome"
    item.snapshot = {"TestDome": snapshot_value}

    with (
        mock.patch("mw4.base.indiClass.Worker"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls,
    ):
        mock_txQ = mock.MagicMock()
        mock_rxQ = mock.MagicMock()
        mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]
        mock_rxQ.get.side_effect = [item, queue.Empty()]

        result = function.discoverDevices("dome", "localhost", 7624)

    assert result == ["TestDome"]
