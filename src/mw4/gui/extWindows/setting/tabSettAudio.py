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
from functools import partial
from mw4.base.audioManager import AUDIO_SOUNDS
from typing import Any


class SettAudio:
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.guiAudioList: dict = {}
        self.audioConfig = {
            "MountSlew": "soundMountSlewFinished",
            "DomeSlew": "soundDomeSlewFinished",
            "MountAlert": "soundMountAlert",
            "RunFinished": "soundRunFinished",
            "ImageSaved": "soundImageSaved",
            "ImageSolved": "soundImageSolved",
            "ConnectionLost": "soundConnectionLost",
            "SatStartTracking": "soundSatStartTracking",
        }
        self.setupAudio()

    def initConfig(self) -> None:
        config = self.app.config.get("SettingAudio", {})
        for sound, uiKey in self.audioConfig.items():
            widget = getattr(self.ui, uiKey)
            widget.setCurrentIndex(config.get(sound, 0))

    def storeConfig(self) -> None:
        self.app.config["SettingAudio"] = {}
        config = self.app.config["SettingAudio"]
        for sound, uiKey in self.audioConfig.items():
            widget = getattr(self.ui, uiKey)
            config[sound] = widget.currentIndex()

    def updateConfig(self, index: int) -> None:
        self.storeConfig()

    def testSound(self, soundOption: str) -> None:
        self.app.playSound.emit(soundOption)

    def setupAudio(self) -> None:
        for sound, uiKey in self.audioConfig.items():
            widget = getattr(self.ui, uiKey)
            for soundOption in AUDIO_SOUNDS:
                widget.addItem(soundOption)
            widget.activated.connect(self.updateConfig)
            widgetTest = getattr(self.ui, uiKey + "T")
            widgetTest.clicked.connect(partial(self.testSound, sound))
