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
import hid
from mw4.base.threadUtils import mainThreadSleep
from mw4.base.tpool import Worker
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.qtHelpers import svg2pixmap
from PySide6.QtMultimedia import QSoundEffect
from typing import Any


class SettGui(TabAddon):
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.worker: Worker | None = None
        self.audioSignalsSet = {}
        self.guiAudioList = {}
        self.gameControllerList = {}
        self.app.update3s.connect(self.populateGameControllerList)
        self.ui.gameControllerGroup.clicked.connect(self.populateGameControllerList)
        self.ui.colorSet.currentIndexChanged.connect(self.updateColorSet)
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
        config = self.app.config.get("SettingGui", {})
        colSet = config.get("colorSet", 0)
        self.ui.colorSet.setCurrentIndex(colSet)
        self.setupAudioGui()
        self.ui.soundMountSlewFinished.setCurrentIndex(config.get("soundMountSlewFinished", 0))
        self.ui.soundDomeSlewFinished.setCurrentIndex(config.get("soundDomeSlewFinished", 0))
        self.ui.soundMountAlert.setCurrentIndex(config.get("soundMountAlert", 0))
        self.ui.soundRunFinished.setCurrentIndex(config.get("soundRunFinished", 0))
        self.ui.soundImageSaved.setCurrentIndex(config.get("soundImageSaved", 0))
        self.ui.soundImageSolved.setCurrentIndex(config.get("soundImageSolved", 0))
        self.ui.soundConnectionLost.setCurrentIndex(config.get("soundConnectionLost", 0))
        self.ui.soundSatStartTracking.setCurrentIndex(config.get("soundSatStartTracking", 0))
        self.ui.gameControllerGroup.setChecked(config.get("gameControllerGroup", False))
        self.ui.gameControllerList.setCurrentIndex(config.get("gameControllerList", 0))
        self.populateGameControllerList()

    def storeConfig(self) -> None:
        self.app.config["SettingGui"] = {}
        config = self.app.config["SettingGui"]
        config["colorSet"] = self.ui.colorSet.currentIndex()
        config["soundMountSlewFinished"] = self.ui.soundMountSlewFinished.currentIndex()
        config["soundDomeSlewFinished"] = self.ui.soundDomeSlewFinished.currentIndex()
        config["soundMountAlert"] = self.ui.soundMountAlert.currentIndex()
        config["soundRunFinished"] = self.ui.soundRunFinished.currentIndex()
        config["soundImageSaved"] = self.ui.soundImageSaved.currentIndex()
        config["soundImageSolved"] = self.ui.soundImageSolved.currentIndex()
        config["soundConnectionLost"] = self.ui.soundConnectionLost.currentIndex()
        config["soundSatStartTracking"] = self.ui.soundSatStartTracking.currentIndex()
        config["gameControllerGroup"] = self.ui.gameControllerGroup.isChecked()
        config["gameControllerList"] = self.ui.gameControllerList.currentIndex()

    def setupIcons(self) -> None:
        pixmap = svg2pixmap("assets/icon/controller.svg", self.parentW.M_PRIM)
        self.parentW.app.mainW.ui.controller1.setPixmap(pixmap.scaled(16, 16))
        self.parentW.app.mainW.ui.controller2.setPixmap(pixmap.scaled(16, 16))
        self.parentW.app.mainW.ui.controller3.setPixmap(pixmap.scaled(16, 16))
        self.parentW.app.mainW.ui.controller4.setPixmap(pixmap.scaled(16, 16))
        self.parentW.app.mainW.ui.controller5.setPixmap(pixmap.scaled(16, 16))
        pixmap = svg2pixmap("assets/icon/controllerNew.svg", self.parentW.M_PRIM)
        self.ui.controllerOverview.setPixmap(pixmap)
        self.parentW.app.mainW.ui.controller1.setEnabled(False)
        self.parentW.app.mainW.ui.controller2.setEnabled(False)
        self.parentW.app.mainW.ui.controller3.setEnabled(False)
        self.parentW.app.mainW.ui.controller4.setEnabled(False)
        self.parentW.app.mainW.ui.controller5.setEnabled(False)

    def sendGameControllerSignals(self, act: list, old: list) -> None:
        if act[0] != old[0]:
            self.app.gameABXY.emit(act[0])
        if act[1] != old[1]:
            self.app.gamePMH.emit(act[1])
        if act[2] != old[2]:
            self.app.gameDirection.emit(act[2])
        if act[3] != old[3] or act[4] != old[4]:
            self.app.gameSL.emit(act[3], act[4])
        if act[5] != old[5] or act[6] != old[6]:
            self.app.gameSR.emit(act[5], act[6])

    def readGameController(self, gamepad: hid.device) -> list:
        result = []
        while self.parentW.app.mainW.gameControllerRunning:
            try:
                data = gamepad.read(64)
            except Exception as e:
                self.parentW.app.mainW.gameControllerRunning = False
                self.parentW.log.warning(f"GameController error {e}")
                return []

            if len(data) == 0:
                break
            result = data
        return result

    def convertData(self, name: str, iR: list) -> list:
        oR = [0, 0, 0, 0, 0, 0, 0]
        if len(iR) == 0:
            return oR
        if name == "Pro Controller":
            oR = [iR[1], iR[2], iR[3], iR[5], iR[7], iR[9], iR[11]]
        elif name == "Controller (XBOX 360 For Windows)":
            if iR[11] == 0b00011100:
                val = 0b00000110
            elif iR[11] == 0b00010100:
                val = 0b00000100
            elif iR[11] == 0b00001100:
                val = 0b00000010
            elif iR[11] == 0b00000100:
                val = 0b00000000
            else:
                val = 0b00001111
            oR = [iR[10], 0, val, iR[1], iR[3], iR[5], iR[7]]
        self.parentW.log.info(f"Controller: [{name}], values: [{oR}]")
        return oR

    @staticmethod
    def isNewerData(act: list, old: list) -> bool:
        if len(act) == 0:
            return False
        for i, dataVal in enumerate(act):
            if dataVal != old[i]:
                break
        else:
            return False
        return True

    def workerGameController(self) -> None:
        gameControllerDevice = hid.device()
        name = self.ui.gameControllerList.currentText()
        gameController = self.gameControllerList.get(name)
        if gameController is None:
            return

        vendorId = gameController["vendorId"]
        productId = gameController["productId"]

        self.parentW.log.debug(f"GameController: [{name} {vendorId}:{productId}]")
        self.msg.emit(1, "System", "GameController", f"Starting {[name]}")
        gameControllerDevice.open(vendorId, productId)
        gameControllerDevice.set_nonblocking(True)

        reportOld = [0] * 16
        while self.parentW.app.mainW.gameControllerRunning:
            mainThreadSleep(100)
            report = self.readGameController(gameControllerDevice)
            if not self.isNewerData(report, reportOld):
                continue
            report = self.convertData(name, report)
            self.sendGameControllerSignals(report, reportOld)
            reportOld = report

    def startGameController(self) -> None:
        self.worker = Worker(self.workerGameController)
        self.app.threadPool.start(self.worker)

    @staticmethod
    def isValidGameControllers(name: str) -> bool:
        validStrings = ["Controller", "Game"]
        for check in validStrings:
            if check in name:
                break
        else:
            return False
        return True

    def populateGameControllerList(self) -> None:
        isController = self.ui.gameControllerGroup.isChecked()
        if not isController:
            self.parentW.app.mainW.gameControllerRunning = False
            return
        if self.parentW.app.mainW.gameControllerRunning:
            return

        self.ui.gameControllerList.clear()
        self.gameControllerList.clear()
        for device in hid.enumerate():
            name = device["product_string"]
            if not self.isValidGameControllers(name):
                continue
            self.gameControllerList[name] = {
                "vendorId": device["vendor_id"],
                "productId": device["product_id"],
            }
            self.ui.gameControllerList.addItem(name)
            self.msg.emit(0, "System", "GameController", f"Found {[name]}")

        if len(self.gameControllerList) == 0:
            return

        self.parentW.app.mainW.gameControllerRunning = True
        self.startGameController()

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

    def updateColorSet(self) -> None:
        Styles.colorSet = self.ui.colorSet.currentIndex()
        self.parentW.setStyleSheet(self.parentW.mw4Style)
        self.setupIcons()
        self.app.colorChange.emit()
