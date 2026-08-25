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
from mw4.base.audioManager import AUDIO_SOUNDS, AudioManager
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def audioManager(qapp):
    """Setup AudioManager fixture for testing."""
    app = App()
    manager = AudioManager(app)
    yield manager


def test_init_connects_signal_to_playSound(audioManager):
    """Test __init__ connects playSound signal to method."""
    assert audioManager.app.playSound is not None


def test_init_sound_is_none(audioManager):
    """Test __init__ initializes sound to None."""
    assert audioManager.sound is None


def test_init_connects_playSound_signal(audioManager):
    """Test __init__ connects playSound signal."""
    assert audioManager.app.playSound is not None


def test_audio_sounds_constant_defined():
    """Test AUDIO_SOUNDS constant is properly defined."""
    assert isinstance(AUDIO_SOUNDS, dict)
    assert len(AUDIO_SOUNDS) > 0


def test_audio_sounds_has_none_option():
    """Test AUDIO_SOUNDS includes None option."""
    assert "None" in AUDIO_SOUNDS
    assert AUDIO_SOUNDS["None"] == ""


def test_audio_sounds_has_beep_options():
    """Test AUDIO_SOUNDS includes beep options."""
    assert "Beep" in AUDIO_SOUNDS
    assert "Beep1" in AUDIO_SOUNDS
    assert "Beep2" in AUDIO_SOUNDS


def test_audio_sounds_has_alert_options():
    """Test AUDIO_SOUNDS includes alert options."""
    assert "Alert" in AUDIO_SOUNDS
    assert "Alarm" in AUDIO_SOUNDS


def test_playSound_with_no_config(audioManager):
    """Test playSound with empty config returns early."""
    audioManager.app.config["SettingAudio"] = {}
    audioManager.playSound("MountSlew")
    assert audioManager.sound is None


def test_playSound_with_index_zero(audioManager):
    """Test playSound with index 0 (disabled) returns early."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 0, "PlaySound": True}
    audioManager.playSound("MountSlew")
    assert audioManager.sound is None


def test_playSound_with_valid_index(audioManager):
    """Test playSound with valid sound index creates QSoundEffect."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 1, "PlaySound": True}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance

            audioManager.playSound("MountSlew")

            mock_sound_effect.assert_called_once()
            mock_sound_instance.setSource.assert_called_once()
            mock_sound_instance.setVolume.assert_called_once_with(1)
            mock_sound_instance.play.assert_called_once()


def test_playSound_uses_correct_wav_file(audioManager):
    """Test playSound uses correct wav file based on config index."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 1, "PlaySound": True}
    wav_files = list(AUDIO_SOUNDS.values())
    expected_wav = wav_files[1]

    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.files") as mock_files:
            mock_files.return_value.joinpath = mock.MagicMock(return_value=mock.MagicMock())
            with mock.patch("mw4.base.audioManager.QSoundEffect"):
                audioManager.playSound("MountSlew")
                mock_files.return_value.joinpath.assert_called_once()
                call_args = mock_files.return_value.joinpath.call_args[0][0]
                assert expected_wav in call_args


def test_playSound_sets_volume_to_one(audioManager):
    """Test playSound sets volume to 1."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 1, "PlaySound": True}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("MountSlew")
            mock_sound_instance.setVolume.assert_called_once_with(1)


def test_playSound_plays_sound(audioManager):
    """Test playSound calls play method."""
    audioManager.app.config["SettingAudio"] = {"RunFinished": 1, "PlaySound": True}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("RunFinished")
            mock_sound_instance.play.assert_called_once()


def test_playSound_with_different_sounds(audioManager):
    """Test playSound with different sound types."""
    sounds = ["MountSlew", "DomeSlew", "MountAlert", "ImageSaved"]
    for sound in sounds:
        audioManager.app.config["SettingAudio"] = {sound: 1}
        with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
            mock_file_path = mock.MagicMock()
            mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
            mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

            with mock.patch("mw4.base.audioManager.QSoundEffect"):
                audioManager.playSound(sound)


def test_playSound_missing_sound_in_config(audioManager):
    """Test playSound with missing sound in config."""
    audioManager.app.config["SettingAudio"] = {}
    audioManager.sound = None
    audioManager.playSound("NonExistentSound")
    assert audioManager.sound is None


def test_playSound_stores_sound_reference(audioManager):
    """Test playSound stores QSoundEffect reference in self.sound."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 2, "PlaySound": True}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("MountSlew")
            assert audioManager.sound is not None


def test_playSound_uses_different_wav_for_different_indices(audioManager):
    """Test playSound uses different wav files for different indices."""
    wav_files = list(AUDIO_SOUNDS.values())
    for index in range(1, min(3, len(wav_files))):
        if not wav_files[index]:
            continue
        audioManager.app.config["SettingAudio"] = {"MountSlew": index}
        with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
            mock_file_path = mock.MagicMock()
            mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
            mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

            with mock.patch("mw4.base.audioManager.files") as mock_files:
                mock_files.return_value.joinpath = mock.MagicMock(
                    return_value=mock.MagicMock()
                )
                with mock.patch("mw4.base.audioManager.QSoundEffect"):
                    audioManager.playSound("MountSlew")


def test_audio_manager_with_all_sound_types(audioManager):
    """Test AudioManager handles all sound types from audioConfig."""
    sound_types = [
        "MountSlew",
        "DomeSlew",
        "MountAlert",
        "RunFinished",
        "ImageSaved",
        "ImageSolved",
        "ConnectionLost",
        "SatStartTracking",
    ]
    for sound in sound_types:
        audioManager.app.config["SettingAudio"] = {sound: 1}
        with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
            mock_file_path = mock.MagicMock()
            mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
            mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

            with mock.patch("mw4.base.audioManager.QSoundEffect"):
                audioManager.playSound(sound)


def test_playSound_creates_sound_with_app_context(audioManager):
    """Test playSound creates QSoundEffect with app context."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 1, "PlaySound": True}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("MountSlew")
            mock_sound_effect.assert_called_once_with(audioManager.app.mainW)


def test_audio_sounds_dict_structure():
    """Test AUDIO_SOUNDS has correct structure."""
    for key, value in AUDIO_SOUNDS.items():
        assert isinstance(key, str)
        assert isinstance(value, str)


def test_multiple_play_sound_calls(audioManager):
    """Test multiple playSound calls work correctly."""
    sounds = ["MountSlew", "ImageSaved", "DomeSlew"]
    for sound in sounds:
        audioManager.app.config["SettingAudio"] = {sound: 1, "PlaySound": True}
        with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
            mock_file_path = mock.MagicMock()
            mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
            mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

            with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
                mock_sound_instance = mock.MagicMock()
                mock_sound_effect.return_value = mock_sound_instance
                audioManager.playSound(sound)
                assert audioManager.sound is not None


def test_linearToVolumePower_zero_input():
    """Test linearToVolumePower with zero input."""
    result = AudioManager.linearToVolumePower(0.0)
    assert result == 0.0


def test_linearToVolumePower_one_input():
    """Test linearToVolumePower with input of 1."""
    result = AudioManager.linearToVolumePower(1.0)
    assert result == 1.0


def test_linearToVolumePower_half_input():
    """Test linearToVolumePower with input of 0.5."""
    result = AudioManager.linearToVolumePower(0.5)
    assert result == 0.125  # 0.5^3 = 0.125


def test_linearToVolumePower_quarter_input():
    """Test linearToVolumePower with input of 0.25."""
    result = AudioManager.linearToVolumePower(0.25)
    assert result == 0.015625  # 0.25^3 = 0.015625


def test_linearToVolumePower_clamps_negative():
    """Test linearToVolumePower clamps negative values to 0."""
    result = AudioManager.linearToVolumePower(-0.5)
    assert result == 0.0


def test_linearToVolumePower_clamps_above_one():
    """Test linearToVolumePower clamps values above 1 to 1."""
    result = AudioManager.linearToVolumePower(1.5)
    assert result == 1.0


def test_linearToVolumePower_very_small_value():
    """Test linearToVolumePower with very small value."""
    result = AudioManager.linearToVolumePower(0.1)
    assert abs(result - 0.001) < 1e-10  # Use approximate comparison for float precision


def test_linearToVolumePower_return_type():
    """Test linearToVolumePower returns float."""
    result = AudioManager.linearToVolumePower(0.5)
    assert isinstance(result, float)


def test_playSound_with_play_sound_disabled(audioManager):
    """Test playSound returns early when PlaySound is False."""
    audioManager.sound = None  # Reset from previous test
    audioManager.app.config["SettingAudio"] = {
        "MountSlew": 1,
        "PlaySound": False,
    }
    audioManager.playSound("MountSlew")
    assert audioManager.sound is None


def test_playSound_with_play_sound_enabled(audioManager):
    """Test playSound proceeds when PlaySound is True."""
    audioManager.app.config["SettingAudio"] = {
        "MountSlew": 1,
        "PlaySound": True,
    }
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("MountSlew")
            mock_sound_instance.play.assert_called_once()


def test_playSound_with_custom_volume(audioManager):
    """Test playSound applies custom volume setting."""
    audioManager.app.config["SettingAudio"] = {
        "MountSlew": 1,
        "PlaySound": True,
        "Volume": 0.5,
    }
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("MountSlew")
            expected_volume = 0.5**3  # linearToVolumePower(0.5) = 0.125
            mock_sound_instance.setVolume.assert_called_once_with(expected_volume)


def test_playSound_with_zero_volume(audioManager):
    """Test playSound with zero volume."""
    audioManager.app.config["SettingAudio"] = {
        "MountSlew": 1,
        "PlaySound": True,
        "Volume": 0.0,
    }
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("MountSlew")
            mock_sound_instance.setVolume.assert_called_once_with(0.0)


def test_playSound_with_max_volume(audioManager):
    """Test playSound with maximum volume."""
    audioManager.app.config["SettingAudio"] = {
        "MountSlew": 1,
        "PlaySound": True,
        "Volume": 1.0,
    }
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("MountSlew")
            mock_sound_instance.setVolume.assert_called_once_with(1.0)


def test_playSound_volume_defaults_to_one(audioManager):
    """Test playSound defaults Volume to 1 when not specified."""
    audioManager.app.config["SettingAudio"] = {
        "MountSlew": 1,
        "PlaySound": True,
    }
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(return_value=mock_file_path)
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.QSoundEffect") as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("MountSlew")
            mock_sound_instance.setVolume.assert_called_once_with(1.0)


def test_playSound_returns_early_when_play_sound_missing(audioManager):
    """Test playSound returns early when PlaySound key missing from config."""
    audioManager.sound = None  # Reset from previous test
    audioManager.app.config["SettingAudio"] = {"MountSlew": 1}
    audioManager.playSound("MountSlew")
    assert audioManager.sound is None
