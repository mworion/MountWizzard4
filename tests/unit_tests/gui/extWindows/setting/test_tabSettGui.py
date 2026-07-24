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
from mw4.gui.extWindows.setting.tabSettGui import SettGui
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QCheckBox, QComboBox, QPushButton
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def settGui(qapp):
    """Setup SettGui fixture for testing."""
    parentW = MWidget()
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    parentW.ui.colorSet = QComboBox()
    parentW.ui.colorSet.addItem("Color1")
    parentW.ui.colorSet.addItem("Color2")
    parentW.ui.colorSet.addItem("Color3")
    parentW.ui.soundSatStartTracking = QComboBox()
    parentW.ui.soundSatStartTracking.addItem("None")
    parentW.ui.soundSatStartTracking.addItem("Beep")
    parentW.ui.controllerOverview = mock.MagicMock()
    parentW.ui.hidDome = QCheckBox()
    parentW.ui.hidAltAz = QCheckBox()
    parentW.ui.hidRaDec = QCheckBox()
    parentW.ui.hidTracking = QCheckBox()
    parentW.ui.hidParkStop = QCheckBox()
    parentW.ui.writeLinuxConfig = QPushButton()
    parentW.ui.writeWindowsConfig = QPushButton()
    parentW.ui.transparency = mock.MagicMock()
    parentW.ui.transparency.value = mock.MagicMock(return_value=1)
    parentW.ui.transparency.setValue = mock.MagicMock()
    parentW.ui.transparency.valueChanged = mock.MagicMock()
    parentW.ui.transparency.valueChanged.connect = mock.MagicMock()
    parentW.ui.scale = mock.MagicMock()
    parentW.ui.scale.value = mock.MagicMock(return_value=1)
    parentW.ui.scale.setValue = mock.MagicMock()
    parentW.ui.dpi = mock.MagicMock()
    parentW.ui.dpi.value = mock.MagicMock(return_value=96)
    parentW.ui.dpi.setValue = mock.MagicMock()
    parentW.setStyleSheet = mock.MagicMock()

    window = SettGui(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_initConfig_with_defaults(settGui):
    """Test initConfig loads default values."""
    settGui.app.config["SettingGui"] = {}
    settGui.initConfig()
    assert settGui.ui.colorSet.currentIndex() == 0
    assert settGui.ui.hidParkStop.isChecked() is True


def test_storeConfig_saves_color(settGui):
    """Test storeConfig saves colorSet."""
    settGui.ui.colorSet.setCurrentIndex(1)
    settGui.storeConfig()
    config = settGui.app.config["SettingGui"]
    assert config["colorSet"] == 1


def test_storeConfig_saves_hidParkStop(settGui):
    """Test storeConfig saves hidParkStop."""
    settGui.ui.hidParkStop.setChecked(False)
    settGui.storeConfig()
    cfg = settGui.app.dReg["hidController"].instance.config
    assert cfg.parkStop is False


def test_initConfig_hidParkStop_unchecked(settGui):
    """Test initConfig with hidParkStop unchecked."""
    settGui.app.dReg["hidController"].instance.config.parkStop = False
    settGui.ui.hidParkStop.setChecked(True)
    settGui.initConfig()
    assert settGui.ui.hidParkStop.isChecked() is False


def test_setupIcons_creates_icons(settGui):
    """Test setupIcons method."""
    settGui.setupIcons()


def test_updateColorSet_updates_app(settGui):
    """Test updateColorSet updates color set."""
    settGui.ui.colorSet.setCurrentIndex(1)
    settGui.updateColorSet()

    from mw4.gui.styles.styles import Styles

    assert Styles.colorSet == 1


def test_writeLinuxDesktopData(settGui, tmp_path):
    """Test writeLinuxDesktopData creates desktop file."""
    with mock.patch("mw4.gui.extWindows.setting.tabSettGui.Path") as mock_path_class:
        mock_home_path = mock.MagicMock()
        mock_desktop_file = mock.MagicMock()
        mock_path_class.home.return_value = mock_home_path
        mock_home_path.__truediv__ = mock.MagicMock(return_value=mock_desktop_file)
        mock_file = mock.mock_open()
        with mock.patch("builtins.open", mock_file):
            settGui.writeLinuxDesktopData()
            mock_file.assert_called_once()


def test_setPermissionLinuxDesktopData(settGui):
    """Test setPermissionLinuxDesktopData sets permissions."""
    with mock.patch("mw4.gui.extWindows.setting.tabSettGui.Path") as mock_path_class:
        mock_home_path = mock.MagicMock()
        mock_desktop_file = mock.MagicMock()
        mock_path_class.home.return_value = mock_home_path
        mock_home_path.__truediv__ = mock.MagicMock(return_value=mock_desktop_file)

        SettGui.setPermissionLinuxDesktopData()
        mock_desktop_file.chmod.assert_called_once_with(0o755)


def test_runLinuxConfig(settGui):
    """Test runLinuxConfig calls both methods."""
    with mock.patch.object(
        settGui, "writeLinuxDesktopData"
    ) as mock_write, mock.patch.object(
        SettGui, "setPermissionLinuxDesktopData"
    ) as mock_perm:
        settGui.runLinuxConfig()
        mock_write.assert_called_once()
        mock_perm.assert_called_once()


def test_initConfig_connects_writeLinuxConfig(settGui):
    """Test initConfig connects writeLinuxConfig button."""
    settGui.app.config["SettingGui"] = {}
    settGui.initConfig()
    assert settGui.ui.writeLinuxConfig is not None


def test_initConfig_writeLinuxConfig_enabled_on_linux(settGui):
    """Test writeLinuxConfig button enabled on Linux."""
    settGui.app.config["SettingGui"] = {}
    with mock.patch("platform.system") as mock_platform:
        mock_platform.return_value = "Linux"
        settGui.initConfig()
        assert settGui.ui.writeLinuxConfig.isEnabled() is True


def test_initConfig_writeLinuxConfig_disabled_on_non_linux(settGui):
    """Test writeLinuxConfig button disabled on non-Linux."""
    settGui.app.config["SettingGui"] = {}
    with mock.patch("platform.system") as mock_platform:
        mock_platform.return_value = "Darwin"
        settGui.initConfig()
        assert settGui.ui.writeLinuxConfig.isEnabled() is False


def test_storeConfig_saves_transparency(settGui):
    """Test storeConfig saves transparency."""
    settGui.ui.transparency.value.return_value = 0.8
    settGui.storeConfig()
    config = settGui.app.config["SettingGui"]
    assert config["transparency"] == 0.8


def test_storeConfig_saves_all_hid_settings(settGui):
    """Test storeConfig saves all HID settings."""
    settGui.ui.colorSet.setCurrentIndex(2)
    settGui.ui.hidDome.setChecked(True)
    settGui.ui.hidAltAz.setChecked(False)
    settGui.ui.hidRaDec.setChecked(True)
    settGui.ui.hidTracking.setChecked(False)
    settGui.storeConfig()

    cfg = settGui.app.dReg["hidController"].instance.config
    assert cfg.dome is True
    assert cfg.moveAltAz is False
    assert cfg.moveRaDec is True
    assert cfg.tracking is False


def test_initConfig_loads_all_settings(settGui):
    """Test initConfig loads all saved settings."""
    settGui.app.config["SettingGui"] = {"colorSet": 2, "transparency": 0.5}
    settGui.app.dReg["hidController"].instance.config.dome = True
    settGui.app.dReg["hidController"].instance.config.moveAltAz = False
    settGui.app.dReg["hidController"].instance.config.moveRaDec = True
    settGui.app.dReg["hidController"].instance.config.tracking = False
    settGui.initConfig()

    assert settGui.ui.colorSet.currentIndex() == 2
    assert settGui.ui.transparency.setValue.called
    assert settGui.ui.hidDome.isChecked() is True
    assert settGui.ui.hidAltAz.isChecked() is False
    assert settGui.ui.hidRaDec.isChecked() is True
    assert settGui.ui.hidTracking.isChecked() is False


def test_initConfig_loads_scale_and_dpi(settGui):
    """Test initConfig loads scale and dpi values."""
    settGui.app.config["SettingGui"] = {"scale": 1.5, "dpi": 120}
    settGui.initConfig()

    assert settGui.ui.scale.setValue.called
    assert settGui.ui.dpi.setValue.called


def test_storeConfig_saves_scale(settGui):
    """Test storeConfig saves scale."""
    settGui.ui.scale.value.return_value = 1.25
    settGui.storeConfig()
    config = settGui.app.config["SettingGui"]
    assert config["scale"] == 1.25


def test_storeConfig_saves_dpi(settGui):
    """Test storeConfig saves dpi."""
    settGui.ui.dpi.value.return_value = 120
    settGui.storeConfig()
    config = settGui.app.config["SettingGui"]
    assert config["dpi"] == 120


def test_initConfig_writeWindowsConfig_enabled_on_windows(settGui):
    """Test writeWindowsConfig button enabled on Windows."""
    settGui.app.config["SettingGui"] = {}
    with mock.patch("platform.system") as mock_platform:
        mock_platform.return_value = "Windows"
        settGui.initConfig()
        assert settGui.ui.writeWindowsConfig.isEnabled() is True


def test_initConfig_writeWindowsConfig_disabled_on_non_windows(settGui):
    """Test writeWindowsConfig button disabled on non-Windows."""
    settGui.app.config["SettingGui"] = {}
    with mock.patch("platform.system") as mock_platform:
        mock_platform.return_value = "Darwin"
        settGui.initConfig()
        assert settGui.ui.writeWindowsConfig.isEnabled() is False


def test_runWindowsConfig(settGui):
    """Test runWindowsConfig calls pylnk3."""
    with mock.patch("mw4.gui.extWindows.setting.tabSettGui.pylnk3") as mock_pylnk3:
        settGui.runWindowsConfig()
        mock_pylnk3.for_file.assert_called_once()
