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
from PySide6.QtMultimedia import QSoundEffect
from typing import Any


class SettAudio:
    AUDIO_SOUNDS: dict[str, QSoundEffect] = {
        "None": None,
        "Beep": ":/sound/beep.wav",
        "Beep1": ":/sound/beep1.wav",
        "Horn": ":/sound/horn.wav",
        "Beep2": ":/sound/Beep2.wav",
        "Bleep": ":/sound/Bleep.wav",
        "Pan1": ":/sound/Pan1.wav",
        "Pan2": ":/sound/Pan2.wav",
        "Alert": ":/sound/alert.wav",
        "Alarm": ":/sound/alarm.wav",
    }

    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.guiAudioList: dict = {}
        self.audioConfig = {
            "MountSlew": {
                "configKey": "soundMountSlewFinished",
                "uiWidget": "soundMountSlewFinished",
                "device": "mount",
                "signal": "slewed",
            },
            "DomeSlew": {
                "configKey": "soundDomeSlewFinished",
                "uiWidget": "soundDomeSlewFinished",
                "device": "dome",
                "signal": "slewed",
            },
            "MountAlert": {
                "configKey": "soundMountAlert",
                "uiWidget": "soundMountAlert",
                "device": "mount",
                "signal": "alert",
            },
            "RunFinished": {
                "configKey": "soundRunFinished",
                "uiWidget": "soundRunFinished",
                "device": None,
                "signal": None,
            },
            "ImageSaved": {
                "configKey": "soundImageSaved",
                "uiWidget": "soundImageSaved",
                "device": "camera",
                "signal": "saved",
            },
            "ImageSolved": {
                "configKey": "soundImageSolved",
                "uiWidget": "soundImageSolved",
                "device": "plateSolve",
                "signal": "result",
            },
            "ConnectionLost": {
                "configKey": "soundConnectionLost",
                "uiWidget": "soundConnectionLost",
                "device": "mount",
                "signal": "deviceDisconnected",
            },
            "SatStartTracking": {
                "configKey": "soundSatStartTracking",
                "uiWidget": "soundSatStartTracking",
                "device": None,
                "signal": None,
            },
        }
        self.setupAudio()
        self.setupAudioSignals()
        self.app.playSound.connect(self.playSound)

    def initConfig(self) -> None:
        config = self.app.config.get("SettingAudio", {})
        for soundKey, soundData in self.audioConfig.items():
            widget = getattr(self.ui, soundData["uiWidget"])
            configKey = soundData["configKey"]
            widget.setCurrentIndex(config.get(configKey, 0))

    def storeConfig(self) -> None:
        self.app.config["SettingAudio"] = {}
        config = self.app.config["SettingAudio"]
        for soundKey, soundData in self.audioConfig.items():
            widget = getattr(self.ui, soundData["uiWidget"])
            configKey = soundData["configKey"]
            config[configKey] = widget.currentIndex()

    def setupAudio(self) -> None:
        for soundKey, soundData in self.audioConfig.items():
            widget = getattr(self.ui, soundData["uiWidget"])
            self.guiAudioList[soundKey] = widget
            for sound in self.AUDIO_SOUNDS:
                widget.addItem(sound)

    def setupAudioSignals(self) -> None:
        for soundKey, soundData in self.audioConfig.items():
            device = soundData.get("device")
            signal = soundData.get("signal")
            if device is None or signal is None:
                continue
            deviceObj = self.app.dReg[device]
            signalObj = getattr(deviceObj.signals, signal)
            signalObj.connect(lambda value=soundKey: self.playSound(value))

    def playSound(self, value: str) -> None:
        if value not in self.guiAudioList:
            return
        sound = self.guiAudioList[value].currentText()
        if sound in self.AUDIO_SOUNDS and self.AUDIO_SOUNDS[sound]:
            QSoundEffect.play(self.AUDIO_SOUNDS[sound])
