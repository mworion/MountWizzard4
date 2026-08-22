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
from importlib.resources import as_file, files
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect
from typing import Any

AUDIO_SOUNDS: dict[str, str] = {
    "None": "",
    "Beep": "beep.wav",
    "Beep1": "beep1.wav",
    "Horn": "horn.wav",
    "Beep2": "beep2.wav",
    "Bleep": "bleep.wav",
    "Pan1": "pan1.wav",
    "Pan2": "pan2.wav",
    "Alert": "alert.wav",
    "Alarm": "alarm.wav",
}

class AudioManager:

    def __init__(self, app: Any) -> None:
        self.app = app
        self.sound: QSoundEffect | None = None
        self.app.playSound.connect(self.playSound)

    def playSound(self, sound: str) -> None:
        config = self.app.config.get("SettingAudio", {})
        soundOptionIndex = config.get(sound, 0)
        if not soundOptionIndex:
            return
        waveName = list(AUDIO_SOUNDS.values())[soundOptionIndex]
        with as_file(files("mw4").joinpath(f"assets/sound/{waveName}")) as waveFile:
            self.sound = QSoundEffect(self.app.mainW)
            self.sound.setSource(QUrl.fromLocalFile(waveFile))
            self.sound.setVolume(1)
            self.sound.play()
