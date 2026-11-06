# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from importlib.resources import as_file, files
from mw4.base.appProtocol import AppProtocol
from PySide6.QtCore import QObject, QUrl, Slot
from PySide6.QtMultimedia import QSoundEffect

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


class AudioManager(QObject):
    def __init__(self, app: AppProtocol) -> None:
        super().__init__()
        self.app = app
        self.sound: QSoundEffect | None = None
        self.app.signals.ui.playSound.connect(self.playSound)
        self.app.dReg.mount.signals.alert.connect(self.playMountAlert)
        self.app.dReg.dome.signals.slewed.connect(self.playDomeSlew)
        self.app.dReg.mount.signals.slewed.connect(self.playMountSlew)
        self.app.dReg.camera.signals.saved.connect(self.playImageSaved)
        self.app.dReg.plateSolve.signals.result.connect(self.playImageSolved)

    @staticmethod
    def linearToVolumePower(x: float) -> float:
        x = max(0.0, min(1.0, x))  # Clamp between 0.0 and 1.0
        return x**3

    @Slot(str)
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
            self.sound = QSoundEffect(self)
            self.sound.setSource(QUrl.fromLocalFile(waveFile))
            self.sound.setVolume(self.linearToVolumePower(volume))
            self.sound.play()

    @Slot()
    def playMountAlert(self) -> None:
        self.playSound("MountAlert")

    @Slot()
    def playDomeSlew(self) -> None:
        self.playSound("DomeSlew")

    @Slot()
    def playMountSlew(self) -> None:
        self.playSound("MountSlew")

    @Slot()
    def playImageSaved(self) -> None:
        self.playSound("ImageSaved")

    @Slot()
    def playImageSolved(self) -> None:
        self.playSound("ImageSolved")
