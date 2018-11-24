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
# Python  v3.6.5
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
import numpy as np
import matplotlib.pyplot
from mountcontrol import convert
# local import
from mw4.gui import widget
from mw4.gui.widgets import main_ui


class MainWindow(widget.MWidget):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    __all__ = ['MainWindow',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    CYCLE_GUI = 1000

    def __init__(self, app):
        super().__init__()

        self.app = app
        # self.tPool = PyQt5.QtCore.QThreadPool()
        self.relayDropDown = list()
        self.relayButton = list()
        self.relayText = list()

        # load and init the gui
        self.ui = main_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()
        self.setupIcons()
        self.setWindowTitle('MountWizzard4   (' + self.app.mwGlob['build'] + ')')
        self.setupRelayGui()

        # defining the necessary instances of classes
        self.polarPlot = self.embedMatplot(self.ui.modelPolar)
        self.showModelPolar()

        # connect signals for refreshing the gui
        self.app.mount.signals.pointDone.connect(self.updatePointGUI)
        self.app.mount.signals.settDone.connect(self.updateSettingGUI)
        self.app.mount.signals.alignDone.connect(self.updateAlignGUI)
        self.app.mount.signals.alignDone.connect(self.showModelPolar)
        self.app.mount.signals.namesDone.connect(self.setNameList)
        self.app.mount.signals.fwDone.connect(self.updateFwGui)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)
        self.app.mount.signals.mountClear.connect(self.clearMountGUI)
        self.app.relay.statusReady.connect(self.updateRelayGui)
        self.app.environment.client.signals.serverConnected.connect(self.indiEnvironConnected)
        self.app.environment.client.signals.serverDisconnected.connect(self.indiEnvironDisconnected)
        self.app.environment.client.signals.newDevice.connect(self.newEnvironDevice)
        self.app.environment.client.signals.newProperty.connect(self.deviceEnvironConnected)
        self.app.environment.client.signals.removeDevice.connect(self.deviceEnvironConnected)
        self.app.environment.client.signals.newNumber.connect(self.updateEnvironGUI)

        # connect gui signals
        self.ui.checkShowErrorValues.stateChanged.connect(self.showModelPolar)
        self.ui.saveConfigQuit.clicked.connect(self.app.quitSave)
        self.ui.mountOn.clicked.connect(self.mountBoot)
        self.ui.mountOff.clicked.connect(self.mountShutdown)
        self.ui.park.clicked.connect(self.changePark)
        self.ui.tracking.clicked.connect(self.changeTracking)
        self.ui.setLunarTracking.clicked.connect(self.setLunarTracking)
        self.ui.setSiderealTracking.clicked.connect(self.setSiderealTracking)
        self.ui.setSolarTracking.clicked.connect(self.setSolarTracking)
        self.ui.loadFrom.clicked.connect(self.loadProfile)
        self.ui.saveConfigAs.clicked.connect(self.saveProfileAs)
        self.ui.saveConfig.clicked.connect(self.saveProfile)
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelInfo.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelWarning.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelError.clicked.connect(self.setLoggingLevel)
        self.clickable(self.ui.meridianLimitTrack).connect(self.setMeridianLimitTrack)
        self.clickable(self.ui.meridianLimitSlew).connect(self.setMeridianLimitSlew)
        self.clickable(self.ui.horizonLimitHigh).connect(self.setHorizonLimitHigh)
        self.clickable(self.ui.horizonLimitLow).connect(self.setHorizonLimitLow)
        self.clickable(self.ui.slewRate).connect(self.setSlewRate)
        self.clickable(self.ui.siteLatitude).connect(self.setLatitude)
        self.clickable(self.ui.siteLongitude).connect(self.setLongitude)
        self.clickable(self.ui.siteElevation).connect(self.setElevation)
        for button in self.relayButton:
            button.clicked.connect(self.toggleRelay)
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
        self.enableRelay()
        self.initConfig()
        self.show()

        self.timerGui = PyQt5.QtCore.QTimer()
        self.timerGui.setSingleShot(False)
        self.timerGui.timeout.connect(self.updateGUICyclic)
        self.timerGui.start(self.CYCLE_GUI)

    def initConfig(self):
        if 'mainW' not in self.app.config:
            return
        config = self.app.config['mainW']
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        self.ui.loglevelDebug.setChecked(config.get('loglevelDebug', True))
        self.ui.loglevelInfo.setChecked(config.get('loglevelInfo', False))
        self.ui.loglevelWarning.setChecked(config.get('loglevelWarning', False))
        self.ui.loglevelError.setChecked(config.get('loglevelError', False))
        self.ui.checkShowErrorValues.setChecked(config.get('checkShowErrorValues', False))
        self.ui.checkRefracNone.setChecked(config.get('checkRefracNone', False))
        self.ui.checkRefracCont.setChecked(config.get('checkRefracCont', False))
        self.ui.checkRefracNoTrack.setChecked(config.get('checkRefracNoTrack', False))
        self.ui.profile.setText(self.app.config.get('profileName'))
        for i, line in enumerate(self.relayText):
            key = 'relayText{0:1d}'.format(i)
            line.setText(config.get(key, 'Relay{0:1d}'.format(i)))
        for i, button in enumerate(self.relayButton):
            key = 'relayText{0:1d}'.format(i)
            button.setText(config.get(key, 'Relay{0:1d}'.format(i)))
        for i, drop in enumerate(self.relayDropDown):
            key = 'relayFun{0:1d}'.format(i)
            drop.setCurrentIndex(config.get(key, 0))
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
        self.ui.checkJ2000.setChecked(config.get('checkJ2000', False))
        self.ui.checkJNow.setChecked(config.get('checkJNow', False))

    def storeConfig(self):
        if 'mainW' not in self.app.config:
            self.app.config['mainW'] = {}
        config = self.app.config['mainW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['loglevelDebug'] = self.ui.loglevelDebug.isChecked()
        config['loglevelInfo'] = self.ui.loglevelInfo.isChecked()
        config['loglevelWarning'] = self.ui.loglevelWarning.isChecked()
        config['loglevelError'] = self.ui.loglevelError.isChecked()
        config['loglevelError'] = self.ui.loglevelError.isChecked()
        config['checkShowErrorValues'] = self.ui.checkShowErrorValues.isChecked()
        config['checkRefracNone'] = self.ui.checkRefracNone.isChecked()
        config['checkRefracCont'] = self.ui.checkRefracCont.isChecked()
        config['checkRefracNoTrack'] = self.ui.checkRefracNoTrack.isChecked()
        config['profile'] = self.ui.profile.text()
        for i, line in enumerate(self.relayText):
            key = 'relayText{0:1d}'.format(i)
            config[key] = line.text()
        for i, drop in enumerate(self.relayDropDown):
            key = 'relayFun{0:1d}'.format(i)
            config[key] = drop.currentIndex()
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
        config['checkJ2000'] = self.ui.checkJ2000.isChecked()
        config['checkJNow'] = self.ui.checkJNow.isChecked()

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
        self.wIcon(self.ui.generateInitialPoints, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.plateSolveSync, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildGrid, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMax, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMed, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildNorm, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMin, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildDSO, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.runFlexure, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.runHysteresis, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelAnalyse, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.stop, PyQt5.QtWidgets.QStyle.SP_MessageBoxWarning)
        self.wIcon(self.ui.runTargetRMS, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.cancelTargetRMS, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.loadName, PyQt5.QtWidgets.QStyle.SP_DirOpenIcon)
        self.wIcon(self.ui.saveName, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.deleteName, PyQt5.QtWidgets.QStyle.SP_TrashIcon)
        self.wIcon(self.ui.refreshName, PyQt5.QtWidgets.QStyle.SP_BrowserReload)
        self.wIcon(self.ui.refreshModel, PyQt5.QtWidgets.QStyle.SP_BrowserReload)

        pixmap = PyQt5.QtGui.QPixmap(':/azimuth1.png')
        self.ui.picAZ.setPixmap(pixmap)
        pixmap = PyQt5.QtGui.QPixmap(':/altitude1.png')
        self.ui.picALT.setPixmap(pixmap)
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

        :return: nothing
        """
        self.updateAlignGUI()
        self.updateFwGui()
        self.updatePointGUI()
        self.updateSettingGUI()
        self.setNameList()
        self.showModelPolar()

    def updateMountConnStat(self, status):
        ui = self.ui.mountConnected
        if status:
            self.changeStyleDynamic(ui, 'color', 'green')
        else:
            self.changeStyleDynamic(ui, 'color', 'red')
        return True

    def updateGUICyclic(self):
        """
        updateGUICyclic update gui elements on regular bases (actually 1 second) for items,
        which are not events based.

        :return: success
        """
        self.ui.timeComputer.setText(datetime.datetime.now().strftime('%H:%M:%S'))
        self.deviceEnvironConnected()
        return True

    def updatePointGUI(self):
        """
        updatePointGUI update the gui upon events triggered be the reception of new data
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

        :return:    True if ok for testing
        """
        obs = self.app.mount.obsSite

        if obs.Alt is not None:
            self.ui.ALT.setText('{0:5.2f}'.format(obs.Alt.degrees))
        else:
            self.ui.ALT.setText('-')

        if obs.Az is not None:
            self.ui.AZ.setText('{0:5.2f}'.format(obs.Az.degrees))
        else:
            self.ui.AZ.setText('-')

        if obs.raJNow is not None:
            raFormat = '{0:02.0f}:{1:02.0f}:{2:02.0f}'
            raText = raFormat.format(*obs.raJNow.dms())
            self.ui.RA.setText(raText)
        else:
            self.ui.RA.setText('-')

        if obs.decJNow is not None:
            decFormat = '{sign}{0:02.0f}:{1:02.0f}:{2:02.0f}'
            decText = decFormat.format(*obs.decJNow.signed_dms()[1:4],
                                       sign='+' if obs.decJNow.degrees > 0 else '-')
            self.ui.DEC.setText(decText)
        else:
            self.ui.DEC.setText('-')

        if obs.timeJD is not None:
            self.ui.timeJD.setText(obs.timeJD.utc_strftime('%H:%M:%S'))
        else:
            self.ui.timeJD.setText('-')

        if obs.pierside is not None:
            self.ui.pierside.setText('WEST' if obs.pierside == 'W' else 'EAST')
        else:
            self.ui.pierside.setText('-')

        if obs.timeSidereal is not None:
            self.ui.timeSidereal.setText(obs.timeSidereal[:8])
        else:
            self.ui.timeSidereal.setText('-')

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

    def updateSettingGUI(self):
        """
        updateSetGUI update the gui upon events triggered be the reception of new settings
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

        :return:    True if ok for testing
        """

        sett = self.app.mount.sett
        obs = self.app.mount.obsSite

        if sett.slewRate is not None:
            self.ui.slewRate.setText('{0:2.0f}'.format(sett.slewRate))
        else:
            self.ui.slewRate.setText('-')

        if sett.timeToFlip is not None:
            self.ui.timeToFlip.setText('{0:3.0f}'.format(sett.timeToFlip))
        else:
            self.ui.timeToFlip.setText('-')

        if sett.timeToMeridian() is not None:
            self.ui.timeToMeridian.setText('{0:3.0f}'.format(sett.timeToMeridian()))
        else:
            self.ui.timeToMeridian.setText('-')

        if sett.UTCExpire is not None:
            ui = self.ui.UTCExpire
            ui.setText(sett.UTCExpire)
            # coloring if close to end:
            now = datetime.datetime.now()
            expire = datetime.datetime.strptime(sett.UTCExpire, '%Y-%m-%d')
            deltaYellow = datetime.timedelta(days=30)
            if now > expire:
                self.changeStyleDynamic(ui, 'color', 'red')
            elif now > expire - deltaYellow:
                self.changeStyleDynamic(ui, 'color', 'yellow')
            else:
                self.changeStyleDynamic(ui, 'color', '')
        else:
            self.ui.UTCExpire.setText('-')

        if sett.refractionTemp is not None:
            self.ui.refractionTemp.setText('{0:+4.1f}'.format(sett.refractionTemp))
            self.ui.refractionTemp1.setText('{0:+4.1f}'.format(sett.refractionTemp))
        else:
            self.ui.refractionTemp.setText('-')
            self.ui.refractionTemp1.setText('-')

        if sett.refractionPress is not None:
            self.ui.refractionPress.setText('{0:6.1f}'.format(sett.refractionPress))
            self.ui.refractionPress1.setText('{0:6.1f}'.format(sett.refractionPress))
        else:
            self.ui.refractionPress.setText('-')
            self.ui.refractionPress1.setText('-')

        if sett.statusUnattendedFlip is not None:
            self.ui.statusUnattendedFlip.setText('ON' if sett.statusUnattendedFlip else 'OFF')
        else:
            self.ui.statusUnattendedFlip.setText('-')

        if sett.statusDualTracking is not None:
            self.ui.statusDualTracking.setText('ON' if sett.statusDualTracking else 'OFF')
        else:
            self.ui.statusDualTracking.setText('-')

        if sett.statusRefraction is not None:
            self.ui.statusRefraction.setText('ON' if sett.statusRefraction else 'OFF')
        else:
            self.ui.statusRefraction.setText('-')

        if sett.meridianLimitTrack is not None:
            self.ui.meridianLimitTrack.setText(str(sett.meridianLimitTrack))
        else:
            self.ui.meridianLimitTrack.setText('-')

        if sett.meridianLimitSlew is not None:
            self.ui.meridianLimitSlew.setText(str(sett.meridianLimitSlew))
        else:
            self.ui.meridianLimitSlew.setText('-')

        if sett.horizonLimitLow is not None:
            self.ui.horizonLimitLow.setText(str(sett.horizonLimitLow))
        else:
            self.ui.horizonLimitLow.setText('-')

        if sett.horizonLimitHigh is not None:
            self.ui.horizonLimitHigh.setText(str(sett.horizonLimitHigh))
        else:
            self.ui.horizonLimitHigh.setText('-')

        if obs.location is not None:
            self.ui.siteLongitude.setText(obs.location.longitude.dstr())
            self.ui.siteLatitude.setText(obs.location.latitude.dstr())
            self.ui.siteElevation.setText(str(obs.location.elevation.m))
        else:
            self.ui.siteLongitude.setText('-')
            self.ui.siteLatitude.setText('-')
            self.ui.siteElevation.setText('-')

        # check tracking speed
        if self.app.mount.sett.checkRateLunar():
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', 'true')
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', 'false')
        elif self.app.mount.sett.checkRateSidereal():
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', 'true')
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', 'false')
        elif self.app.mount.sett.checkRateSolar():
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', 'true')

        return True

    def updateFwGui(self):
        """
        updateFwGui write all firmware data to the gui.

        :return:    True if ok for testing
        """

        fw = self.app.mount.fw

        if fw.productName is not None:
            self.ui.productName.setText(fw.productName)
        else:
            self.ui.productName.setText('-')

        if fw.numberString is not None:
            self.ui.numberString.setText(fw.numberString)
        else:
            self.ui.numberString.setText('-')

        if fw.fwdate is not None:
            self.ui.fwdate.setText(fw.fwdate)
        else:
            self.ui.fwdate.setText('-')

        if fw.fwtime is not None:
            self.ui.fwtime.setText(fw.fwtime)
        else:
            self.ui.fwtime.setText('-')

        if fw.hwVersion is not None:
            self.ui.hwVersion.setText(fw.hwVersion)
        else:
            self.ui.hwVersion.setText('-')

        return True

    def setNameList(self):
        """
        setNameList populates the list of model names in the main window. before adding the
        data, the existent list will be deleted.

        :return:    True if ok for testing
        """

        model = self.app.mount.model
        self.ui.nameList.clear()
        for name in model.nameList:
            self.ui.nameList.addItem(name)
        self.ui.nameList.sortItems()
        self.ui.nameList.update()
        return True

    def updateAlignGUI(self):
        """
        updateAlignGUI shows the data which is received through the getain command. this is
        mainly polar and ortho errors as well as basic model data.

        :return:    True if ok for testing
        """

        model = self.app.mount.model

        if model.numberStars is not None:
            self.ui.numberStars.setText(str(model.numberStars))
            self.ui.numberStars1.setText(str(model.numberStars))
        else:
            self.ui.numberStars.setText('-')
            self.ui.numberStars1.setText('-')

        if model.terms is not None:
            self.ui.terms.setText(str(model.terms))
        else:
            self.ui.terms.setText('-')

        if model.errorRMS is not None:
            self.ui.errorRMS.setText(str(model.errorRMS))
            self.ui.errorRMS1.setText(str(model.errorRMS))
        else:
            self.ui.errorRMS.setText('-')
            self.ui.errorRMS1.setText('-')

        if model.positionAngle is not None:
            self.ui.positionAngle.setText('{0:5.1f}'.format(model.positionAngle.degrees))
        else:
            self.ui.positionAngle.setText('-')

        if model.polarError is not None:
            self.ui.polarError.setText(model.polarError.dstr(places=0))
        else:
            self.ui.polarError.setText('-')

        if model.orthoError is not None:
            self.ui.orthoError.setText(model.orthoError.dstr(places=0))
        else:
            self.ui.orthoError.setText('-')

        if model.azimuthError is not None:
            self.ui.azimuthError.setText(model.azimuthError.dstr(places=0))
        else:
            self.ui.azimuthError.setText('-')

        if model.altitudeError is not None:
            self.ui.altitudeError.setText(model.altitudeError.dstr(places=0))
        else:
            self.ui.altitudeError.setText('-')
        return True

    def showModelPolar(self):
        """
        showModelPolar draws a polar plot of the align model stars and their errors in
        color. the basic setup of the plot is taking place in the central widget class.
        which is instantiated from there.

        :return:    True if ok for testing
        """

        if not self.app.mount.obsSite.location:
            # clear the plot and return
            fig, axes = self.clearPolar(self.polarPlot)
            fig.subplots_adjust(left=0.1,
                                right=0.9,
                                bottom=0.1,
                                top=0.85,
                                )
            axes.figure.canvas.draw()
            return False

        model = self.app.mount.model
        lat = self.app.mount.obsSite.location.latitude.degrees

        # preparing the polar plot and the axes
        fig, axes = self.clearPolar(self.polarPlot)

        # now prepare the data
        if not model.starList:
            self.logger.error('no model data available for display')
            return False
        altitude = []
        azimuth = []
        error = []
        for star in model.starList:
            alt, az = convert.topoToAltAz(star.coord.ra.hours,
                                          star.coord.dec.degrees,
                                          lat)
            altitude.append(alt)
            azimuth.append(az)
            error.append(star.errorRMS)
        altitude = np.asarray(altitude)
        azimuth = np.asarray(azimuth)
        error = np.asarray(error)

        # and plot it
        cm = matplotlib.pyplot.cm.get_cmap('RdYlGn_r')
        colors = np.asarray(error)
        scaleErrorMax = max(colors)
        scaleErrorMin = min(colors)
        area = [200 if x >= max(colors) else 60 for x in error]
        theta = azimuth / 180.0 * np.pi
        r = 90 - altitude
        scatter = axes.scatter(theta,
                               r,
                               c=colors,
                               vmin=scaleErrorMin,
                               vmax=scaleErrorMax,
                               s=area,
                               cmap=cm,
                               zorder=0,
                               )
        if self.ui.checkShowErrorValues.isChecked():
            for star in model.starList:
                text = '{0:3.1f}'.format(star.errorRMS)
                axes.annotate(text,
                              xy=(theta[star.number-1],
                                  r[star.number-1]),
                              color='#2090C0',
                              fontsize=9,
                              fontweight='bold',
                              zorder=1,
                              )
        formatString = matplotlib.ticker.FormatStrFormatter('%1.0f')
        colorbar = fig.colorbar(scatter,
                                pad=0.1,
                                fraction=0.12,
                                aspect=25,
                                shrink=0.9,
                                format=formatString,
                                )
        colorbar.set_label('Error [arcsec]', color='white')
        yTicks = matplotlib.pyplot.getp(colorbar.ax.axes, 'yticklabels')
        matplotlib.pyplot.setp(yTicks,
                               color='#2090C0',
                               fontweight='bold')
        axes.set_rmax(90)
        axes.set_rmin(0)
        axes.figure.canvas.draw()
        return True

    def changeTracking(self):
        obs = self.app.mount.obsSite
        if obs.status == 0:
            suc = obs.stopTracking()
            if not suc:
                self.app.message.emit('Cannot stop tracking', 2)
            else:
                self.app.message.emit('Stopped tracking', 0)
        else:
            suc = obs.startTracking()
            if not suc:
                self.app.message.emit('Cannot start tracking', 2)
            else:
                self.app.message.emit('Started tracking', 0)
        return True

    def changePark(self):
        obs = self.app.mount.obsSite
        if obs.status == 5:
            suc = obs.unpark()
            if not suc:
                self.app.message.emit('Cannot unpark mount', 2)
            else:
                self.app.message.emit('Mount unparked', 0)
        else:
            suc = obs.park()
            if not suc:
                self.app.message.emit('Cannot park mount', 2)
            else:
                self.app.message.emit('Mount parked', 0)
        return True

    def setLunarTracking(self):
        obs = self.app.mount.obsSite
        suc = obs.setLunarTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Lunar', 2)
            return False
        else:
            self.app.message.emit('Tracking set to Lunar', 0)
            return True

    def setSiderealTracking(self):
        obs = self.app.mount.obsSite
        suc = obs.setSiderealTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Sidereal', 2)
            return False
        else:
            self.app.message.emit('Tracking set to Sidereal', 0)
            return True

    def setSolarTracking(self):
        obs = self.app.mount.obsSite
        suc = obs.setSolarTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Solar', 2)
            return False
        else:
            self.app.message.emit('Tracking set to Solar', 0)
            return True

    @staticmethod
    def checkExtension(filePath, ext):
        if not filePath.endswith(ext):
            filePath += ext
        return filePath

    def loadProfile(self):
        folder = self.app.mwGlob['configDir'] + '/config'
        configFilePath, name, ext = self.openFile(self,
                                                  'Open config file',
                                                  folder,
                                                  'Config files (*.cfg)',
                                                  )
        if not configFilePath:
            return False
        configFilePath = self.checkExtension(configFilePath, '.cfg')
        suc = self.app.loadConfig(configFilePath=configFilePath)
        if suc:
            self.ui.profile.setText(name)
            self.app.message.emit('Profile: [{0}] loaded'.format(name), 0)
        else:
            self.app.message.emit('Profile: [{0}] cannot no be loaded'.format(name), 2)
        return True

    def saveProfileAs(self):
        folder = self.app.mwGlob['configDir'] + '/config'
        configFilePath, name, ext = self.saveFile(self,
                                                  'Save config file',
                                                  folder,
                                                  'Config files (*.cfg)',
                                                  )
        if not configFilePath:
            return False
        self.app.config['profileName'] = name
        configFilePath = self.checkExtension(configFilePath, '.cfg')
        suc = self.app.saveConfig(configFilePath=configFilePath)
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

    def setMeridianLimitTrack(self):
        """
        setMeridianLimitTrack implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        sett = self.app.mount.sett
        msg = PyQt5.QtWidgets.QMessageBox
        obs = self.app.mount.obsSite
        actValue = sett.meridianLimitTrack
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Meridian Limit Track',
                               'Value (-20-20):',
                               actValue,
                               -20,
                               20,
                               1,
                               )
        if ok:
            if obs.setMeridianLimitTrack(value):
                self.app.message.emit('Meridian Limit Track: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Meridian Limit Track cannot be set', 2)
                return False
        else:
            return False

    def setMeridianLimitSlew(self):
        """
        setMeridianLimitSlew implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        sett = self.app.mount.sett
        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = sett.meridianLimitSlew
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Meridian Limit Slew',
                               'Value (-20-20):',
                               actValue,
                               -20,
                               20,
                               1,
                               )
        if ok:
            if obs.setMeridianLimitSlew(value):
                self.app.message.emit('Meridian Limit Slew: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Meridian Limit Slew cannot be set', 2)
                return False
        else:
            return False

    def setHorizonLimitHigh(self):
        """
        setHorizonLimitHigh implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        sett = self.app.mount.sett
        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = sett.horizonLimitHigh
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Horizon Limit High',
                               'Value (0-90):',
                               actValue,
                               0,
                               90,
                               1,
                               )
        if ok:
            if obs.setHorizonLimitHigh(value):
                self.app.message.emit('Horizon Limit High: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Horizon Limit High cannot be set', 2)
                return False
        else:
            return False

    def setHorizonLimitLow(self):
        """
        setHorizonLimitLow implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        sett = self.app.mount.sett
        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = sett.horizonLimitLow
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Horizon Limit Low',
                               'Value (0-90):',
                               actValue,
                               0,
                               90,
                               1,
                               )
        if ok:
            if obs.setHorizonLimitLow(value):
                self.app.message.emit('Horizon Limit Low: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Horizon Limit Low cannot be set', 2)
                return False
        else:
            return False

    def setSlewRate(self):
        """
        setSlewRate implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """
        sett = self.app.mount.sett
        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = sett.slewRate
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Slew Rate',
                               'Value (1-20):',
                               actValue,
                               1,
                               20,
                               1,
                               )
        if ok:
            if obs.setSlewRate(value):
                self.app.message.emit('Slew Rate: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Slew Rate cannot be set', 2)
                return False
        else:
            return False

    def setLongitude(self):
        """
        setSiteLongitude implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        if obs.location is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getText(self,
                                'Set Site Longitude',
                                'Value: (East positive)',
                                PyQt5.QtWidgets.QLineEdit.Normal,
                                obs.location.longitude.dstr(),
                                )
        if ok:
            if obs.setLongitude(value):
                self.app.message.emit('Longitude: [{0}]'.format(value), 0)
                self.app.mount.getLocation()
                return True
            else:
                self.app.message.emit('Longitude cannot be set', 2)
                return False
        else:
            return False

    def setLatitude(self):
        """
        setSiteLatitude implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        if obs.location is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getText(self,
                                'Set Site Latitude',
                                'Value:',
                                PyQt5.QtWidgets.QLineEdit.Normal,
                                obs.location.latitude.dstr(),
                                )
        if ok:
            if obs.setLatitude(value):
                self.app.message.emit('Latitude: [{0}]'.format(value), 0)
                self.app.mount.getLocation()
                return True
            else:
                self.app.message.emit('Latitude cannot be set', 2)
                return False
        else:
            return False

    def setElevation(self):
        """
        setSiteElevation implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        if obs.location is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getDouble(self,
                                  'Set Site Elevation',
                                  'Value: (meters)',
                                  obs.location.elevation.m,
                                  0,
                                  8000,
                                  1,
                                  )
        if ok:
            if obs.setElevation(value):
                self.app.message.emit('Elevation: [{0}]'.format(value), 0)
                self.app.mount.getLocation()
                return True
            else:
                self.app.message.emit('Elevation cannot be set', 2)
        else:
            return False

    def setupRelayGui(self):
        """
        setupRelayGui handles the build of list for relay handling. to keep many relay in
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

    def updateRelayGui(self):
        """
        updateRelayGui changes the style of the button related to the state of the relay

        :return: success for test
        """

        status = self.app.relay.status
        for i, button in enumerate(self.relayButton):
            if status[i]:
                self.changeStyleDynamic(button, 'running', 'true')
            else:
                self.changeStyleDynamic(button, 'running', 'false')
        return True

    def toggleRelay(self):
        """
        toggleRelay reads the button and toggles the relay on the box.

        :return: success for test
        """

        if not self.ui.checkEnableRelay.isChecked():
            self.app.message.emit('Relay box off', 2)
            return False
        suc = False
        for i, button in enumerate(self.relayButton):
            if button != self.sender():
                continue
            suc = self.app.relay.switch(i)
        if not suc:
            self.app.message.emit('Relay cannot be switched', 2)
            return False
        self.app.relay.cyclePolling()
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

    def newEnvironDevice(self, deviceName):
        self.app.message.emit('INDI device [{0}] found'.format(deviceName), 0)

    def indiEnvironConnected(self):
        self.app.message.emit('INDI server connected', 0)

    def indiEnvironDisconnected(self):
        self.app.message.emit('INDI server disconnected', 0)

    def deviceEnvironConnected(self):
        uiList = {'localWeather': self.ui.localWeatherName,
                  'globalWeather': self.ui.globalWeatherName,
                  'sqm': self.ui.sqmName,
                  }
        for deviceKey, color in self.app.environment.getDeviceStatus():
            self.changeStyleDynamic(uiList[deviceKey],
                                    'color',
                                    color,
                                    )

    def updateEnvironGUI(self, deviceName):
        """
        updateEnvironGUI shows the data which is received through INDI client

        :return:    True if ok for testing
        """

        environ = self.app.environment

        if deviceName == environ.sqmName:
            value = environ.sqmData.get('SKY_BRIGHTNESS', 0)
            self.ui.SQR.setText('{0:5.2f}'.format(value))

        if deviceName == environ.localWeatherName:
            value = environ.localWeatherData.get('WEATHER_TEMPERATURE', 0)
            self.ui.localTemp.setText('{0:4.1f}'.format(value))
            value = environ.localWeatherData.get('WEATHER_BAROMETER', 0)
            self.ui.localPress.setText('{0:5.1f}'.format(value))
            value = environ.localWeatherData.get('WEATHER_DEWPOINT', 0)
            self.ui.localDewPoint.setText('{0:4.1f}'.format(value))
            value = environ.localWeatherData.get('WEATHER_HUMIDITY', 0)
            self.ui.localHumidity.setText('{0:3.0f}'.format(value))

        if deviceName == environ.globalWeatherName:
            value = environ.globalWeatherData.get('WEATHER_TEMPERATURE', 0)
            self.ui.globalTemp.setText('{0:4.1f}'.format(value))
            value = environ.globalWeatherData.get('WEATHER_PRESSURE', 0)
            self.ui.globalPress.setText('{0:5.1f}'.format(value))
            value = environ.globalWeatherData.get('WEATHER_DEWPOINT', 0)
            self.ui.globalDewPoint.setText('{0:4.1f}'.format(value))
            value = environ.globalWeatherData.get('WEATHER_HUMIDITY', 0)
            self.ui.globalHumidity.setText('{0:4.1f}'.format(value))
            value = environ.globalWeatherData.get('WEATHER_CLOUD_COVER', 0)
            self.ui.cloudCover.setText('{0:3.0f}'.format(value))
            value = environ.globalWeatherData.get('WEATHER_WIND_SPEED', 0)
            self.ui.windSpeed.setText('{0:3.0f}'.format(value))
            value = environ.globalWeatherData.get('WEATHER_RAIN_HOUR', 0)
            self.ui.rainVol.setText('{0:3.0f}'.format(value))
            value = environ.globalWeatherData.get('WEATHER_SNOW_HOUR', 0)
            self.ui.snowVol.setText('{0:3.0f}'.format(value))
