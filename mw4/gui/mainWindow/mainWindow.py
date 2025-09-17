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
import time
from datetime import datetime
import shutil
from pathlib import Path

# external packages
from PySide6.QtCore import Qt
from skyfield.almanac import dark_twilight_day, TWILIGHTS

# local import
from base import packageConfig
from gui.styles.styles import Styles
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWindow.externalWindows import ExternalWindows
from gui.mainWindow.mainWindowAddons import MainWindowAddons
from logic.profiles.profile import loadProfile, saveProfile, blendProfile
from mountcontrol.obsSite import ObsSite
from gui.utilities.toolsQtWidget import changeStyleDynamic


class MainWindow(MWidget):
    """ """

    __all__ = ["MainWindow"]

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"MountWizzard4 - v{self.app.__version__}")
        self.activateWindow()

        self.externalWindows = ExternalWindows(self)
        self.mainWindowAddons = MainWindowAddons(self)

        self.satStatus = False
        self.gameControllerRunning = False
        self.deviceStatGui = {
            "dome": self.ui.domeConnected,
            "camera": self.ui.cameraConnected,
            "refraction": self.ui.refractionConnected,
            "plateSolve": self.ui.plateSolveConnected,
            "mount": self.ui.mountConnected,
        }
        self.smartTabs = {
            "Power": {
                "statID": "power",
                "tab": self.ui.toolsTabWidget,
            },
            "Relay": {
                "statID": "relay",
                "tab": self.ui.toolsTabWidget,
            },
            "RelaySett": {
                "statID": "relay",
                "tab": self.ui.settingsTabWidget,
            },
        }

        self.app.mount.signals.pointDone.connect(self.updateStatusGUI)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)
        self.app.remoteCommand.connect(self.remoteCommand)
        self.app.plateSolve.signals.message.connect(self.updatePlateSolveStatus)
        self.app.dome.signals.message.connect(self.updateDomeStatus)
        self.app.camera.signals.message.connect(self.updateCameraStatus)
        self.ui.saveConfigQuit.clicked.connect(self.quitSave)
        self.ui.loadFrom.clicked.connect(self.loadProfileGUI)
        self.ui.addFrom.clicked.connect(self.addProfileGUI)
        self.ui.saveConfigAs.clicked.connect(self.saveProfileAs)
        self.ui.saveConfig.clicked.connect(self.saveProfile)
        self.app.seeingWeather.b = self.ui.label_b.property("a")
        self.ui.colorSet.currentIndexChanged.connect(self.updateColorSet)
        self.ui.tabsMovable.clicked.connect(self.enableTabsMovable)
        self.app.update1s.connect(self.updateTime)
        self.app.update1s.connect(self.updateControllerStatus)
        self.app.update1s.connect(self.updateThreadAndOnlineStatus)
        self.app.update1s.connect(self.smartFunctionGui)
        self.app.update1s.connect(self.smartTabGui)
        self.app.update1s.connect(self.setEnvironDeviceStats)
        self.app.update1s.connect(self.updateDeviceStats)

    def initConfig(self) -> None:
        """ """
        config = self.app.config
        if "mainW" not in config:
            config["mainW"] = {}

        colSet = config.get("colorSet", 0)
        Styles.colorSet = colSet
        self.ui.colorSet.setCurrentIndex(colSet)
        self.setStyleSheet(self.mw4Style)
        self.ui.profile.setText(config.get("profileName"))
        config = config["mainW"]
        self.positionWindow(config)
        self.setTabAndIndex(self.ui.mainTabWidget, config, "orderMain")
        self.setTabAndIndex(self.ui.mountTabWidget, config, "orderMount")
        self.setTabAndIndex(self.ui.imagingTabWidget, config, "orderImaging")
        self.setTabAndIndex(self.ui.modelingTabWidget, config, "orderModeling")
        self.setTabAndIndex(self.ui.manageTabWidget, config, "orderManage")
        self.setTabAndIndex(self.ui.settingsTabWidget, config, "orderSettings")
        self.setTabAndIndex(self.ui.toolsTabWidget, config, "orderTools")
        self.setTabAndIndex(self.ui.satTabWidget, config, "orderSatellite")
        changeStyleDynamic(self.ui.mountConnected, "color", "gray")
        self.mainWindowAddons.initConfig()
        self.smartTabGui()
        self.enableTabsMovable()
        self.setupIcons()
        self.show()
        self.externalWindows.showExtendedWindows()

    def storeConfig(self) -> None:
        """ """
        config = self.app.config
        config["colorSet"] = self.ui.colorSet.currentIndex()
        config["profileName"] = self.ui.profile.text()
        if "mainW" not in config:
            config["mainW"] = {}
        else:
            config["mainW"].clear()
        config = config["mainW"]

        config["winPosX"] = self.pos().x()
        config["winPosY"] = self.pos().y()
        self.getTabAndIndex(self.ui.mainTabWidget, config, "orderMain")
        self.getTabAndIndex(self.ui.mountTabWidget, config, "orderMount")
        self.getTabAndIndex(self.ui.imagingTabWidget, config, "orderImaging")
        self.getTabAndIndex(self.ui.modelingTabWidget, config, "orderModeling")
        self.getTabAndIndex(self.ui.manageTabWidget, config, "orderManage")
        self.getTabAndIndex(self.ui.settingsTabWidget, config, "orderSettings")
        self.getTabAndIndex(self.ui.toolsTabWidget, config, "orderTools")
        self.getTabAndIndex(self.ui.satTabWidget, config, "orderSatellite")
        self.externalWindows.storeConfigExtendedWindows()
        self.mainWindowAddons.storeConfig()
        self.app.storeConfig()

    def setupIcons(self) -> None:
        """ """
        self.wIcon(self.ui.saveConfigAs, "save")
        self.wIcon(self.ui.loadFrom, "load")
        self.wIcon(self.ui.addFrom, "load")
        self.wIcon(self.ui.saveConfig, "save")
        self.wIcon(self.ui.saveConfigQuit, "save")
        self.wIcon(self.ui.mountOn, "power-on")
        self.wIcon(self.ui.mountOff, "power-off")
        self.wIcon(self.ui.stop, "hand")
        self.wIcon(self.ui.tracking, "target")
        self.wIcon(self.ui.followSat, "satellite")
        self.wIcon(self.ui.flipMount, "flip")
        self.wIcon(self.ui.setSiderealTracking, "sidereal")
        self.wIcon(self.ui.setLunarTracking, "lunar")
        self.wIcon(self.ui.setSolarTracking, "solar")
        self.wIcon(self.ui.park, "park")
        self.mainWindowAddons.setupIcons()

    def updateColorSet(self) -> None:
        """ """
        Styles.colorSet = self.ui.colorSet.currentIndex()
        self.setStyleSheet(self.mw4Style)
        self.setupIcons()
        self.mainWindowAddons.updateColorSet()
        self.app.colorChange.emit()

    def enableTabsMovable(self) -> None:
        """ """
        isMovable = self.ui.tabsMovable.isChecked()
        self.ui.mainTabWidget.setMovable(isMovable)
        self.ui.mountTabWidget.setMovable(isMovable)
        self.ui.imagingTabWidget.setMovable(isMovable)
        self.ui.modelingTabWidget.setMovable(isMovable)
        self.ui.manageTabWidget.setMovable(isMovable)
        self.ui.settingsTabWidget.setMovable(isMovable)
        self.ui.toolsTabWidget.setMovable(isMovable)
        self.ui.satTabWidget.setMovable(isMovable)
        self.app.tabsMovable.emit(isMovable)

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.gameControllerRunning = False
        self.app.timer0_1s.stop()
        changeStyleDynamic(self.ui.pauseModel, "pause", False)
        self.externalWindows.closeExtendedWindows()
        self.mainWindowAddons.addons["SettDevice"].stopDrivers()
        self.threadPool.waitForDone(10000)
        super().closeEvent(closeEvent)
        self.app.quit()

    def quitSave(self) -> None:
        """ """
        self.saveProfile()
        self.close()

    def smartFunctionGui(self) -> None:
        """ """
        isMountReady = bool(self.app.deviceStat.get("mount"))
        isDomeReady = bool(self.app.deviceStat.get("dome"))
        isModelingReady = all(
            bool(self.app.deviceStat.get(x)) for x in ["mount", "camera", "plateSolve"]
        )
        isPause = self.ui.pauseModel.property("pause")

        if isModelingReady and self.app.data.buildP and not isPause:
            self.ui.runModel.setEnabled(True)
        else:
            self.ui.runModel.setEnabled(False)

        if isModelingReady:
            self.ui.runModel.setEnabled(True)
            self.ui.runFlexure.setEnabled(True)
            self.ui.runHysteresis.setEnabled(True)
        else:
            self.ui.runModel.setEnabled(False)
            self.ui.runFlexure.setEnabled(False)
            self.ui.runHysteresis.setEnabled(False)

        if isMountReady:
            self.ui.refractionGroup.setEnabled(True)
            self.ui.dsoGroup.setEnabled(True)
            self.ui.mountCommandTable.setEnabled(True)
            self.ui.mountUpdateTimeDelta.setEnabled(True)
            self.ui.mountUpdateFirmware.setEnabled(True)
            self.ui.mountDocumentation.setEnabled(True)
            self.ui.satProgDatabaseGroup.setEnabled(True)
            self.ui.cometProgDatabaseGroup.setEnabled(True)
            self.ui.asteroidProgDatabaseGroup.setEnabled(True)
            self.ui.progEarthRotationData.setEnabled(True)
            self.ui.use10micronDef.setEnabled(True)
        else:
            self.ui.dsoGroup.setEnabled(False)
            self.ui.refractionGroup.setEnabled(False)
            self.ui.mountCommandTable.setEnabled(False)
            self.ui.mountUpdateTimeDelta.setEnabled(False)
            self.ui.mountUpdateFirmware.setEnabled(False)
            self.ui.mountDocumentation.setEnabled(False)
            self.ui.satProgDatabaseGroup.setEnabled(False)
            self.ui.cometProgDatabaseGroup.setEnabled(False)
            self.ui.asteroidProgDatabaseGroup.setEnabled(False)
            self.ui.progEarthRotationData.setEnabled(False)
            self.ui.use10micronDef.setEnabled(False)

        if isDomeReady and isMountReady:
            self.ui.useDomeAz.setEnabled(True)
        else:
            self.ui.useDomeAz.setEnabled(False)

    def smartTabGui(self) -> None:
        """ """
        tabChanged = False
        for key, tab in self.smartTabs.items():
            tabIndex = self.getTabIndex(self.smartTabs[key]["tab"], key)
            tabStatus = self.smartTabs[key]["tab"].isTabVisible(tabIndex)

            stat = bool(self.app.deviceStat.get(self.smartTabs[key]["statID"]))
            self.smartTabs[key]["tab"].setTabVisible(tabIndex, stat)
            actChanged = tabStatus != stat
            tabChanged = tabChanged or actChanged

        tabIndex = self.getTabIndex(self.ui.imagingTabWidget, "reference")
        self.ui.imagingTabWidget.setTabVisible(tabIndex, packageConfig.isReference)
        tabIndex = self.getTabIndex(self.ui.toolsTabWidget, "AnalyseFlexure")
        self.ui.toolsTabWidget.setTabVisible(tabIndex, packageConfig.isAnalyse)

        # redraw tabs only when a change occurred. this is necessary, because
        # enable and disable does not remove tabs
        if tabChanged:
            ui = self.ui.mainTabWidget
            ui.setStyleSheet(ui.styleSheet())
            ui = self.ui.toolsTabWidget
            ui.setStyleSheet(ui.styleSheet())

    def setEnvironDeviceStats(self) -> None:
        """ """
        refracOn = self.app.mount.setting.statusRefraction == 1
        isManual = self.ui.refracManual.isChecked()
        isTabEnabled = self.ui.showTabEnviron.isChecked()
        if not refracOn or not isTabEnabled:
            self.app.deviceStat["refraction"] = None
            self.ui.refractionConnected.setText("Refraction")
        elif isManual:
            self.ui.refractionConnected.setText("Refrac Manu")
            self.app.deviceStat["refraction"] = True
        else:
            self.ui.refractionConnected.setText("Refrac Auto")
            isSource = self.app.deviceStat.get(
                self.mainWindowAddons.addons["EnvironWeather"].refractionSource, False
            )
            self.app.deviceStat["refraction"] = isSource

    def updateDeviceStats(self) -> None:
        """ """
        for device, ui in self.deviceStatGui.items():
            if self.app.deviceStat.get(device) is None:
                changeStyleDynamic(ui, "color", "gray")
            elif self.app.deviceStat[device]:
                changeStyleDynamic(ui, "color", "green")
            else:
                changeStyleDynamic(ui, "color", "red")

        isMount = self.app.deviceStat.get("mount", False)
        changeStyleDynamic(self.ui.mountOn, "running", isMount)
        changeStyleDynamic(self.ui.mountOff, "running", not isMount)

    def updateMountConnStat(self, status: bool) -> None:
        """ """
        self.app.deviceStat["mount"] = status

    def updatePlateSolveStatus(self, text: str) -> None:
        """ """
        self.ui.plateSolveText.setText(text)

    def updateDomeStatus(self, text: str) -> None:
        """ """
        self.ui.domeText.setText(text)

    def updateCameraStatus(self, text: str) -> None:
        """ """
        self.ui.cameraText.setText(text)

    def updateControllerStatus(self) -> None:
        """ """
        gcStatus = self.gameControllerRunning
        self.ui.controller1.setEnabled(gcStatus)
        self.ui.controller2.setEnabled(gcStatus)
        self.ui.controller3.setEnabled(gcStatus)
        self.ui.controller4.setEnabled(gcStatus)
        self.ui.controller5.setEnabled(gcStatus)

    def updateThreadAndOnlineStatus(self) -> None:
        """ """
        mode = "Online" if self.ui.isOnline.isChecked() else "Offline"
        moon = self.ui.moonPhaseIllumination.text()

        f = dark_twilight_day(self.app.ephemeris, self.app.mount.obsSite.location)
        twilight = TWILIGHTS[int(f(self.app.mount.obsSite.ts.now()))]

        activeCount = self.threadPool.activeThreadCount()

        diskUsage = shutil.disk_usage(self.app.mwGlob["workDir"])
        free = int(diskUsage[2] / diskUsage[0] * 100)

        t = f"{mode} - {twilight} - Moon: {moon}%"
        t += f" - Threads:{activeCount:2d} / 30 - Disk free: {free}%"
        self.ui.statusOnline.setTitle(t)

    def updateTime(self) -> None:
        """ """
        self.ui.timeComputer.setText(datetime.now().strftime("%H:%M:%S"))
        tzT = time.tzname[1] if time.daylight else time.tzname[0]
        t = f"TZ: {tzT}"
        self.ui.statusTime.setTitle(t)

    def updateStatusGUI(self, obs: ObsSite) -> None:
        """ """
        if obs.statusText() is not None:
            self.ui.statusText.setText(obs.statusText())
        else:
            self.ui.statusText.setText("-")

        if self.app.mount.obsSite.status == 0:
            changeStyleDynamic(self.ui.tracking, "running", True)
        else:
            changeStyleDynamic(self.ui.tracking, "running", False)

        if self.app.mount.obsSite.status == 5:
            changeStyleDynamic(self.ui.park, "running", True)
        else:
            changeStyleDynamic(self.ui.park, "running", False)

        if self.app.mount.obsSite.status == 1:
            changeStyleDynamic(self.ui.stop, "running", True)
        else:
            changeStyleDynamic(self.ui.stop, "running", False)

        if self.app.mount.obsSite.status == 10 and not self.satStatus:
            self.app.playSound.emit("SatStartTracking")
            self.satStatus = True
        elif self.app.mount.obsSite.status != 10:
            self.satStatus = False

    def switchProfile(self, config: dict) -> None:
        """ """
        self.externalWindows.closeExtendedWindows()
        self.mainWindowAddons.addons["SettDevice"].stopDrivers()
        self.threadPool.waitForDone(10000)
        self.app.config = config
        topo = self.app.initConfig()
        self.app.mount.obsSite.location = topo
        self.initConfig()

    def loadProfileGUI(self) -> None:
        """ """
        folder = self.app.mwGlob["configDir"]
        loadProfilePath = self.openFile(
            self, "Open config file", folder, "Config files (*.cfg)"
        )
        if not loadProfilePath.is_file():
            return
        config = loadProfile(loadProfilePath)
        self.switchProfile(config)
        self.ui.profile.setText(loadProfilePath.stem)
        self.msg.emit(1, "System", "Profile", f"{loadProfilePath.stem} loaded")

    def addProfileGUI(self) -> None:
        """ """
        config = self.app.config
        folder = self.app.mwGlob["configDir"]
        loadProfilePath = self.openFile(
            self, "Open add-on config file", folder, "Config files (*.cfg)"
        )
        if not loadProfilePath.is_file():
            self.ui.profileAdd.setText("-")
            return

        configAdd = loadProfile(loadProfilePath)
        config = blendProfile(config, configAdd)
        self.switchProfile(config)
        self.ui.profileAdd.setText(loadProfilePath.stem)
        profile = self.ui.profile.text()
        self.msg.emit(1, "System", "Profile", f"Base: {profile}")
        self.msg.emit(1, "System", "Profile", f"Add : {loadProfilePath.name}")

    def saveProfileBase(self, saveProfilePath: Path) -> None:
        """ """
        self.storeConfig()
        saveProfile(saveProfilePath, self.app.config)
        self.ui.profile.setText(saveProfilePath.stem)
        self.msg.emit(1, "System", "Profile", f"saved {saveProfilePath.stem}")
        self.ui.profileAdd.setText("-")

    def saveProfileAs(self) -> None:
        """ """
        folder = self.app.mwGlob["configDir"]
        saveProfilePath = self.saveFile(
            self, "Save config file", folder, "Config files (*.cfg)", enableDir=False
        )
        if not saveProfilePath.name:
            return
        self.saveProfileBase(saveProfilePath)

    def saveProfile(self) -> None:
        """ """
        saveProfilePath = self.app.mwGlob["configDir"] / (self.ui.profile.text() + ".cfg")
        self.saveProfileBase(saveProfilePath)

    def remoteCommand(self, command: str) -> None:
        """ """
        if command == "shutdown":
            self.quitSave()
            self.msg.emit(2, "System", "Remote", "Shutdown MW4 remotely")
        elif command == "shutdown mount":
            self.mainWindowAddons.addons["SettMount"].mountShutdown()
            self.msg.emit(2, "System", "Remote", "Shutdown MW4 remotely")
        elif command == "boot mount":
            self.mainWindowAddons.addons["SettMount"].mountBoot()
            self.msg.emit(2, "System", "Remote", "Boot Mount remotely")
