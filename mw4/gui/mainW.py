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
from mw4.gui import widget
from mw4.gui.widgets import main_ui
from mw4.gui.mainWmixin import tabSettHorizon
from mw4.gui.mainWmixin import tabAlignMount
from mw4.gui.mainWmixin import tabBuildModel
from mw4.gui.mainWmixin import tabSiteStatus
from mw4.gui.mainWmixin import tabRelay
from mw4.gui.mainWmixin import tabMount
from mw4.gui.mainWmixin import tabManageModel


class MainWindow(widget.MWidget,
                 tabSettHorizon.SettHorizon,
                 tabAlignMount.AlignMount,
                 tabBuildModel.BuildModel,
                 tabSiteStatus.SiteStatus,
                 tabRelay.Relay,
                 tabMount.Mount,
                 tabManageModel.ManageModel):
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
        self.config = {}
        super().__init__()
        # load and init the gui
        self.ui = main_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()
        self.setupIcons()
        self.setWindowTitle('MountWizzard4   (' + self.app.mwGlob['modeldata'] + ')')

        # polarPlot ui instance has to be defined central, not in the mixins
        self.polarPlot = self.embedMatplot(self.ui.modelPolar)

        # connect signals for refreshing the gui
        ms = self.app.mount.signals
        ms.pointDone.connect(self.updateStatusGUI)
        ms.namesDone.connect(self.setNameList)
        ms.fwDone.connect(self.updateFwGui)
        ms.mountUp.connect(self.updateMountConnStat)
        ms.mountClear.connect(self.clearMountGUI)

        # connect gui signals
        self.ui.saveConfigQuit.clicked.connect(self.app.quitSave)
        self.ui.mountOn.clicked.connect(self.mountBoot)
        self.ui.mountOff.clicked.connect(self.mountShutdown)
        self.ui.loadFrom.clicked.connect(self.loadProfile)
        self.ui.saveConfigAs.clicked.connect(self.saveProfileAs)
        self.ui.saveConfig.clicked.connect(self.saveProfile)
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelInfo.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelWarning.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelError.clicked.connect(self.setLoggingLevel)
        self.ui.checkEnableRelay.clicked.connect(self.enableRelay)
        self.ui.relayHost.editingFinished.connect(self.relayHost)
        self.ui.relayUser.editingFinished.connect(self.relayUser)
        self.ui.relayPassword.editingFinished.connect(self.relayPassword)
        self.ui.mountHost.editingFinished.connect(self.mountHost)
        self.ui.mountMAC.editingFinished.connect(self.mountMAC)
        self.ui.indiHost.editingFinished.connect(self.indiHost)
        self.ui.localWeatherName.editingFinished.connect(self.localWeatherName)
        self.ui.globalWeatherName.editingFinished.connect(self.globalWeatherName)
        self.ui.sqmName.editingFinished.connect(self.sqmName)
        self.ui.reconnectIndiServer.clicked.connect(self.app.environment.reconnectIndiServer)

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
        if 'mainW' not in self.app.config:
            self.app.config['mainW'] = {}
        config = self.app.config['mainW']
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        self.ui.mainTabWidget.setCurrentIndex(config.get('mainTabWidget', 0))
        self.ui.settingsTabWidget.setCurrentIndex(config.get('settingsTabWidget', 0))
        self.ui.loglevelDebug.setChecked(config.get('loglevelDebug', True))
        self.ui.loglevelInfo.setChecked(config.get('loglevelInfo', False))
        self.ui.loglevelWarning.setChecked(config.get('loglevelWarning', False))
        self.ui.loglevelError.setChecked(config.get('loglevelError', False))
        self.ui.expiresYes.setChecked(config.get('expiresYes', True))
        self.ui.expiresNo.setChecked(config.get('expiresNo', False))
        self.ui.profile.setText(self.app.config.get('profileName'))
        self.ui.checkEnableRelay.setChecked(config.get('checkEnableRelay', False))
        self.enableRelay()
        self.ui.relayHost.setText(config.get('relayHost', ''))
        self.relayHost()
        self.ui.relayUser.setText(config.get('relayUser', ''))
        self.relayUser()
        self.ui.relayPassword.setText(config.get('relayPassword', ''))
        self.relayPassword()
        self.ui.mountHost.setText(config.get('mountHost', ''))
        self.mountHost()
        self.ui.mountMAC.setText(config.get('mountMAC', ''))
        self.mountMAC()
        environ = self.app.environment
        self.ui.indiHost.setText(config.get('indiHost', ''))
        environ.client.host = config.get('indiHost', '')
        self.ui.globalWeatherName.setText(config.get('globalWeatherName', ''))
        environ.globalWeatherName = config.get('globalWeatherName', '')
        self.ui.localWeatherName.setText(config.get('localWeatherName', ''))
        environ.localWeatherName = config.get('localWeatherName', '')
        self.ui.sqmName.setText(config.get('sqmName', ''))
        environ.sqmName = config.get('sqmName', '')
        self.ui.ccdName.setText(config.get('ccdName', ''))
        self.ui.domeName.setText(config.get('domeName', ''))

        self.setLoggingLevel()

        super().initConfig()
        return True

    def storeConfig(self):
        if 'mainW' not in self.app.config:
            self.app.config['mainW'] = {}
        config = self.app.config['mainW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['mainTabWidget'] = self.ui.mainTabWidget.currentIndex()
        config['settingsTabWidget'] = self.ui.settingsTabWidget.currentIndex()
        config['loglevelDebug'] = self.ui.loglevelDebug.isChecked()
        config['loglevelInfo'] = self.ui.loglevelInfo.isChecked()
        config['loglevelWarning'] = self.ui.loglevelWarning.isChecked()
        config['loglevelError'] = self.ui.loglevelError.isChecked()
        config['expiresYes'] = self.ui.expiresYes.isChecked()
        config['expiresNo'] = self.ui.expiresNo.isChecked()
        config['profile'] = self.ui.profile.text()
        config['checkEnableRelay'] = self.ui.checkEnableRelay.isChecked()
        config['relayHost'] = self.ui.relayHost.text()
        config['relayUser'] = self.ui.relayUser.text()
        config['relayPassword'] = self.ui.relayPassword.text()
        config['mountHost'] = self.ui.mountHost.text()
        config['mountMAC'] = self.ui.mountMAC.text()
        config['indiHost'] = self.ui.indiHost.text()
        config['localWeatherName'] = self.ui.localWeatherName.text()
        config['globalWeatherName'] = self.ui.globalWeatherName.text()
        config['sqmName'] = self.ui.sqmName.text()
        config['domeName'] = self.ui.domeName.text()
        config['ccdName'] = self.ui.ccdName.text()

        super().storeConfig()
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

        super().setupIcons()
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

        super().clearMountGUI()
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
        folder = self.app.mwGlob['configDir'] + '/config'
        loadFilePath, name, ext = self.openFile(self,
                                                'Open config file',
                                                folder,
                                                'Config files (*.cfg)',
                                                )
        if not loadFilePath:
            return False
        loadFilePath = self.checkExtension(loadFilePath, '.cfg')
        suc = self.app.loadConfig(loadFilePath=loadFilePath)
        if suc:
            self.ui.profile.setText(name)
            self.app.message.emit('Profile: [{0}] loaded'.format(name), 0)
        else:
            self.app.message.emit('Profile: [{0}] cannot no be loaded'.format(name), 2)
        return True

    def saveProfileAs(self):
        folder = self.app.mwGlob['configDir'] + '/config'
        saveFilePath, name, ext = self.saveFile(self,
                                                'Save config file',
                                                folder,
                                                'Config files (*.cfg)',
                                                )
        if not saveFilePath:
            return False
        self.app.storeConfig()
        self.app.config['profileName'] = name
        saveFilePath = self.checkExtension(saveFilePath, '.cfg')
        suc = self.app.saveConfig(saveFilePath=saveFilePath)
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

    def setLoggingLevel(self):
        """
        Setting the log level according to the setting in the gui.

        :return: nothing
        """

        if self.ui.loglevelDebug.isChecked():
            logging.getLogger().setLevel(logging.DEBUG)
        elif self.ui.loglevelInfo.isChecked():
            logging.getLogger().setLevel(logging.INFO)
        elif self.ui.loglevelWarning.isChecked():
            logging.getLogger().setLevel(logging.WARNING)
        elif self.ui.loglevelError.isChecked():
            logging.getLogger().setLevel(logging.ERROR)

    def setupRelayGui(self):
        """
        setupRelayGui handles the modeldata of list for relay handling. to keep many relay in
        order i collect them in the list for list handling afterwards.

        :return: success for test
        """

        self.relayDropDown = list()
        self.relayButton = list()
        self.relayText = list()
        for i in range(0, 8):
            self.relayDropDown.append(eval('self.ui.relayFun{0:1d}'.format(i)))
            self.relayButton.append(eval('self.ui.relayButton{0:1d}'.format(i)))
            self.relayText.append(eval('self.ui.relayText{0:1d}'.format(i)))
        # and setting the entries of the drop down menus
        for dropDown in self.relayDropDown:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('Switch - Toggle')
            dropDown.addItem('Pulse 0.5 sec')
        return True

    def enableRelay(self):
        """
        enableRelay allows to run the relay box.

        :return: success for test
        """

        # get index for relay tab
        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Relay')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)

        if self.ui.checkEnableRelay.isChecked():
            self.ui.mainTabWidget.setTabEnabled(tabIndex, True)
            self.app.message.emit('Relay enabled', 0)
            self.app.relay.startTimers()
        else:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
            self.app.message.emit('Relay disabled', 0)
            self.app.relay.stopTimers()
        # update the style for showing the Relay tab
        self.ui.mainTabWidget.style().unpolish(self.ui.mainTabWidget)
        self.ui.mainTabWidget.style().polish(self.ui.mainTabWidget)
        return True

    def relayHost(self):
        self.app.relay.host = self.ui.relayHost.text()

    def relayUser(self):
        self.app.relay.user = self.ui.relayUser.text()

    def relayPassword(self):
        self.app.relay.password = self.ui.relayPassword.text()

    def mountHost(self):
        self.app.mount.host = self.ui.mountHost.text()

    def mountMAC(self):
        self.app.mount.MAC = self.ui.mountMAC.text()

    def indiHost(self):
        host = self.ui.indiHost.text()
        self.app.environment.client.host = host

    def localWeatherName(self):
        environ = self.app.environment
        environ.localWeatherName = self.ui.localWeatherName.text()

    def globalWeatherName(self):
        environ = self.app.environment
        environ.globalWeatherName = self.ui.globalWeatherName.text()

    def sqmName(self):
        environ = self.app.environment
        environ.sqmName = self.ui.sqmName.text()

    def autoDeletePoints(self):
        """
        autoDeletePoints removes all generated or visible build points below the horizon line
        and redraws the hemisphere window.

        :return: True for test purpose
        """

        if self.ui.checkAutoDeletePoints.isChecked():
            self.app.data.deleteBelowHorizon()
        self.app.hemisphereW.drawHemisphere()
        return True
