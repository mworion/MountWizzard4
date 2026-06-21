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
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.audioSignalsSet = {}
        self.guiAudioList: dict = {}
        self.setupAudioSignals()
        self.app.dReg["mount"].signals.alert.connect(lambda: self.playSound("MountAlert"))
        self.app.dReg["dome"].signals.slewed.connect(lambda: self.playSound("DomeSlew"))
        self.app.dReg["mount"].signals.slewed.connect(lambda: self.playSound("MountSlew"))
        self.app.dReg["camera"].signals.saved.connect(lambda: self.playSound("ImageSaved"))
        self.app.dReg["plateSolve"].signals.result.connect(
            lambda: self.playSound("ImageSolved")
        )
        self.app.playSound.connect(self.playSound)

    def initConfig(self) -> None:
        config = self.app.config.get("SettingAudio", {})
        self.setupAudioGui()
        self.ui.soundMountSlewFinished.setCurrentIndex(config.get("soundMountSlewFinished", 0))
        self.ui.soundDomeSlewFinished.setCurrentIndex(config.get("soundDomeSlewFinished", 0))
        self.ui.soundMountAlert.setCurrentIndex(config.get("soundMountAlert", 0))
        self.ui.soundRunFinished.setCurrentIndex(config.get("soundRunFinished", 0))
        self.ui.soundImageSaved.setCurrentIndex(config.get("soundImageSaved", 0))
        self.ui.soundImageSolved.setCurrentIndex(config.get("soundImageSolved", 0))
        self.ui.soundConnectionLost.setCurrentIndex(config.get("soundConnectionLost", 0))
        self.ui.soundSatStartTracking.setCurrentIndex(config.get("soundSatStartTracking", 0))

    def storeConfig(self) -> None:
        self.app.config["SettingAudio"] = {}
        config = self.app.config["SettingAudio"]
        config["soundMountSlewFinished"] = self.ui.soundMountSlewFinished.currentIndex()
        config["soundDomeSlewFinished"] = self.ui.soundDomeSlewFinished.currentIndex()
        config["soundMountAlert"] = self.ui.soundMountAlert.currentIndex()
        config["soundRunFinished"] = self.ui.soundRunFinished.currentIndex()
        config["soundImageSaved"] = self.ui.soundImageSaved.currentIndex()
        config["soundImageSolved"] = self.ui.soundImageSolved.currentIndex()
        config["soundConnectionLost"] = self.ui.soundConnectionLost.currentIndex()
        config["soundSatStartTracking"] = self.ui.soundSatStartTracking.currentIndex()

    def setupAudioGui(self) -> None:
        self.guiAudioList["MountSlew"] = self.ui.soundMountSlewFinished
        self.guiAudioList["DomeSlew"] = self.ui.soundDomeSlewFinished
        self.guiAudioList["MountAlert"] = self.ui.soundMountAlert
        self.guiAudioList["RunFinished"] = self.ui.soundRunFinished
        self.guiAudioList["ImageSaved"] = self.ui.soundImageSaved
        self.guiAudioList["ConnectionLost"] = self.ui.soundConnectionLost
        self.guiAudioList["SatStartTracking"] = self.ui.soundSatStartTracking
        self.guiAudioList["ImageSolved"] = self.ui.soundImageSolved

        for itemKey, itemValue in self.guiAudioList.items():
            self.guiAudioList[itemKey].addItem("None")
            self.guiAudioList[itemKey].addItem("Beep")
            self.guiAudioList[itemKey].addItem("Beep1")
            self.guiAudioList[itemKey].addItem("Beep2")
            self.guiAudioList[itemKey].addItem("Bleep")
            self.guiAudioList[itemKey].addItem("Pan1")
            self.guiAudioList[itemKey].addItem("Pan2")
            self.guiAudioList[itemKey].addItem("Horn")
            self.guiAudioList[itemKey].addItem("Alarm")

    def setupAudioSignals(self) -> None:
        self.audioSignalsSet["Beep"] = ":/sound/beep.wav"
        self.audioSignalsSet["Beep1"] = ":/sound/beep1.wav"
        self.audioSignalsSet["Horn"] = ":/sound/horn.wav"
        self.audioSignalsSet["Beep2"] = ":/sound/Beep2.wav"
        self.audioSignalsSet["Bleep"] = ":/sound/Bleep.wav"
        self.audioSignalsSet["Pan1"] = ":/sound/Pan1.wav"
        self.audioSignalsSet["Pan2"] = ":/sound/Pan2.wav"
        self.audioSignalsSet["Alert"] = ":/sound/alert.wav"
        self.audioSignalsSet["Alarm"] = ":/sound/alarm.wav"

    def playSound(self, value: str) -> None:
        if value not in self.guiAudioList:
            return
        sound = self.guiAudioList[value].currentText()
        if sound in self.audioSignalsSet:
            QSoundEffect.play(self.audioSignalsSet[sound])
