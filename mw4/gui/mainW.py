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
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import
from mw4.gui.widget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.mainWmixin.tabMount import Mount
from mw4.gui.mainWmixin.tabSiteStatus import SiteStatus
from mw4.gui.mainWmixin.tabAlignMount import AlignMount
from mw4.gui.mainWmixin.tabBuildModel import BuildModel
from mw4.gui.mainWmixin.tabManageModel import ManageModel
from mw4.gui.mainWmixin.tabRelay import Relay
from mw4.gui.mainWmixin.tabSettIndi import SettIndi
from mw4.gui.mainWmixin.tabSettHorizon import SettHorizon
from mw4.gui.mainWmixin.tabSettParkPos import SettParkPos
from mw4.gui.mainWmixin.tabSettRelay import SettRelay
from mw4.gui.mainWmixin.tabSettMisc import SettMisc


class MainWindow(MWidget,
                 Mount,
                 SiteStatus,
                 AlignMount,
                 BuildModel,
                 ManageModel,
                 Relay,
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

    CYCLE_GUI = 1000
    CYCLE_UPDATE_TASK = 10000

    def __init__(self, app):
        self.app = app
        super().__init__()

        # load and init the gui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()
        self.setupIcons()
        self.setWindowTitle('MountWizzard4')

        # local init of following
        Mount.__init__(self)
        SiteStatus.__init__(self)
        AlignMount.__init__(self)
        BuildModel.__init__(self)
        ManageModel.__init__(self)
        Relay.__init__(self)
        SettIndi.__init__(self)
        SettHorizon.__init__(self)
        SettParkPos.__init__(self)
        SettRelay.__init__(self)
        SettMisc.__init__(self)

        # polarPlot ui instance has to be defined central, not in the mixins
        self.polarPlot = self.embedMatplot(self.ui.modelPolar)

        # connect signals for refreshing the gui
        ms = self.app.mount.signals
        ms.pointDone.connect(self.updateStatusGUI)
        ms.settDone.connect(self.setMountMAC)
        ms.mountUp.connect(self.updateMountConnStat)
        ms.mountClear.connect(self.clearMountGUI)

        # connect gui signals
        self.ui.saveConfigQuit.clicked.connect(self.app.quitSave)
        self.ui.mountOn.clicked.connect(self.mountBoot)
        self.ui.mountOff.clicked.connect(self.mountShutdown)
        self.ui.loadFrom.clicked.connect(self.loadProfile)
        self.ui.saveConfigAs.clicked.connect(self.saveProfileAs)
        self.ui.saveConfig.clicked.connect(self.saveProfile)
        self.ui.mountHost.editingFinished.connect(self.mountHost)
        self.ui.mountMAC.editingFinished.connect(self.mountMAC)

        # initial call for writing the gui
        self.updateMountConnStat(False)
        self.initConfig()
        self.show()

        self.timerGui = PyQt5.QtCore.QTimer()
        self.timerGui.setSingleShot(False)
        self.timerGui.timeout.connect(self.updateGUI)
        self.timerGui.start(self.CYCLE_GUI)
        self.timerTask = PyQt5.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.updateTask)
        self.timerTask.start(self.CYCLE_UPDATE_TASK)

    def initConfig(self):
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

        Mount.initConfig(self)
        SiteStatus.initConfig(self)
        AlignMount.initConfig(self)
        BuildModel.initConfig(self)
        ManageModel.initConfig(self)
        Relay.initConfig(self)
        SettIndi.initConfig(self)
        SettHorizon.initConfig(self)
        SettParkPos.initConfig(self)
        SettRelay.initConfig(self)
        SettMisc.initConfig(self)
        return True

    def storeConfig(self):
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

        Mount.storeConfig(self)
        SiteStatus.storeConfig(self)
        AlignMount.storeConfig(self)
        BuildModel.storeConfig(self)
        ManageModel.storeConfig(self)
        Relay.storeConfig(self)
        SettIndi.storeConfig(self)
        SettHorizon.storeConfig(self)
        SettParkPos.storeConfig(self)
        SettRelay.storeConfig(self)
        SettMisc.storeConfig(self)
        return True

    def closeEvent(self, closeEvent):
        """
        we overwrite the close event of the window just for the main window to close the
        application as well. because it does not make sense to have child windows open if
        main is already closed.

        :return:    nothing
        """

        self.showStatus = False
        self.hide()
        self.app.quit()

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """

        self.wIcon(self.ui.openMessageW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.openAnalyseW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.openImageW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.openHemisphereW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.openSatelliteW, PyQt5.QtWidgets.QStyle.SP_ComputerIcon)
        self.wIcon(self.ui.saveConfigAs, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.loadFrom, PyQt5.QtWidgets.QStyle.SP_DirOpenIcon)
        self.wIcon(self.ui.saveConfig, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.saveConfigQuit, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.mountOn, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.mountOff, PyQt5.QtWidgets.QStyle.SP_MessageBoxCritical)
        self.wIcon(self.ui.runInitialModel, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelFullModel, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.runFullModel, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelInitialModel, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.runFlexure, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.runHysteresis, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelAnalyse, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)

        Mount.setupIcons(self)
        SiteStatus.setupIcons(self)
        AlignMount.setupIcons(self)
        BuildModel.setupIcons(self)
        ManageModel.setupIcons(self)
        Relay.setupIcons(self)
        SettIndi.setupIcons(self)
        SettHorizon.setupIcons(self)
        SettParkPos.setupIcons(self)
        SettRelay.setupIcons(self)
        SettMisc.setupIcons(self)
        return True

    def mountBoot(self):
        if self.app.mount.bootMount():
            self.app.message.emit('Mount booted', 0)
            return True
        else:
            self.app.message.emit('Mount cannot be booted', 2)
            return False

    def mountShutdown(self):
        if self.app.mount.obsSite.shutdown():
            self.app.message.emit('Shutting mount down', 0)
            return True
        else:
            self.app.message.emit('Mount cannot be shutdown', 2)
            return False

    def clearMountGUI(self):
        """
        clearMountGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """

        self.updateStatusGUI()

        Mount.clearMountGUI(self)
        SiteStatus.clearMountGUI(self)
        AlignMount.clearMountGUI(self)
        BuildModel.clearMountGUI(self)
        ManageModel.clearMountGUI(self)
        Relay.clearMountGUI(self)
        SettIndi.clearMountGUI(self)
        SettHorizon.clearMountGUI(self)
        SettParkPos.clearMountGUI(self)
        SettRelay.clearMountGUI(self)
        SettMisc.clearMountGUI(self)

        return True

    def updateMountConnStat(self, status):
        ui = self.ui.mountConnected
        if status:
            self.changeStyleDynamic(ui, 'color', 'green')
        else:
            self.changeStyleDynamic(ui, 'color', 'red')
        return True

    def updateGUI(self):
        """
        updateGUI update gui elements on regular bases (actually 1 second) for items,
        which are not events based.

        :return: success
        """
        self.ui.timeComputer.setText(datetime.datetime.now().strftime('%H:%M:%S'))
        return True

    def updateTask(self):
        """
        updateTask calls tasks for items, which are not event based, like updating
        refraction parameters.

        :return: success for test purpose
        """

        self.updateRefractionParameters()
        return True

    def updateStatusGUI(self):
        """
        updateStatusGUI update the gui upon events triggered be the reception of new data
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

        :return:    True if ok for testing
        """
        obs = self.app.mount.obsSite

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
        if not filePath.endswith(ext):
            filePath += ext
        return filePath

    def loadProfile(self):
        folder = self.app.mwGlob['configDir']
        loadFilePath, name, ext = self.openFile(self,
                                                'Open config file',
                                                folder,
                                                'Config files (*.cfg)',
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
        folder = self.app.mwGlob['configDir']
        saveFilePath, name, ext = self.saveFile(self,
                                                'Save config file',
                                                folder,
                                                'Config files (*.cfg)',
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

    def mountHost(self):
        self.app.mount.host = self.ui.mountHost.text()

    def mountMAC(self):
        self.app.mount.MAC = self.ui.mountMAC.text()

    def setMountMAC(self):
        sett = self.app.mount.sett
        if sett.addressLanMAC is not None and sett.addressLanMAC:
            self.app.mount.MAC = sett.addressLanMAC
        if self.app.mount.MAC is not None:
            self.ui.mountMAC.setText(self.app.mount.MAC)
        typeConnectionTexts = ['serial RS-232 port',
                               'GPS or GPS/RS-232 port',
                               'cabled LAN port',
                               'wireless LAN',
                               ]
        if sett.typeConnection is not None:
            text = typeConnectionTexts[sett.typeConnection]
            self.ui.mountTypeConnection.setText(text)

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
