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
from mw4.gui.extWindows.setting.tabSettRelay import SettRelay
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QComboBox, QLineEdit
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


def createMockComboBox() -> QComboBox:
    """Create a mock combo box for relay functions."""
    m = QComboBox()
    m.currentIndexChanged = mock.MagicMock()
    return m


def createMockLineEdit() -> QLineEdit:
    """Create a mock line edit for relay button text."""
    m = QLineEdit()
    m.textChanged = mock.MagicMock()
    return m


@pytest.fixture(autouse=True, scope="module")
def settRelay(qapp):
    """Setup SettRelay fixture for testing."""
    parentW = MWidget()
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    # Create mock UI elements for relays
    for i in range(8):
        setattr(parentW.ui, f"relayFun{i}", createMockComboBox())
        setattr(parentW.ui, f"relayButtonText{i}", createMockLineEdit())

    window = SettRelay(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_settRelay_class_exists():
    """Test SettRelay class exists."""
    assert SettRelay is not None


def test_settRelay_can_instantiate(settRelay):
    """Test SettRelay can be instantiated."""
    assert settRelay is not None


def test_settRelay_instance_is_settRelay_type(settRelay):
    """Test instance is of SettRelay type."""
    assert isinstance(settRelay, SettRelay)


def test_settRelay_has_parentW_attribute(settRelay):
    """Test SettRelay has parentW attribute."""
    assert hasattr(settRelay, "parentW")
    assert settRelay.parentW is not None


def test_settRelay_has_app_attribute(settRelay):
    """Test SettRelay has app attribute."""
    assert hasattr(settRelay, "app")
    assert settRelay.app is not None


def test_settRelay_has_msg_attribute(settRelay):
    """Test SettRelay has msg attribute."""
    assert hasattr(settRelay, "msg")
    assert settRelay.msg is not None


def test_settRelay_has_ui_attribute(settRelay):
    """Test SettRelay has ui attribute."""
    assert hasattr(settRelay, "ui")
    assert settRelay.ui is not None


def test_settRelay_has_relayDropDowns_attribute(settRelay):
    """Test SettRelay has relayDropDowns attribute."""
    assert hasattr(settRelay, "relayDropDowns")
    assert settRelay.relayDropDowns is not None


def test_settRelay_relayDropDowns_is_list(settRelay):
    """Test relayDropDowns is a list."""
    assert isinstance(settRelay.relayDropDowns, list)


def test_settRelay_relayDropDowns_has_eight_elements(settRelay):
    """Test relayDropDowns has 8 elements."""
    assert len(settRelay.relayDropDowns) == 8


def test_settRelay_has_relayButtonTexts_attribute(settRelay):
    """Test SettRelay has relayButtonTexts attribute."""
    assert hasattr(settRelay, "relayButtonTexts")
    assert settRelay.relayButtonTexts is not None


def test_settRelay_relayButtonTexts_is_list(settRelay):
    """Test relayButtonTexts is a list."""
    assert isinstance(settRelay.relayButtonTexts, list)


def test_settRelay_relayButtonTexts_has_eight_elements(settRelay):
    """Test relayButtonTexts has 8 elements."""
    assert len(settRelay.relayButtonTexts) == 8


def test_settRelay_has_initConfig_method(settRelay):
    """Test SettRelay has initConfig method."""
    assert hasattr(settRelay, "initConfig")
    assert callable(settRelay.initConfig)


def test_settRelay_has_storeConfig_method(settRelay):
    """Test SettRelay has storeConfig method."""
    assert hasattr(settRelay, "storeConfig")
    assert callable(settRelay.storeConfig)


def test_settRelay_has_setupRelayGui_method(settRelay):
    """Test SettRelay has setupRelayGui method."""
    assert hasattr(settRelay, "setupRelayGui")
    assert callable(settRelay.setupRelayGui)


def test_initConfig_empty_config(settRelay):
    """Test initConfig loads defaults with empty config."""
    settRelay.app.config = {}
    settRelay.initConfig()


def test_initConfig_with_custom_text(settRelay):
    """Test initConfig loads custom relay button text."""
    config = {
        "SettingRelay": {
            "RelayText0": "Shutter",
            "RelayText1": "Light",
            "Action0": 0,
            "Action1": 1,
        }
    }
    settRelay.app.config = config
    settRelay.initConfig()
    assert settRelay.relayButtonTexts[0].text() == "Shutter"
    assert settRelay.relayButtonTexts[1].text() == "Light"


def test_initConfig_with_all_relays(settRelay):
    """Test initConfig loads all relay settings."""
    config = {"SettingRelay": {}}
    for i in range(8):
        config["SettingRelay"][f"RelayText{i}"] = f"Relay {i}"
        config["SettingRelay"][f"Action{i}"] = i % 2
    settRelay.app.config = config
    settRelay.initConfig()
    for i in range(8):
        assert settRelay.relayButtonTexts[i].text() == f"Relay {i}"
        assert settRelay.relayDropDowns[i].currentIndex() == i % 2


def test_initConfig_sets_default_text(settRelay):
    """Test initConfig sets default dash text."""
    settRelay.app.config = {"SettingRelay": {}}
    settRelay.initConfig()
    assert settRelay.relayButtonTexts[0].text() == "-"


def test_initConfig_sets_default_action(settRelay):
    """Test initConfig sets default action to 0."""
    settRelay.app.config = {"SettingRelay": {}}
    settRelay.initConfig()
    for dropdown in settRelay.relayDropDowns:
        assert dropdown.currentIndex() == 0


def test_storeConfig_saves_button_texts(settRelay):
    """Test storeConfig saves button texts."""
    settRelay.relayButtonTexts[0].setText("Custom Text")
    settRelay.relayButtonTexts[5].setText("Another Text")
    settRelay.storeConfig()
    config = settRelay.app.config["SettingRelay"]
    assert config["RelayText0"] == "Custom Text"
    assert config["RelayText5"] == "Another Text"


def test_storeConfig_saves_actions(settRelay):
    """Test storeConfig saves relay actions."""
    settRelay.relayDropDowns[0].setCurrentIndex(0)
    settRelay.relayDropDowns[1].setCurrentIndex(1)
    settRelay.storeConfig()
    config = settRelay.app.config["SettingRelay"]
    assert config["Action0"] == 0
    assert config["Action1"] == 1


def test_storeConfig_saves_all_relays(settRelay):
    """Test storeConfig saves all relay settings."""
    for i in range(8):
        settRelay.relayButtonTexts[i].setText(f"Relay {i}")
        if i < settRelay.relayDropDowns[i].count():
            settRelay.relayDropDowns[i].setCurrentIndex(i % 2)
    settRelay.storeConfig()
    config = settRelay.app.config["SettingRelay"]
    for i in range(8):
        assert config[f"RelayText{i}"] == f"Relay {i}"


def test_storeConfig_overwrites_previous_config(settRelay):
    """Test storeConfig overwrites previous config."""
    settRelay.app.config["SettingRelay"] = {"OldKey": "OldValue"}
    settRelay.relayButtonTexts[0].setText("New Text")
    settRelay.storeConfig()
    config = settRelay.app.config["SettingRelay"]
    assert "OldKey" not in config
    assert config["RelayText0"] == "New Text"


def test_setupRelayGui_creates_dropdown_items(settRelay):
    """Test setupRelayGui creates dropdown items."""
    settRelay.setupRelayGui()
    for dropdown in settRelay.relayDropDowns:
        assert dropdown.count() >= 2


def test_setupRelayGui_items_text(settRelay):
    """Test setupRelayGui items have correct text."""
    settRelay.setupRelayGui()
    for dropdown in settRelay.relayDropDowns:
        assert dropdown.itemText(0) == "Switch - Toggle"
        assert dropdown.itemText(1) == "Pulse 0.5 sec"


def test_initConfig_emits_signal(settRelay):
    """Test initConfig emits relayChanged signal."""
    settRelay.app.config = {"SettingRelay": {}}
    with mock.patch.object(settRelay.app, "relayChanged"):
        settRelay.initConfig()
        settRelay.app.relayChanged.emit.assert_called()


def test_storeConfig_emits_signal(settRelay):
    """Test storeConfig emits relayChanged signal."""
    with mock.patch.object(settRelay.app, "relayChanged"):
        settRelay.storeConfig()
        settRelay.app.relayChanged.emit.assert_called()


def test_relayButtonText_elements_exist(settRelay):
    """Test relay button text elements exist and are connected."""
    for i in range(8):
        assert settRelay.relayButtonTexts[i] is not None


def test_relayDropDown_elements_exist(settRelay):
    """Test relay dropdown elements exist and are connected."""
    for i in range(8):
        assert settRelay.relayDropDowns[i] is not None


def test_initConfig_handles_missing_config_keys(settRelay):
    """Test initConfig handles missing config keys gracefully."""
    settRelay.app.config = {"SettingRelay": {"RelayText0": "Test"}}
    settRelay.initConfig()
    assert settRelay.relayButtonTexts[1].text() == "-"


def test_initConfig_partial_config(settRelay):
    """Test initConfig with partial config."""
    settRelay.app.config = {
        "SettingRelay": {
            "RelayText0": "Custom",
            "Action0": 1,
        }
    }
    settRelay.initConfig()
    assert settRelay.relayButtonTexts[0].text() == "Custom"
    assert settRelay.relayDropDowns[0].currentIndex() == 1
    assert settRelay.relayButtonTexts[1].text() == "-"
    assert settRelay.relayDropDowns[1].currentIndex() == 0


def test_storeConfig_creates_settingRelay_key(settRelay):
    """Test storeConfig creates SettingRelay key in config."""
    settRelay.app.config = {}
    settRelay.storeConfig()
    assert "SettingRelay" in settRelay.app.config


def test_relay_settings_roundtrip(settRelay):
    """Test save and load relay settings roundtrip."""
    original_config = {
        "SettingRelay": {
            "RelayText0": "Shutter",
            "RelayText1": "Light",
            "RelayText2": "Fan",
            "Action0": 0,
            "Action1": 1,
            "Action2": 0,
        }
    }
    settRelay.app.config = original_config
    settRelay.initConfig()
    settRelay.storeConfig()
    saved_config = settRelay.app.config["SettingRelay"]
    assert saved_config["RelayText0"] == "Shutter"
    assert saved_config["RelayText1"] == "Light"
    assert saved_config["Action0"] == 0
    assert saved_config["Action1"] == 1
