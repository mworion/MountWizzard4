# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.base.indiClass import IndiClass
from mw4.logic.powerswitch.pegasusUPB import PegasusUPB
from mw4.logic.powerswitch.pegasusUPBIndi import PegasusUPBIndi
from queue import Queue
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        upb = PegasusUPB(App())
        func = PegasusUPBIndi(parent=upb)
        func.config.deviceName = "test_upb"
    except (
        RuntimeError,
        ImportError,
        AttributeError,
        ConnectionError,
        OSError,
        ValueError,
    ) as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func
    func.app.threadPool.waitForDone(5000)


def test_checkDriverInfo_absent(function):
    function.modelVersion = 0
    function.checkDriverInfo({})
    assert function.modelVersion == 0


def test_checkDriverInfo_upb_model_changes_to_1(function):
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"DRIVER_INFO": {"members": {"DEVICE_MODEL": "UPB"}}}
    function.checkDriverInfo(vectors)
    slot.assert_called_once_with(1)
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


def test_checkDriverInfo_upb_model_already_1(function):
    function.modelVersion = 1
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"DRIVER_INFO": {"members": {"DEVICE_MODEL": "UPB"}}}
    function.checkDriverInfo(vectors)
    slot.assert_not_called()
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


def test_checkDriverInfo_non_upb_changes_to_2(function):
    function.modelVersion = 1
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"DRIVER_INFO": {"members": {"DEVICE_MODEL": "UPBv2"}}}
    function.checkDriverInfo(vectors)
    slot.assert_called_once_with(2)
    assert function.modelVersion == 2
    function.signals.version.disconnect(slot)


def test_checkDriverInfo_non_upb_already_2(function):
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"DRIVER_INFO": {"members": {"DEVICE_MODEL": "UPBv2"}}}
    function.checkDriverInfo(vectors)
    slot.assert_not_called()
    assert function.modelVersion == 2
    function.signals.version.disconnect(slot)


def test_parseVersion_valid(function):
    assert function.parseVersion("1.10") == (1, 10)
    assert function.parseVersion("1.10") > function.parseVersion("1.4")


def test_parseVersion_invalid(function):
    assert function.parseVersion("abc") == (0,)


def test_checkFirmwareInfo_absent(function):
    function.modelVersion = 0
    function.checkFirmwareInfo({})
    assert function.modelVersion == 0


def test_checkFirmwareInfo_old_firmware_changes_to_1(function):
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {"VERSION": {"value": "1.4"}}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_called_once_with(1)
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


def test_checkFirmwareInfo_old_firmware_already_1(function):
    function.modelVersion = 1
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {"VERSION": {"value": "1.4"}}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_not_called()
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


def test_checkFirmwareInfo_new_firmware_changes_to_2(function):
    function.modelVersion = 1
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {"VERSION": {"value": "1.5"}}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_called_once_with(2)
    assert function.modelVersion == 2
    function.signals.version.disconnect(slot)


def test_checkFirmwareInfo_new_firmware_already_2(function):
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {"VERSION": {"value": "1.6"}}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_not_called()
    assert function.modelVersion == 2
    function.signals.version.disconnect(slot)


def test_checkFirmwareInfo_missing_version_defaults_old(function):
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_called_once_with(1)
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


def test_writeVectorsToData(function):
    item = mock.MagicMock()
    vectors = {}
    with (
        mock.patch.object(IndiClass, "writeVectorsToData") as mock_super,
        mock.patch.object(function, "checkDriverInfo") as mock_drv,
        mock.patch.object(function, "checkFirmwareInfo") as mock_fw,
    ):
        function.writeVectorsToData(item, vectors)
        mock_super.assert_called_once_with(item, vectors)
        mock_drv.assert_called_once_with(vectors)
        mock_fw.assert_called_once_with(vectors)


def test_togglePowerPort_indi_off_to_on(function):
    function.txQ = Queue()
    function.isINDIGO = False
    function.data["POWER_CHANNELS.POWER_CHANNEL_1"] = False
    function.togglePowerPort(port="1")
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "POWER_CHANNELS", {"POWER_CHANNEL_1": "On"})


def test_togglePowerPort_indi_on_to_off(function):
    function.txQ = Queue()
    function.isINDIGO = False
    function.data["POWER_CHANNELS.POWER_CHANNEL_2"] = True
    function.togglePowerPort(port="2")
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "POWER_CHANNELS", {"POWER_CHANNEL_2": "Off"})


def test_togglePowerPort_indigo_off_to_on(function):
    function.txQ = Queue()
    function.isINDIGO = True
    function.data["AUX_POWER_OUTLET.OUTLET_1"] = False
    function.togglePowerPort(port="1")
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "AUX_POWER_OUTLET", {"OUTLET_1": "On"})


def test_togglePowerPort_indigo_on_to_off(function):
    function.txQ = Queue()
    function.isINDIGO = True
    function.data["AUX_POWER_OUTLET.OUTLET_2"] = True
    function.togglePowerPort(port="2")
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "AUX_POWER_OUTLET", {"OUTLET_2": "Off"})


def test_toggleHubUSB_indigo_returns_early(function):
    function.txQ = Queue()
    function.isINDIGO = True
    function.toggleHubUSB()
    assert function.txQ.qsize() == 0


def test_toggleHubUSB_indi_off_to_on(function):
    function.txQ = Queue()
    function.isINDIGO = False
    function.data["USB_HUB_CONTROL.INDI_ENABLED"] = False
    function.toggleHubUSB()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "USB_HUB_CONTROL", {"INDI_ENABLED": "On"})


def test_toggleHubUSB_indi_on_to_off(function):
    function.txQ = Queue()
    function.isINDIGO = False
    function.data["USB_HUB_CONTROL.INDI_ENABLED"] = True
    function.toggleHubUSB()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "USB_HUB_CONTROL", {"INDI_ENABLED": "Off"})


def test_togglePortUSB_indi_off_to_on(function):
    function.txQ = Queue()
    function.isINDIGO = False
    function.data["USB_PORTS.USB_PORT_1"] = False
    function.togglePortUSB(port="1")
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "USB_PORTS", {"USB_PORT_1": "On"})


def test_togglePortUSB_indi_on_to_off(function):
    function.txQ = Queue()
    function.isINDIGO = False
    function.data["USB_PORTS.USB_PORT_2"] = True
    function.togglePortUSB(port="2")
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "USB_PORTS", {"USB_PORT_2": "Off"})


def test_togglePortUSB_indigo_off_to_on(function):
    function.txQ = Queue()
    function.isINDIGO = True
    function.data["AUX_USB_PORT.PORT_1"] = False
    function.togglePortUSB(port="1")
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "AUX_USB_PORT", {"PORT_1": "On"})


def test_togglePortUSB_indigo_on_to_off(function):
    function.txQ = Queue()
    function.isINDIGO = True
    function.data["AUX_USB_PORT.PORT_2"] = True
    function.togglePortUSB(port="2")
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "AUX_USB_PORT", {"PORT_2": "Off"})


def test_sendDew_indi(function):
    function.txQ = Queue()
    function.isINDIGO = False
    function.sendDew(port="1", value=75)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "DEW_DUTY_CYCLES", {"DEW_CHANNEL_1": 75})


def test_sendDew_indigo(function):
    function.txQ = Queue()
    function.isINDIGO = True
    function.sendDew(port="2", value=30)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "AUX_HEATER_OUTLET", {"OUTLET_2": 30})


def test_sendAdjustableOutput_indi(function):
    function.txQ = Queue()
    function.isINDIGO = False
    function.sendAdjustableOutput(12.0)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "VARIABLE_VOLTAGES", {"VAR_CHANNEL_1": 12.0})


def test_sendAdjustableOutput_indigo(function):
    function.txQ = Queue()
    function.isINDIGO = True
    function.sendAdjustableOutput(12.0)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == (
        "test_upb",
        "X_AUX_VARIABLE_POWER_OUTLET",
        {"OUTLET_1": 12.0},
    )


def test_reboot_indi(function):
    function.txQ = Queue()
    function.isINDIGO = False
    function.reboot()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "REBOOT_DEVICE", {"REBOOT": "On"})


def test_reboot_indigo(function):
    function.txQ = Queue()
    function.isINDIGO = True
    function.reboot()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_upb", "X_AUX_REBOOT", {"REBOOT": "On"})
