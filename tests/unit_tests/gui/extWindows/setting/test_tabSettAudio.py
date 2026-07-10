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
    settAudio.guiAudioList["MountSlew"] = settAudio.ui.soundMountSlewFinished
    settAudio.guiAudioList["MountSlew"].clear()
    settAudio.guiAudioList["MountSlew"].addItem("Pan1")
    with mock.patch.object(QSoundEffect, "play"):
        settAudio.playSound("MountSlew")


def test_playSound_skips_unknown_audio(settAudio):
    """Test playSound skips unknown audio."""
    settAudio.guiAudioList["MountSlew"] = settAudio.ui.soundMountSlewFinished
    settAudio.guiAudioList["MountSlew"].clear()
    settAudio.guiAudioList["MountSlew"].addItem("Pan5")

    with mock.patch.object(QSoundEffect, "play"):
        settAudio.playSound("MountSlew")


def test_audio_sounds_constant(settAudio):
    """Test AUDIO_SOUNDS constant contains all sounds."""
    assert "Beep" in settAudio.AUDIO_SOUNDS
    assert "Pan1" in settAudio.AUDIO_SOUNDS
    assert "Horn" in settAudio.AUDIO_SOUNDS
    assert "None" in settAudio.AUDIO_SOUNDS
    assert settAudio.AUDIO_SOUNDS["None"] is None
    assert settAudio.AUDIO_SOUNDS["Beep"] == ":/sound/beep.wav"


def test_audioConfig_complete(settAudio):
    """Test audioConfig contains all 8 audio events."""
    assert "MountSlew" in settAudio.audioConfig
    assert "DomeSlew" in settAudio.audioConfig
    assert "MountAlert" in settAudio.audioConfig
    assert "RunFinished" in settAudio.audioConfig
    assert "ImageSaved" in settAudio.audioConfig
    assert "ImageSolved" in settAudio.audioConfig
    assert "ConnectionLost" in settAudio.audioConfig
    assert "SatStartTracking" in settAudio.audioConfig


def test_audioConfig_has_required_keys(settAudio):
    """Test audioConfig entries have required keys."""
    for soundKey, soundData in settAudio.audioConfig.items():
        assert "configKey" in soundData
        assert "uiWidget" in soundData
        assert "device" in soundData
        assert "signal" in soundData


def test_storeConfig_saves_audio_settings(settAudio):
    """Test storeConfig saves all audio UI state."""
    settAudio.ui.soundMountSlewFinished = createMockComboBox()
    settAudio.ui.soundDomeSlewFinished = createMockComboBox()
    settAudio.ui.soundMountAlert = createMockComboBox()
    settAudio.ui.soundRunFinished = createMockComboBox()
    settAudio.ui.soundImageSaved = createMockComboBox()
    settAudio.ui.soundImageSolved = createMockComboBox()
    settAudio.ui.soundConnectionLost = createMockComboBox()
    settAudio.ui.soundSatStartTracking = createMockComboBox()
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
    assert config["soundConnectionLost"] == 1


def test_setupAudio_populates_dropdowns(settAudio):
    """Test setupAudio initializes all audio dropdowns."""
    # Create fresh combo box to test setupAudio
    fresh_combo = QComboBox()
    original_soundMountSlewFinished = settAudio.ui.soundMountSlewFinished
    settAudio.ui.soundMountSlewFinished = fresh_combo
    settAudio.ui.soundMountSlewFinished.clear()

    settAudio.setupAudio()

    assert settAudio.ui.soundMountSlewFinished.count() > 0
    assert settAudio.ui.soundMountSlewFinished.itemText(0) == "None"

    # Restore original
    settAudio.ui.soundMountSlewFinished = original_soundMountSlewFinished


def test_setupAudioSignals_connects_device_signals(settAudio):
    """Test setupAudioSignals connects device signals."""
    # Mock device signals
    with (
        mock.patch.object(settAudio.app.dReg["mount"].signals, "slewed") as mock_slewed,
        mock.patch.object(settAudio.app.dReg["mount"].signals, "alert") as mock_alert,
        mock.patch.object(settAudio.app.dReg["dome"].signals, "slewed"),
    ):
        settAudio.setupAudioSignals()
        # Verify signal connect was called (at least for the device signals)
        assert mock_slewed.connect.called or mock_alert.connect.called


def test_initConfig_loads_audio_settings(settAudio):
    """Test initConfig loads saved audio settings."""
    settAudio.ui.soundMountSlewFinished = createMockComboBox()
    settAudio.ui.soundDomeSlewFinished = createMockComboBox()
    settAudio.ui.soundMountAlert = createMockComboBox()
    settAudio.ui.soundRunFinished = createMockComboBox()
    settAudio.ui.soundImageSaved = createMockComboBox()
    settAudio.ui.soundImageSolved = createMockComboBox()
    settAudio.ui.soundConnectionLost = createMockComboBox()
    settAudio.ui.soundSatStartTracking = createMockComboBox()
    settAudio.app.config["SettingAudio"] = {
        "soundMountSlewFinished": 1,
        "soundDomeSlewFinished": 2,
        "soundMountAlert": 3,
        "soundRunFinished": 1,
        "soundImageSaved": 2,
        "soundImageSolved": 1,
        "soundConnectionLost": 2,
        "soundSatStartTracking": 1,
    }

    settAudio.initConfig()

    assert settAudio.ui.soundMountSlewFinished.currentIndex() == 1
    assert settAudio.ui.soundDomeSlewFinished.currentIndex() == 2
    assert settAudio.ui.soundMountAlert.currentIndex() == 3
    assert settAudio.ui.soundConnectionLost.currentIndex() == 2


def test_guiAudioList_populated(settAudio):
    """Test guiAudioList is populated correctly."""
    assert "MountSlew" in settAudio.guiAudioList
    assert "DomeSlew" in settAudio.guiAudioList
    assert "MountAlert" in settAudio.guiAudioList
    assert "ImageSaved" in settAudio.guiAudioList
    assert "ImageSolved" in settAudio.guiAudioList
    assert "ConnectionLost" in settAudio.guiAudioList
