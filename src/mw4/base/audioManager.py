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
        self.app.dReg["mount"].signals.alert.connect(lambda: self.playSound("MountAlert"))
        self.app.dReg["dome"].signals.slewed.connect(lambda: self.playSound("DomeSlew"))
        self.app.dReg["mount"].signals.slewed.connect(lambda: self.playSound("MountSlew"))
        self.app.dReg["camera"].signals.saved.connect(lambda: self.playSound("ImageSaved"))
        self.app.dReg["plateSolve"].signals.result.connect(
            lambda: self.playSound("ImageSolved")
        )

    @staticmethod
    def linearToVolumePower(x: float) -> float:
        x = max(0.0, min(1.0, x))  # Clamp between 0.0 and 1.0
        return x**3

    def playSound(self, sound: str) -> None:
        config = self.app.config.get("SettingAudio", {})
        if not config.get("PlaySound", False):
            return
        soundOptionIndex = config.get(sound, 0)
        volume = config.get("Volume", 1)
        if not soundOptionIndex:
            return
        waveName = list(AUDIO_SOUNDS.values())[soundOptionIndex]
        with as_file(files("mw4").joinpath(f"assets/sound/{waveName}")) as waveFile:
            self.sound = QSoundEffect(self.app.mainW)
            self.sound.setSource(QUrl.fromLocalFile(waveFile))
            self.sound.setVolume(self.linearToVolumePower(volume))
            self.sound.play()
