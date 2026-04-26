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
import unittest.mock as mock
from queue import Queue

from mw4.base.indiClass import IndiClass
from mw4.logic.powerswitch.pegasusUPB import PegasusUPB
from mw4.logic.powerswitch.pegasusUPBIndi import PegasusUPBIndi
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    upb = PegasusUPB(App())
    func = PegasusUPBIndi(parent=upb)
    yield func
    func.app.threadPool.waitForDone(5000)


# ---------------------------------------------------------------------------
# setUpdateConfig
# ---------------------------------------------------------------------------

def test_setUpdateConfig(function):
    """setUpdateConfig() puts POLLING_PERIOD with updateRate into sendQ."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.updateRate = 1500
    function.setUpdateConfig("ignored")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "POLLING_PERIOD", {"PERIOD_MS": 1500})


# ---------------------------------------------------------------------------
# checkDriverInfo
# ---------------------------------------------------------------------------

def test_checkDriverInfo_absent(function):
    """No 'DRIVER_INFO' key → early return, modelVersion unchanged."""
    function.modelVersion = 0
    function.checkDriverInfo({})
    assert function.modelVersion == 0


def test_checkDriverInfo_upb_model_changes_to_1(function):
    """DEVICE_MODEL='UPB' and modelVersion != 1 → emit version 1."""
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"DRIVER_INFO": {"members": {"DEVICE_MODEL": "UPB"}}}
    function.checkDriverInfo(vectors)
    slot.assert_called_once_with(1)
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


def test_checkDriverInfo_upb_model_already_1(function):
    """DEVICE_MODEL='UPB' and modelVersion already 1 → no emit."""
    function.modelVersion = 1
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"DRIVER_INFO": {"members": {"DEVICE_MODEL": "UPB"}}}
    function.checkDriverInfo(vectors)
    slot.assert_not_called()
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


def test_checkDriverInfo_non_upb_changes_to_2(function):
    """DEVICE_MODEL != 'UPB' and modelVersion != 2 → emit version 2."""
    function.modelVersion = 1
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"DRIVER_INFO": {"members": {"DEVICE_MODEL": "UPBv2"}}}
    function.checkDriverInfo(vectors)
    slot.assert_called_once_with(2)
    assert function.modelVersion == 2
    function.signals.version.disconnect(slot)


def test_checkDriverInfo_non_upb_already_2(function):
    """DEVICE_MODEL != 'UPB' and modelVersion already 2 → no emit."""
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"DRIVER_INFO": {"members": {"DEVICE_MODEL": "UPBv2"}}}
    function.checkDriverInfo(vectors)
    slot.assert_not_called()
    assert function.modelVersion == 2
    function.signals.version.disconnect(slot)


# ---------------------------------------------------------------------------
# checkFirmwareInfo
# ---------------------------------------------------------------------------

def test_checkFirmwareInfo_absent(function):
    """No 'FIRMWARE_INFO' key → early return, modelVersion unchanged."""
    function.modelVersion = 0
    function.checkFirmwareInfo({})
    assert function.modelVersion == 0


def test_checkFirmwareInfo_old_firmware_changes_to_1(function):
    """VERSION < 1.5 and modelVersion != 1 → emit version 1."""
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {"VERSION": "1.4"}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_called_once_with(1)
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


def test_checkFirmwareInfo_old_firmware_already_1(function):
    """VERSION < 1.5 and modelVersion already 1 → no emit."""
    function.modelVersion = 1
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {"VERSION": "1.4"}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_not_called()
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


def test_checkFirmwareInfo_new_firmware_changes_to_2(function):
    """VERSION >= 1.5 and modelVersion != 2 → emit version 2."""
    function.modelVersion = 1
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {"VERSION": "1.5"}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_called_once_with(2)
    assert function.modelVersion == 2
    function.signals.version.disconnect(slot)


def test_checkFirmwareInfo_new_firmware_already_2(function):
    """VERSION >= 1.5 and modelVersion already 2 → no emit."""
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {"VERSION": "1.6"}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_not_called()
    assert function.modelVersion == 2
    function.signals.version.disconnect(slot)


def test_checkFirmwareInfo_missing_version_defaults_old(function):
    """Missing VERSION key defaults to '1.4' (< 1.5) → treated as old firmware."""
    function.modelVersion = 2
    slot = mock.MagicMock()
    function.signals.version.connect(slot)
    vectors = {"FIRMWARE_INFO": {"members": {}}}
    function.checkFirmwareInfo(vectors)
    slot.assert_called_once_with(1)
    assert function.modelVersion == 1
    function.signals.version.disconnect(slot)


# ---------------------------------------------------------------------------
# writeVectorsToData
# ---------------------------------------------------------------------------

def test_writeVectorsToData(function):
    """All delegates and super() are called with the vectors dict."""
    vectors = {}
    with mock.patch.object(IndiClass, "writeVectorsToData") as mock_super:
        with mock.patch.object(function, "checkDriverInfo") as mock_drv:
            with mock.patch.object(function, "checkFirmwareInfo") as mock_fw:
                function.writeVectorsToData(vectors)
                mock_super.assert_called_once_with(vectors)
                mock_drv.assert_called_once_with(vectors)
                mock_fw.assert_called_once_with(vectors)


# ---------------------------------------------------------------------------
# togglePowerPort
# ---------------------------------------------------------------------------

def test_togglePowerPort_indi_off_to_on(function):
    """isINDIGO=False, current value 'Off' → queues 'On'."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.data["POWER_CONTROL.POWER_CONTROL_1"] = "Off"
    function.togglePowerPort(port="1")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "POWER_CONTROL", {"POWER_CONTROL_1": "On"}
    )


def test_togglePowerPort_indi_on_to_off(function):
    """isINDIGO=False, current value 'On' → queues 'Off'."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.data["POWER_CONTROL.POWER_CONTROL_2"] = "On"
    function.togglePowerPort(port="2")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "POWER_CONTROL", {"POWER_CONTROL_2": "Off"}
    )


def test_togglePowerPort_indigo_off_to_on(function):
    """isINDIGO=True, current value 'Off' → queues 'On' to AUX_POWER_OUTLET."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.data["AUX_POWER_OUTLET.OUTLET_1"] = "Off"
    function.togglePowerPort(port="1")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "AUX_POWER_OUTLET", {"OUTLET_1": "On"}
    )


def test_togglePowerPort_indigo_on_to_off(function):
    """isINDIGO=True, current value 'On' → queues 'Off' to AUX_POWER_OUTLET."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.data["AUX_POWER_OUTLET.OUTLET_2"] = "On"
    function.togglePowerPort(port="2")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "AUX_POWER_OUTLET", {"OUTLET_2": "Off"}
    )


# ---------------------------------------------------------------------------
# togglePowerPortBoot
# ---------------------------------------------------------------------------

def test_togglePowerPortBoot_indigo_returns_early(function):
    """isINDIGO=True → early return, nothing put into sendQ."""
    function.sendQ = Queue()
    function.isINDIGO = True
    function.togglePowerPortBoot(port="1")
    assert function.sendQ.qsize() == 0


def test_togglePowerPortBoot_indi_off_to_on(function):
    """isINDIGO=False, current value 'Off' → queues 'On'."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.data["POWER_ON_BOOT.POWER_PORT_1"] = "Off"
    function.togglePowerPortBoot(port="1")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "POWER_ON_BOOT", {"POWER_PORT_1": "On"}
    )


def test_togglePowerPortBoot_indi_on_to_off(function):
    """isINDIGO=False, current value 'On' → queues 'Off'."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.data["POWER_ON_BOOT.POWER_PORT_2"] = "On"
    function.togglePowerPortBoot(port="2")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "POWER_ON_BOOT", {"POWER_PORT_2": "Off"}
    )


# ---------------------------------------------------------------------------
# toggleHubUSB
# ---------------------------------------------------------------------------

def test_toggleHubUSB_indigo_returns_early(function):
    """isINDIGO=True → early return, nothing put into sendQ."""
    function.sendQ = Queue()
    function.isINDIGO = True
    function.toggleHubUSB()
    assert function.sendQ.qsize() == 0


def test_toggleHubUSB_indi_off_to_on(function):
    """isINDIGO=False, USB hub 'Off' → queues 'On'."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.data["USB_HUB_CONTROL.INDI_ENABLED"] = "Off"
    function.toggleHubUSB()
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "USB_HUB_CONTROL", {"INDI_ENABLED": "On"}
    )


def test_toggleHubUSB_indi_on_to_off(function):
    """isINDIGO=False, USB hub 'On' → queues 'Off'."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.data["USB_HUB_CONTROL.INDI_ENABLED"] = "On"
    function.toggleHubUSB()
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "USB_HUB_CONTROL", {"INDI_ENABLED": "Off"}
    )


# ---------------------------------------------------------------------------
# togglePortUSB
# ---------------------------------------------------------------------------

def test_togglePortUSB_indi_off_to_on(function):
    """isINDIGO=False, port 'Off' → queues 'On' to USB_PORT_CONTROL."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.data["USB_PORT_CONTROL.PORT_1"] = "Off"
    function.togglePortUSB(port="1")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "USB_PORT_CONTROL", {"PORT_1": "On"}
    )


def test_togglePortUSB_indi_on_to_off(function):
    """isINDIGO=False, port 'On' → queues 'Off' to USB_PORT_CONTROL."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.data["USB_PORT_CONTROL.PORT_2"] = "On"
    function.togglePortUSB(port="2")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "USB_PORT_CONTROL", {"PORT_2": "Off"}
    )


def test_togglePortUSB_indigo_off_to_on(function):
    """isINDIGO=True, port 'Off' → queues 'On' to AUX_USB_PORT."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.data["AUX_USB_PORT.PORT_1"] = "Off"
    function.togglePortUSB(port="1")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "AUX_USB_PORT", {"PORT_1": "On"})


def test_togglePortUSB_indigo_on_to_off(function):
    """isINDIGO=True, port 'On' → queues 'Off' to AUX_USB_PORT."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.data["AUX_USB_PORT.PORT_2"] = "On"
    function.togglePortUSB(port="2")
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "AUX_USB_PORT", {"PORT_2": "Off"})


# ---------------------------------------------------------------------------
# toggleAutoDew  (legacy: still uses self.device / self.client)
# ---------------------------------------------------------------------------

def test_toggleAutoDew_device_none(function):
    """device=None → early return, nothing put into sendQ."""
    function.sendQ = Queue()
    function.device = None
    function.toggleAutoDew()
    assert function.sendQ.qsize() == 0


def test_toggleAutoDew_indigo_manual_on(function):
    """isINDIGO=True, MANUAL='On' → sends MANUAL=Off and AUTOMATIC=On."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.device = mock.MagicMock()
    function.data["AUX_DEW_CONTROL.MANUAL"] = "On"
    function.toggleAutoDew()
    assert function.sendQ.qsize() == 2
    assert function.sendQ.get() == ("test_upb", "AUX_DEW_CONTROL", {"MANUAL": "Off"})
    assert function.sendQ.get() == ("test_upb", "AUX_DEW_CONTROL", {"AUTOMATIC": "On"})


def test_toggleAutoDew_indigo_manual_off(function):
    """isINDIGO=True, MANUAL='Off' → sends MANUAL=On and AUTOMATIC=Off."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.device = mock.MagicMock()
    function.data["AUX_DEW_CONTROL.MANUAL"] = "Off"
    function.toggleAutoDew()
    assert function.sendQ.qsize() == 2
    assert function.sendQ.get() == ("test_upb", "AUX_DEW_CONTROL", {"MANUAL": "On"})
    assert function.sendQ.get() == ("test_upb", "AUX_DEW_CONTROL", {"AUTOMATIC": "Off"})


def test_toggleAutoDew_indi_v1_no_indi_enabled(function):
    """modelVersion=1, 'AUTO_DEW.INDI_ENABLED' not in data → early return."""
    function.sendQ = Queue()
    function.isINDIGO = False
    function.modelVersion = 1
    function.device = mock.MagicMock()
    function.data.pop("AUTO_DEW.INDI_ENABLED", None)
    function.toggleAutoDew()
    assert function.sendQ.qsize() == 0


def test_toggleAutoDew_indi_v1_enabled_on(function):
    """modelVersion=1, INDI_ENABLED='On' → queues INDI_ENABLED=Off."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.modelVersion = 1
    function.device = mock.MagicMock()
    function.data["AUTO_DEW.INDI_ENABLED"] = "On"
    function.toggleAutoDew()
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "AUTO_DEW", {"INDI_ENABLED": "Off"})


def test_toggleAutoDew_indi_v1_enabled_off(function):
    """modelVersion=1, INDI_ENABLED='Off' → queues INDI_ENABLED=On."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.modelVersion = 1
    function.device = mock.MagicMock()
    function.data["AUTO_DEW.INDI_ENABLED"] = "Off"
    function.toggleAutoDew()
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "AUTO_DEW", {"INDI_ENABLED": "On"})


def test_toggleAutoDew_indi_v2_no_dew_a(function):
    """modelVersion=2, 'AUTO_DEW.DEW_A' not in data → early return."""
    function.sendQ = Queue()
    function.isINDIGO = False
    function.modelVersion = 2
    function.device = mock.MagicMock()
    function.data.pop("AUTO_DEW.DEW_A", None)
    function.toggleAutoDew()
    assert function.sendQ.qsize() == 0


def test_toggleAutoDew_indi_v2_dew_a_on(function):
    """modelVersion=2, DEW_A='On' → queues DEW_A/B/C=Off."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.modelVersion = 2
    function.device = mock.MagicMock()
    function.data["AUTO_DEW.DEW_A"] = "On"
    function.toggleAutoDew()
    assert function.sendQ.qsize() == 3
    assert function.sendQ.get() == ("test_upb", "AUTO_DEW", {"DEW_A": "Off"})
    assert function.sendQ.get() == ("test_upb", "AUTO_DEW", {"DEW_B": "Off"})
    assert function.sendQ.get() == ("test_upb", "AUTO_DEW", {"DEW_C": "Off"})


def test_toggleAutoDew_indi_v2_dew_a_off(function):
    """modelVersion=2, DEW_A='Off' → queues DEW_A/B/C=On."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.modelVersion = 2
    function.device = mock.MagicMock()
    function.data["AUTO_DEW.DEW_A"] = "Off"
    function.toggleAutoDew()
    assert function.sendQ.qsize() == 3
    assert function.sendQ.get() == ("test_upb", "AUTO_DEW", {"DEW_A": "On"})
    assert function.sendQ.get() == ("test_upb", "AUTO_DEW", {"DEW_B": "On"})
    assert function.sendQ.get() == ("test_upb", "AUTO_DEW", {"DEW_C": "On"})


# ---------------------------------------------------------------------------
# sendDew  (sendQ-based)
# ---------------------------------------------------------------------------

def test_sendDew_indi(function):
    """isINDIGO=False → queues DEW_PWM with correct port key."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.sendDew(port="A", value=75)
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "DEW_PWM", {"DEW_A": 75})


def test_sendDew_indi_port_b(function):
    """isINDIGO=False, port B → queues DEW_B."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.sendDew(port="B", value=50)
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "DEW_PWM", {"DEW_B": 50})


def test_sendDew_indigo(function):
    """isINDIGO=True, port A → queues AUX_HEATER_OUTLET with OUTLET_1."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.sendDew(port="A", value=50)
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "AUX_HEATER_OUTLET", {"OUTLET_1": 50})


def test_sendDew_indigo_port_b(function):
    """isINDIGO=True, port B → queues OUTLET_2."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.sendDew(port="B", value=30)
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "AUX_HEATER_OUTLET", {"OUTLET_2": 30})


# ---------------------------------------------------------------------------
# sendAdjustableOutput  (sendQ-based)
# ---------------------------------------------------------------------------

def test_sendAdjustableOutput_indi(function):
    """isINDIGO=False → queues ADJUSTABLE_VOLTAGE_VALUE."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.sendAdjustableOutput(12.0)
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "ADJUSTABLE_VOLTAGE", {"ADJUSTABLE_VOLTAGE_VALUE": 12.0}
    )


def test_sendAdjustableOutput_indigo(function):
    """isINDIGO=True → queues X_AUX_VARIABLE_POWER_OUTLET OUTLET_1."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.sendAdjustableOutput(12.0)
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_upb", "X_AUX_VARIABLE_POWER_OUTLET", {"OUTLET_1": 12.0}
    )


# ---------------------------------------------------------------------------
# reboot  (sendQ-based)
# ---------------------------------------------------------------------------

def test_reboot_device_none(function):
    """device=None → early return, nothing in sendQ."""
    function.sendQ = Queue()
    function.device = None
    function.reboot()
    assert function.sendQ.qsize() == 0


def test_reboot_indi(function):
    """isINDIGO=False → queues REBOOT_DEVICE REBOOT=On."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = False
    function.device = mock.MagicMock()
    function.reboot()
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "REBOOT_DEVICE", {"REBOOT": "On"})


def test_reboot_indigo(function):
    """isINDIGO=True → queues X_AUX_REBOOT REBOOT=On."""
    function.sendQ = Queue()
    function.deviceName = "test_upb"
    function.isINDIGO = True
    function.device = mock.MagicMock()
    function.reboot()
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == ("test_upb", "X_AUX_REBOOT", {"REBOOT": "On"})
