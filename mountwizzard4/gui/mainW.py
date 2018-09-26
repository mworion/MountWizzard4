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
import matplotlib
# local import
import mw4_global
import base.widget as mWidget
import base.tpool
import mountcontrol.convert as convert


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
        self.tPool = PyQt5.QtCore.QThreadPool()

        # load and init the gui
        guiPath = mw4_global.work_dir + '/mountwizzard4/gui/main.ui'
        self.ui = PyQt5.uic.loadUi(guiPath, self)
        self.initUI()
        self.setupIcons()

        # defining the necessary instances of classes
        self.polarPlot = mWidget.IntMatplotlib(self.ui.modelPolar)

        # connect signals for refreshing the gui
        self.app.mount.signals.pointDone.connect(self.updatePointGUI)
        self.app.mount.signals.settDone.connect(self.updateSettingGUI)
        self.app.mount.signals.alignDone.connect(self.updateAlignGui)
        self.app.mount.signals.alignDone.connect(self.showModelPolar)
        self.app.mount.signals.namesDone.connect(self.setNameList)
        self.app.mount.signals.fwDone.connect(self.updateFwGui)
        self.app.mount.signals.mountUp.connect(self.updateMountConnStat)

        # connect gui signals
        self.ui.checkShowErrorValues.stateChanged.connect(self.showModelPolar)
        self.ui.saveConfigQuit.clicked.connect(self.app.quit)

        # initial call for writing the gui
        self.updateFwGui()
        self.show()

        self.timerGui = PyQt5.QtCore.QTimer()
        self.timerGui.setSingleShot(False)
        self.timerGui.timeout.connect(self.updateGui)
        self.timerGui.start(self.CYCLE_GUI)

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
        # show icon in main gui and add some icons for push buttons
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
        self.wIcon(self.ui.startTracking, PyQt5.QtWidgets.QStyle.SP_DialogYesButton)
        self.wIcon(self.ui.stopTracking, PyQt5.QtWidgets.QStyle.SP_DialogNoButton)
        self.wIcon(self.ui.runInitialModel, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.cancelFullModel, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.runFullModel, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.cancelInitialModel, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.generateInitialPoints, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.plateSolveSync, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.generateGridPoints, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.generateMaxPoints, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.generateNormalPoints, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.generateMinPoints, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.generateDSOPoints, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.runFlexure, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.runHysteresis, PyQt5.QtWidgets.QStyle.SP_ArrowForward)
        self.wIcon(self.ui.cancelAnalyse, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)
        self.wIcon(self.ui.stop, PyQt5.QtWidgets.QStyle.SP_MessageBoxWarning)
        self.wIcon(self.ui.loadModel, PyQt5.QtWidgets.QStyle.SP_DirOpenIcon)
        self.wIcon(self.ui.saveModel, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.deleteModel, PyQt5.QtWidgets.QStyle.SP_TrashIcon)

        pixmap = PyQt5.QtGui.QPixmap(':/azimuth1.png')
        self.ui.picAZ.setPixmap(pixmap)
        pixmap = PyQt5.QtGui.QPixmap(':/altitude1.png')
        self.ui.picALT.setPixmap(pixmap)

    def updateMountConnStat(self, status):
        ui = self.ui.mountConnected
        if status:
            self.changeStylesheet(ui, 'color', 'green')
            self.app.loadStartData()
        else:
            self.changeStylesheet(ui, 'color', 'red')

    def updateGui(self):
        self.ui.timeComputer.setText(datetime.datetime.now().strftime('%H:%M:%S'))

    def updatePointGUI(self):
        """
        updatePointGUI update the gui upon events triggered be the reception of new data
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

        :return:
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

    def updateSettingGUI(self):
        """
        updateSetGUI update the gui upon events triggered be the reception of new settings
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

        :return:
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

    def updateFwGui(self):
        """
        updateFwGui write all firmware data to the gui.

        :return:
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

    def setNameList(self):
        """
        setNameList populates the list of model names in the main window. before adding the
        data, the existent list will be deleted.

        :return: nothing
        """

        model = self.app.mount.model
        self.ui.nameList.clear()
        for name in model.nameList:
            self.ui.nameList.addItem(name)
        self.ui.nameList.sortItems()
        self.ui.nameList.update()

    def updateAlignGui(self):
        """
        updateAlignGui shows the data which is received through the getain command. this is
        mainly polar and ortho errors as well as basic model data.

        :return:    nothing
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

    def showModelPolar(self):
        """
        showModelPolar draws a polar plot of the align model stars and their errors in
        color.

        :return:
        """

        if not self.app.mount.obsSite.location:
            return False
        model = self.app.mount.model
        lat = self.app.mount.obsSite.location.latitude.degrees

        # preparing the polar plot and the axes
        wid = self.clearPolar(self.polarPlot)

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
        scatter = wid.axes.scatter(theta,
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
                wid.axes.annotate(text,
                                  xy=(theta[star.number-1],
                                      r[star.number-1]),
                                  color='#2090C0',
                                  fontsize=9,
                                  fontweight='bold',
                                  zorder=1,
                                  )
        formatString = matplotlib.ticker.FormatStrFormatter('%1.0f')
        colorbar = wid.fig.colorbar(scatter,
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
        wid.axes.set_rmax(90)
        wid.axes.set_rmin(0)
        wid.draw()
        return True
