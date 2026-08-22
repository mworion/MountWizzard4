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


def test_init_sets_app_reference(audioManager):
    """Test __init__ sets app reference."""
    assert audioManager.app is not None


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
    audioManager.app.config["SettingAudio"] = {"MountSlew": 0}
    audioManager.playSound("MountSlew")
    assert audioManager.sound is None


def test_playSound_with_valid_index(audioManager):
    """Test playSound with valid sound index creates QSoundEffect."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 1}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(
            return_value=mock_file_path
        )
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch(
            "mw4.base.audioManager.QSoundEffect"
        ) as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance

            audioManager.playSound("MountSlew")

            mock_sound_effect.assert_called_once()
            mock_sound_instance.setSource.assert_called_once()
            mock_sound_instance.setVolume.assert_called_once_with(1)
            mock_sound_instance.play.assert_called_once()


def test_playSound_uses_correct_wav_file(audioManager):
    """Test playSound uses correct wav file based on config index."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 1}
    wav_files = list(AUDIO_SOUNDS.values())
    expected_wav = wav_files[1]

    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(
            return_value=mock_file_path
        )
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("mw4.base.audioManager.files") as mock_files:
            mock_files.return_value.joinpath = mock.MagicMock(
                return_value=mock.MagicMock()
            )
            with mock.patch("mw4.base.audioManager.QSoundEffect"):
                audioManager.playSound("MountSlew")
                mock_files.return_value.joinpath.assert_called_once()
                call_args = mock_files.return_value.joinpath.call_args[0][0]
                assert expected_wav in call_args


def test_playSound_sets_volume_to_one(audioManager):
    """Test playSound sets volume to 1."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 1}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(
            return_value=mock_file_path
        )
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch(
            "mw4.base.audioManager.QSoundEffect"
        ) as mock_sound_effect:
            mock_sound_instance = mock.MagicMock()
            mock_sound_effect.return_value = mock_sound_instance
            audioManager.playSound("MountSlew")
            mock_sound_instance.setVolume.assert_called_once_with(1)


def test_playSound_plays_sound(audioManager):
    """Test playSound calls play method."""
    audioManager.app.config["SettingAudio"] = {"RunFinished": 1}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(
            return_value=mock_file_path
        )
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch(
            "mw4.base.audioManager.QSoundEffect"
        ) as mock_sound_effect:
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
            mock_as_file.return_value.__enter__ = mock.MagicMock(
                return_value=mock_file_path
            )
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
    audioManager.app.config["SettingAudio"] = {"MountSlew": 2}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(
            return_value=mock_file_path
        )
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch(
            "mw4.base.audioManager.QSoundEffect"
        ) as mock_sound_effect:
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
            mock_as_file.return_value.__enter__ = mock.MagicMock(
                return_value=mock_file_path
            )
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
            mock_as_file.return_value.__enter__ = mock.MagicMock(
                return_value=mock_file_path
            )
            mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

            with mock.patch("mw4.base.audioManager.QSoundEffect"):
                audioManager.playSound(sound)


def test_playSound_creates_sound_with_app_context(audioManager):
    """Test playSound creates QSoundEffect with app context."""
    audioManager.app.config["SettingAudio"] = {"MountSlew": 1}
    with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
        mock_file_path = mock.MagicMock()
        mock_as_file.return_value.__enter__ = mock.MagicMock(
            return_value=mock_file_path
        )
        mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch(
            "mw4.base.audioManager.QSoundEffect"
        ) as mock_sound_effect:
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
        audioManager.app.config["SettingAudio"] = {sound: 1}
        with mock.patch("mw4.base.audioManager.as_file") as mock_as_file:
            mock_file_path = mock.MagicMock()
            mock_as_file.return_value.__enter__ = mock.MagicMock(
                return_value=mock_file_path
            )
            mock_as_file.return_value.__exit__ = mock.MagicMock(return_value=False)

            with mock.patch(
                "mw4.base.audioManager.QSoundEffect"
            ) as mock_sound_effect:
                mock_sound_instance = mock.MagicMock()
                mock_sound_effect.return_value = mock_sound_instance
                audioManager.playSound(sound)
                assert audioManager.sound is not None



