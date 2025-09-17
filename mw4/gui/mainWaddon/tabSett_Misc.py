############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import base.packageConfig as pConf

# external packages
if pConf.isAvailable:
    from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QObject
import hid

# local import
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.tpool import Worker


class SettMisc(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.worker: Worker = None

        self.audioSignalsSet = dict()
        self.guiAudioList = dict()
        self.gameControllerList = dict()

        self.uiTabs = {
            "Almanac": {"cb": self.ui.showTabAlmanac, "tab": self.ui.mainTabWidget},
            "Environ": {"cb": self.ui.showTabEnviron, "tab": self.ui.mainTabWidget},
            "Satellite": {
                "cb": self.ui.showTabSatellite,
                "tab": self.ui.mainTabWidget,
            },
            "MPC": {
                "cb": self.ui.showTabMPC,
                "tab": self.ui.mainTabWidget,
            },
            "Tools": {
                "cb": self.ui.showTabTools,
                "tab": self.ui.mainTabWidget,
            },
            "Dome": {
                "cb": self.ui.showTabDome,
                "tab": self.ui.settingsTabWidget,
            },
            "ParkPos": {
                "cb": self.ui.showTabParkPos,
                "tab": self.ui.settingsTabWidget,
            },
            "Profile": {
                "cb": self.ui.showTabProfile,
                "tab": self.ui.settingsTabWidget,
            },
        }
        self.app.update3s.connect(self.populateGameControllerList)
        self.ui.gameControllerGroup.clicked.connect(self.populateGameControllerList)
        self.ui.addProfileGroup.clicked.connect(self.setAddProfileGUI)
        self.ui.showTabAlmanac.clicked.connect(self.minimizeGUI)
        self.ui.showTabEnviron.clicked.connect(self.minimizeGUI)
        self.ui.showTabSatellite.clicked.connect(self.minimizeGUI)
        self.ui.showTabMPC.clicked.connect(self.minimizeGUI)
        self.ui.showTabTools.clicked.connect(self.minimizeGUI)
        self.ui.showTabDome.clicked.connect(self.minimizeGUI)
        self.ui.showTabParkPos.clicked.connect(self.minimizeGUI)
        self.ui.showTabProfile.clicked.connect(self.minimizeGUI)

        if pConf.isAvailable:
            self.app.mount.signals.alert.connect(lambda: self.playSound("MountAlert"))
            self.app.dome.signals.slewed.connect(lambda: self.playSound("DomeSlew"))
            self.app.mount.signals.slewed.connect(lambda: self.playSound("MountSlew"))
            self.app.camera.signals.saved.connect(lambda: self.playSound("ImageSaved"))
            self.app.plateSolve.signals.result.connect(lambda: self.playSound("ImageSolved"))
            self.app.playSound.connect(self.playSound)
            self.setupAudioSignals()

    def initConfig(self):
        """ """
        config = self.app.config["mainW"]
        self.setupAudioGui()
        self.ui.tabsMovable.setChecked(config.get("tabsMovable", False))
        self.ui.resetTabOrder.setChecked(config.get("resetTabOrder", False))
        self.ui.unitTimeUTC.setChecked(config.get("unitTimeUTC", True))
        self.ui.unitTimeLocal.setChecked(config.get("unitTimeLocal", False))
        self.ui.addProfileGroup.setChecked(config.get("addProfileGroup", False))
        self.ui.showTabAlmanac.setChecked(config.get("showTabAlmanac", True))
        self.ui.showTabEnviron.setChecked(config.get("showTabEnviron", True))
        self.ui.showTabSatellite.setChecked(config.get("showTabSatellite", True))
        self.ui.showTabMPC.setChecked(config.get("showTabMPC", True))
        self.ui.showTabTools.setChecked(config.get("showTabTools", True))
        self.ui.showTabDome.setChecked(config.get("showTabDome", True))
        self.ui.showTabParkPos.setChecked(config.get("showTabParkPos", True))
        self.ui.showTabProfile.setChecked(config.get("showTabProfile", True))
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

        self.minimizeGUI()
        self.populateGameControllerList()
        self.setAddProfileGUI()
        self.ui.unitTimeUTC.toggled.emit(True)

    def storeConfig(self):
        """ """
        config = self.app.config["mainW"]
        config["tabsMovable"] = self.ui.tabsMovable.isChecked()
        config["resetTabOrder"] = self.ui.resetTabOrder.isChecked()
        config["unitTimeUTC"] = self.ui.unitTimeUTC.isChecked()
        config["unitTimeLocal"] = self.ui.unitTimeLocal.isChecked()
        config["addProfileGroup"] = self.ui.addProfileGroup.isChecked()
        config["showTabAlmanac"] = self.ui.showTabAlmanac.isChecked()
        config["showTabEnviron"] = self.ui.showTabEnviron.isChecked()
        config["showTabSatellite"] = self.ui.showTabSatellite.isChecked()
        config["showTabMPC"] = self.ui.showTabMPC.isChecked()
        config["showTabTools"] = self.ui.showTabTools.isChecked()
        config["showTabDome"] = self.ui.showTabDome.isChecked()
        config["showTabParkPos"] = self.ui.showTabParkPos.isChecked()
        config["showTabProfile"] = self.ui.showTabProfile.isChecked()
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

    def setupIcons(self):
        """ """
        self.mainW.wIcon(self.ui.installVersion, "world")
        pixmap = self.mainW.svg2pixmap(":/icon/controller.svg", self.mainW.M_PRIM)
        self.ui.controller1.setPixmap(pixmap.scaled(16, 16))
        self.ui.controller2.setPixmap(pixmap.scaled(16, 16))
        self.ui.controller3.setPixmap(pixmap.scaled(16, 16))
        self.ui.controller4.setPixmap(pixmap.scaled(16, 16))
        self.ui.controller5.setPixmap(pixmap.scaled(16, 16))
        pixmap = self.mainW.svg2pixmap(":/icon/controllerNew.svg", self.mainW.M_PRIM)
        self.ui.controllerOverview.setPixmap(pixmap)
        self.ui.controller1.setEnabled(False)
        self.ui.controller2.setEnabled(False)
        self.ui.controller3.setEnabled(False)
        self.ui.controller4.setEnabled(False)
        self.ui.controller5.setEnabled(False)

    def sendGameControllerSignals(self, act, old):
        """
        :param act:
        :param old:
        :return:
        """
        if act[0] != old[0]:
            self.app.gameABXY.emit(act[0])
        if act[1] != old[1]:
            self.app.gamePMH.emit(act[1])
        if act[2] != old[2]:
            self.app.gameDirection.emit(act[2])
        if act[3] != old[3] or act[4] != old[4]:
            self.app.game_sL.emit(act[3], act[4])
        if act[5] != old[5] or act[6] != old[6]:
            self.app.game_sR.emit(act[5], act[6])
        self.mainW.log.trace(f"GameController: {[act]}, {[old]}")
        return True

    def readGameController(self, gamepad):
        """
        :param gamepad:
        :return:
        """
        result = []
        while self.mainW.gameControllerRunning:
            try:
                data = gamepad.read(64)
            except Exception as e:
                self.mainW.gameControllerRunning = False
                self.mainW.log.warning(f"GameController error {e}")
                return []

            if len(data) == 0:
                break
            result = data
        return result

    def convertData(self, name, iR):
        """
        :param name:
        :param iR:
        :return:
        """
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
        self.mainW.log.info(f"Controller: [{name}], values: [{oR}]")
        return oR

    @staticmethod
    def isNewerData(act, old):
        """
        :param act:
        :param old:
        :return:
        """
        if len(act) == 0:
            return False
        for i, dataVal in enumerate(act):
            if dataVal != old[i]:
                break
        else:
            return False
        return True

    def workerGameController(self):
        """
        :return:
        """
        gameControllerDevice = hid.device()
        name = self.ui.gameControllerList.currentText()
        gameController = self.gameControllerList.get(name)
        if gameController is None:
            return False

        vendorId = gameController["vendorId"]
        productId = gameController["productId"]

        self.mainW.log.debug(f"GameController: [{name} {vendorId}:{productId}]")
        self.msg.emit(1, "System", "GameController", f"Starting {[name]}")
        gameControllerDevice.open(vendorId, productId)
        gameControllerDevice.set_nonblocking(True)

        reportOld = [0] * 16
        while self.mainW.gameControllerRunning:
            sleepAndEvents(100)
            report = self.readGameController(gameControllerDevice)
            if not self.isNewerData(report, reportOld):
                continue
            report = self.convertData(name, report)
            self.sendGameControllerSignals(report, reportOld)
            reportOld = report
        return True

    def startGameController(self):
        """
        :return:
        """
        self.worker = Worker(self.workerGameController)
        self.app.threadPool.start(self.worker)
        return True

    @staticmethod
    def isValidGameControllers(name):
        """
        :param name:
        :return:
        """
        validStrings = ["Controller", "Game"]
        for check in validStrings:
            if check in name:
                break
        else:
            return False
        return True

    def populateGameControllerList(self):
        """
        :return:
        """
        isController = self.ui.gameControllerGroup.isChecked()
        if not isController:
            self.mainW.gameControllerRunning = False
            return False
        if self.mainW.gameControllerRunning:
            return False

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
            return False

        self.mainW.gameControllerRunning = True
        self.startGameController()
        return True

    def setupAudioGui(self):
        """
        :return: True for test purpose
        """
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
            self.guiAudioList[itemKey].addItem("Alert")
        return True

    def setupAudioSignals(self):
        """
        :return: True for test purpose
        """
        self.audioSignalsSet["Beep"] = ":/sound/beep.wav"
        self.audioSignalsSet["Beep1"] = ":/sound/beep1.wav"
        self.audioSignalsSet["Horn"] = ":/sound/horn.wav"
        self.audioSignalsSet["Beep2"] = ":/sound/Beep2.wav"
        self.audioSignalsSet["Bleep"] = ":/sound/Bleep.wav"
        self.audioSignalsSet["Pan1"] = ":/sound/Pan1.wav"
        self.audioSignalsSet["Pan2"] = ":/sound/Pan2.wav"
        self.audioSignalsSet["Alert"] = ":/sound/alert.wav"
        self.audioSignalsSet["Alarm"] = ":/sound/alarm.wav"
        return True

    def playSound(self, value=""):
        """
        :param value:
        :return: success
        """
        listEntry = self.guiAudioList.get(value, None)
        if listEntry is None:
            return False

        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            QSoundEffect.play(self.audioSignalsSet[sound])
            return True

        else:
            return False

    def setAddProfileGUI(self):
        """
        :return:
        """
        isEnabled = self.ui.addProfileGroup.isChecked()
        self.ui.addFrom.setEnabled(isEnabled)
        self.ui.addFrom.setVisible(isEnabled)
        self.ui.profileAdd.setEnabled(isEnabled)
        self.ui.profileAdd.setVisible(isEnabled)
        return True

    def minimizeGUI(self):
        """
        :return:
        """
        for tab in self.uiTabs:
            isVisible = self.uiTabs[tab]["cb"].isChecked()
            tabIndex = self.mainW.getTabIndex(self.uiTabs[tab]["tab"], tab)
            self.uiTabs[tab]["tab"].setTabVisible(tabIndex, isVisible)
        return True
