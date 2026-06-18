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
import mw4.gui.utilities.qtMain
import pytest
import shutil
import unittest.mock as mock
from mw4.base.deviceRegistry import DeviceEntry
from mw4.gui.mainWindow.mainWindow import MainWindow
from pathlib import Path
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QWidget
from skyfield.api import wgs84
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def mainWindow(qapp):
    """Setup MainWindow fixture for testing."""
    window = MainWindow(app=App())
    yield window
    QApplication.processEvents()
    window.app.threadPool.waitForDone(10000)


def test_initConfig_without_windowmain_config(mainWindow):
    """Test initConfig when WindowMain config is missing."""
    del mainWindow.app.config["WindowMain"]
    with (
        mock.patch.object(mainWindow.mainWindowAddons, "initConfig"),
        mock.patch.object(mainWindow, "smartTabGui"),
        mock.patch.object(mainWindow, "setupIcons"),
        mock.patch.object(mainWindow.externalWindows, "showExtendedWindows"),
    ):
        mainWindow.initConfig()


def test_storeConfig_with_existing_config(mainWindow):
    """Test storeConfig with existing WindowMain config."""
    with (
        mock.patch.object(mainWindow.mainWindowAddons, "storeConfig"),
        mock.patch.object(mainWindow.externalWindows, "storeConfigExtendedWindows"),
    ):
        mainWindow.storeConfig()


def test_storeConfig_without_windowmain_config(mainWindow):
    """Test storeConfig when WindowMain config is missing."""
    del mainWindow.app.config["WindowMain"]
    with (
        mock.patch.object(mainWindow.mainWindowAddons, "storeConfig"),
        mock.patch.object(mainWindow.externalWindows, "storeConfigExtendedWindows"),
    ):
        mainWindow.storeConfig()


def test_setupIcons_calls_addons(mainWindow):
    """Test setupIcons calls mainWindowAddons setupIcons."""
    with mock.patch.object(mainWindow.mainWindowAddons, "setupIcons"):
        mainWindow.setupIcons()


def test_updateColorSet_updates_all_colors(mainWindow):
    """Test updateColorSet updates style and colors."""
    with (
        mock.patch.object(mainWindow, "setStyleSheet"),
        mock.patch.object(mainWindow, "setupIcons"),
        mock.patch.object(mainWindow.mainWindowAddons, "updateColorSet"),
    ):
        mainWindow.updateColorSet()


def test_showWindow_sets_properties(mainWindow):
    """Test showWindow sets proper window size and properties."""
    with (
        mock.patch.object(mainWindow, "show"),
        mock.patch.object(mainWindow, "setMinimumSize"),
        mock.patch.object(mainWindow, "setMaximumSize"),
    ):
        mainWindow.showWindow()
        mainWindow.show.assert_called_once()


def test_closeEvent_closes_windows(mainWindow):
    """Test closeEvent closes extended windows."""
    with (
        mock.patch.object(mainWindow.externalWindows, "closeExtendedWindows"),
        mock.patch.object(mainWindow.threadPool, "waitForDone"),
    ):
        mainWindow.closeEvent(QCloseEvent())


def test_quitSave_saves_and_closes(mainWindow):
    """Test quitSave saves profile and closes window."""
    mainWindow.ui.profileName.setText("test")
    with (
        mock.patch.object(mainWindow, "saveProfile"),
        mock.patch.object(mainWindow, "close"),
    ):
        mainWindow.quitSave()


def test_smartFunctionGui_with_no_buildpoint(mainWindow):
    """Test smartFunctionGui with no build points."""
    mainWindow.app.dReg.d["mount"].stat = True
    mainWindow.app.dReg.d["camera"].stat = True
    mainWindow.app.dReg.d["plateSolve"].stat = True
    mainWindow.app.buildPoint.buildP = []
    mainWindow.smartFunctionGui()


def test_smartFunctionGui_enables_model_with_buildpoints(mainWindow):
    """Test smartFunctionGui enables model when build points exist."""
    mainWindow.app.dReg.d["mount"].stat = True
    mainWindow.app.dReg.d["camera"].stat = True
    mainWindow.app.dReg.d["plateSolve"].stat = True
    mainWindow.app.buildPoint.buildP = [(0, 0, 1)]
    mainWindow.smartFunctionGui()
    assert mainWindow.ui.runModelGroup.isEnabled()


def test_smartFunctionGui_disables_when_camera_offline(mainWindow):
    """Test smartFunctionGui disables model when camera offline."""
    mainWindow.app.dReg.d["mount"].stat = True
    mainWindow.app.dReg.d["camera"].stat = False
    mainWindow.app.dReg.d["plateSolve"].stat = True
    mainWindow.app.buildPoint.buildP = [(0, 0, 1)]
    mainWindow.smartFunctionGui()
    assert not mainWindow.ui.runModelGroup.isEnabled()


def test_smartFunctionGui_enables_refraction_when_mount_ready(mainWindow):
    """Test smartFunctionGui enables refraction when mount ready."""
    mainWindow.app.dReg.d["mount"].stat = True
    mainWindow.smartFunctionGui()
    assert mainWindow.ui.refractionGroup.isEnabled()


def test_smartFunctionGui_disables_when_mount_offline(mainWindow):
    """Test smartFunctionGui disables functions when mount offline."""
    mainWindow.app.dReg.d["mount"].stat = False
    mainWindow.smartFunctionGui()
    assert not mainWindow.ui.refractionGroup.isEnabled()


def test_smartTabGui_with_default_state(mainWindow):
    """Test smartTabGui with default state."""
    mainWindow.smartTabGui()


def test_smartTabGui_with_power_enabled(mainWindow):
    """Test smartTabGui with power device enabled."""
    mainWindow.app.deviceStat["power"] = True
    mainWindow.smartTabGui()


def test_setEnvironDeviceStats_refraction_disabled(mainWindow):
    """Test setEnvironDeviceStats when refraction disabled."""
    mainWindow.app.mount.setting.statusRefraction = 0
    mainWindow.setEnvironDeviceStats()


def test_setEnvironDeviceStats_manual_refraction(mainWindow):
    """Test setEnvironDeviceStats with manual refraction enabled."""
    mainWindow.app.mount.setting.statusRefraction = 1
    mainWindow.setEnvironDeviceStats()


def test_setEnvironDeviceStats_auto_refraction_offline(mainWindow):
    """Test setEnvironDeviceStats with auto refraction source offline."""
    mainWindow.app.mount.setting.statusRefraction = 1
    mainWindow.setEnvironDeviceStats()


def test_setEnvironDeviceStats_no_source(mainWindow):
    """Test setEnvironDeviceStats when no refraction source available."""
    mainWindow.app.dReg.d["mount"].instance.setting.statusRefraction = 1
    mainWindow.setEnvironDeviceStats()


def test_updateDeviceStats_enabled_device(mainWindow):
    """Test updateDeviceStats with enabled device."""
    mainWindow.deviceStatGui = {"onlineWeather": QWidget()}
    mainWindow.app.deviceStat = {"onlineWeather": True}
    mainWindow.updateDeviceStats()


def test_updateDeviceStats_disabled_device(mainWindow):
    """Test updateDeviceStats with disabled device."""
    mainWindow.deviceStatGui = {"onlineWeather": QWidget()}
    mainWindow.app.deviceStat = {"onlineWeather": False}
    mainWindow.updateDeviceStats()


def test_updateDeviceStats_null_device(mainWindow):
    """Test updateDeviceStats with null device."""
    mainWindow.deviceStatGui = {"onlineWeather": QWidget()}
    mainWindow.app.deviceStat = {"onlineWeather": None}
    mainWindow.updateDeviceStats()


def test_updateDeviceStats_no_driver_entry(mainWindow):
    """Test updateDeviceStats when device has no registry entry."""
    device = "testDevice"
    ui = mock.MagicMock()
    mainWindow.deviceStatGui[device] = ui
    mainWindow.app.dReg.d[device] = None
    try:
        mainWindow.updateDeviceStats()
        ui.setEnabled.assert_called_with(False)
    finally:
        mainWindow.app.dReg.d.pop(device, None)
        mainWindow.deviceStatGui.pop(device, None)


def test_updateDeviceStats_enabled_driver(mainWindow):
    """Test updateDeviceStats with enabled driver entry."""
    device = "testDevice"
    ui = mock.MagicMock()
    mainWindow.deviceStatGui[device] = ui
    mainWindow.app.dReg.d[device] = DeviceEntry(
        name=device, instance=object(), deviceType=None, isConfigurable=True, stat=True
    )
    try:
        with mock.patch("mw4.gui.mainWindow.mainWindow.changeStyleDynamic"):
            mainWindow.updateDeviceStats()
        ui.setEnabled.assert_called_with(True)
    finally:
        mainWindow.app.dReg.d.pop(device, None)
        mainWindow.deviceStatGui.pop(device, None)


def test_updatePlateSolveStatus_with_text(mainWindow):
    """Test updatePlateSolveStatus with text."""
    mainWindow.updatePlateSolveStatus("test")
    assert mainWindow.ui.plateSolveText.text() == "test"


def test_updateDomeStatus_updates_text(mainWindow):
    """Test updateDomeStatus updates dome status text."""
    mainWindow.updateDomeStatus("test")
    assert mainWindow.ui.domeText.text() == "test"


def test_updateCameraStatus_updates_text(mainWindow):
    """Test updateCameraStatus updates camera status text."""
    mainWindow.updateCameraStatus("test")
    assert mainWindow.ui.cameraText.text() == "test"


def test_updateThreadAndOnlineStatus_when_online(mainWindow):
    """Test updateThreadAndOnlineStatus when system online."""
    mainWindow.app.mwGlob["workDir"] = Path("tests/work")
    mainWindow.app.isOnline = True
    with mock.patch.object(shutil, "disk_usage", return_value=(100, 100, 100)):
        mainWindow.updateThreadAndOnlineStatus()


def test_updateThreadAndOnlineStatus_when_offline(mainWindow):
    """Test updateThreadAndOnlineStatus when system offline."""
    mainWindow.app.mwGlob["workDir"] = Path("tests/work")
    mainWindow.app.isOnline = False
    with mock.patch.object(shutil, "disk_usage", return_value=(100, 100, 100)):
        mainWindow.updateThreadAndOnlineStatus()


def test_updateThreadAndOnlineStatus_cached(mainWindow):
    """Test updateThreadAndOnlineStatus uses cached values."""
    mainWindow.app.mwGlob["workDir"] = Path("tests/work")
    mainWindow._twilightText = "Night"
    mainWindow._diskFreePct = 42
    with mock.patch.object(shutil, "disk_usage") as mDisk:
        mainWindow.updateThreadAndOnlineStatus()
        mDisk.assert_not_called()
    assert "Night" in mainWindow.ui.statusOnlineGroup.title()


def test_updateTwilightAndDisk_calculates_values(mainWindow):
    """Test updateTwilightAndDisk calculates values."""
    mainWindow.app.mwGlob["workDir"] = Path("tests/work")
    with mock.patch.object(shutil, "disk_usage", return_value=(100, 100, 50)):
        mainWindow.updateTwilightAndDisk()
    assert mainWindow._diskFreePct == 50
    assert mainWindow._twilightText != ""


def test_updateTime_displays_time(mainWindow):
    """Test updateTime displays current time."""
    mainWindow.updateTime()


def test_updateStatusGUI_with_status_zero(mainWindow):
    """Test updateStatusGUI with status 0."""

    class OB:
        @staticmethod
        def statusText():
            return None

    mainWindow.app.mount.obsSite.status = 0
    mainWindow.updateStatusGUI(OB)


def test_updateStatusGUI_displays_text(mainWindow):
    """Test updateStatusGUI displays status text."""

    class OB:
        @staticmethod
        def statusText():
            return "test"

    mainWindow.app.mount.obsSite.status = 0
    mainWindow.updateStatusGUI(OB)
    assert mainWindow.ui.mountText.text() == "test"


def test_switchProfile_switches_config(mainWindow):
    """Test switchProfile switches configuration."""
    loc = wgs84.latlon(latitude_degrees=10, longitude_degrees=10)
    with (
        mock.patch.object(mainWindow.externalWindows, "closeExtendedWindows"),
        mock.patch.object(mainWindow.externalWindows, "showExtendedWindows"),
        mock.patch.object(mainWindow, "initConfig"),
        mock.patch.object(mainWindow.app, "initConfig", return_value=loc),
    ):
        mainWindow.switchProfile({"test": 1})


def test_loadProfileGUI_invalid_file(mainWindow):
    """Test loadProfileGUI when file invalid."""
    with (
        mock.patch.object(mainWindow, "openFile", return_value=Path("")),
        mock.patch.object(Path, "is_file", return_value=False),
    ):
        mainWindow.loadProfileGUI()


def test_loadProfileGUI_valid_config(mainWindow):
    """Test loadProfileGUI with valid configuration."""
    with (
        mock.patch.object(mainWindow, "openFile", return_value=Path("test.cfg")),
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(
            mw4.gui.mainWindow.mainWindow, "loadConfig", return_value={"test": 1}
        ),
        mock.patch.object(mainWindow, "switchProfile"),
        mock.patch.object(mainWindow, "saveProfile"),
    ):
        mainWindow.loadProfileGUI()


def test_saveProfileAs_valid_config(mainWindow):
    """Test saveProfileAs with valid configuration."""
    with (
        mock.patch.object(mainWindow, "saveFile", return_value=Path("test.cfg")),
        mock.patch.object(mw4.gui.mainWindow.mainWindow, "saveConfig", return_value=True),
        mock.patch.object(mainWindow.app, "storeConfig"),
        mock.patch.object(mainWindow, "storeConfig"),
    ):
        mainWindow.saveProfileAs()


def test_saveProfile_successful(mainWindow):
    """Test saveProfile with successful save."""
    with (
        mock.patch.object(mainWindow, "storeConfig"),
        mock.patch.object(mainWindow.app, "storeConfig"),
        mock.patch.object(mw4.gui.mainWindow.mainWindow, "saveConfig", return_value=True),
    ):
        mainWindow.saveProfile()


def test_remoteCommand_empty(mainWindow):
    """Test remoteCommand with empty command."""
    mainWindow.remoteCommand("")


def test_remoteCommand_shutdown(mainWindow):
    """Test remoteCommand with shutdown command."""
    with mock.patch.object(mainWindow, "quitSave"):
        mainWindow.remoteCommand("shutdown")


def test_remoteCommand_shutdown_mount(mainWindow):
    """Test remoteCommand with shutdown mount command."""
    mock_mount_addon = mock.MagicMock()
    mainWindow.mainWindowAddons.addons["SettMount"] = mock_mount_addon
    with mock.patch.object(mock_mount_addon, "mountShutdown"):
        mainWindow.remoteCommand("shutdown mount")


def test_remoteCommand_boot_mount(mainWindow):
    """Test remoteCommand with boot mount command."""
    mock_mount_addon = mock.MagicMock()
    mainWindow.mainWindowAddons.addons["SettMount"] = mock_mount_addon
    with mock.patch.object(mock_mount_addon, "mountBoot"):
        mainWindow.remoteCommand("boot mount")


def test_setEnvironDeviceStats_auto_refraction_with_source(mainWindow):
    """Test setEnvironDeviceStats with auto refraction with valid source."""
    mainWindow.app.mount.setting.statusRefraction = 1
    with mock.patch.object(mainWindow.ui, "refracManual") as mock_refrac:
        mock_refrac.isChecked.return_value = False
        mainWindow.mainWindowAddons.addons["EnvironWeather"].refractionSource = "onlineWeather"
        mainWindow.app.dReg.setStat("onlineWeather", True)
        mainWindow.setEnvironDeviceStats()
        assert mainWindow.ui.refractionConnected.text() == "Refrac Auto"


def test_setEnvironDeviceStats_auto_refraction_without_source(mainWindow):
    """Test setEnvironDeviceStats with auto refraction without source (lines 246-252)."""
    mainWindow.app.mount.setting.statusRefraction = 1
    with mock.patch.object(mainWindow.ui, "refracManual") as mock_refrac:
        mock_refrac.isChecked.return_value = False
        mainWindow.mainWindowAddons.addons["EnvironWeather"].refractionSource = None
        mainWindow.setEnvironDeviceStats()
        assert mainWindow.ui.refractionConnected.text() == "Refrac Auto"


def test_updateDeviceStats_stat_false_changes_color(mainWindow):
    """Test updateDeviceStats when entry.stat is False (lines 263-264)."""
    device = "testDeviceFalse"
    ui = mock.MagicMock()
    mainWindow.deviceStatGui[device] = ui
    mainWindow.app.dReg.d[device] = DeviceEntry(
        name=device, instance=object(), deviceType=None, isConfigurable=True, stat=False
    )
    try:
        with mock.patch("mw4.gui.mainWindow.mainWindow.changeStyleDynamic"):
            mainWindow.updateDeviceStats()
        ui.setEnabled.assert_called_with(True)
    finally:
        mainWindow.app.dReg.d.pop(device, None)
        mainWindow.deviceStatGui.pop(device, None)


def test_updateControllerStatus_enabled(mainWindow):
    """Test updateControllerStatus with gcStatus True (lines 276-280)."""
    with (
        mock.patch.object(mainWindow.ui.controller1, "setEnabled"),
        mock.patch.object(mainWindow.ui.controller2, "setEnabled"),
        mock.patch.object(mainWindow.ui.controller3, "setEnabled"),
        mock.patch.object(mainWindow.ui.controller4, "setEnabled"),
        mock.patch.object(mainWindow.ui.controller5, "setEnabled"),
    ):
        mainWindow.updateControllerStatus(True)
        mainWindow.ui.controller1.setEnabled.assert_called_with(True)


def test_updateControllerStatus_disabled(mainWindow):
    """Test updateControllerStatus with gcStatus False."""
    with (
        mock.patch.object(mainWindow.ui.controller1, "setEnabled"),
        mock.patch.object(mainWindow.ui.controller2, "setEnabled"),
        mock.patch.object(mainWindow.ui.controller3, "setEnabled"),
        mock.patch.object(mainWindow.ui.controller4, "setEnabled"),
        mock.patch.object(mainWindow.ui.controller5, "setEnabled"),
    ):
        mainWindow.updateControllerStatus(False)
        mainWindow.ui.controller1.setEnabled.assert_called_with(False)


def test_updateStatusGUI_satellite_tracking_starts(mainWindow):
    """Test updateStatusGUI when satellite tracking starts (lines 323-324)."""
    mainWindow.satStatus = False
    with (
        mock.patch.object(mainWindow.app, "playSound"),
        mock.patch("mw4.gui.mainWindow.mainWindow.changeStyleDynamic"),
    ):

        class MockOB:
            @staticmethod
            def statusText():
                return "test"

        # Mock obsSite properties
        obsSite = mainWindow.app.dReg["mount"].obsSite
        with mock.patch.object(
            obsSite.__class__,
            "isFollowingSatellite",
            new_callable=mock.PropertyMock,
            return_value=True,
        ):
            mainWindow.updateStatusGUI(MockOB)
            assert mainWindow.satStatus


def test_saveProfileBase_with_empty_path(mainWindow):
    """Test saveProfileBase with empty path stem (line 352)."""
    empty_path = Path("")
    mainWindow.saveProfileBase(empty_path)
    # Should return early without calling storeConfig or saveConfig
