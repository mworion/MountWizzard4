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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import datetime
import os
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
import wakeonlan
# local import
from mw4.gui.widget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.mainWmixin.tabMount import Mount
from mw4.gui.mainWmixin.tabEnviron import EnvironGui
from mw4.gui.mainWmixin.tabModel import Model
from mw4.gui.mainWmixin.tabBuildPoints import BuildPoints
from mw4.gui.mainWmixin.tabManageModel import ManageModel
from mw4.gui.mainWmixin.tabSatellite import Satellite
from mw4.gui.mainWmixin.tabRelay import Relay
from mw4.gui.mainWmixin.tabPower import Power
from mw4.gui.mainWmixin.tabTools import Tools
from mw4.gui.mainWmixin.tabSettDevice import SettDevice
from mw4.gui.mainWmixin.tabSettIndi import SettIndi
from mw4.gui.mainWmixin.tabSettMount import SettMount
from mw4.gui.mainWmixin.tabSettHorizon import SettHorizon
from mw4.gui.mainWmixin.tabSettImaging import SettImaging
from mw4.gui.mainWmixin.tabSettParkPos import SettParkPos
from mw4.gui.mainWmixin.tabSettRelay import SettRelay
from mw4.gui.mainWmixin.tabSettMisc import SettMisc


class MainWindow(MWidget,
                 Mount,
                 EnvironGui,
                 Model,
                 BuildPoints,
                 ManageModel,
                 Satellite,
                 Relay,
                 Power,
                 Tools,
                 SettIndi,
                 SettDevice,
                 SettMount,
                 SettHorizon,
                 SettImaging,
                 SettParkPos,
                 SettRelay,
                 SettMisc,
                 ):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    __all__ = ['MainWindow',
               ]
    version = '0.101'
    logger = logging.getLogger(__name__)

    def __init__(self, app, threadPool):
        self.app = app
        self.threadPool = threadPool
        super().__init__()

        # load and init the gui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()
        self.setupIcons()
        self.setWindowTitle(f'MountWizzard4 - v{self.app.__version__}')

        self.deviceStat = {
            'dome': None,
            'mount': None,
            'imaging': None,
            'astrometry': None,
            'environOverall': None,
            'environ': None,
            'internalSensor': None,
            'weather': None,
            'skymeter': None,
            'cover': None,
            'telescope': None,
            'power': None,
            'remote': None,
            'relay': None,
            'measure': None,
        }
        self.deviceStatGui = {'dome': self.ui.domeConnected,
                              'imaging': self.ui.imagingConnected,
                              'environOverall': self.ui.environConnected,
                              'astrometry': self.ui.astrometryConnected,
                              'mount': self.ui.mountConnected}

        self.mwSuper('__init__')

        # polarPlot ui instance has to be defined central, not in the mixins
        self.polarPlot = self.embedMatplot(self.ui.modelPolar)

        # connect signals for refreshing the gui
        self.app.mount.signals.pointDone.connect(self.updateStatusGUI)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)
        self.app.remoteCommand.connect(self.remoteCommand)
        self.app.astrometry.signals.message.connect(self.updateAstrometryStatus)
        self.app.dome.signals.message.connect(self.updateDomeStatus)
        self.app.imaging.signals.message.connect(self.updateImagingStatus)
        self.app.weather.signals.connected.connect(self.updateWeatherStat)

        # connect gui signals
        self.ui.saveConfigQuit.clicked.connect(self.app.quitSave)
        self.ui.loadFrom.clicked.connect(self.loadProfile)
        self.ui.saveConfigAs.clicked.connect(self.saveProfileAs)
        self.ui.saveConfig.clicked.connect(self.saveProfile)

        # initial call for writing the gui
        self.updateMountConnStat(None)
        self.initConfig()

        # cyclic updates
        self.app.update1s.connect(self.updateTime)
        self.app.update1s.connect(self.updateWindowsStats)
        self.app.update1s.connect(self.smartDeviceGui)
        self.app.update1s.connect(self.smartEnvironGui)
        self.app.update1s.connect(self.updateWindowsStats)
        self.app.update1s.connect(self.updateDeviceStats)

    def mwSuper(self, func):
        """
        mwSuper is a replacement for super() to manage the mixin style of implementation
        it's not an ideal way to do it, but mwSuper() call the method of every ! parent
        class if they exist.

        :param func:
        :return: true for test purpose
        """

        for base in self.__class__.__bases__:
            if base.__name__ == 'MWidget':
                continue
            if hasattr(base, func):
                funcAttrib = getattr(base, func)
                funcAttrib(self)
        return True

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config
        self.ui.profile.setText(config.get('profileName'))
        if 'mainW' not in config:
            config['mainW'] = {}
        config = config['mainW']
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        self.ui.mainTabWidget.setCurrentIndex(config.get('mainTabWidget', 0))
        self.ui.settingsTabWidget.setCurrentIndex(config.get('settingsTabWidget', 0))

        ################################################################################
        # remove analysis tab while not developed
        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Analyse')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)
        self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
        self.ui.mainTabWidget.setStyleSheet(self.getStyle())
        ################################################################################

        self.mwSuper('initConfig')
        self.changeStyleDynamic(self.ui.mountConnected, 'color', 'gray')

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

        self.mwSuper('storeConfig')
        return True

    def closeEvent(self, closeEvent):
        """
        we overwrite the close event of the window just for the main window to close the
        application as well. because it does not make sense to have child windows open if
        main is already closed.

        :return:    nothing
        """
        super().closeEvent(closeEvent)
        self.close()
        self.app.quit()

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """

        self.wIcon(self.ui.openMessageW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.openMeasureW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.openImageW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.openHemisphereW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.openSatelliteW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.saveConfigAs, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.loadFrom, PyQt5.QtWidgets.QStyle.SP_DirOpenIcon)
        self.wIcon(self.ui.saveConfig, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.saveConfigQuit, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.runFlexure, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.runHysteresis, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelAnalyse, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)

        self.wIcon(self.ui.plateSolveSync, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        pixmap = PyQt5.QtGui.QPixmap(':/azimuth1.png')
        self.ui.picAZ.setPixmap(pixmap)
        pixmap = PyQt5.QtGui.QPixmap(':/altitude1.png')
        self.ui.picALT.setPixmap(pixmap)
        pixmap = PyQt5.QtGui.QPixmap(':/offset.png')
        self.ui.picDome1.setPixmap(pixmap)

        self.wIcon(self.ui.cancelModel, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.runModel, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)

        self.wIcon(self.ui.genBuildGrid, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMax, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMed, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildNorm, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMin, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildDSO, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)

        self.wIcon(self.ui.runTargetRMS, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelTargetRMS, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.loadName, PyQt5.QtWidgets.QStyle.SP_DirOpenIcon)
        self.wIcon(self.ui.saveName, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.deleteName, PyQt5.QtWidgets.QStyle.SP_TrashIcon)
        self.wIcon(self.ui.refreshName, PyQt5.QtWidgets.QStyle.SP_BrowserReload)
        self.wIcon(self.ui.refreshModel, PyQt5.QtWidgets.QStyle.SP_BrowserReload)

        self.wIcon(self.ui.stop, PyQt5.QtWidgets.QStyle.SP_MessageBoxWarning)

        self.wIcon(self.ui.mountOn, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.mountOff, PyQt5.QtWidgets.QStyle.SP_MessageBoxCritical)
        self.wIcon(self.ui.renameStart, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)

        return True

    def updateMountConnStat(self, status):
        """
        updateMountConnStat show the connection status of the mount. if status is None,
        which means there is no valid host entry for connection, the status is grey

        :param status:
        :return: true for test purpose
        """

        self.deviceStat['mount'] = status
        return True

    def smartDeviceGui(self):
        """
        smartGui enables and disables gui actions depending on the actual state of the
        different devices. this should be the core of avoiding user misused during running
        operations. smartGui is run every 1 second synchronously, because it can't be
        simpler done with dynamic approach. all different situations in a running
        environment is done locally.

        :return: true for test purpose
        """

        tabChanged = False

        # check if modeling would work (mount + solve + image)
        if all(self.deviceStat[x] for x in ['mount', 'imaging', 'astrometry']):
            self.ui.runModel.setEnabled(True)
            self.ui.plateSolveSync.setEnabled(True)
            self.ui.runFlexure.setEnabled(True)
            self.ui.runHysteresis.setEnabled(True)
        else:
            self.ui.runModel.setEnabled(False)
            self.ui.plateSolveSync.setEnabled(False)
            self.ui.runFlexure.setEnabled(False)
            self.ui.runHysteresis.setEnabled(False)

        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'ManageModel')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)
        tabStatus = self.ui.mainTabWidget.isTabEnabled(tabIndex)

        if self.deviceStat.get('mount', False):
            self.ui.batchModel.setEnabled(True)
            self.ui.mainTabWidget.setTabEnabled(tabIndex, True)
            if not tabStatus:
                tabChanged = True
        else:
            self.ui.batchModel.setEnabled(False)
            self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
            if tabStatus:
                tabChanged = True

        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Power')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)
        tabStatus = self.ui.mainTabWidget.isTabEnabled(tabIndex)

        stat = self.deviceStat.get('power', None)
        if stat is None:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
            if tabStatus:
                tabChanged = True
        elif stat:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, True)
            if not tabStatus:
                tabChanged = True
        else:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, True)
            if not tabStatus:
                tabChanged = True

        stat = self.deviceStat.get('environOverall', None)
        if stat is None:
            self.ui.refractionGroup.setEnabled(False)
            self.ui.setRefractionManual.setEnabled(False)
        elif stat:
            self.ui.refractionGroup.setEnabled(True)
            self.ui.setRefractionManual.setEnabled(True)
        else:
            self.ui.refractionGroup.setEnabled(False)
            self.ui.setRefractionManual.setEnabled(False)

        # relay
        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Relay')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)
        tabStatus = self.ui.mainTabWidget.isTabEnabled(tabIndex)
        if tabStatus != self.deviceStat['relay']:
            tabChanged = True
        self.ui.mainTabWidget.setTabEnabled(tabIndex, self.deviceStat['relay'])

        # and setting
        tabWidget = self.ui.settingsTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'KMTronic')
        tabIndex = self.ui.settingsTabWidget.indexOf(tabWidget)
        tabStatus = self.ui.settingsTabWidget.isTabEnabled(tabIndex)
        if tabStatus != self.deviceStat['relay']:
            tabChanged = True
        self.ui.settingsTabWidget.setTabEnabled(tabIndex, self.deviceStat['relay'])

        # redraw tabs only when a change occurred
        if tabChanged:
            self.ui.mainTabWidget.setStyleSheet(self.getStyle())
            self.ui.settingsTabWidget.setStyleSheet(self.getStyle())

        return True

    def smartEnvironGui(self):
        """
        smartEnvironGui enables and disables gui actions depending on the actual state
        of the different environment devices. it is run every 1 second synchronously,
        because it can't be simpler done with dynamic approach. all different situations
        in a running environment is done locally.

        :return: true for test purpose
        """

        stat = self.deviceStat.get('internalSensor', None)
        if stat is None:
            self.ui.internalGroup.setFixedWidth(0)
            self.ui.internalGroup.setEnabled(False)
        elif stat:
            self.ui.internalGroup.setMinimumSize(75, 0)
            self.ui.internalGroup.setEnabled(True)
        else:
            self.ui.internalGroup.setMinimumSize(75, 0)
            self.ui.internalGroup.setEnabled(False)

        stat = self.deviceStat.get('environ', None)
        if stat is None:
            self.ui.environGroup.setFixedWidth(0)
            self.ui.environGroup.setEnabled(False)
        elif stat:
            self.ui.environGroup.setMinimumSize(75, 0)
            self.ui.environGroup.setEnabled(True)
        else:
            self.ui.environGroup.setMinimumSize(75, 0)
            self.ui.environGroup.setEnabled(False)

        stat = self.deviceStat.get('weather', None)
        if stat is None:
            self.ui.weatherGroup.setFixedWidth(0)
            self.ui.weatherGroup.setEnabled(False)
        elif stat:
            self.ui.weatherGroup.setMinimumSize(75, 0)
            self.ui.weatherGroup.setEnabled(True)
        else:
            self.ui.weatherGroup.setMinimumSize(75, 0)
            self.ui.weatherGroup.setEnabled(False)

        stat = self.deviceStat.get('skymeter', None)
        if stat is None:
            self.ui.skymeterGroup.setFixedWidth(0)
            self.ui.skymeterGroup.setEnabled(False)
        elif stat:
            self.ui.skymeterGroup.setMinimumSize(75, 0)
            self.ui.skymeterGroup.setEnabled(True)
        else:
            self.ui.skymeterGroup.setMinimumSize(75, 0)
            self.ui.skymeterGroup.setEnabled(False)

        stat = self.deviceStat.get('power', None)
        if stat is None:
            self.ui.powerGroup.setFixedWidth(0)
            self.ui.powerGroup.setEnabled(False)
        elif stat:
            self.ui.powerGroup.setMinimumSize(75, 0)
            self.ui.powerGroup.setEnabled(True)
        else:
            self.ui.powerGroup.setMinimumSize(75, 0)
            self.ui.powerGroup.setEnabled(False)

        return True

    def updateWindowsStats(self):
        """

        :return: True for test purpose
        """

        if self.app.messageW:
            self.changeStyleDynamic(self.ui.openMessageW, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.openMessageW, 'running', False)

        if self.app.hemisphereW:
            self.changeStyleDynamic(self.ui.openHemisphereW, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.openHemisphereW, 'running', False)

        if self.app.imageW:
            self.changeStyleDynamic(self.ui.openImageW, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.openImageW, 'running', False)

        if self.app.measureW:
            self.changeStyleDynamic(self.ui.openMeasureW, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.openMeasureW, 'running', False)

        if self.app.satelliteW:
            self.changeStyleDynamic(self.ui.openSatelliteW, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.openSatelliteW, 'running', False)

        return True

    def updateDeviceStats(self):
        """
        updateDeviceStats sets the colors in main window upper bar for getting
        important overview, which functions are available.

        :return: True for test purpose
        """

        # the refraction sources etc are defined in tabEnviron, but it is optimal
        # setting the selected source right at this point as it is synchronous if
        # state is switching

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

    def updateWeatherStat(self, stat):
        """

        :param stat:
        :return: True for test purpose
        """

        self.deviceStat['weather'] = stat

        return True

    def updateTime(self):
        """
        updateTime updates the time display in gui, show the actual thread count an the
        online status set

        :return: success
        """

        self.ui.timeComputer.setText(datetime.datetime.now().strftime('%H:%M:%S'))
        if self.ui.isOnline.isChecked():
            text = 'Internet Online Mode'
        else:
            text = 'Offline Mode'
        text = f'{self.threadPool.activeThreadCount():2d} - {text}'
        self.ui.statusOnline.setTitle(text)

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

    def updateImagingStatus(self, text):
        """

        :param text:
        :return: true for test purpose
        """

        self.ui.imagingText.setText(text)
        return True

    def updateStatusGUI(self, obs):
        """
        updateStatusGUI update the gui upon events triggered be the reception of new data
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

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

        :return:
        """

        folder = self.app.mwGlob['configDir']
        loadFilePath, name, ext = self.openFile(self,
                                                'Open config file',
                                                folder,
                                                'Config files (*.cfg)',
                                                enableDir=False,
                                                )
        if not name:
            return False
        suc = self.app.loadConfig(name=name)
        if suc:
            self.ui.profile.setText(name)
            self.app.message.emit('Profile: [{0}] loaded'.format(name), 0)
        else:
            self.app.message.emit('Profile: [{0}] cannot no be loaded'.format(name), 2)
        return True

    def saveProfileAs(self):
        """

        :return:
        """

        folder = self.app.mwGlob['configDir']
        saveFilePath, name, ext = self.saveFile(self,
                                                'Save config file',
                                                folder,
                                                'Config files (*.cfg)',
                                                enableDir=False,
                                                )
        if not name:
            return False
        self.app.storeConfig()
        self.app.config['profileName'] = name
        suc = self.app.saveConfig(name=name)
        if suc:
            self.ui.profile.setText(name)
            self.app.message.emit('Profile: [{0}] saved'.format(name), 0)
        else:
            self.app.message.emit('Profile: [{0}] cannot no be saved'.format(name), 2)
        return True

    def saveProfile(self):
        """
        saveProfile calls save profile in main and sends a message to the user about
        success.

        :return: nothing
        """

        self.app.storeConfig()
        suc = self.app.saveConfig()
        if suc:
            self.app.message.emit('Actual profile saved', 0)
        else:
            self.app.message.emit('Actual profile cannot not be saved', 2)
        return suc

    def remoteCommand(self, command):
        """

        :param command:
        :return:
        """

        if command == 'shutdown':
            self.app.quitSave()
            self.app.message.emit('Shutdown MW remotely', 2)
        elif command == 'shutdown mount':
            self.mountShutdown()
            self.app.message.emit('Shutdown mount remotely', 2)
        elif command == 'boot mount':
            self.mountBoot()
            self.app.message.emit('Boot mount remotely', 2)
