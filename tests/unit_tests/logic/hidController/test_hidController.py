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


def test_runnerHidController_deviceNotFound(hc):
    hc.config.deviceName = "NotExisting"
    hc.running = True
    disconnected = []
    hc.signals.deviceDisconnected.connect(lambda name: disconnected.append(name))
    with mock.patch.object(hid, "enumerate", return_value=[]):
        hc.runnerHidController()
    assert hc.running is False
    assert "NotExisting" in disconnected
    hc.signals.deviceDisconnected.disconnect()


def test_runnerHidController_normalRun(hc):
    hc.config.deviceName = "Pro Controller"
    hc.running = True

    class MockDevice:
        def open(self, vid, pid):
            pass

        def set_nonblocking(self, val):
            pass

        def read(self, size):
            hc.running = False
            return []

        def close(self):
            pass

    hid_devices = [{"product_string": "Pro Controller", "vendor_id": 1, "product_id": 2}]
    with (
        mock.patch.object(hid, "enumerate", return_value=hid_devices),
        mock.patch.object(hid, "device", return_value=MockDevice()),
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

        def read(self, size):
            call_count[0] += 1
            if call_count[0] == 1:
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


def test_startCommunication_autoStartFalse(hc):
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
    assert connected == ["TestController"]
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
    assert connected == ["TestController"]
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
