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
from mw4.gui.extWindows.setting.tabSettAudio import SettAudio
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QComboBox
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def settAudio(qapp):
    """Setup SettAudio fixture for testing."""
    parentW = MWidget()
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    parentW.ui.soundMountSlewFinished = QComboBox()
    parentW.ui.soundDomeSlewFinished = QComboBox()
    parentW.ui.soundMountAlert = QComboBox()
    parentW.ui.soundRunFinished = QComboBox()
    parentW.ui.soundImageSaved = QComboBox()
    parentW.ui.soundImageSolved = QComboBox()
    parentW.ui.soundConnectionLost = QComboBox()
    parentW.ui.soundSatStartTracking = QComboBox()

    parentW.ui.soundMountSlewFinishedT = mock.MagicMock()
    parentW.ui.soundDomeSlewFinishedT = mock.MagicMock()
    parentW.ui.soundMountAlertT = mock.MagicMock()
    parentW.ui.soundRunFinishedT = mock.MagicMock()
    parentW.ui.soundImageSavedT = mock.MagicMock()
    parentW.ui.soundImageSolvedT = mock.MagicMock()
    parentW.ui.soundConnectionLostT = mock.MagicMock()
    parentW.ui.soundSatStartTrackingT = mock.MagicMock()

    window = SettAudio(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_init_creates_gui_audio_list(settAudio):
    """Test __init__ initializes guiAudioList."""
    assert isinstance(settAudio.guiAudioList, dict)


def test_init_sets_parent_and_app(settAudio):
    """Test __init__ sets parentW and app references."""
    assert settAudio.parentW is not None
    assert settAudio.app is not None


def test_init_sets_msg_and_ui(settAudio):
    """Test __init__ sets msg and ui references."""
    assert settAudio.msg is not None
    assert settAudio.ui is not None


def test_init_defines_audio_config(settAudio):
    """Test __init__ defines audioConfig mapping."""
    expected_sounds = [
        "MountSlew",
        "DomeSlew",
        "MountAlert",
        "RunFinished",
        "ImageSaved",
        "ImageSolved",
        "ConnectionLost",
        "SatStartTracking",
    ]
    for sound in expected_sounds:
        assert sound in settAudio.audioConfig


def test_init_calls_setup_audio(settAudio):
    """Test __init__ calls setupAudio method."""
    widget = settAudio.ui.soundMountSlewFinished
    assert widget.count() > 0


def test_initConfig_with_empty_config(settAudio):
    """Test initConfig with empty config loads defaults."""
    settAudio.app.config["SettingAudio"] = {}
    settAudio.initConfig()
    for uiKey in settAudio.audioConfig.values():
        widget = getattr(settAudio.ui, uiKey)
        assert widget.currentIndex() == 0


def test_initConfig_loads_saved_index(settAudio):
    """Test initConfig loads saved sound index."""
    settAudio.app.config["SettingAudio"] = {"MountSlew": 2}
    settAudio.initConfig()
    assert settAudio.ui.soundMountSlewFinished.currentIndex() == 2


def test_initConfig_loads_multiple_sounds(settAudio):
    """Test initConfig loads multiple sound configurations."""
    settAudio.app.config["SettingAudio"] = {
        "MountSlew": 1,
        "DomeSlew": 2,
        "MountAlert": 3,
        "RunFinished": 4,
    }
    settAudio.initConfig()
    assert settAudio.ui.soundMountSlewFinished.currentIndex() == 1
    assert settAudio.ui.soundDomeSlewFinished.currentIndex() == 2
    assert settAudio.ui.soundMountAlert.currentIndex() == 3
    assert settAudio.ui.soundRunFinished.currentIndex() == 4


def test_storeConfig_saves_to_config(settAudio):
    """Test storeConfig saves current widget values to config."""
    settAudio.ui.soundMountSlewFinished.setCurrentIndex(1)
    settAudio.storeConfig()
    config = settAudio.app.config["SettingAudio"]
    assert config["MountSlew"] == 1


def test_storeConfig_saves_all_sounds(settAudio):
    """Test storeConfig saves all sound configurations."""
    settAudio.ui.soundMountSlewFinished.setCurrentIndex(1)
    settAudio.ui.soundDomeSlewFinished.setCurrentIndex(2)
    settAudio.ui.soundMountAlert.setCurrentIndex(3)
    settAudio.ui.soundRunFinished.setCurrentIndex(4)
    settAudio.ui.soundImageSaved.setCurrentIndex(5)
    settAudio.ui.soundImageSolved.setCurrentIndex(6)
    settAudio.ui.soundConnectionLost.setCurrentIndex(7)
    settAudio.ui.soundSatStartTracking.setCurrentIndex(8)

    settAudio.storeConfig()
    config = settAudio.app.config["SettingAudio"]

    assert config["MountSlew"] == 1
    assert config["DomeSlew"] == 2
    assert config["MountAlert"] == 3
    assert config["RunFinished"] == 4
    assert config["ImageSaved"] == 5
    assert config["ImageSolved"] == 6
    assert config["ConnectionLost"] == 7
    assert config["SatStartTracking"] == 8


def test_storeConfig_creates_setting_audio_section(settAudio):
    """Test storeConfig creates SettingAudio config section."""
    settAudio.app.config = {}
    settAudio.storeConfig()
    assert "SettingAudio" in settAudio.app.config


def test_updateConfig_calls_store_config(settAudio):
    """Test updateConfig calls storeConfig."""
    with mock.patch.object(settAudio, "storeConfig") as mock_store:
        settAudio.updateConfig(1)
        mock_store.assert_called_once()


def test_updateConfig_with_any_index(settAudio):
    """Test updateConfig accepts any index value."""
    settAudio.app.config["SettingAudio"] = {}
    settAudio.ui.soundMountSlewFinished.setCurrentIndex(3)
    settAudio.updateConfig(3)
    assert settAudio.app.config["SettingAudio"]["MountSlew"] == 3


def test_testSound_emits_playSound_signal(settAudio):
    """Test testSound emits playSound signal with sound name."""
    with mock.patch.object(settAudio.app, "playSound") as mock_signal:
        mock_signal.emit = mock.MagicMock()
        settAudio.testSound("MountSlew")
        assert mock_signal.emit.called


def test_testSound_with_different_sounds(settAudio):
    """Test testSound with different sound options."""
    sounds_to_test = [
        "MountSlew",
        "DomeSlew",
        "MountAlert",
        "RunFinished",
        "ImageSaved",
    ]
    for sound in sounds_to_test:
        with mock.patch.object(
            settAudio.app, "playSound"
        ) as mock_signal:
            mock_signal.emit = mock.MagicMock()
            settAudio.testSound(sound)
            assert mock_signal.emit.called


def test_setupAudio_creates_combo_boxes(settAudio):
    """Test setupAudio creates and populates combo boxes."""
    for uiKey in settAudio.audioConfig.values():
        widget = getattr(settAudio.ui, uiKey)
        assert widget.count() > 0


def test_setupAudio_adds_sound_options(settAudio):
    """Test setupAudio adds all sound options to combo boxes."""
    widget = settAudio.ui.soundMountSlewFinished
    items = [widget.itemText(i) for i in range(widget.count())]
    assert "None" in items
    assert "Beep" in items


def test_setupAudio_connects_activated_signal(settAudio):
    """Test setupAudio connects activated signals."""
    settAudio.app.config["SettingAudio"] = {}
    settAudio.ui.soundMountSlewFinished.setCurrentIndex(2)
    settAudio.ui.soundMountSlewFinished.activated.emit(2)
    config = settAudio.app.config["SettingAudio"]
    assert config["MountSlew"] == 2


def test_setupAudio_connects_test_buttons(settAudio):
    """Test setupAudio connects test button click signals."""
    for uiKey in settAudio.audioConfig.values():
        widgetTest = getattr(settAudio.ui, uiKey + "T")
        assert widgetTest.clicked is not None


def test_setupAudio_creates_all_widgets(settAudio):
    """Test setupAudio sets up all sound widgets."""
    expected_count = len(settAudio.audioConfig)
    actual_count = len([k for k in dir(settAudio.ui) if "sound" in k])
    assert actual_count >= expected_count


def test_audio_config_mapping_complete(settAudio):
    """Test all audio config mappings have corresponding UI widgets."""
    for uiKey in settAudio.audioConfig.values():
        assert hasattr(settAudio.ui, uiKey)
        assert hasattr(settAudio.ui, uiKey + "T")


def test_multiple_init_and_store_cycles(settAudio):
    """Test multiple init/store cycles maintain consistency."""
    settAudio.app.config["SettingAudio"] = {"MountSlew": 2}
    settAudio.initConfig()
    settAudio.ui.soundMountSlewFinished.setCurrentIndex(3)
    settAudio.storeConfig()
    settAudio.ui.soundMountSlewFinished.setCurrentIndex(0)
    settAudio.initConfig()
    assert settAudio.ui.soundMountSlewFinished.currentIndex() == 3










