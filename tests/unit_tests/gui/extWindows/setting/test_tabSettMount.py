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
import mw4.gui.extWindows.setting.tabSettMount
import pytest
import unittest.mock as mock
import wakeonlan
from mw4.gui.extWindows.setting.tabSettMount import SettMount
from mw4.gui.widgets.setting_ui import Ui_SettingDialog
from PySide6.QtWidgets import QWidget
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from typing import Any


@pytest.fixture()
def settMount(qapp: Any) -> SettMount:
    """Create a SettMount instance with mocked parent window."""
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_SettingDialog()
    mainW.ui.setupUi(mainW)
    mainW.wIcon = mock.MagicMock()

    window = SettMount(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initialization(settMount: SettMount) -> None:
    """Test SettMount is properly initialized."""
    assert settMount.parentW is not None
    assert settMount.app is not None
    assert settMount.msg is not None
    assert settMount.ui is not None


def test_initConfigLoadsDefaults(settMount: SettMount) -> None:
    """Test initConfig loads configuration with defaults."""
    settMount.app.config["SettingMount"] = {}
    with mock.patch.object(settMount.app.dReg["mount"].instance, "getFW"):
        settMount.initConfig()
    assert settMount.ui.rackCompMAC.text() == "00:00:00:00:00"
    assert settMount.ui.rackCompWolAddress.text() == "255.255.255.255"
    assert settMount.ui.rackCompWolPort.text() == "9"


def test_initConfigLoadsFromConfig(settMount: SettMount) -> None:
    """Test initConfig loads configuration from app.config."""
    settMount.app.config["SettingMount"] = {
        "rackCompMAC": "AA:BB:CC:DD:EE:FF",
        "rackCompWolAddress": "192.168.1.255",
        "rackCompWolPort": "7",
    }
    with mock.patch.object(settMount.app.dReg["mount"].instance, "getFW"):
        settMount.initConfig()
    assert settMount.ui.rackCompMAC.text() == "AA:BB:CC:DD:EE:FF"
    assert settMount.ui.rackCompWolAddress.text() == "192.168.1.255"
    assert settMount.ui.rackCompWolPort.text() == "7"


def test_storeConfig(settMount: SettMount) -> None:
    """Test storeConfig saves configuration to app.config."""
    settMount.ui.rackCompMAC.setText("AA:BB:CC:DD:EE:FF")
    settMount.ui.rackCompWolAddress.setText("192.168.1.255")
    settMount.ui.rackCompWolPort.setText("7")
    settMount.ui.hostAddress.setText("192.168.1.100")
    settMount.ui.MAC.setText("11:22:33:44:55:66")
    settMount.ui.wolAddress.setText("192.168.1.1")
    settMount.ui.wolPort.setText("9000")
    settMount.ui.wolAutomatic.setChecked(True)
    settMount.ui.port3492.setChecked(True)

    settMount.storeConfig()

    config = settMount.app.config["SettingMount"]
    assert config["rackCompMAC"] == "AA:BB:CC:DD:EE:FF"
    assert config["rackCompWolAddress"] == "192.168.1.255"
    assert config["rackCompWolPort"] == "7"
    assert settMount.app.dReg["mount"].instance.config.hostAddress == "192.168.1.100"
    assert settMount.app.dReg["mount"].instance.config.MAC == "11:22:33:44:55:66"
    assert settMount.app.dReg["mount"].instance.config.wolAddress == "192.168.1.1"
    assert settMount.app.dReg["mount"].instance.config.wolPort == 9000
    assert settMount.app.dReg["mount"].instance.config.wolAutomatic is True
    assert settMount.app.dReg["mount"].instance.config.port == 3492


def test_storeConfigPort3490(settMount: SettMount) -> None:
    """Test storeConfig with port 3490 selected."""
    settMount.ui.port3490.setChecked(True)
    settMount.ui.port3492.setChecked(False)
    settMount.storeConfig()
    assert settMount.app.dReg["mount"].instance.config.port == 3490


def test_setMountCapabilitiesWithHW2012(settMount: SettMount) -> None:
    """Test setMountCapabilities enables WOL group for HW2012."""
    original_firmware = settMount.app.dReg["mount"].instance.firmware
    try:
        mock_fw = mock.MagicMock()
        mock_fw.isHW2012 = mock.MagicMock(return_value=True)
        settMount.app.dReg["mount"].instance.firmware = mock_fw
        settMount.setMountCapabilities(mock_fw)
        assert settMount.ui.GroupWOL.isEnabled()
    finally:
        settMount.app.dReg["mount"].instance.firmware = original_firmware


def test_setMountCapabilitiesWithoutHW2012(settMount: SettMount) -> None:
    """Test setMountCapabilities disables WOL group for non-HW2012."""
    original_firmware = settMount.app.dReg["mount"].instance.firmware
    try:
        mock_fw = mock.MagicMock()
        mock_fw.isHW2012 = mock.MagicMock(return_value=False)
        settMount.app.dReg["mount"].instance.firmware = mock_fw
        settMount.setMountCapabilities(mock_fw)
        assert not settMount.ui.GroupWOL.isEnabled()
    finally:
        settMount.app.dReg["mount"].instance.firmware = original_firmware


def test_mountBootSuccess(settMount: SettMount) -> None:
    """Test mountBoot with successful boot command."""
    settMount.msg = mock.MagicMock()
    with mock.patch.object(
        settMount.app.dReg["mount"].instance, "bootMount", return_value=True
    ):
        settMount.mountBoot()
    settMount.msg.emit.assert_called_with(0, "Mount", "Command", "Sent boot command to mount")


def test_mountBootFailure(settMount: SettMount) -> None:
    """Test mountBoot with failed boot command."""
    settMount.msg = mock.MagicMock()
    with mock.patch.object(
        settMount.app.dReg["mount"].instance, "bootMount", return_value=False
    ):
        settMount.mountBoot()
    settMount.msg.emit.assert_called_with(2, "Mount", "Command", "Mount cannot be booted")


def test_mountShutdownSuccess(settMount: SettMount) -> None:
    """Test mountShutdown with successful shutdown command."""
    settMount.msg = mock.MagicMock()
    with mock.patch.object(
        settMount.app.dReg["mount"].instance, "shutdown", return_value=True
    ):
        settMount.mountShutdown()
    settMount.msg.emit.assert_called_with(0, "Mount", "Command", "Shutting mount down")


def test_mountShutdownFailure(settMount: SettMount) -> None:
    """Test mountShutdown with failed shutdown command."""
    settMount.msg = mock.MagicMock()
    with mock.patch.object(
        settMount.app.dReg["mount"].instance, "shutdown", return_value=False
    ):
        settMount.mountShutdown()
    settMount.msg.emit.assert_called_with(2, "Mount", "Command", "Mount cannot be shutdown")


def test_bootRackCompWithValidMAC(settMount: SettMount) -> None:
    """Test bootRackComp with valid MAC address."""
    settMount.msg = mock.MagicMock()
    settMount.ui.rackCompMAC.setText("AA:BB:CC:DD:EE:FF")
    with (
        mock.patch.object(
            mw4.gui.extWindows.setting.tabSettMount,
            "checkFormatMAC",
            return_value="AA:BB:CC:DD:EE:FF",
        ),
        mock.patch.object(wakeonlan, "send_magic_packet") as mock_send,
    ):
        settMount.bootRackComp()
    mock_send.assert_called_once()
    settMount.msg.emit.assert_called_with(
        0, "Rack", "Command", "Sent boot command to rack computer"
    )


def test_bootRackCompWithInvalidMAC(settMount: SettMount) -> None:
    """Test bootRackComp with invalid MAC address."""
    settMount.msg = mock.MagicMock()
    settMount.ui.rackCompMAC.setText("invalid")
    with mock.patch.object(
        mw4.gui.extWindows.setting.tabSettMount, "checkFormatMAC", return_value=False
    ):
        settMount.bootRackComp()
    settMount.msg.emit.assert_called_with(
        2, "Rack", "Command", "Rack computer cannot be booted"
    )


def test_setMountMACWithNone(settMount: SettMount) -> None:
    """Test setMountMAC with None setting."""
    settMount.setMountMAC(None)
    # Should return early without error


def test_setMountMACWithoutAddressLanMAC(settMount: SettMount) -> None:
    """Test setMountMAC with setting that has no addressLanMAC."""
    mock_setting = mock.MagicMock()
    mock_setting.addressLanMAC = None
    settMount.setMountMAC(mock_setting)
    # Should return early without error


def test_setMountMACWithValidMAC(settMount: SettMount) -> None:
    """Test setMountMAC with valid MAC address."""
    mock_setting = mock.MagicMock()
    mock_setting.addressLanMAC = "AA:BB:CC:DD:EE:FF"
    settMount.setMountMAC(mock_setting)
    assert settMount.ui.MAC.text() == "AA:BB:CC:DD:EE:FF"


def test_showMountStatusTrue(settMount: SettMount) -> None:
    """Test showMountStatus with True status."""
    settMount.showMountStatus(True)
    assert settMount.ui.use10micronDef.isEnabled()


def test_showMountStatusFalse(settMount: SettMount) -> None:
    """Test showMountStatus with False status."""
    settMount.showMountStatus(False)
    assert not settMount.ui.use10micronDef.isEnabled()


def test_updateFwGui(settMount: SettMount) -> None:
    """Test updateFwGui updates firmware GUI elements."""
    mock_fw = mock.MagicMock()
    mock_fw.product = "Mount Product"
    mock_fw.vString = mock.MagicMock()
    mock_fw.vString.public = "1.0.0"
    mock_fw.date = "2026-06-22"
    mock_fw.time = "12:00:00"
    mock_fw.hardware = "HW2024"

    settMount.updateFwGui(mock_fw)
    assert settMount.ui.product.text() == "Mount Product"
    assert settMount.ui.vString.text() == "1.0.0"
    assert settMount.ui.fwdate.text() == "2026-06-22"
    assert settMount.ui.fwtime.text() == "12:00:00"
    assert settMount.ui.hardware.text() == "HW2024"


def test_setupIcons(settMount: SettMount) -> None:
    """Test setupIcons calls wIcon for all buttons."""
    settMount.setupIcons()
    settMount.parentW.wIcon.assert_called()


def test_closeEvent(settMount: SettMount) -> None:
    """Test closeEvent disconnects signals successfully."""
    # This should execute without raising any errors
    settMount.closeEvent()
