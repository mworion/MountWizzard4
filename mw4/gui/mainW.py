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
from mw4.gui.mainWmixin.tabEnviron import Environ
from mw4.gui.mainWmixin.tabAlignMount import AlignMount
from mw4.gui.mainWmixin.tabBuildModel import BuildModel
from mw4.gui.mainWmixin.tabBuildFunc import BuildFunc
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
                 Environ,
                 AlignMount,
                 BuildModel,
                 BuildFunc,
                 ManageModel,
                 Satellite,
                 Relay,
                 Power,
                 Tools,
                 SettDevice,
                 SettIndi,
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
        self.setWindowTitle(f'MountWizzard4 - v{self.app.version}')

        self.deviceStat = {
            'dome': None,
            'mount': None,
            'imaging': None,
            'astrometry': None,
            'environ': None,
            'skymeter': None,
            'power': None,
        }
        self.deviceStatGui = {'dome': self.ui.domeConnected,
                              'imaging': self.ui.imagingConnected,
                              'environment': self.ui.environConnected,
                              'astrometry': self.ui.astrometryConnected,
                              'mount': self.ui.mountConnected}

        # local init of following
        Mount.__init__(self)
        Environ.__init__(self)
        AlignMount.__init__(self)
        BuildModel.__init__(self)
        BuildFunc.__init__(self)
        ManageModel.__init__(self)
        Satellite.__init__(self)
        Relay.__init__(self)
        Power.__init__(self)
        Tools.__init__(self)
        SettIndi.__init__(self)
        SettMount.__init__(self)
        SettDevice.__init__(self)
        SettHorizon.__init__(self)
        SettImaging.__init__(self)
        SettParkPos.__init__(self)
        SettRelay.__init__(self)
        SettMisc.__init__(self)

        # polarPlot ui instance has to be defined central, not in the mixins
        self.polarPlot = self.embedMatplot(self.ui.modelPolar)

        # connect signals for refreshing the gui
        self.app.mount.signals.pointDone.connect(self.updateStatusGUI)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)
        self.app.remoteCommand.connect(self.remoteCommand)
        self.app.astrometry.signals.message.connect(self.updateAstrometryStatus)
        self.app.dome.signals.message.connect(self.updateDomeStatus)
        self.app.imaging.signals.message.connect(self.updateImagingStatus)

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
        self.app.update1s.connect(self.smartGui)
        self.app.update1s.connect(self.updateWindowsStats)
        self.app.update1s.connect(self.updateDeviceStats)

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

        Mount.initConfig(self)
        Environ.initConfig(self)
        AlignMount.initConfig(self)
        BuildModel.initConfig(self)
        BuildFunc.initConfig(self)
        ManageModel.initConfig(self)
        Satellite.initConfig(self)
        Relay.initConfig(self)
        Power.initConfig(self)
        Tools.initConfig(self)
        SettIndi.initConfig(self)
        SettMount.initConfig(self)
        SettHorizon.initConfig(self)
        SettImaging.initConfig(self)
        SettParkPos.initConfig(self)
        SettRelay.initConfig(self)
        SettMisc.initConfig(self)
        SettDevice.initConfig(self)

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

        Mount.storeConfig(self)
        Environ.storeConfig(self)
        AlignMount.storeConfig(self)
        BuildModel.storeConfig(self)
        BuildFunc.storeConfig(self)
        ManageModel.storeConfig(self)
        Satellite.storeConfig(self)
        Relay.storeConfig(self)
        Power.storeConfig(self)
        Tools.storeConfig(self)
        SettIndi.storeConfig(self)
        SettMount.storeConfig(self)
        SettHorizon.storeConfig(self)
        SettImaging.storeConfig(self)
        SettParkPos.storeConfig(self)
        SettRelay.storeConfig(self)
        SettMisc.storeConfig(self)
        SettDevice.storeConfig(self)

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

        Mount.setupIcons(self)
        Environ.setupIcons(self)
        AlignMount.setupIcons(self)
        BuildModel.setupIcons(self)
        BuildFunc.setupIcons(self)
        ManageModel.setupIcons(self)
        Satellite.setupIcons(self)
        Relay.setupIcons(self)
        Power.setupIcons(self)
        Tools.setupIcons(self)
        SettDevice.setupIcons(self)
        SettIndi.setupIcons(self)
        SettMount.setupIcons(self)
        SettHorizon.setupIcons(self)
        SettImaging.setupIcons(self)
        SettParkPos.setupIcons(self)
        SettRelay.setupIcons(self)
        SettMisc.setupIcons(self)
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

    def smartGui(self):
        """
        smartGui enables and disables gui actions depending on the actual state of the
        different devices. this should be the core of avoiding user misused during running
        operations. smartGui is run every 1 second synchronously, because it can't be
        simpler done with dynamic approach. all different situations in a running
        environment is done locally.

        :return: true for test purpose
        """
        # check if modeling would work (mount + solve + image)
        if all(self.deviceStat[x] for x in ['mount', 'imaging', 'astrometry']):
            self.ui.runFullModel.setEnabled(True)
            self.ui.runAlignModel.setEnabled(True)
            self.ui.plateSolveSync.setEnabled(True)
            self.ui.runFlexure.setEnabled(True)
            self.ui.runHysteresis.setEnabled(True)
        else:
            self.ui.runFullModel.setEnabled(False)
            self.ui.runAlignModel.setEnabled(False)
            self.ui.plateSolveSync.setEnabled(False)
            self.ui.runFlexure.setEnabled(False)
            self.ui.runHysteresis.setEnabled(False)

        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'ManageModel')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)

        if self.deviceStat['mount']:
            self.ui.batchModel.setEnabled(True)
            self.ui.mainTabWidget.setTabEnabled(tabIndex, True)
            self.ui.mainTabWidget.setStyleSheet(self.getStyle())
        else:
            self.ui.batchModel.setEnabled(False)
            self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
            self.ui.mainTabWidget.setStyleSheet(self.getStyle())

        if self.deviceStat['environment']:
            self.ui.environGroup.setEnabled(True)
            self.ui.refractionGroup.setEnabled(True)
            self.ui.setRefractionManual.setEnabled(True)
        else:
            self.ui.environGroup.setEnabled(False)
            self.ui.refractionGroup.setEnabled(False)
            self.ui.setRefractionManual.setEnabled(False)

        if self.deviceStat['skymeter']:
            self.ui.skymeterGroup.setEnabled(True)
        else:
            self.ui.skymeterGroup.setEnabled(False)

        if self.deviceStat['power']:
            self.ui.powerGroup.setEnabled(True)
        else:
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

        :return: True for test purpose
        """

        for device, ui in self.deviceStatGui.items():
            if self.deviceStat[device] is None:
                self.changeStyleDynamic(ui, 'color', 'gray')
            elif self.deviceStat[device]:
                self.changeStyleDynamic(ui, 'color', 'green')
            else:
                self.changeStyleDynamic(ui, 'color', 'red')

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
        self.ui.statusOnline.setText(text)

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

    def autoDeletePoints(self):
        """
        autoDeletePoints removes all generated or visible build points below the horizon line
        and redraws the hemisphere window.

        :return: True for test purpose
        """

        if self.ui.checkAutoDeletePoints.isChecked():
            self.app.data.deleteBelowHorizon()
        self.app.redrawHemisphere.emit()
        return True

    def autoSortPoints(self):
        """
        autoSortPoints sort the given build point first to east and west and than based
        on the decision high altitude to low altitude or east to west in each hemisphere

        :return: success if sorted
        """

        eastwest = self.ui.checkSortEW.isChecked()
        highlow = self.ui.checkSortHL.isChecked()

        if not eastwest and not highlow:
            return False

        self.app.data.sort(eastwest=eastwest, highlow=highlow)
        self.app.redrawHemisphere.emit()

        return True
