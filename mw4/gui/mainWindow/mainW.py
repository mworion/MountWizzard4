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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import time
from datetime import datetime
import shutil

# external packages
from PySide6.QtCore import Qt
from PySide6.QtGui import QTransform
from skyfield.almanac import dark_twilight_day, TWILIGHTS

# local import
from base import packageConfig
from gui.mainWindow.externalWindows import ExternalWindows
from gui.mainWindow.externalMixins import ExternalMixins
from gui.utilities.stylesQtCss import Styles
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from logic.profiles.profile import loadProfile, saveProfile, blendProfile


class MainWindow(MWidget):
    """
    the main window class handles the main menu as well as the show and no show
    part of any other window. all necessary processing for functions of that gui
    will be linked to this class. therefore, window classes will have a
    threadpool for managing async processing if needed.
    """
    __all__ = ['MainWindow']

    def __init__(self, app):
        colSet = app.config.get('colorSet', 0)
        Styles.colorSet = colSet
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.extWindows = ExternalWindows(self)
        self.extMixin = ExternalMixins(self)
        self.satStatus = False
        self.gameControllerRunning = False
        self.setWindowTitle(f'MountWizzard4 - v{self.app.__version__}')
        self.deviceStatGui = {
            'dome': self.ui.domeConnected,
            'camera': self.ui.cameraConnected,
            'refraction': self.ui.refractionConnected,
            'plateSolve': self.ui.plateSolveConnected,
            'mount': self.ui.mountConnected,
        }
        self.mwSuper('__init__')
        self.extMixin.initConfig()
        self.app.mount.signals.pointDone.connect(self.updateStatusGUI)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)
        self.app.mount.signals.settingDone.connect(self.updateMountWeatherStat)
        self.app.remoteCommand.connect(self.remoteCommand)
        self.app.plateSolve.signals.message.connect(self.updatePlateSolveStatus)
        self.app.dome.signals.message.connect(self.updateDomeStatus)
        self.app.camera.signals.message.connect(self.updateCameraStatus)
        self.ui.saveConfigQuit.clicked.connect(self.quitSave)
        self.ui.loadFrom.clicked.connect(self.loadProfileGUI)
        self.ui.addFrom.clicked.connect(self.addProfileGUI)
        self.ui.saveConfigAs.clicked.connect(self.saveConfigAs)
        self.ui.saveConfig.clicked.connect(self.saveConfig)
        self.app.seeingWeather.b = self.ui.label_b.property('a')

        self.initConfig()
        self.ui.colorSet.currentIndexChanged.connect(self.refreshColorSet)
        self.extWindows.showExtendedWindows()
        self.activateWindow()

        self.ui.tabsMovable.clicked.connect(self.enableTabsMovable)
        self.app.update1s.connect(self.updateTime)
        self.app.update1s.connect(self.updateControllerStatus)
        self.app.update1s.connect(self.updateThreadAndOnlineStatus)
        self.app.update1s.connect(self.updateWindowsStats)
        self.app.update1s.connect(self.smartFunctionGui)
        self.app.update1s.connect(self.smartTabGui)
        self.app.update1s.connect(self.updateWindowsStats)
        self.app.update1s.connect(self.setEnvironDeviceStats)
        self.app.update1s.connect(self.updateDeviceStats)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        self.ui.profile.setText(config.get('profileName'))
        colSet = config.get('colorSet', 0)
        Styles.colorSet = colSet
        self.ui.colorSet.setCurrentIndex(colSet)
        self.setStyleSheet(self.mw4Style)

        if 'mainW' not in config:
            config['mainW'] = {}
        config = config['mainW']

        self.positionWindow(config)
        self.mwSuper('initConfig')
        self.setTabAndIndex(self.ui.mainTabWidget, config, 'orderMain')
        self.setTabAndIndex(self.ui.mountTabWidget, config, 'orderMount')
        self.setTabAndIndex(self.ui.imagingTabWidget, config, 'orderImaging')
        self.setTabAndIndex(self.ui.modelingTabWidget, config, 'orderModeling')
        self.setTabAndIndex(self.ui.manageTabWidget, config, 'orderManage')
        self.setTabAndIndex(self.ui.settingsTabWidget, config, 'orderSettings')
        self.setTabAndIndex(self.ui.toolsTabWidget, config, 'orderTools')
        self.setTabAndIndex(self.ui.satTabWidget, config, 'orderSatellite')

        self.changeStyleDynamic(self.ui.mountConnected, 'color', 'gray')
        self.smartTabGui()
        self.enableTabsMovable()
        self.setupIcons()
        self.show()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        config['colorSet'] = self.ui.colorSet.currentIndex()
        config['profileName'] = self.ui.profile.text()
        if 'mainW' not in config:
            config['mainW'] = {}
        else:
            config['mainW'].clear()
        config = config['mainW']

        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        self.getTabAndIndex(self.ui.mainTabWidget, config, 'orderMain')
        self.getTabAndIndex(self.ui.mountTabWidget, config, 'orderMount')
        self.getTabAndIndex(self.ui.imagingTabWidget, config, 'orderImaging')
        self.getTabAndIndex(self.ui.modelingTabWidget, config, 'orderModeling')
        self.getTabAndIndex(self.ui.manageTabWidget, config, 'orderManage')
        self.getTabAndIndex(self.ui.settingsTabWidget, config, 'orderSettings')
        self.getTabAndIndex(self.ui.toolsTabWidget, config, 'orderTools')
        self.getTabAndIndex(self.ui.satTabWidget, config, 'orderSatellite')
        self.mwSuper('storeConfig')
        self.extMixin.storeConfig()
        self.extWindows.storeConfig()
        return True

    def enableTabsMovable(self):
        """
        :return: True for test purpose
        """
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
        return True

    def closeEvent(self, closeEvent):
        """
        :return:    nothing
        """
        self.gameControllerRunning = False
        self.app.timer0_1s.stop()
        self.changeStyleDynamic(self.ui.pauseModel, 'pause', False)
        self.extWindows.closeExtendedWindows()
        self.stopDrivers()
        self.threadPool.waitForDone(5000)
        super().closeEvent(closeEvent)
        self.app.quit()

    def quitSave(self):
        """
        :return:    true for test purpose
        """
        self.app.storeConfig()
        self.saveConfig()
        self.close()
        return True

    def setupIcons(self) -> None:
        """
        """
        self.wIcon(self.ui.saveConfigAs, 'save')
        self.wIcon(self.ui.loadFrom, 'load')
        self.wIcon(self.ui.addFrom, 'load')
        self.wIcon(self.ui.saveConfig, 'save')
        self.wIcon(self.ui.saveConfigQuit, 'save')
        self.wIcon(self.ui.mountOn, 'power-on')
        self.wIcon(self.ui.mountOff, 'power-off')
        self.wIcon(self.ui.stop, 'hand')
        self.wIcon(self.ui.tracking, 'target')
        self.wIcon(self.ui.followSat, 'satellite')
        self.wIcon(self.ui.flipMount, 'flip')
        self.wIcon(self.ui.setSiderealTracking, 'sidereal')
        self.wIcon(self.ui.setLunarTracking, 'lunar')
        self.wIcon(self.ui.setSolarTracking, 'solar')
        self.wIcon(self.ui.park, 'park')

    def updateMountConnStat(self, status):
        """
        updateMountConnStat show the connection status of the mount. if status
        is None, which means there is no valid host entry for connection,
        the status is grey

        :param status:
        :return: true for test purpose
        """
        hasSim = packageConfig.isAvailable
        self.app.deviceStat['mount'] = status

        if status and hasSim:
            self.ui.mountConnected.setEnabled(status)
            self.ui.mountConnected.setText('Mount 3D')
        elif status:
            self.ui.mountConnected.setText('Mount')
        elif not status and hasSim:
            self.ui.mountConnected.setText('Mount')
            # if self.uiWindows['showSimulatorW']['classObj']:
            #     self.uiWindows['showSimulatorW']['classObj'].close()
        return True

    def updateMountWeatherStat(self, setting):
        """
        updateMountWeatherStat show the connection status of the mount weather
        station connected. if the data values are None there is no station
        attached to the GPS port.

        :return: true for test purpose
        """
        if setting.weatherTemperature is None and setting.weatherPressure is None:
            self.app.deviceStat['directWeather'] = None
        else:
            if setting.weatherStatus is None:
                self.app.deviceStat['directWeather'] = False
            else:
                self.app.deviceStat['directWeather'] = True
        return True

    def smartFunctionGui(self):
        """
        smartFunctionGui enables and disables gui actions depending on the
        actual state of the different devices. this should be the core of
        avoiding user misused during running operations. smartGui is run every
        1 second synchronously, because it can't be simpler done with dynamic
        approach. all different situations in a running environment is done
        locally.

        :return: true for test purpose
        """
        isMountReady = bool(self.app.deviceStat.get('mount'))
        isDomeReady = bool(self.app.deviceStat.get('dome'))
        isModelingReady = all(
            bool(self.app.deviceStat.get(x)) for x in ['mount', 'camera', 'plateSolve'])
        isPause = self.ui.pauseModel.property('pause')

        if isModelingReady and self.app.data.buildP and not isPause:
            self.ui.runModel.setEnabled(True)
        else:
            self.ui.runModel.setEnabled(False)

        if isModelingReady:
            self.ui.runModel.setEnabled(True)
            self.ui.plateSolveSync.setEnabled(True)
            self.ui.dataModel.setEnabled(True)
            self.ui.runFlexure.setEnabled(True)
            self.ui.runHysteresis.setEnabled(True)
        else:
            self.ui.runModel.setEnabled(False)
            self.ui.plateSolveSync.setEnabled(False)
            self.ui.dataModel.setEnabled(False)
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

        return True

    def smartTabGui(self):
        """
        smartTabGui enables and disables tab visibility depending on the actual
        state of the different devices.
        :return: true for test purpose
        """
        smartTabs = {
            'Power': {
                'statID': 'power',
                'tab': self.ui.toolsTabWidget,
            },
            'Relay': {
                'statID': 'relay',
                'tab': self.ui.toolsTabWidget,
            },
            'RelaySett': {
                'statID': 'relay',
                'tab': self.ui.settingsTabWidget,
            },
        }
        tabChanged = False

        for key, tab in smartTabs.items():
            tabIndex = self.getTabIndex(smartTabs[key]['tab'], key)
            tabStatus = smartTabs[key]['tab'].isTabVisible(tabIndex)

            stat = bool(self.app.deviceStat.get(smartTabs[key]['statID']))
            smartTabs[key]['tab'].setTabVisible(tabIndex, stat)
            actChanged = tabStatus != stat
            tabChanged = tabChanged or actChanged

        tabIndex = self.getTabIndex(self.ui.imagingTabWidget, 'reference')
        self.ui.imagingTabWidget.setTabVisible(tabIndex, packageConfig.isReference)
        tabIndex = self.getTabIndex(self.ui.toolsTabWidget, 'AnalyseFlexure')
        self.ui.toolsTabWidget.setTabVisible(tabIndex, packageConfig.isAnalyse)

        # redraw tabs only when a change occurred. this is necessary, because
        # enable and disable does not remove tabs
        if tabChanged:
            ui = self.ui.mainTabWidget
            ui.setStyleSheet(ui.styleSheet())
            ui = self.ui.toolsTabWidget
            ui.setStyleSheet(ui.styleSheet())
        return True

    def updateWindowsStats(self):
        """
        :return: True for test purpose
        """
        for win in self.extWindows.uiWindows:
            winObj = self.extWindows.uiWindows[win]

            if winObj['classObj']:
                self.changeStyleDynamic(winObj['button'], 'running', True)
            else:
                self.changeStyleDynamic(winObj['button'], 'running', False)
        return True

    def setEnvironDeviceStats(self):
        """
        :return:
        """
        refracOn = self.app.mount.setting.statusRefraction == 1
        isManual = self.ui.refracManual.isChecked()
        isTabEnabled = self.ui.showTabEnviron.isChecked()
        if not refracOn or not isTabEnabled:
            self.app.deviceStat['refraction'] = None
            self.ui.refractionConnected.setText('Refraction')
        elif isManual:
            self.ui.refractionConnected.setText('Refrac Manu')
            self.app.deviceStat['refraction'] = True
        else:
            self.ui.refractionConnected.setText('Refrac Auto')
            isSource = self.app.deviceStat.get(self.refractionSource, False)
            self.app.deviceStat['refraction'] = isSource
        return True

    def updateDeviceStats(self):
        """
        :return: True for test purpose
        """
        for device, ui in self.deviceStatGui.items():
            if self.app.deviceStat.get(device) is None:
                self.changeStyleDynamic(ui, 'color', 'gray')
            elif self.app.deviceStat[device]:
                self.changeStyleDynamic(ui, 'color', 'green')
            else:
                self.changeStyleDynamic(ui, 'color', 'red')

        isMount = self.app.deviceStat.get('mount', False)
        self.changeStyleDynamic(self.ui.mountOn, 'running', isMount)
        self.changeStyleDynamic(self.ui.mountOff, 'running', not isMount)
        return True

    def updatePlateSolveStatus(self, text):
        """
        :param text:
        :return: true for test purpose
        """
        self.ui.plateSolveText.setText(text)
        return True

    def updateDomeStatus(self, text):
        """
        :param text:
        :return: true for test purpose
        """
        self.ui.domeText.setText(text)
        return True

    def updateCameraStatus(self, text):
        """
        :param text:
        :return: true for test purpose
        """
        self.ui.cameraText.setText(text)
        return True

    def updateControllerStatus(self):
        """
        :return: True for test purpose
        """
        gcStatus = self.gameControllerRunning
        self.ui.controller1.setEnabled(gcStatus)
        self.ui.controller2.setEnabled(gcStatus)
        self.ui.controller3.setEnabled(gcStatus)
        self.ui.controller4.setEnabled(gcStatus)
        self.ui.controller5.setEnabled(gcStatus)
        return True

    def updateThreadAndOnlineStatus(self):
        """
        :return: True for test purpose
        """
        if self.ui.isOnline.isChecked():
            mode = 'Online'
        else:
            mode = 'Offline'

        moon = self.ui.moonPhaseIllumination.text()

        f = dark_twilight_day(self.app.ephemeris, self.app.mount.obsSite.location)
        twilight = TWILIGHTS[int(f(self.app.mount.obsSite.ts.now()))]

        activeCount = self.threadPool.activeThreadCount()

        diskUsage = shutil.disk_usage(self.app.mwGlob['workDir'])
        free = int(diskUsage[2] / diskUsage[0] * 100)

        t = f'{mode} - {twilight} - Moon: {moon}%'
        t += f' - Threads:{activeCount:2d} / 30 - Disk free: {free}%'
        self.ui.statusOnline.setTitle(t)
        return True

    def updateTime(self):
        """
        :return: True for test purpose
        """
        self.ui.timeComputer.setText(datetime.now().strftime('%H:%M:%S'))
        tzT = time.tzname[1] if time.daylight else time.tzname[0]
        t = f'TZ: {tzT}'
        self.ui.statusTime.setTitle(t)
        return True

    def updateStatusGUI(self, obs):
        """
        :return:    True if ok for testing
        """
        if obs.statusText() is not None:
            self.ui.statusText.setText(obs.statusText())
        else:
            self.ui.statusText.setText('-')

        if self.app.mount.obsSite.status == 0:
            self.changeStyleDynamic(self.ui.tracking, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.tracking, 'running', False)

        if self.app.mount.obsSite.status == 5:
            self.changeStyleDynamic(self.ui.park, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.park, 'running', False)

        if self.app.mount.obsSite.status == 1:
            self.changeStyleDynamic(self.ui.stop, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.stop, 'running', False)

        if self.app.mount.obsSite.status == 10 and not self.satStatus:
            self.app.playSound.emit('SatStartTracking')
            self.satStatus = True
        elif self.app.mount.obsSite.status != 10:
            self.satStatus = False

        return True

    def setColorSet(self):
        """
        :return:
        """
        Styles.colorSet = self.ui.colorSet.currentIndex()
        return True

    def refreshColorSet(self):
        """
        :return:
        """
        self.setColorSet()
        self.setStyleSheet(self.mw4Style)
        self.setupIcons()
        self.app.colorChange.emit()
        return True

    @staticmethod
    def checkExtension(filePath, ext):
        """
        :param filePath:
        :param ext:
        :return:
        """
        if not filePath.endswith(ext):
            filePath += ext
        return filePath

    def switchProfile(self, config):
        """
        :param config:
        :return:
        """
        self.extWindows.closeExtendedWindows()
        self.stopDrivers()
        self.app.config = config
        topo = self.app.initConfig()
        self.app.mount.obsSite.location = topo
        self.initConfig()
        self.extWindows.showExtendedWindows()
        return True

    def loadProfileGUI(self):
        """
        :return:
        """
        folder = self.app.mwGlob['configDir']
        loadFilePath, name, ext = self.openFile(
            self, 'Open config file', folder, 'Config files (*.cfg)',
            enableDir=False)
        if not name:
            return False

        config = loadProfile(configDir=self.app.mwGlob['configDir'], name=name)
        if config:
            self.ui.profile.setText(name)
            self.msg.emit(1, 'System', 'Profile', f'loaded {name}')
        else:
            self.msg.emit(2, 'System', 'Profile error',
                          f'{name}] cannot no be loaded')
            return False

        self.switchProfile(config)
        return True

    def addProfileGUI(self):
        """
        :return:
        """
        config = self.app.config
        folder = self.app.mwGlob['configDir']
        loadFilePath, name, ext = self.openFile(
            self, 'Open add-on config file', folder, 'Config files (*.cfg)',
            enableDir=False)
        if not name:
            self.ui.profileAdd.setText('-')
            return False

        self.storeConfig()
        self.app.storeConfig()
        configAdd = loadProfile(configDir=self.app.mwGlob['configDir'], name=name)
        if configAdd:
            self.ui.profileAdd.setText(name)
            profile = self.ui.profile.text()
            self.msg.emit(1, 'System', 'Profile', f'Base: {profile}')
            self.msg.emit(1, 'System', 'Profile', f'Add : {name}')
        else:
            self.ui.profileAdd.setText('-')
            self.msg.emit(2, 'System', 'Profile error',
                          f'{name}] cannot no be loaded')
            return False

        config = blendProfile(config, configAdd)
        self.switchProfile(config)
        return True

    def saveConfigAs(self):
        """
        :return:
        """
        folder = self.app.mwGlob['configDir']
        saveFilePath, name, ext = self.saveFile(
            self, 'Save config file', folder, 'Config files (*.cfg)',
            enableDir=False)
        if not name:
            return False

        self.storeConfig()
        self.app.storeConfig()
        suc = saveProfile(configDir=self.app.mwGlob['configDir'],
                          name=name,
                          config=self.app.config)
        if suc:
            self.ui.profile.setText(name)
            self.msg.emit(1, 'System', 'Profile', f'saved {name}')
            self.ui.profileAdd.setText('-')
        else:
            self.msg.emit(2, 'System', 'Profile error',
                          f'{name}] cannot no be saved')
        return True

    def saveConfig(self):
        """
        :return: nothing
        """
        self.storeConfig()
        self.app.storeConfig()
        suc = saveProfile(configDir=self.app.mwGlob['configDir'],
                          name=self.ui.profile.text(),
                          config=self.app.config)
        if suc:
            self.ui.profileAdd.setText('-')
            self.msg.emit(1, 'System', 'Profile', 'Actual profile saved')
        else:
            self.msg.emit(2, 'System', 'Profile',
                          'Actual profile cannot not be saved')
        return suc

    def remoteCommand(self, command):
        """
        remoteCommand received signals from remote class and executes them.
        :param command:
        :return: True for test purpose
        """
        if command == 'shutdown':
            self.quitSave()
            self.msg.emit(2, 'System', 'Remote', 'Shutdown MW4 remotely')
        elif command == 'shutdown mount':
            self.mountShutdown()
            self.msg.emit(2, 'System', 'Remote', 'Shutdown MW4 remotely')
        elif command == 'boot mount':
            self.mountBoot()
            self.msg.emit(2, 'System', 'Remote', 'Boot Mount remotely')
        return True
