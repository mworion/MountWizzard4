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
from mw4.gui.utilities.qtHelpers import svg2pixmap
from typing import Any


class SettGui(TabAddon):
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.worker: Worker | None = None
        self.gameControllerList: dict = {}
        self.gameControllerRunning: bool = False
        self.ui.gameControllerGroup.clicked.connect(self.switchStatusGameController)
        self.ui.colorSet.currentIndexChanged.connect(self.updateColorSet)

    def initConfig(self) -> None:
        config = self.app.config.get("SettingGui", {})
        colSet = config.get("colorSet", 0)
        self.ui.colorSet.setCurrentIndex(colSet)
        self.ui.soundSatStartTracking.setCurrentIndex(config.get("soundSatStartTracking", 0))
        self.ui.gameControllerGroup.setChecked(config.get("gameControllerGroup", False))
        self.ui.gameControllerList.setCurrentIndex(config.get("gameControllerList", 0))
        self.populateGameControllerList()

    def storeConfig(self) -> None:
        self.app.config["SettingGui"] = {}
        config = self.app.config["SettingGui"]
        config["colorSet"] = self.ui.colorSet.currentIndex()
        config["gameControllerGroup"] = self.ui.gameControllerGroup.isChecked()
        config["gameControllerList"] = self.ui.gameControllerList.currentIndex()

    def setupIcons(self) -> None:
        pixmap = svg2pixmap("assets/icon/controllerNew.svg", self.parentW.M_PRIM)
        self.ui.controllerOverview.setPixmap(pixmap)

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
        while self.gameControllerRunning:
            try:
                data = gamepad.read(64)
            except Exception as e:
                self.gameControllerRunning = False
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
        while self.gameControllerRunning:
            mainThreadSleep(100)
            report = self.readGameController(gameControllerDevice)
            if not self.isNewerData(report, reportOld):
                continue
            report = self.convertData(name, report)
            self.sendGameControllerSignals(report, reportOld)
            reportOld = report

    def startGameController(self) -> None:
        self.gameControllerRunning = True
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
        self.app.gameControllerIsRunning.emit(True)
        self.startGameController()

    def switchStatusGameController(self) -> None:
        isController = self.ui.gameControllerGroup.isChecked()
        if isController and not self.gameControllerRunning:
            self.populateGameControllerList()
        if not isController:
            self.gameControllerRunning = False
            self.app.gameControllerIsRunning.emit(False)
