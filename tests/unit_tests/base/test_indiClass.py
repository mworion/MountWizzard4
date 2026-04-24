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
import pytest
import threading
import time
from mw4.base.indiClass import IndiClass
from mw4.base.signalsDevices import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


class Parent:
    def __init__(self) -> None:
        self.app = App()
        self.data: dict = {}
        self.signals = Signals()
        self.loadConfig = True
        self.updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    func = IndiClass(parent=Parent())
    yield func


# ─── Properties ──────────────────────────────────────────────────────────────


def test_properties_hostaddress(function):
    function.hostaddress = "192.168.1.1"
    assert function.hostaddress == "192.168.1.1"
    function.hostaddress = None
    assert function.hostaddress is None


def test_properties_port_int(function):
    function.port = 7624
    assert function.port == 7624


def test_properties_port_str(function):
    function.port = "8080"
    assert function.port == 8080


def test_properties_host_getter(function):
    function._host = ("localhost", 7624)
    assert function.host == ("localhost", 7624)


def test_properties_host_setter(function):
    function.host = ("localhost", 7624)
    assert function._host == ("localhost", 7624)


def test_defaultConfig(function):
    assert function.defaultConfig["hostaddress"] == "localhost"
    assert function.defaultConfig["port"] == 7624
    assert function.defaultConfig["loadConfig"] is False
    assert function.defaultConfig["messages"] is False
    assert function.defaultConfig["updateRate"] == 1000


# ─── setStatusDeviceConnected ─────────────────────────────────────────────────


def test_setStatusDeviceConnected_becomeConnected(function):
    function.deviceConnected = False
    function.deviceName = "telescope"
    received = []
    function.signals.deviceConnected.connect(lambda name: received.append(name))
    function.setStatusDeviceConnected(True)
    assert received == ["telescope"]
    assert function.deviceConnected is True


def test_setStatusDeviceConnected_becomeDisconnected(function):
    function.deviceConnected = True
    function.deviceName = "telescope"
    received = []
    function.signals.deviceDisconnected.connect(lambda name: received.append(name))
    function.setStatusDeviceConnected(False)
    assert received == ["telescope"]
    assert function.deviceConnected is False


def test_setStatusDeviceConnected_stayConnected(function):
    function.deviceConnected = True
    function.deviceName = "telescope"
    received = []
    function.signals.deviceConnected.connect(lambda name: received.append(name))
    function.setStatusDeviceConnected(True)
    assert received == []
    assert function.deviceConnected is True


def test_setStatusDeviceConnected_stayDisconnected(function):
    function.deviceConnected = False
    function.deviceName = "telescope"
    received = []
    function.signals.deviceDisconnected.connect(lambda name: received.append(name))
    function.setStatusDeviceConnected(False)
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
    function.writeVectorsToData(vectors)
    assert function.data["TEST_VECTOR.MEMBER"] == "hello"


def test_writeVectorsToData_floatvalue(function):
    function.isINDIGO = False
    function.data = {}
    vectors = {
        "v1": {
            "name": "TEST_VECTOR",
            "members": {"MEMBER": {"floatvalue": 3.14, "value": "ignored"}},
        }
    }
    function.writeVectorsToData(vectors)
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
    function.writeVectorsToData(vectors)
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
    function.writeVectorsToData(vectors)
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
        time.sleep(0.15)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()


def test_processRxQueue_deviceNotInSnapshot(function):
    function.commandRunning = True
    function.deviceName = "MyDevice"

    item = mock.MagicMock()
    item.snapshot = {}  # deviceName not present → .get() returns None → continue
    function.receiveQ.put(item)

    def stopper():
        time.sleep(0.15)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()


def test_processRxQueue_connectionOn(function):
    function.commandRunning = True
    function.deviceName = "MyDevice"
    function.deviceConnected = False

    conn_data = mock.MagicMock()
    conn_data.get.return_value = "On"
    snap_val = _make_snap_val(connection=conn_data, vectors=None)

    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_val}
    item.devicename = "MyDevice"
    function.receiveQ.put(item)

    def stopper():
        time.sleep(0.15)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()
    assert function.deviceConnected is True


def test_processRxQueue_connectionOff(function):
    function.commandRunning = True
    function.deviceName = "MyDevice"
    function.deviceConnected = True

    conn_data = mock.MagicMock()
    conn_data.get.return_value = "Off"
    snap_val = _make_snap_val(connection=conn_data, vectors=None)

    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_val}
    item.devicename = "MyDevice"
    function.receiveQ.put(item)

    def stopper():
        time.sleep(0.15)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()
    assert function.deviceConnected is False


def test_processRxQueue_devicenameMismatch(function):
    """item.devicename != deviceName → continue before vector processing."""
    function.commandRunning = True
    function.deviceName = "MyDevice"

    snap_val = _make_snap_val(connection=None, vectors=None)
    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_val}
    item.devicename = "OtherDevice"
    function.receiveQ.put(item)

    def stopper():
        time.sleep(0.15)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()


def test_processRxQueue_withVectors(function):
    function.commandRunning = True
    function.deviceName = "MyDevice"
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
    function.receiveQ.put(item)

    def stopper():
        time.sleep(0.15)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()
    assert function.data["TEST_VECTOR.M1"] == 99


def test_processRxQueue_noVectors(function):
    """vectors is falsy → writeVectorsToData is NOT called."""
    function.commandRunning = True
    function.deviceName = "MyDevice"
    function.data = {}

    snap_val = _make_snap_val(connection=None, vectors=None)

    item = mock.MagicMock()
    item.snapshot = {"MyDevice": snap_val}
    item.devicename = "MyDevice"
    function.receiveQ.put(item)

    def stopper():
        time.sleep(0.15)
        function.commandRunning = False

    t = threading.Thread(target=stopper)
    t.start()
    function.processRxQueue()
    t.join()
    assert function.data == {}


# ─── cleanupStop ─────────────────────────────────────────────────────────────


def test_cleanupStop(function):
    function.clientMutex.lock()
    function.commandRunning = True
    function.cleanupStop()
    assert function.commandRunning is False
    # Verify mutex was unlocked by successfully locking it again
    assert function.clientMutex.tryLock() is True
    function.clientMutex.unlock()


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
    function.deviceName = "telescope"
    function.deviceConnected = True
    function.commandRunning = True
    function.stopCommunication()
    assert function.deviceName == ""
    assert function.deviceConnected is False
    assert function.commandRunning is False
    assert not function.sendQ.empty()
    assert function.sendQ.get() is None


# ─── loadIndiConfig ──────────────────────────────────────────────────────────


def test_loadIndiConfig(function):
    function.deviceName = "TestDevice"
    function.loadIndiConfig("TestDevice")
    item = function.sendQ.get_nowait()
    assert item == ("TestDevice", "CONFIG_PROCESS", {"CONFIG_PROCESS": True})


# ─── discoverDevices ─────────────────────────────────────────────────────────


def test_discoverDevices_mutexLocked(function):
    function.discoverMutex.lock()
    result = function.discoverDevices("dome")
    assert result == []
    function.discoverMutex.unlock()


def test_discoverDevices_maxSearchZero(function, monkeypatch):
    """Loop never entered when MAX_SEARCH == 0; verifies setup/teardown path."""
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 0)
    with mock.patch("mw4.base.indiClass.Worker"):
        with mock.patch.object(function.threadPool, "start"):
            result = function.discoverDevices("dome")
    assert result == []


def test_discoverDevices_loopEmptyQueue(function, monkeypatch):
    """Loop branch: queue is empty → time.sleep is called."""
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    with mock.patch("mw4.base.indiClass.Worker"):
        with mock.patch.object(function.threadPool, "start"):
            with mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls:
                mock_txQ = mock.MagicMock()
                mock_rxQ = mock.MagicMock()
                mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]
                mock_rxQ.empty.return_value = True  # always empty → sleep branch
                with mock.patch("mw4.base.indiClass.time") as mock_time:
                    mock_time.sleep.side_effect = StopIteration
                    with pytest.raises(StopIteration):
                        function.discoverDevices("dome")
    function.discoverMutex.unlock()


def test_discoverDevices_loopNoneItem(function, monkeypatch):
    """Loop branch: rxQ yields None → continue without incrementing n."""
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    with mock.patch("mw4.base.indiClass.Worker"):
        with mock.patch.object(function.threadPool, "start"):
            with mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls:
                mock_txQ = mock.MagicMock()
                mock_rxQ = mock.MagicMock()
                mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]

                call_count = [0]

                def empty_se():
                    call_count[0] += 1
                    return call_count[0] != 1  # first call: not empty; rest: empty

                mock_rxQ.empty.side_effect = empty_se
                mock_rxQ.get.return_value = None  # None item → continue
                with mock.patch("mw4.base.indiClass.time") as mock_time:
                    mock_time.sleep.side_effect = StopIteration
                    with pytest.raises(StopIteration):
                        function.discoverDevices("dome")
    function.discoverMutex.unlock()


def test_discoverDevices_loopDefineEventMatch(function, monkeypatch):
    """Loop branch: Define event with matching device type → added to result."""
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    driver_info = {"DRIVER_INTERFACE": str(1 << 5)}  # dome interface bit
    snap = mock.MagicMock()
    snap.get.return_value = driver_info

    item = mock.MagicMock()
    item.eventtype = "Define"
    item.devicename = "TestDome"
    item.snapshot = {"TestDome": snap}

    with mock.patch("mw4.base.indiClass.Worker"):
        with mock.patch.object(function.threadPool, "start"):
            with mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls:
                mock_txQ = mock.MagicMock()
                mock_rxQ = mock.MagicMock()
                mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]

                call_count = [0]

                def empty_se():
                    call_count[0] += 1
                    return call_count[0] != 1

                mock_rxQ.empty.side_effect = empty_se
                mock_rxQ.get.return_value = item
                with mock.patch("mw4.base.indiClass.time") as mock_time:
                    mock_time.sleep.side_effect = StopIteration
                    with pytest.raises(StopIteration):
                        function.discoverDevices("dome")
    function.discoverMutex.unlock()


def test_discoverDevices_loopDefineEventNoDriver(function, monkeypatch):
    """Loop branch: Define event but DRIVER_INFO is None → device not added."""
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    snap = mock.MagicMock()
    snap.get.return_value = None  # no DRIVER_INFO

    item = mock.MagicMock()
    item.eventtype = "Define"
    item.devicename = "TestDome"
    item.snapshot = {"TestDome": snap}

    with mock.patch("mw4.base.indiClass.Worker"):
        with mock.patch.object(function.threadPool, "start"):
            with mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls:
                mock_txQ = mock.MagicMock()
                mock_rxQ = mock.MagicMock()
                mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]

                call_count = [0]

                def empty_se():
                    call_count[0] += 1
                    return call_count[0] != 1

                mock_rxQ.empty.side_effect = empty_se
                mock_rxQ.get.return_value = item
                with mock.patch("mw4.base.indiClass.time") as mock_time:
                    mock_time.sleep.side_effect = StopIteration
                    with pytest.raises(StopIteration):
                        function.discoverDevices("dome")
    function.discoverMutex.unlock()


def test_discoverDevices_loopDefineEventNoTypeMatch(function, monkeypatch):
    """Loop branch: Define event but interface bits don't match device type."""
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    driver_info = {"DRIVER_INTERFACE": str(1 << 1)}  # camera bit, not dome

    snap = mock.MagicMock()
    snap.get.return_value = driver_info

    item = mock.MagicMock()
    item.eventtype = "Define"
    item.devicename = "TestCamera"
    item.snapshot = {"TestCamera": snap}

    with mock.patch("mw4.base.indiClass.Worker"):
        with mock.patch.object(function.threadPool, "start"):
            with mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls:
                mock_txQ = mock.MagicMock()
                mock_rxQ = mock.MagicMock()
                mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]

                call_count = [0]

                def empty_se():
                    call_count[0] += 1
                    return call_count[0] != 1

                mock_rxQ.empty.side_effect = empty_se
                mock_rxQ.get.return_value = item
                with mock.patch("mw4.base.indiClass.time") as mock_time:
                    mock_time.sleep.side_effect = StopIteration
                    with pytest.raises(StopIteration):
                        function.discoverDevices("dome")
    function.discoverMutex.unlock()


def test_discoverDevices_loopNonDefineEvent(function, monkeypatch):
    """Loop branch: non-Define event → device not added."""
    monkeypatch.setattr(IndiClass, "MAX_SEARCH", 1)
    item = mock.MagicMock()
    item.eventtype = "Remove"
    item.devicename = "TestDome"

    with mock.patch("mw4.base.indiClass.Worker"):
        with mock.patch.object(function.threadPool, "start"):
            with mock.patch("mw4.base.indiClass.Queue") as mock_queue_cls:
                mock_txQ = mock.MagicMock()
                mock_rxQ = mock.MagicMock()
                mock_queue_cls.side_effect = [mock_txQ, mock_rxQ]

                call_count = [0]

                def empty_se():
                    call_count[0] += 1
                    return call_count[0] != 1

                mock_rxQ.empty.side_effect = empty_se
                mock_rxQ.get.return_value = item
                with mock.patch("mw4.base.indiClass.time") as mock_time:
                    mock_time.sleep.side_effect = StopIteration
                    with pytest.raises(StopIteration):
                        function.discoverDevices("dome")
    function.discoverMutex.unlock()
