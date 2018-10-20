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
import time
import json
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
import numpy as np
import matplotlib
# local import
import mw4_global
import base.widget as mWidget
import base.tpool
import mountcontrol.convert as convert
from gui import main_ui
from base.widget import InputDialog


class MainWindow(mWidget.MWidget):
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

        # load and init the gui
        self.ui = main_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()
        self.setupIcons()
        self.setWindowTitle('MountWizzard4   (' + mw4_global.BUILD + ')')

        # defining the necessary instances of classes
        self.polarPlot = self.integrateMatplotlib(self.ui.modelPolar)
        self.showModelPolar()

        # connect signals for refreshing the gui
        self.app.mount.signals.pointDone.connect(self.updatePointGUI)
        self.app.mount.signals.settDone.connect(self.updateSettingGUI)
        self.app.mount.signals.alignDone.connect(self.updateAlignGui)
        self.app.mount.signals.alignDone.connect(self.showModelPolar)
        self.app.mount.signals.namesDone.connect(self.setNameList)
        self.app.mount.signals.fwDone.connect(self.updateFwGui)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)
        self.app.mount.signals.mountClear.connect(self.clearMountGui)

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
        self.ui.setMeridianLimitTrack.clicked.connect(self.setMeridianLimitTrack)
        self.ui.setMeridianLimitSlew.clicked.connect(self.setMeridianLimitSlew)
        self.ui.setHorizonLimitHigh.clicked.connect(self.setHorizonLimitHigh)
        self.ui.setHorizonLimitLow.clicked.connect(self.setHorizonLimitLow)

        # initial call for writing the gui
        self.updateMountConnStat(False)
        self.initConfig()
        self.show()

        self.timerGui = PyQt5.QtCore.QTimer()
        self.timerGui.setSingleShot(False)
        self.timerGui.timeout.connect(self.updateGuiCyclic)
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
        self.ui.profile.setText(config.get('profile'))

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
        config['profile'] = self.ui.profile.text()

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
        self.wIcon(self.ui.generateGridPoints, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.generateMaxPoints, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.generateNormalPoints, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.generateMinPoints, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.generateDSOPoints, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
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
        else:
            self.app.message.emit('Mount cannot be booted', 2)

    def mountShutdown(self):
        if self.app.mount.obsSite.shutdown():
            self.app.message.emit('Shutting mount down', 0)
        else:
            self.app.message.emit('Mount cannot be shutdown', 2)

    def clearMountGui(self):
        self.updateAlignGui()
        self.updateFwGui()
        self.updatePointGUI()
        self.updateSettingGUI()
        self.setNameList()
        self.showModelPolar()

    def updateMountConnStat(self, status):
        ui = self.ui.mountConnected
        if status:
            self.changeStylesheet(ui, 'color', 'green')
        else:
            self.changeStylesheet(ui, 'color', 'red')
        return True

    def updateGuiCyclic(self):
        self.ui.timeComputer.setText(datetime.datetime.now().strftime('%H:%M:%S'))
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
            self.changeStylesheet(self.ui.tracking, 'running', 'true')
        else:
            self.changeStylesheet(self.ui.tracking, 'running', 'false')

        if self.app.mount.obsSite.status == 5:
            self.changeStylesheet(self.ui.park, 'running', 'true')
        else:
            self.changeStylesheet(self.ui.park, 'running', 'false')

        if self.app.mount.obsSite.status == 1:
            self.changeStylesheet(self.ui.stop, 'running', 'true')
        else:
            self.changeStylesheet(self.ui.stop, 'running', 'false')

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
                self.changeStylesheet(ui, 'color', 'red')
            elif now > expire - deltaYellow:
                self.changeStylesheet(ui, 'color', 'yellow')
            else:
                self.changeStylesheet(ui, 'color', '')
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
            self.changeStylesheet(self.ui.setLunarTracking, 'running', 'true')
            self.changeStylesheet(self.ui.setSiderealTracking, 'running', 'false')
            self.changeStylesheet(self.ui.setSolarTracking, 'running', 'false')
        elif self.app.mount.sett.checkRateSidereal():
            self.changeStylesheet(self.ui.setLunarTracking, 'running', 'false')
            self.changeStylesheet(self.ui.setSiderealTracking, 'running', 'true')
            self.changeStylesheet(self.ui.setSolarTracking, 'running', 'false')
        elif self.app.mount.sett.checkRateSolar():
            self.changeStylesheet(self.ui.setLunarTracking, 'running', 'false')
            self.changeStylesheet(self.ui.setSiderealTracking, 'running', 'false')
            self.changeStylesheet(self.ui.setSolarTracking, 'running', 'true')

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

    def updateAlignGui(self):
        """
        updateAlignGui shows the data which is received through the getain command. this is
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
                text = '{0:3.1f}'.format(star.number)
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
        obsSite = self.app.mount.obsSite
        if obsSite.status == 0:
            suc = obsSite.stopTracking()
            if not suc:
                self.app.message.emit('Cannot stop tracking', 2)
            else:
                self.app.message.emit('Stopped tracking', 0)
        else:
            suc = obsSite.startTracking()
            if not suc:
                self.app.message.emit('Cannot start tracking', 2)
            else:
                self.app.message.emit('Started tracking', 0)
        return True

    def changePark(self):
        obsSite = self.app.mount.obsSite
        if obsSite.status == 5:
            suc = obsSite.unpark()
            if not suc:
                self.app.message.emit('Cannot unpark mount', 2)
            else:
                self.app.message.emit('Mount unparked', 0)
        else:
            suc = obsSite.park()
            if not suc:
                self.app.message.emit('Cannot park mount', 2)
            else:
                self.app.message.emit('Mount parked', 0)
        return True

    def setLunarTracking(self):
        obsSite = self.app.mount.obsSite
        suc = obsSite.setLunarTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Lunar', 2)
        else:
            self.app.message.emit('Tracking set to Lunar', 0)

    def setSiderealTracking(self):
        obsSite = self.app.mount.obsSite
        suc = obsSite.setSiderealTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Sidereal', 2)
        else:
            self.app.message.emit('Tracking set to Sidereal', 0)

    def setSolarTracking(self):
        obsSite = self.app.mount.obsSite
        suc = obsSite.setSolarTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Solar', 2)
        else:
            self.app.message.emit('Tracking set to Solar', 0)

    def loadProfile(self):
        filePath, name, ext = self.openFile(self,
                                            'Open config file',
                                            '/config',
                                            'Config files (*.cfg)',
                                            )
        if not filePath:
            return
        suc = self.app.loadConfig(filePath=filePath, name=name)
        if suc:
            self.app.message.emit('Profile: [{0}] loaded'.format(short), 0)
        else:
            self.app.message.emit('Profile: [{0}] cannot no be loaded'.format(short), 2)

    def saveProfileAs(self):
        filePath, name, ext = self.saveFile(self,
                                            'Save config file',
                                            '/config',
                                            'Config files (*.cfg)',
                                            )
        if not filePath:
            return
        suc = self.app.saveConfig(filePath=filePath, name=name)
        if suc:
            self.app.message.emit('Profile: [{0}] saved'.format(short), 0)
        else:
            self.app.message.emit('Profile: [{0}] cannot no be saved'.format(short), 2)

    def saveProfile(self):
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
        sett = self.app.mount.sett
        msg = PyQt5.QtWidgets.QMessageBox
        dlg = InputDialog()
        actValue = sett.meridianLimitTrack
        actValue = 15
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        value, okPressed = dlg.getInt(self,
                                      title='Set Meridian Limit Track',
                                      message='Value (0-20):',
                                      actValue=actValue,
                                      minValue=0,
                                      maxValue=20,
                                      stepValue=1)
        return True

    def setMeridianLimitSlew(self):
        pass

    def setHorizonLimitHigh(self):
        pass

    def setHorizonLimitLow(self):
        pass