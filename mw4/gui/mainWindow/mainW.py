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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
from base import packageConfig

# standard libraries
from datetime import datetime
import time

# external packages
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QWidget

# local import
if packageConfig.isAvailable:
    from gui.extWindows.simulatorW import SimulatorWindow

from gui.utilities.toolsQtWidget import sleepAndEvents
from gui.extWindows.keypadW import KeypadWindow
from gui.utilities.stylesQtCss import Styles
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.messageW import MessageWindow
from gui.extWindows.hemisphereW import HemisphereWindow
from gui.extWindows.measureW import MeasureWindow
from gui.extWindows.imageW import ImageWindow
from gui.extWindows.satelliteW import SatelliteWindow
from gui.extWindows.analyseW import AnalyseWindow
from gui.extWindows.videoW1 import VideoWindow1
from gui.extWindows.videoW2 import VideoWindow2
from gui.extWindows.videoW3 import VideoWindow3
from gui.extWindows.videoW4 import VideoWindow4
from gui.extWindows.bigPopupW import BigPopup
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabMount import Mount
from gui.mainWmixin.tabEnviron import Environ
from gui.mainWmixin.tabAlmanac import Almanac
from gui.mainWmixin.tabModel import Model
from gui.mainWmixin.runBasic import BasicRun
from gui.mainWmixin.tabBuildPoints import BuildPoints
from gui.mainWmixin.tabManageModel import ManageModel
from gui.mainWmixin.tabSatSearch import SatSearch
from gui.mainWmixin.tabSatTrack import SatTrack
from gui.mainWmixin.tabMinorPlanetTime import MinorPlanetTime
from gui.mainWmixin.tabRelay import Relay
from gui.mainWmixin.tabTools import Tools
from gui.mainWmixin.tabAnalysis import Analysis
from gui.mainWmixin.tabPower import Power
from gui.mainWmixin.tabSettDevice import SettDevice
from gui.mainWmixin.tabSettMount import SettMount
from gui.mainWmixin.tabSettImaging import SettImaging
from gui.mainWmixin.tabSettImageStats import SettImageStats
from gui.mainWmixin.tabSettDome import SettDome
from gui.mainWmixin.tabSettParkPos import SettParkPos
from gui.mainWmixin.tabSettRelay import SettRelay
from gui.mainWmixin.tabSettMisc import SettMisc
from logic.profiles.profile import loadProfile, saveProfile, blendProfile


class MainWindow(
    MWidget,
    SettMisc,
    Mount,
    Environ,
    Almanac,
    Model,
    BasicRun,
    BuildPoints,
    ManageModel,
    SatSearch,
    SatTrack,
    MinorPlanetTime,
    Relay,
    Power,
    Tools,
    Analysis,
    SettDevice,
    SettMount,
    SettImaging,
    SettImageStats,
    SettDome,
    SettParkPos,
    SettRelay,
):
    """
    the main window class handles the main menu as well as the show and no show
    part of any other window. all necessary processing for functions of that gui
    will be linked to this class. therefore, window classes will have a threadpool
    for managing async processing if needed.
    """

    __all__ = ['MainWindow']

    def __init__(self, app):
        # has to be put before super to adjust the color before the stylesheet
        # on the parent classes is drawn first
        colSet = app.config.get('colorSet', 0)
        Styles.colorSet = colSet
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.deviceStat = app.deviceStat
        self.uiWindows = app.uiWindows
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.satStatus = False
        self.gameControllerRunning = False
        self.setWindowTitle(f'MountWizzard4 - v{self.app.__version__}')

        self.uiWindows['showMessageW'] = {
            'button': self.ui.openMessageW,
            'classObj': None,
            'name': 'MessageDialog',
            'class': MessageWindow,
        }
        self.uiWindows['showHemisphereW'] = {
            'button': self.ui.openHemisphereW,
            'classObj': None,
            'name': 'HemisphereDialog',
            'class': HemisphereWindow,
        }
        self.uiWindows['showImageW'] = {
            'button': self.ui.openImageW,
            'classObj': None,
            'name': 'ImageDialog',
            'class': ImageWindow,
        }
        self.uiWindows['showMeasureW'] = {
            'button': self.ui.openMeasureW,
            'classObj': None,
            'name': 'MeasureDialog',
            'class': MeasureWindow,
        }
        self.uiWindows['showSatelliteW'] = {
            'button': self.ui.openSatelliteW,
            'classObj': None,
            'name': 'SatelliteDialog',
            'class': SatelliteWindow,
        }
        self.uiWindows['showAnalyseW'] = {
            'button': self.ui.openAnalyseW,
            'classObj': None,
            'name': 'AnalyseDialog',
            'class': AnalyseWindow,
        }
        self.uiWindows['showVideoW1'] = {
            'button': self.ui.openV1,
            'classObj': None,
            'name': 'Video1',
            'class': VideoWindow1,
        }
        self.uiWindows['showVideoW2'] = {
            'button': self.ui.openV2,
            'classObj': None,
            'name': 'Video2',
            'class': VideoWindow2,
        }
        self.uiWindows['showVideoW3'] = {
            'button': self.ui.openV3,
            'classObj': None,
            'name': 'Video3',
            'class': VideoWindow3,
        }
        self.uiWindows['showVideoW4'] = {
            'button': self.ui.openV4,
            'classObj': None,
            'name': 'Video4',
            'class': VideoWindow4,
        }
        if packageConfig.isAvailable:
            self.uiWindows['showSimulatorW'] = {
                'button': self.ui.mountConnected,
                'classObj': None,
                'name': 'SimulatorDialog',
                'class': SimulatorWindow,
            }
        self.uiWindows['showKeypadW'] = {
            'button': self.ui.openKeypadW,
            'classObj': None,
            'name': 'KeypadDialog',
            'class': KeypadWindow,
        }
        self.uiWindows['showBigPopupW'] = {
            'button': self.ui.big,
            'classObj': None,
            'name': 'BigPopup',
            'class': BigPopup,
        }
        self.deviceStatGui = {
            'dome': self.ui.domeConnected,
            'camera': self.ui.cameraConnected,
            'refraction': self.ui.refractionConnected,
            'plateSolve': self.ui.plateSolveConnected,
            'mount': self.ui.mountConnected,
        }
        self.mwSuper('__init__')
        self.app.mount.signals.pointDone.connect(self.updateStatusGUI)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)
        self.app.mount.signals.settingDone.connect(self.updateMountWeatherStat)
        self.app.remoteCommand.connect(self.remoteCommand)
        self.app.plateSolve.signals.message.connect(self.updatePlateSolveStatus)
        self.app.dome.signals.message.connect(self.updateDomeStatus)
        self.app.camera.signals.message.connect(self.updateCameraStatus)
        self.ui.saveConfigQuit.clicked.connect(self.quitSave)
        self.ui.loadFrom.clicked.connect(self.loadProfile)
        self.ui.addFrom.clicked.connect(self.addProfile)
        self.ui.saveConfigAs.clicked.connect(self.saveConfigAs)
        self.ui.saveConfig.clicked.connect(self.saveConfig)
        self.app.seeingWeather.b = self.ui.label_b.property('a')

        for window in self.uiWindows:
            self.uiWindows[window]['button'].clicked.connect(self.toggleWindow)

        self.initConfig()
        self.ui.colorSet.currentIndexChanged.connect(self.refreshColorSet)
        self.ui.collectWindows.clicked.connect(self.collectWindows)
        self.showExtendedWindows()
        self.activateWindow()

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
        self.setTabAndIndex(self.ui.mainTabWidget, config, 'tabMain')
        self.setTabAndIndex(self.ui.mountTabWidget, config, 'tabMount')
        self.setTabAndIndex(self.ui.imagingTabWidget, config, 'tabImaging')
        self.setTabAndIndex(self.ui.modelingTabWidget, config, 'tabModeling')
        self.setTabAndIndex(self.ui.manageTabWidget, config, 'tabManage')
        self.setTabAndIndex(self.ui.settingsTabWidget, config, 'tabSettings')
        self.setTabAndIndex(self.ui.toolsTabWidget, config, 'tabTools')
        self.setTabAndIndex(self.ui.satTabWidget, config, 'tabSatellite')
        self.mwSuper('initConfig')
        self.smartTabGui()
        self.changeStyleDynamic(self.ui.mountConnected, 'color', 'gray')
        self.setupIcons()
        self.show()
        return True

    def storeConfigExtendedWindows(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        for window in self.uiWindows:
            config[window] = bool(self.uiWindows[window]['classObj'])
            if config[window]:
                self.uiWindows[window]['classObj'].storeConfig()

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
        store = self.ui.storeTabOrder.isChecked()
        self.getTabAndIndex(self.ui.mainTabWidget, config, 'tabMain', store)
        self.getTabAndIndex(self.ui.mountTabWidget, config, 'tabMount', store)
        self.getTabAndIndex(self.ui.imagingTabWidget, config, 'tabImaging', store)
        self.getTabAndIndex(self.ui.modelingTabWidget, config, 'tabModeling', store)
        self.getTabAndIndex(self.ui.manageTabWidget, config, 'tabManage', store)
        self.getTabAndIndex(self.ui.settingsTabWidget, config, 'tabSettings', store)
        self.getTabAndIndex(self.ui.toolsTabWidget, config, 'tabTools', store)
        self.getTabAndIndex(self.ui.satTabWidget, config, 'tabSatellite', store)
        self.mwSuper('storeConfig')
        self.storeConfigExtendedWindows()
        return True

    def closeEvent(self, closeEvent):
        """
        :return:    nothing
        """
        self.gameControllerRunning = False
        self.app.timer0_1s.stop()
        self.changeStyleDynamic(self.ui.pauseModel, 'pause', False)
        self.closeExtendedWindows()
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

    def setupIcons(self):
        """
        :return:    True if success for test
        """
        # main window
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

        # model points
        self.wIcon(self.ui.loadBuildPoints, 'load')
        self.wIcon(self.ui.saveBuildPoints, 'save')
        self.wIcon(self.ui.saveBuildPointsAs, 'save')
        self.wIcon(self.ui.clearBuildP, 'trash')

        # model
        self.wIcon(self.ui.plateSolveSync, 'start')
        pixmap = self.img2pixmap(':/pics/azimuth.png').scaled(101, 101)
        self.ui.picAZ.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/pics/altitude.png').scaled(101, 101)
        self.ui.picALT.setPixmap(pixmap)

        self.wIcon(self.ui.cancelModel, 'cross-circle')
        self.wIcon(self.ui.runModel, 'start')
        self.wIcon(self.ui.pauseModel, 'pause')
        self.wIcon(self.ui.endModel, 'stop_m')
        self.wIcon(self.ui.dataModel, 'choose')

        # manage model
        self.wIcon(self.ui.runOptimize, 'start')
        self.wIcon(self.ui.cancelOptimize, 'cross-circle')
        self.wIcon(self.ui.deleteWorstPoint, 'circle-minus')
        self.wIcon(self.ui.clearModel, 'trash')
        self.wIcon(self.ui.openAnalyseW, 'bar-chart')
        self.wIcon(self.ui.showActualModelAnalyse, 'copy')
        self.wIcon(self.ui.showOriginalModelAnalyse, 'copy')

        self.wIcon(self.ui.loadName, 'load')
        self.wIcon(self.ui.saveName, 'save')
        self.wIcon(self.ui.deleteName, 'trash')
        self.wIcon(self.ui.refreshName, 'reload')
        self.wIcon(self.ui.refreshModel, 'reload')

        # minor planets
        self.wIcon(self.ui.progMinorPlanetsFull, 'run')
        self.wIcon(self.ui.progMinorPlanetsFiltered, 'run')
        self.wIcon(self.ui.progEarthRotationData, 'run')
        self.wIcon(self.ui.downloadIERS, 'run')

        # satellite
        self.wIcon(self.ui.stopSatelliteTracking, 'cross-circle')
        self.wIcon(self.ui.startSatelliteTracking, 'start')
        self.wIcon(self.ui.progSatellitesFull, 'run')
        self.wIcon(self.ui.progSatellitesFiltered, 'run')
        self.wIcon(self.ui.progTrajectory, 'run')

        # analyse
        self.wIcon(self.ui.runFlexure, 'start')
        self.wIcon(self.ui.runHysteresis, 'start')
        self.wIcon(self.ui.cancelAnalysis, 'cross-circle')

        # tools
        self.wIcon(self.ui.renameStart, 'start')
        self.wIcon(self.ui.renameInputSelect, 'folder')
        self.wIcon(self.ui.posButton0, 'target')
        self.wIcon(self.ui.posButton1, 'target')
        self.wIcon(self.ui.posButton2, 'target')
        self.wIcon(self.ui.posButton3, 'target')
        self.wIcon(self.ui.posButton4, 'target')
        self.wIcon(self.ui.posButton5, 'target')
        self.wIcon(self.ui.posButton6, 'target')
        self.wIcon(self.ui.posButton7, 'target')
        self.wIcon(self.ui.posButton8, 'target')
        self.wIcon(self.ui.posButton9, 'target')

        self.wIcon(self.ui.moveNorth, 'north')
        self.wIcon(self.ui.moveEast, 'east')
        self.wIcon(self.ui.moveSouth, 'south')
        self.wIcon(self.ui.moveWest, 'west')
        self.wIcon(self.ui.moveNorthEast, 'northEast')
        self.wIcon(self.ui.moveNorthWest, 'northWest')
        self.wIcon(self.ui.moveSouthEast, 'southEast')
        self.wIcon(self.ui.moveSouthWest, 'southWest')
        self.wIcon(self.ui.moveNorthAltAz, 'north')
        self.wIcon(self.ui.moveEastAltAz, 'east')
        self.wIcon(self.ui.moveSouthAltAz, 'south')
        self.wIcon(self.ui.moveWestAltAz, 'west')
        self.wIcon(self.ui.moveNorthEastAltAz, 'northEast')
        self.wIcon(self.ui.moveNorthWestAltAz, 'northWest')
        self.wIcon(self.ui.moveSouthEastAltAz, 'southEast')
        self.wIcon(self.ui.moveSouthWestAltAz, 'southWest')
        self.wIcon(self.ui.stopMoveAll, 'stop_m')
        self.wIcon(self.ui.moveAltAzAbsolute, 'target')
        self.wIcon(self.ui.moveRaDecAbsolute, 'target')

        # driver setting
        for driver in self.drivers:
            if self.drivers[driver]['uiSetup'] is not None:
                ui = self.drivers[driver]['uiSetup']
                self.wIcon(ui, 'cogs')

        self.wIcon(self.ui.ascomConnect, 'link')
        self.wIcon(self.ui.ascomDisconnect, 'unlink')

        # imaging
        self.wIcon(self.ui.copyFromTelescopeDriver, 'copy')
        self.wIcon(self.ui.haltFocuser, 'bolt-alt')
        self.wIcon(self.ui.moveFocuserIn, 'exit-down')
        self.wIcon(self.ui.moveFocuserOut, 'exit-up')
        self.wIcon(self.ui.coverPark, 'exit-down')
        self.wIcon(self.ui.coverUnpark, 'exit-up')

        # dome setting
        pixmap = self.img2pixmap(':/dome/radius.png')
        self.ui.picDome1.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/dome/north.png')
        self.ui.picDome2.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/dome/east.png')
        self.ui.picDome3.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/dome/z_gem.png')
        self.ui.picDome4.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/dome/z_10micron.png')
        self.ui.picDome5.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/dome/gem.png')
        self.ui.picDome6.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/dome/lat.png')
        self.ui.picDome7.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/dome/shutter.png')
        self.ui.picDome8.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/dome/hysteresis.png')
        self.ui.picDome9.setPixmap(pixmap)
        pixmap = self.img2pixmap(':/dome/zenith.png')
        self.ui.picDome10.setPixmap(pixmap)
        self.wIcon(self.ui.copyFromDomeDriver, 'copy')
        self.wIcon(self.ui.domeCloseShutter, 'exit-down')
        self.wIcon(self.ui.domeOpenShutter, 'exit-up')
        self.wIcon(self.ui.domeAbortSlew, 'bolt-alt')

        # park positions
        self.wIcon(self.ui.posSave0, 'download')
        self.wIcon(self.ui.posSave1, 'download')
        self.wIcon(self.ui.posSave2, 'download')
        self.wIcon(self.ui.posSave3, 'download')
        self.wIcon(self.ui.posSave4, 'download')
        self.wIcon(self.ui.posSave5, 'download')
        self.wIcon(self.ui.posSave6, 'download')
        self.wIcon(self.ui.posSave7, 'download')
        self.wIcon(self.ui.posSave8, 'download')
        self.wIcon(self.ui.posSave9, 'download')

        # misc setting
        self.wIcon(self.ui.installVersion, 'world')
        pixmap = self.svg2pixmap(':/icon/controller.svg', self.M_BLUE)
        self.ui.controller1.setPixmap(pixmap.scaled(16, 16))
        self.ui.controller2.setPixmap(pixmap.scaled(16, 16))
        self.ui.controller3.setPixmap(pixmap.scaled(16, 16))
        self.ui.controller4.setPixmap(pixmap.scaled(16, 16))
        self.ui.controller5.setPixmap(pixmap.scaled(16, 16))
        pixmap = self.svg2pixmap(':/icon/controllerNew.svg', self.M_BLUE)
        self.ui.controllerOverview.setPixmap(pixmap)
        self.ui.controller1.setEnabled(False)
        self.ui.controller2.setEnabled(False)
        self.ui.controller3.setEnabled(False)
        self.ui.controller4.setEnabled(False)
        self.ui.controller5.setEnabled(False)

        # environment
        pixmap = self.svg2pixmap(':/icon/meteoblue.svg', '#124673')
        pixmap = pixmap.transformed(QTransform().rotate(-90))
        pixmap = pixmap.scaled(37, 128, 1)
        self.ui.meteoblueIcon.setPixmap(pixmap)
        return True

    def updateMountConnStat(self, status):
        """
        updateMountConnStat show the connection status of the mount. if status
        is None, which means there is no valid host entry for connection,
        the status is grey

        :param status:
        :return: true for test purpose
        """
        hasSim = packageConfig.isAvailable
        self.deviceStat['mount'] = status

        if status and hasSim:
            self.ui.mountConnected.setEnabled(status)
            self.ui.mountConnected.setText('Mount 3D')
        elif status:
            self.ui.mountConnected.setText('Mount')
        elif not status and hasSim:
            self.ui.mountConnected.setText('Mount')
            if self.uiWindows['showSimulatorW']['classObj']:
                self.uiWindows['showSimulatorW']['classObj'].close()
        return True

    def updateMountWeatherStat(self, setting):
        """
        updateMountWeatherStat show the connection status of the mount weather
        station connected. if the data values are None there is no station
        attached to the GPS port.

        :return: true for test purpose
        """
        if setting.weatherTemperature is None and setting.weatherPressure is None:
            self.deviceStat['directWeather'] = None
        else:
            if setting.weatherStatus is None:
                self.deviceStat['directWeather'] = False
            else:
                self.deviceStat['directWeather'] = True
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
        isMountReady = bool(self.deviceStat.get('mount'))
        isDomeReady = bool(self.deviceStat.get('dome'))
        isModelingReady = all(
            bool(self.deviceStat.get(x)) for x in ['mount', 'camera', 'plateSolve'])
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
        else:
            self.ui.dsoGroup.setEnabled(False)
            self.ui.refractionGroup.setEnabled(False)
            self.ui.mountCommandTable.setEnabled(False)

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
            tabWidget = smartTabs[key]['tab'].findChild(QWidget, key)
            tabIndex = smartTabs[key]['tab'].indexOf(tabWidget)
            tabStatus = smartTabs[key]['tab'].isTabVisible(tabIndex)

            stat = bool(self.deviceStat.get(smartTabs[key]['statID']))
            smartTabs[key]['tab'].setTabVisible(tabIndex, stat)
            actChanged = tabStatus != stat
            tabChanged = tabChanged or actChanged

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
        for win in self.uiWindows:
            winObj = self.uiWindows[win]

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
            self.deviceStat['refraction'] = None
            self.ui.refractionConnected.setText('Refraction')
        elif isManual:
            self.ui.refractionConnected.setText('Refrac Manu')
            self.deviceStat['refraction'] = True
        else:
            self.ui.refractionConnected.setText('Refrac Auto')
            isSource = self.deviceStat.get(self.refractionSource, False)
            self.deviceStat['refraction'] = isSource
        return True

    def updateDeviceStats(self):
        """
        :return: True for test purpose
        """
        for device, ui in self.deviceStatGui.items():
            if self.deviceStat.get(device) is None:
                self.changeStyleDynamic(ui, 'color', 'gray')
            elif self.deviceStat[device]:
                self.changeStyleDynamic(ui, 'color', 'green')
            else:
                self.changeStyleDynamic(ui, 'color', 'red')

        isMount = self.deviceStat.get('mount', False)
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
            mode = 'Internet Online Mode'
        else:
            mode = 'Offline Mode'

        activeCount = self.threadPool.activeThreadCount()
        t = f'{mode}  -  Active Threads: {activeCount:2d} / 30'
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

    def deleteWindowResource(self, widget=None):
        """
        :return: success
        """
        if not widget:
            return False

        for window in self.uiWindows:
            if self.uiWindows[window]['name'] != widget.objectName():
                continue
            self.uiWindows[window]['classObj'] = None

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

    def buildWindow(self, window):
        """
        buildWindow makes new object instance from window class. both are
        stored in the uiWindows dict for usage.

        :return: true for test purpose
        """
        self.uiWindows[window]['classObj'] = self.uiWindows[window]['class'](self.app)
        self.uiWindows[window]['classObj'].destroyed.connect(self.deleteWindowResource)
        self.uiWindows[window]['classObj'].initConfig()
        self.uiWindows[window]['classObj'].showWindow()
        return True

    def toggleWindow(self):
        """
        :return: true for test purpose
        """
        for window in self.uiWindows:
            if self.uiWindows[window]['button'] != self.sender():
                continue

            if not self.uiWindows[window]['classObj']:
                self.buildWindow(window)
            else:
                self.uiWindows[window]['classObj'].close()
        return True

    def showExtendedWindows(self):
        """
        showExtendedWindows opens all extended windows depending on their
        opening status stored in the configuration dict.

        :return: true for test purpose
        """
        for window in self.uiWindows:
            if window == 'showSimulatorW':
                continue
            if not self.app.config.get(window, False):
                continue

            self.buildWindow(window)
        return True

    def waitClosedExtendedWindows(self):
        """
        waits until the window class is deleted
        :return:
        """
        waitDeleted = True
        while waitDeleted:
            for window in self.uiWindows:
                if self.uiWindows[window]['classObj']:
                    continue

                waitDeleted = False
            sleepAndEvents(100)
        return True

    def closeExtendedWindows(self):
        """
        closeExtendedWindows closes all open extended windows by calling
        close.

        :return: true for test purpose
        """
        for window in self.uiWindows:
            if not self.uiWindows[window]['classObj']:
                continue

            self.uiWindows[window]['classObj'].close()
        self.waitClosedExtendedWindows()
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
        self.closeExtendedWindows()
        # self.stopDrivers()
        self.app.config = config
        topo = self.app.initConfig()
        self.app.mount.obsSite.location = topo
        self.initConfig()
        self.showExtendedWindows()
        return True

    def loadProfile(self):
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

    def addProfile(self):
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

    def collectWindows(self):
        """
        :return:
        """
        for i, window in enumerate(self.uiWindows):
            if self.uiWindows[window]['classObj']:
                self.uiWindows[window]['classObj'].resize(800, 600)
                self.uiWindows[window]['classObj'].move(i * 50 + 10, i * 50 + 10)
                self.uiWindows[window]['classObj'].activateWindow()
        self.move(i * 50 + 10, i * 50 + 10)
        self.activateWindow()
        return True
