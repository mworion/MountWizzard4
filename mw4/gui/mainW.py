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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
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
from mw4.gui.mainWmixin.tabManageModel import ManageModel
from mw4.gui.mainWmixin.tabRelay import Relay
from mw4.gui.mainWmixin.tabPower import Power
from mw4.gui.mainWmixin.tabTools import Tools
from mw4.gui.mainWmixin.tabSettDevice import SettDevice
from mw4.gui.mainWmixin.tabSettIndi import SettIndi
from mw4.gui.mainWmixin.tabSettHorizon import SettHorizon
from mw4.gui.mainWmixin.tabSettParkPos import SettParkPos
from mw4.gui.mainWmixin.tabSettRelay import SettRelay
from mw4.gui.mainWmixin.tabSettMisc import SettMisc


class MainWindow(MWidget,
                 Mount,
                 Environ,
                 AlignMount,
                 BuildModel,
                 ManageModel,
                 Relay,
                 Power,
                 Tools,
                 SettDevice,
                 SettIndi,
                 SettHorizon,
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
    version = '0.6'
    logger = logging.getLogger(__name__)

    def __init__(self, app):
        self.app = app
        super().__init__()

        # load and init the gui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()
        self.setupIcons()
        self.setWindowTitle('MountWizzard4')
        self.typeConnectionTexts = ['serial RS-232 port',
                                    'GPS or GPS/RS-232 port',
                                    'cabled LAN port',
                                    'wireless LAN',
                                    ]

        self.status = False

        # local init of following
        Mount.__init__(self)
        Environ.__init__(self)
        AlignMount.__init__(self)
        BuildModel.__init__(self)
        ManageModel.__init__(self)
        Relay.__init__(self)
        Power.__init__(self)
        Tools.__init__(self)
        SettIndi.__init__(self)
        SettDevice.__init__(self)
        SettHorizon.__init__(self)
        SettParkPos.__init__(self)
        SettRelay.__init__(self)
        SettMisc.__init__(self)

        # polarPlot ui instance has to be defined central, not in the mixins
        self.polarPlot = self.embedMatplot(self.ui.modelPolar)

        # connect signals for refreshing the gui
        self.app.mount.signals.pointDone.connect(self.updateStatusGUI)
        self.app.mount.signals.settDone.connect(self.setMountMAC)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)
        self.app.remoteCommand.connect(self.remoteCommand)
        self.app.astrometry.signals.message.connect(self.updateAstrometryStatus)
        self.app.dome.signals.message.connect(self.updateDomeStatus)
        self.app.imaging.signals.message.connect(self.updateImagingStatus)

        # connect gui signals
        self.ui.saveConfigQuit.clicked.connect(self.app.quitSave)
        self.ui.mountOn.clicked.connect(self.mountBoot)
        self.ui.mountOff.clicked.connect(self.mountShutdown)
        self.ui.loadFrom.clicked.connect(self.loadProfile)
        self.ui.saveConfigAs.clicked.connect(self.saveProfileAs)
        self.ui.saveConfig.clicked.connect(self.saveProfile)
        self.ui.mountHost.editingFinished.connect(self.mountHost)
        self.ui.mountMAC.editingFinished.connect(self.mountMAC)
        self.ui.bootRackComp.clicked.connect(self.bootRackComp)

        # initial call for writing the gui
        self.updateMountConnStat(False)
        self.initConfig()

        # cyclic updates
        self.app.update1s.connect(self.updateTime)
        self.app.update1s.connect(self.updateWindowsStats)

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
        self.ui.mountHost.setText(config.get('mountHost', ''))
        self.mountHost()
        self.ui.mountMAC.setText(config.get('mountMAC', ''))
        self.mountMAC()
        self.ui.rackCompMAC.setText(config.get('rackCompMAC', ''))
        self.ui.expTime.setValue(config.get('expTime', 1))
        self.ui.binning.setValue(config.get('binning', 1))
        self.ui.subFrame.setValue(config.get('subFrame', 100))
        self.ui.checkFastDownload.setChecked(config.get('checkFastDownload', False))
        self.ui.checkKeepImages.setChecked(config.get('checkKeepImages', False))
        self.ui.settleTimeMount.setValue(config.get('settleTimeMount', 1))
        self.ui.settleTimeDome.setValue(config.get('settleTimeDome', 1))

        Mount.initConfig(self)
        Environ.initConfig(self)
        AlignMount.initConfig(self)
        BuildModel.initConfig(self)
        ManageModel.initConfig(self)
        Relay.initConfig(self)
        Power.initConfig(self)
        Tools.initConfig(self)
        SettIndi.initConfig(self)
        SettHorizon.initConfig(self)
        SettParkPos.initConfig(self)
        SettRelay.initConfig(self)
        SettMisc.initConfig(self)
        SettDevice.initConfig(self)

        fileName = self.app.config['mainW'].get('horizonFileName')
        self.app.data.loadHorizonP(fileName=fileName)
        self.changeStyleDynamic(self.ui.mountConnected, 'color', 'red')
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
        config['mountHost'] = self.ui.mountHost.text()
        config['mountMAC'] = self.ui.mountMAC.text()
        config['rackCompMAC'] = self.ui.rackCompMAC.text()
        config['expTime'] = self.ui.expTime.value()
        config['binning'] = self.ui.binning.value()
        config['subFrame'] = self.ui.subFrame.value()
        config['checkFastDownload'] = self.ui.checkFastDownload.isChecked()
        config['checkKeepImages'] = self.ui.checkKeepImages.isChecked()
        config['settleTimeMount'] = self.ui.settleTimeMount.value()
        config['settleTimeDome'] = self.ui.settleTimeDome.value()

        Mount.storeConfig(self)
        Environ.storeConfig(self)
        AlignMount.storeConfig(self)
        BuildModel.storeConfig(self)
        ManageModel.storeConfig(self)
        Relay.storeConfig(self)
        Power.storeConfig(self)
        Tools.storeConfig(self)
        SettIndi.storeConfig(self)
        SettHorizon.storeConfig(self)
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
        self.wIcon(self.ui.mountOn, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.mountOff, PyQt5.QtWidgets.QStyle.SP_MessageBoxCritical)
        self.wIcon(self.ui.runAlignModel, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelFullModel, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.runFullModel, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelAlignModel, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.runFlexure, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.runHysteresis, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelAnalyse, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)

        Mount.setupIcons(self)
        Environ.setupIcons(self)
        AlignMount.setupIcons(self)
        BuildModel.setupIcons(self)
        ManageModel.setupIcons(self)
        Relay.setupIcons(self)
        Power.setupIcons(self)
        Tools.setupIcons(self)
        SettDevice.setupIcons(self)
        SettIndi.setupIcons(self)
        SettHorizon.setupIcons(self)
        SettParkPos.setupIcons(self)
        SettRelay.setupIcons(self)
        SettMisc.setupIcons(self)
        return True

    def mountBoot(self):
        if self.app.mount.bootMount():
            self.app.message.emit('Sent boot command to mount', 0)
            return True
        else:
            self.app.message.emit('Mount cannot be booted', 2)
            return False

    def mountShutdown(self):
        if self.app.mount.shutdown():
            self.app.message.emit('Shutting mount down', 0)
            return True
        else:
            self.app.message.emit('Mount cannot be shutdown', 2)
            return False

    def checkFormatMAC(self, value):
        """
        checkFormatMAC makes some checks to ensure that the format of the string is ok for
        WOL package.

        :param      value: string with mac address
        :return:    checked string in upper cases
        """

        if not value:
            self.logger.error('wrong MAC value: {0}'.format(value))
            return None
        if not isinstance(value, str):
            self.logger.error('wrong MAC value: {0}'.format(value))
            return None
        value = value.upper()
        value = value.replace('.', ':')
        value = value.split(':')
        if len(value) != 6:
            self.logger.error('wrong MAC value: {0}'.format(value))
            return None
        for chunk in value:
            if len(chunk) != 2:
                self.logger.error('wrong MAC value: {0}'.format(value))
                return None
            for char in chunk:
                if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                                'A', 'B', 'C', 'D', 'E', 'F']:
                    self.logger.error('wrong MAC value: {0}'.format(value))
                    return None
        # now we build the right format
        value = '{0:2s}:{1:2s}:{2:2s}:{3:2s}:{4:2s}:{5:2s}'.format(*value)
        return value

    def bootRackComp(self):
        MAC = self.ui.rackCompMAC.text()
        MAC = self.checkFormatMAC(MAC)
        if MAC is not None:
            wakeonlan.send_magic_packet(MAC)
            self.app.message.emit('Sent boot command to rack computer', 0)
            return True
        else:
            self.app.message.emit('Rack computer cannot be booted', 2)
            return False

    def updateMountConnStat(self, status):
        """
        updateMountConnStat show the connection status of the mount.

        :param status:
        :return: status changed or new
        """

        ui = self.ui.mountConnected
        if self.status == status:
            return False

        if status:
            self.changeStyleDynamic(ui, 'color', 'green')
            self.ui.runFullModel.setEnabled(True)
            self.ui.runAlignModel.setEnabled(True)
            self.ui.plateSolveSync.setEnabled(True)
            self.ui.runFlexure.setEnabled(True)
            self.ui.runHysteresis.setEnabled(True)
        else:
            self.changeStyleDynamic(ui, 'color', 'red')
            self.ui.runFullModel.setEnabled(False)
            self.ui.runAlignModel.setEnabled(False)
            self.ui.plateSolveSync.setEnabled(False)
            self.ui.runFlexure.setEnabled(False)
            self.ui.runHysteresis.setEnabled(False)

        self.status = status
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

        return True

    def updateTime(self):
        """
        updateTime updates the time display in gui

        :return: success
        """

        self.ui.timeComputer.setText(datetime.datetime.now().strftime('%H:%M:%S'))
        # print(self.app.threadPool.activeThreadCount())

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

    def mountHost(self):
        self.app.mount.host = self.ui.mountHost.text()

    def mountMAC(self):
        self.app.mount.MAC = self.ui.mountMAC.text()

    def setMountMAC(self, sett):
        """

        :param sett:
        :return:
        """

        if sett.addressLanMAC is not None and sett.addressLanMAC:
            self.app.mount.MAC = sett.addressLanMAC
        if self.app.mount.MAC is not None:
            self.ui.mountMAC.setText(self.app.mount.MAC)

        if sett.typeConnection is not None:
            text = self.typeConnectionTexts[sett.typeConnection]
            self.ui.mountTypeConnection.setText(text)

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
