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
import hid
import pytest
from mw4.logic.hidController.hidController import (
    DeviceConfigHidController,
    HidController,
    HidControllerSignals,
)
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock
from unittest.mock import MagicMock


@pytest.fixture(autouse=True, scope="module")
def hc(qapp):
    app = App()
    instance = HidController(app)
    yield instance
    app.threadPool.waitForDone(1000)


def test_deviceConfigDefaults():
    cfg = DeviceConfigHidController()
    assert cfg.deviceName == ""
    assert cfg.moveRaDec is True
    assert cfg.moveAltAz is True
    assert cfg.tracking is True
    assert cfg.dome is True


def test_hidControllerSignalsInstantiable():
    sig = HidControllerSignals()
    assert hasattr(sig, "deviceConnected")
    assert hasattr(sig, "deviceDisconnected")
    assert hasattr(sig, "hidABXY")
    assert hasattr(sig, "hidPMH")
    assert hasattr(sig, "hidDirection")
    assert hasattr(sig, "hidSL")
    assert hasattr(sig, "hidSR")


def test_initAttributes(hc):
    assert hc.framework == "hid"
    assert hc.DEVICE_TYPE == "hid"
    assert hc.run["hid"] is hc
    assert isinstance(hc.config, DeviceConfigHidController)
    assert hc.running is False
    assert hc.workerHidController is None
    assert isinstance(hc.data, dict)


def test_isValidHidControllers_proController():
    assert HidController.isValidHidControllers("Pro Controller") is True


def test_isValidHidControllers_game():
    assert HidController.isValidHidControllers("Game Pad") is True


def test_isValidHidControllers_controllerX():
    assert HidController.isValidHidControllers("Controller X") is True


def test_isValidHidControllers_invalid():
    assert HidController.isValidHidControllers("SomeDevice") is False


def test_discoverDevices_empty(hc):
    with mock.patch.object(hid, "enumerate", return_value=[]):
        result = hc.discoverDevices("hid")
    assert result == []


def test_discoverDevices_mixedValid(hc):
    devices = [
        {"product_string": "Pro Controller"},
        {"product_string": "SomeOtherDevice"},
        {"product_string": "Game Pad"},
    ]
    with mock.patch.object(hid, "enumerate", return_value=devices):
        result = hc.discoverDevices("hid")
    assert "Pro Controller" in result
    assert "Game Pad" in result
    assert "SomeOtherDevice" not in result


def test_discoverDevices_deduplicates(hc):
    devices = [
        {"product_string": "Pro Controller"},
        {"product_string": "Pro Controller"},
    ]
    with mock.patch.object(hid, "enumerate", return_value=devices):
        result = hc.discoverDevices("hid")
    assert result.count("Pro Controller") == 1


def test_discoverDevices_deviceTypeIgnored(hc):
    with mock.patch.object(hid, "enumerate", return_value=[]):
        result = hc.discoverDevices("somethingelse")
    assert result == []


def test_isNewerData_emptyList():
    assert HidController.isNewerData([], []) is False


def test_isNewerData_equalLists():
    assert HidController.isNewerData([1, 2, 3], [1, 2, 3]) is False


def test_isNewerData_differentLists():
    assert HidController.isNewerData([1, 2, 4], [1, 2, 3]) is True


def test_convertData_empty(hc):
    result = hc.convertData("unknown", [])
    assert result == [0, 0, 0, 0, 0, 0, 0]


def test_convertData_proController(hc):
    iR = [0, 1, 2, 3, 0, 5, 0, 7, 0, 9, 0, 11]
    result = hc.convertData("Pro Controller", iR)
    assert result == [1, 2, 3, 5, 7, 9, 11]


def test_convertData_xboxDefault(hc):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b00000000]
    result = hc.convertData("Controller (XBOX 360 For Windows)", iR)
    assert result[0] == 10
    assert result[2] == 0b00001111


def test_convertData_xboxUp(hc):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b00011100]
    result = hc.convertData("Controller (XBOX 360 For Windows)", iR)
    assert result[2] == 0b00000110


def test_convertData_xboxRight(hc):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b00010100]
    result = hc.convertData("Controller (XBOX 360 For Windows)", iR)
    assert result[2] == 0b00000100


def test_convertData_xboxDown(hc):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b00001100]
    result = hc.convertData("Controller (XBOX 360 For Windows)", iR)
    assert result[2] == 0b00000010


def test_convertData_xboxLeft(hc):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b00000100]
    result = hc.convertData("Controller (XBOX 360 For Windows)", iR)
    assert result[2] == 0b00000000


def test_sendHidControllerSignals_abxy(hc):
    act = [1, 0, 0, 0, 0, 0, 0]
    old = [0, 0, 0, 0, 0, 0, 0]
    spy = MagicMock()
    hc.signals.hidABXY.connect(spy)
    hc.sendHidControllerSignals(act, old)
    spy.assert_called_once_with(1)
    hc.signals.hidABXY.disconnect(spy)


def test_sendHidControllerSignals_pmh(hc):
    act = [0, 1, 0, 0, 0, 0, 0]
    old = [0, 0, 0, 0, 0, 0, 0]
    spy = MagicMock()
    hc.signals.hidPMH.connect(spy)
    hc.sendHidControllerSignals(act, old)
    spy.assert_called_once_with(1)
    hc.signals.hidPMH.disconnect(spy)


def test_sendHidControllerSignals_direction(hc):
    act = [0, 0, 1, 0, 0, 0, 0]
    old = [0, 0, 0, 0, 0, 0, 0]
    spy = MagicMock()
    hc.signals.hidDirection.connect(spy)
    hc.sendHidControllerSignals(act, old)
    spy.assert_called_once_with(1)
    hc.signals.hidDirection.disconnect(spy)


def test_sendHidControllerSignals_sl(hc):
    act = [0, 0, 0, 1, 2, 0, 0]
    old = [0, 0, 0, 0, 0, 0, 0]
    spy = MagicMock()
    hc.signals.hidSL.connect(spy)
    hc.sendHidControllerSignals(act, old)
    spy.assert_called_once_with(1, 2)
    hc.signals.hidSL.disconnect(spy)


def test_sendHidControllerSignals_sr(hc):
    act = [0, 0, 0, 0, 0, 3, 4]
    old = [0, 0, 0, 0, 0, 0, 0]
    spy = MagicMock()
    hc.signals.hidSR.connect(spy)
    hc.sendHidControllerSignals(act, old)
    spy.assert_called_once_with(3, 4)
    hc.signals.hidSR.disconnect(spy)


def test_sendHidControllerSignals_trackingDisabled(hc):
    hc.config.tracking = False
    act = [1, 0, 0, 0, 0, 0, 0]
    old = [0, 0, 0, 0, 0, 0, 0]
    spy = MagicMock()
    hc.signals.hidABXY.connect(spy)
    hc.sendHidControllerSignals(act, old)
    spy.assert_not_called()
    hc.signals.hidABXY.disconnect(spy)
    hc.config.tracking = True


def test_sendHidControllerSignals_altAzDisabled(hc):
    hc.config.moveAltAz = False
    act = [0, 0, 1, 0, 0, 0, 0]
    old = [0, 0, 0, 0, 0, 0, 0]
    spy = MagicMock()
    hc.signals.hidDirection.connect(spy)
    hc.sendHidControllerSignals(act, old)
    spy.assert_not_called()
    hc.signals.hidDirection.disconnect(spy)
    hc.config.moveAltAz = True


def test_sendHidControllerSignals_domeDisabled(hc):
    hc.config.dome = False
    act = [0, 0, 0, 1, 2, 0, 0]
    old = [0, 0, 0, 0, 0, 0, 0]
    spy = MagicMock()
    hc.signals.hidSL.connect(spy)
    hc.sendHidControllerSignals(act, old)
    spy.assert_not_called()
    hc.signals.hidSL.disconnect(spy)
    hc.config.dome = True


def test_sendHidControllerSignals_raDecDisabled(hc):
    hc.config.moveRaDec = False
    act = [0, 0, 0, 0, 0, 3, 4]
    old = [0, 0, 0, 0, 0, 0, 0]
    spy = MagicMock()
    hc.signals.hidSR.connect(spy)
    hc.sendHidControllerSignals(act, old)
    spy.assert_not_called()
    hc.signals.hidSR.disconnect(spy)
    hc.config.moveRaDec = True


def test_sendHidControllerSignals_noChange(hc):
    act = [0, 0, 0, 0, 0, 0, 0]
    old = [0, 0, 0, 0, 0, 0, 0]
    calls: list = []
    hc.signals.hidABXY.connect(lambda v: calls.append(("ABXY", v)))
    hc.signals.hidPMH.connect(lambda v: calls.append(("PMH", v)))
    hc.signals.hidDirection.connect(lambda v: calls.append(("Dir", v)))
    hc.signals.hidSL.connect(lambda x, y: calls.append(("SL", x, y)))
    hc.signals.hidSR.connect(lambda x, y: calls.append(("SR", x, y)))
    hc.sendHidControllerSignals(act, old)
    assert calls == []
    hc.signals.hidABXY.disconnect()
    hc.signals.hidPMH.disconnect()
    hc.signals.hidDirection.disconnect()
    hc.signals.hidSL.disconnect()
    hc.signals.hidSR.disconnect()


def test_readHidController_returnsData(hc):
    class MockGamepad:
        def __init__(self):
            self.count = 0

        def read(self, size):
            self.count += 1
            if self.count == 1:
                return [1, 2, 3]
            hc.running = False
            return []

    hc.running = True
    result = hc.readHidController(MockGamepad())
    assert result == [1, 2, 3]


def test_readHidController_emptyRead(hc):
    class MockGamepad:
        def read(self, size):
            return []

    hc.running = True
    result = hc.readHidController(MockGamepad())
    assert result == []


def test_readHidController_exception(hc):
    class MockGamepad:
        def read(self, size):
            raise OSError("Device error")

    hc.running = True
    result = hc.readHidController(MockGamepad())
    assert result == []
    assert hc.running is False


def test_isConnected_deviceResponsive(hc):
    mock_device = MagicMock()
    mock_device.read.return_value = [1, 2, 3]
    result = hc.isConnected(mock_device)
    assert result is True
    mock_device.read.assert_called_once_with(64, timeout_ms=0)


def test_isConnected_deviceException(hc):
    mock_device = MagicMock()
    mock_device.read.side_effect = OSError("Device error")
    result = hc.isConnected(mock_device)
    assert result is False


def test_handleConnect_success(hc):
    hc.config.deviceName = "Pro Controller"
    hid_devices = [{"product_string": "Pro Controller", "vendor_id": 1, "product_id": 2}]
    mock_device = MagicMock()
    with (
        mock.patch.object(hid, "enumerate", return_value=hid_devices),
        mock.patch.object(hid, "device", return_value=mock_device),
    ):
        device, vid, pid = hc.handleConnect()
    assert device is mock_device
    assert vid == 1
    assert pid == 2
    mock_device.open.assert_called_once_with(1, 2)
    mock_device.set_nonblocking.assert_called_once_with(True)


def test_handleConnect_deviceNotFound(hc):
    hc.config.deviceName = "NotExisting"
    with mock.patch.object(hid, "enumerate", return_value=[]):
        device, vid, pid = hc.handleConnect()
    assert device is None
    assert vid == 0
    assert pid == 0


def test_handleConnect_exceptionOnOpen(hc):
    hc.config.deviceName = "Pro Controller"
    hid_devices = [{"product_string": "Pro Controller", "vendor_id": 1, "product_id": 2}]
    mock_device = MagicMock()
    mock_device.open.side_effect = OSError("Cannot open device")
    with (
        mock.patch.object(hid, "enumerate", return_value=hid_devices),
        mock.patch.object(hid, "device", return_value=mock_device),
    ):
        device, vid, pid = hc.handleConnect()
    assert device is None
    assert vid == 0
    assert pid == 0


def test_handleDisconnect_success(hc):
    mock_device = MagicMock()
    hc.handleDisconnect(mock_device)
    mock_device.close.assert_called_once()


def test_handleDisconnect_exception(hc):
    mock_device = MagicMock()
    mock_device.close.side_effect = OSError("Cannot close device")
    hc.handleDisconnect(mock_device)
    mock_device.close.assert_called_once()


def test_runnerHidController_deviceNotFound_emitsDisconnect(hc):
    hc.config.deviceName = "NotExisting"
    hc.running = True
    disconnected = []
    hc.signals.deviceDisconnected.connect(lambda name: disconnected.append(name))
    attempt_count = [0]

    def sleep_side_effect(duration):
        attempt_count[0] += 1
        if attempt_count[0] > 1:
            hc.running = False

    with (
        mock.patch.object(hid, "enumerate", return_value=[]),
        mock.patch("time.sleep", side_effect=sleep_side_effect),
    ):
        hc.runnerHidController()
    assert "NotExisting" in disconnected
    hc.signals.deviceDisconnected.disconnect()


def test_runnerHidController_normalRun(hc):
    hc.config.deviceName = "Pro Controller"
    hc.running = True

    class MockDevice:
        def __init__(self):
            self.iteration = 0

        def open(self, vid, pid):
            pass

        def set_nonblocking(self, val):
            pass

        def read(self, size, timeout_ms=None):
            self.iteration += 1
            if timeout_ms == 0:
                return [1, 2, 3]
            if self.iteration == 1:
                return [0, 1, 2, 3, 0, 5, 0, 7, 0, 9, 0, 11]
            hc.running = False
            return []

        def close(self):
            pass

    hid_devices = [{"product_string": "Pro Controller", "vendor_id": 1, "product_id": 2}]
    with (
        mock.patch.object(hid, "enumerate", return_value=hid_devices),
        mock.patch.object(hid, "device", return_value=MockDevice()),
        mock.patch("time.sleep"),
    ):
        hc.runnerHidController()
    assert hc.running is False


def test_runnerHidController_processesNewData(hc):
    hc.config.deviceName = "Pro Controller"
    hc.running = True
    call_count = [0]

    class MockDevice:
        def open(self, vid, pid):
            pass

        def set_nonblocking(self, val):
            pass

        def read(self, size, timeout_ms=None):
            call_count[0] += 1
            if timeout_ms == 0:
                return [1, 2, 3]
            if call_count[0] <= 2:
                return [0, 1, 2, 3, 0, 5, 0, 7, 0, 9, 0, 11]
            hc.running = False
            return []

        def close(self):
            pass

    hid_devices = [{"product_string": "Pro Controller", "vendor_id": 1, "product_id": 2}]
    with (
        mock.patch.object(hid, "enumerate", return_value=hid_devices),
        mock.patch.object(hid, "device", return_value=MockDevice()),
        mock.patch.object(hc, "sendHidControllerSignals") as mock_send,
        mock.patch("time.sleep"),
    ):
        hc.runnerHidController()
    mock_send.assert_called_once()


def test_startCommunication_noEarlySignal(hc):
    hc.running = False
    hc.workerHidController = None
    hc.config.deviceName = "TestController"
    connected = []
    hc.signals.deviceConnected.connect(lambda n: connected.append(n))
    with mock.patch.object(hc.threadPool, "start") as mock_start:
        hc.startCommunication()
    assert hc.running is True
    assert hc.workerHidController is not None
    mock_start.assert_called_once()
    assert connected == []
    hc.running = False
    hc.signals.deviceConnected.disconnect()


def test_startCommunication_autoStartTrue(hc):
    hc.running = False
    hc.workerHidController = None
    hc.config.deviceName = "TestController"
    connected = []
    hc.signals.deviceConnected.connect(lambda n: connected.append(n))
    with mock.patch.object(hc.threadPool, "start") as mock_start:
        hc.startCommunication()
    assert hc.running is True
    assert hc.workerHidController is not None
    mock_start.assert_called_once()
    assert connected == []
    hc.running = False
    hc.signals.deviceConnected.disconnect()


def test_stopCommunication(hc):
    hc.running = True
    hc.config.deviceName = "TestController"
    disconnected = []
    hc.signals.deviceDisconnected.connect(lambda n: disconnected.append(n))
    hc.stopCommunication()
    assert hc.running is False
    assert "TestController" in disconnected
    hc.signals.deviceDisconnected.disconnect()


def test_runnerHidController_emitsConnectedSignal(hc):
    hc.config.deviceName = "Pro Controller"
    hc.running = True
    connected = []
    hc.signals.deviceConnected.connect(lambda name: connected.append(name))

    class MockDevice:
        def open(self, vid, pid):
            pass

        def set_nonblocking(self, val):
            pass

        def read(self, size, timeout_ms=None):
            if timeout_ms == 0:
                return [1, 2, 3]
            hc.running = False
            return []

        def close(self):
            pass

    hid_devices = [{"product_string": "Pro Controller", "vendor_id": 1, "product_id": 2}]
    with (
        mock.patch.object(hid, "enumerate", return_value=hid_devices),
        mock.patch.object(hid, "device", return_value=MockDevice()),
        mock.patch("time.sleep"),
    ):
        hc.runnerHidController()
    assert "Pro Controller" in connected
    hc.signals.deviceConnected.disconnect()


def test_runnerHidController_reconnectionOnDisconnect(hc):
    hc.config.deviceName = "Pro Controller"
    hc.running = True
    connected = []
    disconnected = []
    hc.signals.deviceConnected.connect(lambda name: connected.append(name))
    hc.signals.deviceDisconnected.connect(lambda name: disconnected.append(name))

    device_call_count = [0]

    class MockDevice:
        def open(self, vid, pid):
            pass

        def set_nonblocking(self, val):
            pass

        def read(self, size, timeout_ms=None):
            device_call_count[0] += 1
            if timeout_ms == 0:
                if device_call_count[0] == 1:
                    return [1, 2, 3]
                raise OSError("Device disconnected")
            if device_call_count[0] <= 2:
                return [0, 1, 2, 3, 0, 5, 0, 7, 0, 9, 0, 11]
            hc.running = False
            return []

        def close(self):
            pass

    hid_devices = [{"product_string": "Pro Controller", "vendor_id": 1, "product_id": 2}]
    with (
        mock.patch.object(hid, "enumerate", return_value=hid_devices),
        mock.patch.object(hid, "device", return_value=MockDevice()),
        mock.patch("time.sleep"),
    ):
        hc.runnerHidController()
    assert "Pro Controller" in connected
    hc.signals.deviceConnected.disconnect()
    hc.signals.deviceDisconnected.disconnect()


def test_runnerHidController_retryOnInitialConnectionFailure(hc):
    hc.config.deviceName = "Pro Controller"
    hc.running = True
    disconnected = []
    hc.signals.deviceDisconnected.connect(lambda name: disconnected.append(name))
    enumerate_call_count = [0]

    def enumerate_mock():
        enumerate_call_count[0] += 1
        if enumerate_call_count[0] <= 2:
            return []
        hc.running = False
        return []

    with (
        mock.patch.object(hid, "enumerate", side_effect=enumerate_mock),
        mock.patch("time.sleep") as mock_sleep,
    ):
        hc.runnerHidController()
    assert enumerate_call_count[0] >= 2
    mock_sleep.assert_called_with(0.5)
    hc.signals.deviceDisconnected.disconnect()


def test_runnerHidController_cleansUpOnExit(hc):
    hc.config.deviceName = "Pro Controller"
    hc.running = True
    close_called = []

    class MockDevice:
        def open(self, vid, pid):
            pass

        def set_nonblocking(self, val):
            pass

        def read(self, size, timeout_ms=None):
            if timeout_ms == 0:
                return [1, 2, 3]
            hc.running = False
            return []

        def close(self):
            close_called.append(True)

    hid_devices = [{"product_string": "Pro Controller", "vendor_id": 1, "product_id": 2}]
    with (
        mock.patch.object(hid, "enumerate", return_value=hid_devices),
        mock.patch.object(hid, "device", return_value=MockDevice()),
        mock.patch("time.sleep"),
    ):
        hc.runnerHidController()
    assert len(close_called) == 1
