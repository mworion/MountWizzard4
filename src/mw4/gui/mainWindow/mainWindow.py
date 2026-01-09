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
# Licence APL2.0
#
###########################################################
import shutil
import time
from datetime import datetime
from mw4.base import packageConfig
from mw4.gui.mainWindow.externalWindows import ExternalWindows
from mw4.gui.mainWindow.mainWindowAddons import MainWindowAddons
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.toolsQtWidget import MWidget, changeStyleDynamic
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.logic.profiles.profile import loadProfile, saveProfile
from mw4.mountcontrol.obsSite import ObsSite
from pathlib import Path
from PySide6.QtCore import Qt
from skyfield.almanac import TWILIGHTS, dark_twilight_day


class MainWindow(MWidget):
    """ """

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
        self.satStatus: bool = False
        self.gameControllerRunning: bool = False
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
            "RelaySett": {
                "statID": "relay",
                "tab": self.ui.settingsTabWidget,
            },
        }

        self.app.mount.signals.pointDone.connect(self.updateStatusGUI)
        self.app.mount.signals.mountIsUp.connect(self.updateMountConnStat)
        self.app.remoteCommand.connect(self.remoteCommand)
        self.app.plateSolve.signals.message.connect(self.updatePlateSolveStatus)
        self.app.dome.signals.message.connect(self.updateDomeStatus)
        self.app.camera.signals.message.connect(self.updateCameraStatus)
        self.ui.saveConfigQuit.clicked.connect(self.quitSave)
        self.ui.loadFrom.clicked.connect(self.loadProfileGUI)
        self.ui.saveConfigAs.clicked.connect(self.saveProfileAs)
        self.ui.saveConfig.clicked.connect(self.saveProfile)
        self.app.seeingWeather.b = self.ui.label_b.property("a")
        self.ui.colorSet.currentIndexChanged.connect(self.updateColorSet)
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
        self.mainWindowAddons.initConfig()
        self.smartTabGui()
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
        self.externalWindows.storeConfigExtendedWindows()
        self.mainWindowAddons.storeConfig()
        self.app.storeConfig()

    def setupIcons(self) -> None:
        """ """
        self.wIcon(self.ui.saveConfigAs, "save")
        self.wIcon(self.ui.loadFrom, "load")
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
        isModelingReady = all(
            bool(self.app.deviceStat.get(x)) for x in ["mount", "camera", "plateSolve"]
        )
        isModelRun = bool(isModelingReady and self.app.data.buildP)
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
        self.ui.use10micronDef.setEnabled(isMountReady)
        self.ui.mountTabWidget.setEnabled(isMountReady)
        self.ui.telescopePointingGroup.setEnabled(isMountReady)
        self.ui.trackingGroup.setEnabled(isMountReady)
        self.ui.parkingGroup.setEnabled(isMountReady)

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

        # redraw tabs only when a change occurred. this is necessary because
        # enable and disable do not remove tabs
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
                ui.setEnabled(False)
            elif self.app.deviceStat[device]:
                changeStyleDynamic(ui, "color", "green")
                ui.setEnabled(True)
            else:
                changeStyleDynamic(ui, "color", "red")
                ui.setEnabled(True)

        isMount = self.app.deviceStat.get("mount", False)
        changeStyleDynamic(self.ui.mountOn, "run", isMount)
        changeStyleDynamic(self.ui.mountOff, "run", not isMount)
        changeStyleDynamic(self.ui.mountConnected, "run", isMount)

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
        self.ui.statusText.setText(obs.statusText())

        if self.app.mount.obsSite.status == 0:
            changeStyleDynamic(self.ui.tracking, "run", True)
        else:
            changeStyleDynamic(self.ui.tracking, "run", False)

        if self.app.mount.obsSite.status == 5:
            changeStyleDynamic(self.ui.park, "run", True)
        else:
            changeStyleDynamic(self.ui.park, "run", False)

        if self.app.mount.obsSite.status == 1:
            changeStyleDynamic(self.ui.stop, "run", True)
        else:
            changeStyleDynamic(self.ui.stop, "run", False)

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
        self.saveProfile()
        self.msg.emit(1, "System", "Profile", f"{loadProfilePath.stem} loaded")

    def saveProfileBase(self, saveProfilePath: Path) -> None:
        """ """
        if not saveProfilePath.stem:
            return
        self.storeConfig()
        saveProfile(saveProfilePath, self.app.config)
        self.ui.profile.setText(saveProfilePath.stem)
        self.msg.emit(1, "System", "Profile", f"Saved to [{saveProfilePath.stem}]")

    def saveProfileAs(self) -> None:
        """ """
        folder = self.app.mwGlob["configDir"]
        saveProfilePath = self.saveFile(
            self, "Save config file", folder, "Config files (*.cfg)", enableDir=False
        )
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
