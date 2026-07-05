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
import shutil
import time
from datetime import datetime
from mw4.base import packageConfig
from mw4.gui.mainWindow.externalWindows import ExternalWindows
from mw4.gui.mainWindow.mainWindowAddons import MainWindowAddons
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtHelpers import (
    changeStyleDynamic,
    getTabAndIndex,
    getTabIndex,
    setTabAndIndex,
)
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.logic.profiles.profile import loadConfig, saveConfig
from mw4.mountcontrol.obsSite import ObsSite
from pathlib import Path
from skyfield.almanac import TWILIGHTS, dark_twilight_day
from typing import Any


class MainWindow(MWidget):
    def __init__(self, app: Any) -> None:
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.ws)
        self.setWindowTitle(f"MountWizzard4 - v{self.app.__version__}")
        self.externalWindows = ExternalWindows(self)
        self.mainWindowAddons = MainWindowAddons(self)
        self.satStatus: bool = False
        self.deviceStatGui: dict = {
            "dome": self.ui.domeConnected,
            "camera": self.ui.cameraConnected,
            "refraction": self.ui.refractionConnected,
            "plateSolve": self.ui.plateSolveConnected,
            "mount": self.ui.mountConnected,
        }
        self.smartTabs: dict = {
            "Power": {
                "statID": "power",
                "tab": self.ui.toolsTabWidget,
            },
            "Relay": {
                "statID": "relay",
                "tab": self.ui.toolsTabWidget,
            },
        }
        self.app.dReg["mount"].signals.pointDone.connect(self.updateStatusGUI)
        self.app.remoteCommand.connect(self.remoteCommand)
        self.app.dReg["plateSolve"].signals.message.connect(self.updatePlateSolveStatus)
        self.app.dReg["dome"].signals.message.connect(self.updateDomeStatus)
        self.app.dReg["camera"].signals.message.connect(self.updateCameraStatus)
        self.ui.saveConfigQuit.clicked.connect(self.quitSave)
        self.ui.loadFrom.clicked.connect(self.loadProfileGUI)
        self.ui.saveConfigAs.clicked.connect(self.saveProfileAs)
        self.ui.saveConfig.clicked.connect(self.saveProfile)
        self.app.dReg["seeingWeather"].instance.b = self.ui.label_b.property("a")
        self.app.timeMgr.update1s.connect(self.updateThreadAndOnlineStatus)
        self.app.timeMgr.update1s.connect(self.smartFunctionGui)
        self.app.timeMgr.update1s.connect(self.smartTabGui)
        self.app.timeMgr.update1s.connect(self.setEnvironDeviceStats)
        self.app.timeMgr.update1s.connect(self.updateDeviceStats)
        self.app.timeMgr.update30s.connect(self.updateTwilightAndDisk)
        self.app.colorChange.connect(self.updateColorSet)
        self.twilightText: str = ""
        self.diskFreePct: int = 0

    def initConfig(self) -> None:
        config = self.app.config.get("SettingMisc", {})
        colSet = config.get("colorSet", 0)
        Styles.colorSet = colSet

        config = self.app.config
        if "WindowMain" not in config:
            config["WindowMain"] = {}
        self.ui.profileName.setText(config.get("profileName"))
        config = config["WindowMain"]
        self.setPositionWindow(config)
        setTabAndIndex(self.ui.mainTabWidget, config, "orderMain")
        setTabAndIndex(self.ui.mountTabWidget, config, "orderMount")
        setTabAndIndex(self.ui.imagingTabWidget, config, "orderImaging")
        setTabAndIndex(self.ui.modelingTabWidget, config, "orderModeling")
        setTabAndIndex(self.ui.manageTabWidget, config, "orderManage")
        setTabAndIndex(self.ui.toolsTabWidget, config, "orderTools")
        setTabAndIndex(self.ui.satTabWidget, config, "orderSatellite")
        self.mainWindowAddons.initConfig()
        self.externalWindows.showExtendedWindows()
        self.smartTabGui()
        self.setupIcons()

    def storeConfig(self) -> None:
        config = self.app.config
        config["profileName"] = self.ui.profileName.text()
        if "WindowMain" not in config:
            config["WindowMain"] = {}
        else:
            config["WindowMain"].clear()
        config = config["WindowMain"]
        config["winPosX"] = self.pos().x()
        config["winPosY"] = self.pos().y()
        config["height"] = self.height()
        getTabAndIndex(self.ui.mainTabWidget, config, "orderMain")
        getTabAndIndex(self.ui.mountTabWidget, config, "orderMount")
        getTabAndIndex(self.ui.imagingTabWidget, config, "orderImaging")
        getTabAndIndex(self.ui.modelingTabWidget, config, "orderModeling")
        getTabAndIndex(self.ui.manageTabWidget, config, "orderManage")
        getTabAndIndex(self.ui.toolsTabWidget, config, "orderTools")
        self.externalWindows.storeConfigExtendedWindows()
        self.mainWindowAddons.storeConfig()
        self.app.storeConfig()

    def setupIcons(self) -> None:
        self.wIcon(self.ui.saveConfigAs, "save")
        self.wIcon(self.ui.loadFrom, "load")
        self.wIcon(self.ui.saveConfig, "save")
        self.wIcon(self.ui.saveConfigQuit, "save")
        self.wIcon(self.ui.stop, "hand")
        self.wIcon(self.ui.tracking, "target")
        self.wIcon(self.ui.followSat, "satellite")
        self.wIcon(self.ui.flipMount, "flip")
        self.wIcon(self.ui.setSiderealTracking, "sidereal")
        self.wIcon(self.ui.setLunarTracking, "lunar")
        self.wIcon(self.ui.setSolarTracking, "solar")
        self.wIcon(self.ui.park, "park")
        self.wIcon(self.ui.setting, "cogs")
        self.mainWindowAddons.setupIcons()

    def updateColorSet(self) -> None:
        self.setStyleSheet(self.mw4Style)
        self.setupIcons()
        self.mainWindowAddons.updateColorSet()

    def closeEvent(self, closeEvent) -> None:
        self.app.timeMgr.stop()
        changeStyleDynamic(self.ui.pauseModel, "pause", False)
        self.externalWindows.closeExtendedWindows()
        self.threadPool.waitForDone(5000)
        super().closeEvent(closeEvent)
        self.app.quit()

    def quitSave(self) -> None:
        self.app.dReg.stopDevices()
        self.saveProfile()
        self.close()

    def showWindow(self) -> None:
        self.show()
        self.setMinimumSize(self.FULL_WIDTH, self.FULL_HEIGHT)
        self.setMaximumSize(self.FULL_WIDTH, self.FULL_HEIGHT)
        self.titleBar.normButton.setVisible(False)
        self.titleBar.maxButton.setVisible(False)
        self.titleBar.windowFixed = True

    def smartFunctionGui(self) -> None:
        isMountReady = bool(self.app.dReg["mount"].stat)
        isModelingReady = all(
            bool(self.app.dReg[x].stat) for x in ["mount", "camera", "plateSolve"]
        )
        isModelRun = bool(isModelingReady and self.app.buildPoint.buildP)
        self.ui.runModelGroup.setEnabled(isModelRun)
        self.ui.runFlexure.setEnabled(isModelingReady)
        self.ui.runHysteresis.setEnabled(isModelingReady)
        self.ui.refractionGroup.setEnabled(isMountReady)
        self.ui.dsoGroup.setEnabled(isMountReady)
        self.ui.mountCommandTable.setEnabled(isMountReady)
        self.ui.mountUpdateTimeDelta.setEnabled(isMountReady)
        self.ui.mountUpdateFirmware.setEnabled(isMountReady)
        self.ui.mountDocumentation.setEnabled(isMountReady)
        self.ui.satProgDatabaseGroup.setEnabled(isMountReady)
        self.ui.cometProgDatabaseGroup.setEnabled(isMountReady)
        self.ui.asteroidProgDatabaseGroup.setEnabled(isMountReady)
        self.ui.progEarthRotationData.setEnabled(isMountReady)

    def smartTabGui(self) -> None:
        tabChanged = False
        for key, tab in self.smartTabs.items():
            tabIndex = getTabIndex(self.smartTabs[key]["tab"], key)
            tabStatus = self.smartTabs[key]["tab"].isTabVisible(tabIndex)

            stat = bool(self.app.dReg[self.smartTabs[key]["statID"]].stat)
            self.smartTabs[key]["tab"].setTabVisible(tabIndex, stat)
            actChanged = tabStatus != stat
            tabChanged = tabChanged or actChanged

        tabIndex = getTabIndex(self.ui.imagingTabWidget, "reference")
        self.ui.imagingTabWidget.setTabVisible(tabIndex, packageConfig.isReference)
        tabIndex = getTabIndex(self.ui.toolsTabWidget, "AnalyseFlexure")
        self.ui.toolsTabWidget.setTabVisible(tabIndex, packageConfig.isAnalyse)

        # redraw tabs only when a change occurred. this is necessary because
        # enable and disable do not remove tabs
        if tabChanged:
            ui = self.ui.mainTabWidget
            ui.setStyleSheet(ui.styleSheet())
            ui = self.ui.toolsTabWidget
            ui.setStyleSheet(ui.styleSheet())

    def setEnvironDeviceStats(self) -> None:
        isManual = self.ui.refracManual.isChecked()
        if self.app.dReg["mount"].setting.statusRefraction != 1:
            self.app.dReg.setStat("refraction", None)
            self.ui.refractionConnected.setText("Refraction")
        elif isManual:
            self.ui.refractionConnected.setText("Refrac Manu")
            self.app.dReg.setStat("refraction", True)
        else:
            self.ui.refractionConnected.setText("Refrac Auto")
            source = self.mainWindowAddons.addons["EnvironWeather"].refractionSource
            if source:
                isSource = self.app.dReg[source].stat
                self.app.dReg.setStat("refraction", isSource)
            else:
                self.app.dReg.setStat("refraction", False)

    def updateDeviceStats(self) -> None:
        for device, ui in self.deviceStatGui.items():
            entry = self.app.dReg[device]
            if entry is None or entry.stat is None:
                ui.setEnabled(False)
            elif entry.stat:
                changeStyleDynamic(ui, "color", "green")
                ui.setEnabled(True)
            else:
                changeStyleDynamic(ui, "color", "red")
                ui.setEnabled(True)

    def updatePlateSolveStatus(self, text: str) -> None:
        self.ui.plateSolveText.setText(text)

    def updateDomeStatus(self, text: str) -> None:
        self.ui.domeText.setText(text)

    def updateCameraStatus(self, text: str) -> None:
        self.ui.cameraText.setText(text)

    def updateControllerStatus(self, gcStatus: bool) -> None:
        self.ui.controller1.setEnabled(gcStatus)
        self.ui.controller2.setEnabled(gcStatus)
        self.ui.controller3.setEnabled(gcStatus)
        self.ui.controller4.setEnabled(gcStatus)
        self.ui.controller5.setEnabled(gcStatus)

    def updateThreadAndOnlineStatus(self) -> None:
        mode = "Online" if self.app.isOnline else "Offline"
        moon = self.ui.moonPhaseIllumination.text()
        if not self.twilightText:
            self.updateTwilightAndDisk()
        activeCount = self.threadPool.activeThreadCount()
        maxCount = self.app.MAX_THREAD_COUNT
        t = f"{mode} - {self.twilightText} - Moon: {moon}%"
        t += f" - Threads:{activeCount:2d} / {maxCount} - Disk free: {self.diskFreePct}%"
        self.ui.statusOnlineGroup.setTitle(t)

    def updateTwilightAndDisk(self) -> None:
        f = dark_twilight_day(self.app.ephemeris, self.app.dReg["mount"].location)
        self.twilightText = TWILIGHTS[int(f(self.app.dReg["mount"].obsSite.ts.now()))]
        diskUsage = shutil.disk_usage(self.app.mwGlob["workDir"])
        self.diskFreePct = int(diskUsage[2] / diskUsage[0] * 100)

    def updateTime(self) -> None:
        self.ui.timeComputer.setText(datetime.now().strftime("%H:%M:%S"))
        tzT = time.tzname[1] if time.daylight else time.tzname[0]
        t = f"TZ: {tzT}"
        self.ui.statusTimeGroup.setTitle(t)

    def updateStatusGUI(self, obs: ObsSite) -> None:
        self.ui.mountText.setText(obs.statusText())
        obsSite = self.app.dReg["mount"].obsSite
        statusFlags = (
            (self.ui.tracking, obsSite.isTracking),
            (self.ui.park, obsSite.isParked),
            (self.ui.stop, obsSite.isStopped),
        )
        for widget, isActive in statusFlags:
            changeStyleDynamic(widget, "run", isActive)

        if obsSite.isFollowingSatellite and not self.satStatus:
            self.app.playSound.emit("SatStartTracking")
            self.satStatus = True
        elif not obsSite.isFollowingSatellite:
            self.satStatus = False

    def switchProfile(self, config: dict) -> None:
        self.externalWindows.closeExtendedWindows()
        self.app.dReg.stopDevices()
        self.threadPool.waitForDone(10000)
        self.app.config = config
        topo = self.app.initConfig()
        self.app.dReg["mount"].obsSite.location = topo
        self.initConfig()

    def loadProfileGUI(self) -> None:
        folder = self.app.mwGlob["configDir"]
        loadProfilePath = MWFileDialog.getOpenFileName(
            self, "Open config file", folder, "Config files (*.yaml)"
        )
        if not loadProfilePath.is_file():
            return
        config = loadConfig(loadProfilePath)
        self.switchProfile(config)
        self.ui.profileName.setText(loadProfilePath.stem)
        self.saveProfile()
        self.msg.emit(1, "System", "Profile", f"{loadProfilePath.stem} loaded")

    def saveProfileBase(self, saveProfilePath: Path) -> None:
        if not saveProfilePath.stem:
            return
        self.storeConfig()
        saveConfig(saveProfilePath, self.app.config)
        self.ui.profileName.setText(saveProfilePath.stem)
        self.msg.emit(1, "System", "Profile", f"Saved to [{saveProfilePath.stem}]")

    def saveProfileAs(self) -> None:
        folder = self.app.mwGlob["configDir"]
        saveProfilePath = MWFileDialog.getSaveFileName(
            self, "Save config file", folder, "Config files (*.yaml)"
        )
        self.saveProfileBase(saveProfilePath)

    def saveProfile(self) -> None:
        saveProfilePath = self.app.mwGlob["configDir"] / (self.ui.profileName.text() + ".yaml")
        self.saveProfileBase(saveProfilePath)

    def remoteCommand(self, command: str) -> None:
        if command == "shutdown":
            self.quitSave()
            self.msg.emit(2, "System", "Remote", "Shutdown MW4 remotely")
        elif command == "shutdown mount":
            self.mainWindowAddons.addons["SettMount"].mountShutdown()
            self.msg.emit(2, "System", "Remote", "Shutdown MW4 remotely")
        elif command == "boot mount":
            self.mainWindowAddons.addons["SettMount"].mountBoot()
            self.msg.emit(2, "System", "Remote", "Boot Mount remotely")
