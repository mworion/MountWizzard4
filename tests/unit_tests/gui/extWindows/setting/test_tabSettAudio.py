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
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QComboBox
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


def createMockComboBox() -> QComboBox:
    """Create a mock combo box for sound selection."""
    m = QComboBox()
    m.addItem("None")
    m.addItem("Beep")
    m.addItem("Beep1")
    m.addItem("Beep2")
    m.addItem("Bleep")
    m.addItem("Pan1")
    m.addItem("Pan2")
    m.addItem("Horn")
    m.addItem("Alarm")
    return m


def createMockCheckBox(defaultValue: bool = False):
    """Create a mock checkbox."""
    m = mock.MagicMock()
    m._checked = defaultValue
    m.isChecked = mock.MagicMock(side_effect=lambda: m._checked)
    m.setChecked = mock.MagicMock(side_effect=lambda v: setattr(m, "_checked", v))
    m.clicked = mock.MagicMock()
    return m


@pytest.fixture(autouse=True, scope="module")
def settAudio(qapp):
    """Setup SettAudio fixture for testing."""
    parentW = MWidget()
    parentW.gameControllerRunning = False
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    # Create mock UI elements for sound dropdowns
    parentW.ui.soundMountSlewFinished = createMockComboBox()
    parentW.ui.soundDomeSlewFinished = createMockComboBox()
    parentW.ui.soundMountAlert = createMockComboBox()
    parentW.ui.soundRunFinished = createMockComboBox()
    parentW.ui.soundImageSaved = createMockComboBox()
    parentW.ui.soundImageSolved = createMockComboBox()
    parentW.ui.soundConnectionLost = createMockComboBox()
    parentW.ui.soundSatStartTracking = createMockComboBox()
    parentW.ui.colorSet = QComboBox()
    parentW.ui.colorSet.addItem("Dark")
    parentW.ui.colorSet.addItem("Light")

    window = SettAudio(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_playSound_invalid_sound_name(settAudio):
    """Test playSound with invalid sound name."""
    settAudio.playSound("")


def test_playSound_valid_sound_name(settAudio):
    """Test playSound with valid sound name."""
    with mock.patch.object(QSoundEffect, "play"):
        settAudio.playSound("MountSlew")


def test_playSound_with_custom_audio(settAudio):
    """Test playSound with custom audio selection."""
    settAudio.audioSignalsSet["Pan1"] = "test"
    settAudio.guiAudioList["MountSlew"] = settAudio.ui.soundMountSlewFinished
    settAudio.guiAudioList["MountSlew"].clear()
    settAudio.guiAudioList["MountSlew"].addItem("Pan1")
    with mock.patch.object(QSoundEffect, "play"):
        settAudio.playSound("MountSlew")


def test_playSound_skips_unknown_audio(settAudio):
    """Test playSound skips unknown audio."""
    settAudio.audioSignalsSet["Pan1"] = "test"
    settAudio.guiAudioList["MountSlew"] = settAudio.ui.soundMountSlewFinished
    settAudio.guiAudioList["MountSlew"].clear()
    settAudio.guiAudioList["MountSlew"].addItem("Pan5")

    with mock.patch.object(QSoundEffect, "play"):
        settAudio.playSound("MountSlew")


def test_setupAudioSignals(settAudio):
    """Test setupAudioSignals initializes audio dict."""
    settAudio.setupAudioSignals()
    assert "Beep" in settAudio.audioSignalsSet
    assert "Pan1" in settAudio.audioSignalsSet


def test_storeConfig_saves_audio_settings(settAudio):
    """Test storeConfig saves all audio UI state."""
    settAudio.setupAudioGui()
    settAudio.ui.soundMountSlewFinished.setCurrentIndex(1)
    settAudio.ui.soundDomeSlewFinished.setCurrentIndex(2)
    settAudio.ui.soundMountAlert.setCurrentIndex(1)
    settAudio.ui.soundRunFinished.setCurrentIndex(2)
    settAudio.ui.soundImageSaved.setCurrentIndex(1)
    settAudio.ui.soundImageSolved.setCurrentIndex(2)
    settAudio.ui.soundConnectionLost.setCurrentIndex(1)
    settAudio.ui.soundSatStartTracking.setCurrentIndex(2)

    settAudio.storeConfig()

    config = settAudio.app.config["SettingAudio"]
    assert config["soundMountSlewFinished"] == 1
    assert config["soundDomeSlewFinished"] == 2
    assert config["soundMountAlert"] == 1


def test_setupAudioGui_populates_dropdowns(settAudio):
    """Test setupAudioGui initializes all audio dropdowns."""
    # Create fresh combo boxes to test setupAudioGui
    fresh_combo = QComboBox()
    original_soundMountSlewFinished = settAudio.ui.soundMountSlewFinished
    settAudio.ui.soundMountSlewFinished = fresh_combo
    settAudio.ui.soundMountSlewFinished.clear()

    settAudio.setupAudioGui()

    assert settAudio.ui.soundMountSlewFinished.count() > 0
    assert settAudio.ui.soundMountSlewFinished.itemText(0) == "None"

    # Restore original
    settAudio.ui.soundMountSlewFinished = original_soundMountSlewFinished


def test_updateColorSet_updates_app(settAudio):
    """Test updateColorSet updates color set."""
    settAudio.ui.colorSet.setCurrentIndex(1)
    settAudio.updateColorSet()

    from mw4.gui.styles.styles import Styles

    assert Styles.colorSet == 1
