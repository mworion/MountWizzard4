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
from mw4.gui.extWindows.setting.tabSettPark import SettPark
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QDoubleSpinBox, QLineEdit
from skyfield.api import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


def createMockLineEdit() -> QLineEdit:
    """Create a mock line edit for park position names."""
    m = QLineEdit()
    m.editingFinished = mock.MagicMock()
    return m


def createMockSpinBox() -> QDoubleSpinBox:
    """Create a mock spin box for altitude/azimuth."""
    m = QDoubleSpinBox()
    m.setMinimum(-180)
    m.setMaximum(360)
    m.setValue(0)
    return m


def createMockButton():
    """Create a mock button."""
    return mock.MagicMock()


@pytest.fixture(autouse=True, scope="module")
def settPark(qapp):
    """Setup SettPark fixture for testing."""
    parentW = MWidget()
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    # Create mock UI elements for park positions
    for i in range(0, 10):
        setattr(parentW.ui, f"parkButton{i}", createMockButton())
        setattr(parentW.ui, f"parkSave{i}", createMockButton())
        setattr(parentW.ui, f"parkText{i}", createMockLineEdit())
        setattr(parentW.ui, f"parkAlt{i}", createMockSpinBox())
        setattr(parentW.ui, f"parkAz{i}", createMockSpinBox())

    # Create other UI elements
    parentW.ui.parkMountAfterSlew = mock.MagicMock()
    parentW.ui.parkMountAfterSlew._checked = False
    parentW.ui.parkMountAfterSlew.isChecked = mock.MagicMock(
        side_effect=lambda: parentW.ui.parkMountAfterSlew._checked
    )
    parentW.ui.parkMountAfterSlew.setChecked = mock.MagicMock(
        side_effect=lambda v: setattr(parentW.ui.parkMountAfterSlew, "_checked", v)
    )

    window = SettPark(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)



def test_initConfig_with_default_config(settPark):
    """Test initConfig loads defaults when config empty."""
    settPark.app.config["SettingPark"] = {}
    settPark.initConfig()


def test_initConfig_with_custom_values(settPark):
    """Test initConfig loads custom config values."""
    config = settPark.app.config.get("SettingPark", {})
    if not config:
        settPark.app.config["SettingPark"] = {}
        config = settPark.app.config["SettingPark"]

    for i in range(0, 10):
        config[f"ParkText{i:1d}"] = str(i)
        config[f"ParkAlt{i:1d}"] = i
        config[f"ParkAz{i:1d}"] = i

    settPark.initConfig()

    assert settPark.ui.parkText0.text() == "0"
    assert settPark.ui.parkAlt0.value() == 0
    assert settPark.ui.parkAz0.value() == 0
    assert settPark.ui.parkText4.text() == "4"
    assert settPark.ui.parkAlt4.value() == 4
    assert settPark.ui.parkAz4.value() == 4


def test_storeConfig_saves_all_values(settPark):
    """Test storeConfig properly saves state."""
    settPark.storeConfig()

    config = settPark.app.config["SettingPark"]
    assert "ParkText0" in config
    assert "ParkAlt0" in config
    assert "ParkAz0" in config


def test_setupIcons_creates_icons(settPark):
    """Test setupIcons method."""
    settPark.setupIcons()


def test_setup_creates_park_position_widgets(settPark):
    """Test setup creates 10 park position widgets."""
    # Check all the required attributes exist
    assert len(settPark.parkTexts) == 10
    assert len(settPark.parkAlt) == 10
    assert len(settPark.parkAz) == 10
    assert len(settPark.parkSaveButtons) == 10
    for i in range(0, 10):
        assert settPark.parkTexts[i] is not None
        assert settPark.parkAlt[i] is not None
        assert settPark.parkAz[i] is not None
        assert settPark.parkSaveButtons[i] is not None


def test_saveActualPosition_saves_current_position(settPark):
    """Test saveActualPosition saves current mount position."""
    settPark.app.dReg["mount"].obsSite.Alt = Angle(degrees=10)
    settPark.app.dReg["mount"].obsSite.Az = Angle(degrees=10)
    settPark.saveActualPosition(0)

    assert settPark.ui.parkAlt0.value() == 10
    assert settPark.ui.parkAz0.value() == 10


def test_storeConfig_saves_button_texts(settPark):
    """Test storeConfig saves button texts."""
    settPark.parkTexts[0].setText("Custom Text")
    settPark.parkTexts[5].setText("Another Text")
    settPark.storeConfig()
    config = settPark.app.config["SettingPark"]
    assert config["ParkText0"] == "Custom Text"
    assert config["ParkText5"] == "Another Text"


def test_storeConfig_saves_positions(settPark):
    """Test storeConfig saves park positions."""
    settPark.parkAlt[0].setValue(45.5)
    settPark.parkAz[0].setValue(180.0)
    settPark.storeConfig()
    config = settPark.app.config["SettingPark"]
    assert config["ParkAlt0"] == 45.5
    assert config["ParkAz0"] == 180.0


def test_storeConfig_saves_all_parks(settPark):
    """Test storeConfig saves all park positions."""
    for i in range(10):
        settPark.parkTexts[i].setText(f"Park {i}")
        settPark.parkAlt[i].setValue(i * 10)
        settPark.parkAz[i].setValue(i * 20)
    settPark.storeConfig()
    config = settPark.app.config["SettingPark"]
    for i in range(10):
        assert config[f"ParkText{i:1d}"] == f"Park {i}"
        assert config[f"ParkAlt{i:1d}"] == i * 10
        assert config[f"ParkAz{i:1d}"] == i * 20


def test_storeConfig_creates_settingpark_key(settPark):
    """Test storeConfig creates SettingPark key in config."""
    settPark.app.config = {}
    settPark.storeConfig()
    assert "SettingPark" in settPark.app.config


def test_initConfig_sets_default_empty_text(settPark):
    """Test initConfig sets default empty text."""
    settPark.app.config = {"SettingPark": {}}
    settPark.initConfig()
    assert settPark.parkTexts[0].text() == ""


def test_initConfig_sets_default_alt(settPark):
    """Test initConfig sets default altitude to 0."""
    settPark.app.config = {"SettingPark": {}}
    settPark.initConfig()
    for i in range(10):
        assert settPark.parkAlt[i].value() == 0


def test_initConfig_sets_default_az(settPark):
    """Test initConfig sets default azimuth to 0."""
    settPark.app.config = {"SettingPark": {}}
    settPark.initConfig()
    for i in range(10):
        assert settPark.parkAz[i].value() == 0


def test_initConfig_partial_config(settPark):
    """Test initConfig with partial config."""
    settPark.app.config = {
        "SettingPark": {
            "ParkText0": "Home",
            "ParkAlt0": 85,
            "ParkAz0": 0,
        }
    }
    settPark.initConfig()
    assert settPark.parkTexts[0].text() == "Home"
    assert settPark.parkAlt[0].value() == 85
    assert settPark.parkAz[0].value() == 0
    assert settPark.parkTexts[1].text() == ""
    assert settPark.parkAlt[1].value() == 0


def test_saveActualPosition_updates_all_values(settPark):
    """Test saveActualPosition updates altitude, azimuth and stores."""
    test_alt = 42.5
    test_az = 123.75
    settPark.app.dReg["mount"].obsSite.Alt = Angle(degrees=test_alt)
    settPark.app.dReg["mount"].obsSite.Az = Angle(degrees=test_az)

    settPark.saveActualPosition(3)

    assert settPark.parkAlt[3].value() == test_alt
    assert settPark.parkAz[3].value() == test_az
    config = settPark.app.config["SettingPark"]
    assert config["ParkAlt3"] == test_alt
    assert config["ParkAz3"] == test_az


def test_saveActualPosition_multiple_positions(settPark):
    """Test saveActualPosition can update different positions."""
    for i in range(3):
        settPark.app.dReg["mount"].obsSite.Alt = Angle(degrees=i * 10)
        settPark.app.dReg["mount"].obsSite.Az = Angle(degrees=i * 30)
        settPark.saveActualPosition(i)

    for i in range(3):
        assert settPark.parkAlt[i].value() == i * 10
        assert settPark.parkAz[i].value() == i * 30


def test_park_settings_roundtrip(settPark):
    """Test save and load park settings roundtrip."""
    original_config = {
        "SettingPark": {
            "ParkText0": "Home",
            "ParkText1": "Zenith",
            "ParkText2": "West",
            "ParkAlt0": 85,
            "ParkAlt1": 90,
            "ParkAlt2": 45,
            "ParkAz0": 0,
            "ParkAz1": 180,
            "ParkAz2": 270,
        }
    }
    settPark.app.config = original_config
    settPark.initConfig()
    settPark.storeConfig()
    saved_config = settPark.app.config["SettingPark"]
    assert saved_config["ParkText0"] == "Home"
    assert saved_config["ParkText1"] == "Zenith"
    assert saved_config["ParkAlt0"] == 85
    assert saved_config["ParkAz1"] == 180


def test_settpark_has_parentw_attribute(settPark):
    """Test SettPark has parentW attribute."""
    assert hasattr(settPark, "parentW")
    assert settPark.parentW is not None


def test_settpark_has_app_attribute(settPark):
    """Test SettPark has app attribute."""
    assert hasattr(settPark, "app")
    assert settPark.app is not None


def test_settpark_has_msg_attribute(settPark):
    """Test SettPark has msg attribute."""
    assert hasattr(settPark, "msg")
    assert settPark.msg is not None


def test_settpark_has_ui_attribute(settPark):
    """Test SettPark has ui attribute."""
    assert hasattr(settPark, "ui")
    assert settPark.ui is not None


def test_settpark_has_parkTexts_attribute(settPark):
    """Test SettPark has parkTexts attribute."""
    assert hasattr(settPark, "parkTexts")
    assert isinstance(settPark.parkTexts, list)
    assert len(settPark.parkTexts) == 10


def test_settpark_has_parkAlt_attribute(settPark):
    """Test SettPark has parkAlt attribute."""
    assert hasattr(settPark, "parkAlt")
    assert isinstance(settPark.parkAlt, list)
    assert len(settPark.parkAlt) == 10


def test_settpark_has_parkAz_attribute(settPark):
    """Test SettPark has parkAz attribute."""
    assert hasattr(settPark, "parkAz")
    assert isinstance(settPark.parkAz, list)
    assert len(settPark.parkAz) == 10


def test_settpark_has_parkSaveButtons_attribute(settPark):
    """Test SettPark has parkSaveButtons attribute."""
    assert hasattr(settPark, "parkSaveButtons")
    assert isinstance(settPark.parkSaveButtons, list)
    assert len(settPark.parkSaveButtons) == 10


def test_settpark_has_initConfig_method(settPark):
    """Test SettPark has initConfig method."""
    assert hasattr(settPark, "initConfig")
    assert callable(settPark.initConfig)


def test_settpark_has_storeConfig_method(settPark):
    """Test SettPark has storeConfig method."""
    assert hasattr(settPark, "storeConfig")
    assert callable(settPark.storeConfig)


def test_settpark_has_setupIcons_method(settPark):
    """Test SettPark has setupIcons method."""
    assert hasattr(settPark, "setupIcons")
    assert callable(settPark.setupIcons)


def test_settpark_has_saveActualPosition_method(settPark):
    """Test SettPark has saveActualPosition method."""
    assert hasattr(settPark, "saveActualPosition")
    assert callable(settPark.saveActualPosition)

