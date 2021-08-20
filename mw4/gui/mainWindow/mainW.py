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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
from base import packageConfig

# standard libraries
from datetime import datetime
import gc
import time

# external packages
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtTest import QTest

# local import
if packageConfig.isAvailable:
    from gui.extWindows.simulatorW import SimulatorWindow
    from gui.extWindows.keypadW import KeypadWindow

from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.messageW import MessageWindow
from gui.extWindows.hemisphereW import HemisphereWindow
from gui.extWindows.measureW import MeasureWindow
from gui.extWindows.imageW import ImageWindow
from gui.extWindows.satelliteW import SatelliteWindow
from gui.extWindows.analyseW import AnalyseWindow
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabMount import Mount
from gui.mainWmixin.tabEnviron import Environ
from gui.mainWmixin.tabAlmanac import Almanac
from gui.mainWmixin.tabModel import Model
from gui.mainWmixin.tabBuildPoints import BuildPoints
from gui.mainWmixin.tabManageModel import ManageModel
from gui.mainWmixin.tabSatellite import Satellite
from gui.mainWmixin.tabMinorPlanetTime import MinorPlanetTime
from gui.mainWmixin.tabRelay import Relay
from gui.mainWmixin.tabTools import Tools
from gui.mainWmixin.tabPower import Power
from gui.mainWmixin.tabSettDevice import SettDevice
from gui.mainWmixin.tabSettMount import SettMount
from gui.mainWmixin.tabSettHorizon import SettHorizon
from gui.mainWmixin.tabSettImaging import SettImaging
from gui.mainWmixin.tabSettDome import SettDome
from gui.mainWmixin.tabSettParkPos import SettParkPos
from gui.mainWmixin.tabSettRelay import SettRelay
from gui.mainWmixin.tabSettMisc import SettMisc


class MainWindow(
    MWidget,
    SettMisc,
    Mount,
    Environ,
    Almanac,
    Model,
    BuildPoints,
    ManageModel,
    Satellite,
    MinorPlanetTime,
    Relay,
    Power,
    Tools,
    SettDevice,
    SettMount,
    SettHorizon,
    SettImaging,
    SettDome,
    SettParkPos,
    SettRelay,
):
    """
    the main window class handles the main menu as well as the show and no show
    part of any other window. all necessary processing for functions of that gui
    will be linked to this class. therefore window classes will have a threadpool
    for managing async processing if needed.
    """

    __all__ = [
        "MainWindow",
    ]

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool
        self.deviceStat = app.deviceStat
        self.uiWindows = app.uiWindows
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.closing = False
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
        if packageConfig.isAvailable:
            self.uiWindows['showSimulatorW'] = {
                'button': self.ui.mountConnected,
                'classObj': None,
                'name': 'SimulatorDialog',
                'class': SimulatorWindow,
            }
        if packageConfig.isAvailable:
            self.uiWindows['showKeypadW'] = {
                'button': self.ui.openKeypadW,
                'classObj': None,
                'name': 'KeypadDialog',
                'class': KeypadWindow,
            }
        self.deviceStatGui = {
            'dome': self.ui.domeConnected,
            'camera': self.ui.cameraConnected,
            'environOverall': self.ui.environConnected,
            'astrometry': self.ui.astrometryConnected,
            'mount': self.ui.mountConnected,
        }
        self.mwSuper('__init__')

        self.modelPositionPlot = self.embedMatplot(self.ui.modelPosition)
        self.modelPositionPlot.figure.canvas.mpl_connect(
            'button_press_event', self.onMouseEdit
        )
        self.errorAscendingPlot = self.embedMatplot(self.ui.errorAscending)
        self.errorDistributionPlot = self.embedMatplot(self.ui.errorDistribution)
        self.twilight = self.embedMatplot(self.ui.twilight)

        self.app.mount.signals.pointDone.connect(self.updateStatusGUI)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)
        self.app.mount.signals.settingDone.connect(self.updateMountWeatherStat)
        self.app.remoteCommand.connect(self.remoteCommand)
        self.app.astrometry.signals.message.connect(self.updateAstrometryStatus)
        self.app.dome.signals.message.connect(self.updateDomeStatus)
        self.app.camera.signals.message.connect(self.updateCameraStatus)
        self.ui.saveConfigQuit.clicked.connect(self.quitSave)
        self.ui.loadFrom.clicked.connect(self.loadProfile)
        self.ui.saveConfigAs.clicked.connect(self.saveProfileAs)
        self.ui.saveConfig.clicked.connect(self.saveProfile)

        for window in self.uiWindows:
            self.uiWindows[window]['button'].clicked.connect(self.toggleWindow)

        self.initConfig()
        self.showExtendedWindows()

        self.app.update1s.connect(self.updateTime)
        self.app.update1s.connect(self.updateWindowsStats)
        self.app.update1s.connect(self.smartFunctionGui)
        self.app.update1s.connect(self.smartTabGui)
        self.app.update1s.connect(self.smartEnvironGui)
        self.app.update1s.connect(self.updateWindowsStats)
        self.app.update1s.connect(self.updateDeviceStats)

    def mwSuper(self, func):
        """
        mwSuper is a replacement for super() to manage the mixin style of
        implementation it's not an ideal way to do it, but mwSuper() call the
        method of every ! parent class if they exist.

        :param func:
        :return: true for test purpose
        """
        for base in self.__class__.__bases__:
            if base.__name__ == "MWidget":
                continue

            if hasattr(base, func):
                funcAttrib = getattr(base, func)
                funcAttrib(self)

        return True

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        self.ui.profile.setText(config.get('profileName'))
        if 'mainW' not in config:
            config['mainW'] = {}
        config = config['mainW']
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)

        self.ui.mainTabWidget.setCurrentIndex(config.get('mainTabWidget', 0))
        self.ui.settingsTabWidget.setCurrentIndex(config.get('settingsTabWidget', 0))
        self.ui.toolsTabWidget.setCurrentIndex(config.get('toolsTabWidget', 0))
        if not packageConfig.isAnalyse:
            tabWidget = self.ui.toolsTabWidget.findChild(QWidget, 'Analyse')
            tabIndex = self.ui.toolsTabWidget.indexOf(tabWidget)
            self.ui.toolsTabWidget.setTabEnabled(tabIndex, False)

        tabWidget = self.ui.mainTabWidget.findChild(QWidget, 'Power')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)
        self.ui.mainTabWidget.setTabEnabled(tabIndex, False)

        tabWidget = self.ui.toolsTabWidget.findChild(QWidget, 'Relay')
        tabIndex = self.ui.toolsTabWidget.indexOf(tabWidget)
        self.ui.toolsTabWidget.setTabEnabled(tabIndex, False)
        self.ui.toolsTabWidget.setStyleSheet(self.getStyle())
        self.mwSuper('initConfig')
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
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config
        config['profileName'] = self.ui.profile.text()
        if 'mainW' not in config:
            config['mainW'] = {}

        config = config['mainW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['mainTabWidget'] = self.ui.mainTabWidget.currentIndex()
        config['settingsTabWidget'] = self.ui.settingsTabWidget.currentIndex()
        config['toolsTabWidget'] = self.ui.toolsTabWidget.currentIndex()
        self.mwSuper('storeConfig')
        self.storeConfigExtendedWindows()
        return True

    def closeEvent(self, closeEvent):
        """
        we overwrite the close event of the window just for the main window to
        close the application as well. because it does not make sense to have
        child windows open if main is already closed.

        :return:    nothing
        """
        self.closing = True
        self.stopDrivers()
        self.app.timer0_1s.stop()
        self.changeStyleDynamic(self.ui.pauseModel, 'pause', False)
        self.closeExtendedWindows()
        super().closeEvent(closeEvent)
        self.app.quit()

    def quitSave(self):
        """
        quitSave finished up and calls the quit save function in main for
        saving the parameters

        :return:    true for test purpose
        """
        self.saveProfile()
        self.app.saveConfig()
        self.close()
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        # main window
        self.wIcon(self.ui.saveConfigAs, 'save')
        self.wIcon(self.ui.loadFrom, 'load')
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
        self.wIcon(self.ui.genBuildGrid, 'run')
        self.wIcon(self.ui.genBuildMax, 'run')
        self.wIcon(self.ui.genBuildMed, 'run')
        self.wIcon(self.ui.genBuildNorm, 'run')
        self.wIcon(self.ui.genBuildMin, 'run')
        self.wIcon(self.ui.genBuildFile, 'show')
        self.wIcon(self.ui.genBuildAlign3, 'run')
        self.wIcon(self.ui.genBuildAlign6, 'run')
        self.wIcon(self.ui.genBuildAlign9, 'run')
        self.wIcon(self.ui.genBuildGrid, 'run')
        self.wIcon(self.ui.genBuildSpiralMax, 'run')
        self.wIcon(self.ui.genBuildSpiralMed, 'run')
        self.wIcon(self.ui.genBuildSpiralNorm, 'run')
        self.wIcon(self.ui.genBuildSpiralMin, 'run')
        self.wIcon(self.ui.genBuildDSO, 'run')

        # horizon
        self.wIcon(self.ui.loadHorizonMask, 'load')
        self.wIcon(self.ui.saveHorizonMask, 'save')
        self.wIcon(self.ui.saveHorizonMaskAs, 'save')
        self.wIcon(self.ui.clearHorizonMask, 'trash')

        # model
        self.wIcon(self.ui.plateSolveSync, 'start')
        pixmap = QPixmap(':/pics/azimuth.png')
        self.ui.picAZ.setPixmap(pixmap)
        pixmap = QPixmap(':/pics/altitude.png')
        self.ui.picALT.setPixmap(pixmap)

        self.wIcon(self.ui.cancelModel, 'cross-circle')
        self.wIcon(self.ui.runModel, 'start')
        self.wIcon(self.ui.pauseModel, 'pause')
        self.wIcon(self.ui.endModel, 'stop_m')
        self.wIcon(self.ui.batchModel, 'choose')

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
        self.wIcon(self.ui.runHysteresis, 'check-circle')
        self.wIcon(self.ui.cancelAnalyse, 'cross-circle')

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
        pixmap = QPixmap(':/dome/radius.png')
        self.ui.picDome1.setPixmap(pixmap)
        pixmap = QPixmap(':/dome/north.png')
        self.ui.picDome2.setPixmap(pixmap)
        pixmap = QPixmap(':/dome/east.png')
        self.ui.picDome3.setPixmap(pixmap)
        pixmap = QPixmap(':/dome/z_gem.png')
        self.ui.picDome4.setPixmap(pixmap)
        pixmap = QPixmap(':/dome/z_10micron.png')
        self.ui.picDome5.setPixmap(pixmap)
        pixmap = QPixmap(':/dome/gem.png')
        self.ui.picDome6.setPixmap(pixmap)
        pixmap = QPixmap(':/dome/lat.png')
        self.ui.picDome7.setPixmap(pixmap)
        pixmap = QPixmap(':/dome/shutter.png')
        self.ui.picDome8.setPixmap(pixmap)
        pixmap = QPixmap(':/dome/hysteresis.png')
        self.ui.picDome9.setPixmap(pixmap)
        pixmap = QPixmap(':/dome/zenith.png')
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
        isModelingReady = all(
            self.deviceStat[x] for x in ['mount', 'camera', 'astrometry']
        )
        isPause = self.ui.pauseModel.property('pause')

        if isModelingReady and self.app.data.buildP and not isPause:
            self.ui.runModel.setEnabled(True)
            self.ui.plateSolveSync.setEnabled(True)
            self.ui.runFlexure.setEnabled(True)
            self.ui.runHysteresis.setEnabled(True)

        elif isModelingReady and not isPause:
            self.ui.plateSolveSync.setEnabled(True)

        else:
            self.ui.runModel.setEnabled(False)
            self.ui.plateSolveSync.setEnabled(False)
            self.ui.runFlexure.setEnabled(False)
            self.ui.runHysteresis.setEnabled(False)

        if self.deviceStat.get('mount', False):
            self.ui.batchModel.setEnabled(True)

        else:
            self.ui.batchModel.setEnabled(False)

        stat = self.deviceStat.get('environOverall', None)

        if stat is None:
            self.ui.refractionGroup.setEnabled(False)
            self.ui.setRefractionManual.setEnabled(False)

        elif stat and self.deviceStat.get('mount', None):
            self.ui.refractionGroup.setEnabled(True)
            self.ui.setRefractionManual.setEnabled(True)

        else:
            self.ui.refractionGroup.setEnabled(False)
            self.ui.setRefractionManual.setEnabled(False)
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
                'tab': self.ui.mainTabWidget,
            },
            'Relay': {
                'statID': 'relay',
                'tab': self.ui.toolsTabWidget,
            },
        }
        tabChanged = False

        for key, tab in smartTabs.items():
            tabWidget = smartTabs[key]['tab'].findChild(QWidget, key)
            tabIndex = smartTabs[key]['tab'].indexOf(tabWidget)
            tabStatus = smartTabs[key]['tab'].isTabEnabled(tabIndex)

            stat = bool(self.deviceStat.get(smartTabs[key]['statID']))
            smartTabs[key]['tab'].setTabEnabled(tabIndex, stat)
            tabChanged = tabChanged or (tabStatus != stat)

        # redraw tabs only when a change occurred. this is necessary, because
        # enable and disable does not remove tabs
        if tabChanged:
            self.ui.mainTabWidget.setStyleSheet(self.getStyle())
            self.ui.settingsTabWidget.setStyleSheet(self.getStyle())
        return True

    def smartEnvironGui(self):
        """
        smartEnvironGui enables and disables gui actions depending on the actual
        state of the different environment devices. it is run every 1 second
        synchronously, because it can't be simpler done with dynamic approach.
        all different situations in a running environment is done locally.

        :return: true for test purpose
        """
        environ = {
            'directWeather': self.ui.directWeatherGroup,
            'sensorWeather': self.ui.sensorWeatherGroup,
            'onlineWeather': self.ui.onlineWeatherGroup,
            'skymeter': self.ui.skymeterGroup,
            'powerWeather': self.ui.powerGroup,
        }

        for key, group in environ.items():
            stat = self.deviceStat.get(key, None)

            if stat is None:
                group.setFixedWidth(0)
                group.setEnabled(False)
            elif stat:
                group.setMinimumSize(75, 0)
                group.setEnabled(True)
            else:
                group.setMinimumSize(75, 0)
                group.setEnabled(False)
        return True

    def updateWindowsStats(self):
        """
        :return: True for test purpose
        """
        for win in self.app.uiWindows:
            winObj = self.app.uiWindows[win]

            if winObj['classObj']:
                self.changeStyleDynamic(winObj['button'], 'running', True)
            else:
                self.changeStyleDynamic(winObj['button'], 'running', False)
        return True

    def updateDeviceStats(self):
        """
        updateDeviceStats sets the colors in main window upper bar for getting
        important overview, which functions are available.

        the refraction sources etc are defined in tabEnviron, but it is optimal
        setting the selected source right at this point as it is synchronous if
        state is switching

        :return: True for test purpose
        """
        if self.refractionSource in self.deviceStat:
            self.deviceStat['environOverall'] = self.deviceStat[self.refractionSource]
        else:
            self.deviceStat['environOverall'] = None

        for device, ui in self.deviceStatGui.items():
            if self.deviceStat.get(device, None) is None:
                self.changeStyleDynamic(ui, 'color', 'gray')
            elif self.deviceStat[device]:
                self.changeStyleDynamic(ui, 'color', 'green')
            else:
                self.changeStyleDynamic(ui, 'color', 'red')
        return True

    def updateAstrometryStatus(self, text):
        """
        :param text:
        :return: true for test purpose
        """
        self.ui.astrometryText.setText(text)
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

    def updateTime(self):
        """
        :return: True for test purpose
        """
        self.ui.timeComputer.setText(datetime.now().strftime('%H:%M:%S'))
        timeJD = self.app.mount.obsSite.timeJD
        if timeJD is not None:
            text = timeJD.utc_strftime('%H:%M:%S')
            self.ui.timeUTC.setText('UTC:  ' + text)

        if self.ui.isOnline.isChecked():
            mode = 'Internet Online Mode'
        else:
            mode = 'Offline Mode'

        t = f'{mode}  -  Active Threads: {self.threadPool.activeThreadCount():2d}'
        self.ui.statusOnline.setTitle(t)

        tzT = time.tzname[1] if time.daylight else time.tzname[0]
        tzT = tzT.replace('Summer Time', 'DST')
        t = f'Timezone: {tzT}'
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
            self.changeStyleDynamic(self.ui.tracking, 'running', 'true')
        else:
            self.changeStyleDynamic(self.ui.tracking, 'running', 'false')

        if self.app.mount.obsSite.status == 5:
            self.changeStyleDynamic(self.ui.park, 'running', 'true')
        else:
            self.changeStyleDynamic(self.ui.park, 'running', 'false')

        if self.app.mount.obsSite.status == 1:
            self.changeStyleDynamic(self.ui.stop, 'running', 'true')
        else:
            self.changeStyleDynamic(self.ui.stop, 'running', 'false')

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

        gc.collect()
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

    def closeExtendedWindows(self):
        """
        closeExtendedWindows closes all open extended windows by calling
        close and waits until the window class is deleted.

        :return: true for test purpose
        """
        for window in self.uiWindows:
            if not self.uiWindows[window]['classObj']:
                continue

            self.uiWindows[window]['classObj'].close()

        waitDeleted = True
        while waitDeleted:
            for window in self.uiWindows:
                if self.uiWindows[window]['classObj']:
                    continue

                waitDeleted = False
            QTest.qWait(100)
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

    def loadProfile(self):
        """
        loadProfile interacts to get a new profile name. if a valid is received,
        it closes all extended windows to be sure to have all setup saved,
        than load the new profile and initializes all classes and opens the
        necessary extended windows with their setups stored.
        loadProfile does not save the actual configuration before loading
        another one.

        :return:
        """
        folder = self.app.mwGlob['configDir']
        loadFilePath, name, ext = self.openFile(
            self,
            'Open config file',
            folder,
            'Config files (*.cfg)',
            enableDir=False,
        )
        if not name:
            return False

        # closing all windows to be base lined
        self.closeExtendedWindows()
        self.stopDrivers()
        suc = self.app.loadConfig(name=name)
        if suc:
            self.app.config['profileName'] = name
            self.ui.profile.setText(name)
            t = f'Profile              [{name}] loaded'
            self.app.message.emit(t, 0)
        else:
            t = f'Profile              [{name}] cannot no be loaded'
            self.app.message.emit(t, 2)

        topo = self.app.initConfig()
        self.app.mount.obsSite.location = topo
        self.initConfig()
        self.showExtendedWindows()
        return True

    def saveProfileAs(self):
        """
        :return:
        """
        folder = self.app.mwGlob['configDir']
        saveFilePath, name, ext = self.saveFile(
            self,
            'Save config file',
            folder,
            'Config files (*.cfg)',
            enableDir=False,
        )
        if not name:
            return False

        self.storeConfig()
        self.app.storeConfig()
        suc = self.app.saveConfig(name=name)
        if suc:
            self.ui.profile.setText(name)
            t = f'Profile              [{name}] saved'
            self.app.message.emit(t, 0)
        else:
            t = f'Profile              [{name}] cannot no be saved'
            self.app.message.emit(t, 2)
        return True

    def saveProfile(self):
        """
        saveProfile calls save profile in main and sends a message to the user
        about success.

        :return: nothing
        """
        self.storeConfig()
        self.app.storeConfig()
        suc = self.app.saveConfig(name=self.ui.profile.text())
        if suc:
            self.app.message.emit('Actual profile saved', 0)

        else:
            self.app.message.emit('Actual profile cannot not be saved', 2)
        return suc

    def remoteCommand(self, command):
        """
        remoteCommand received signals from remote class and executes them.

        :param command:
        :return: True for test purpose
        """
        if command == 'shutdown':
            self.quitSave()
            self.app.message.emit('Shutdown MW remotely', 2)
        elif command == 'shutdown mount':
            self.mountShutdown()
            self.app.message.emit('Shutdown mount remotely', 2)
        elif command == 'boot mount':
            self.mountBoot()
            self.app.message.emit('Boot mount remotely', 2)
        return True
