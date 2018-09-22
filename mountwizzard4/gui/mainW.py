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
# local import
import mw4_global
import base.widget
import base.tpool
from mountcontrol.qtmount import Mount


class MainWindow(base.widget.MWidget):
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

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.tPool = PyQt5.QtCore.QThreadPool()

        # load and init the gui
        self.ui = PyQt5.uic.loadUi(mw4_global.work_dir + '/mountwizzard4/gui/main.ui', self)
        self.initUI()
        self.setupIcons()
        self.show()

        # connect signals for refreshing the gui
        self.app.mount.signals.pointDone.connect(self.updatePointGUI)
        self.app.mount.signals.setDone.connect(self.updateSettingGUI)
        self.app.mount.signals.gotAlign.connect(self.gotAlign)
        self.app.mount.signals.gotNames.connect(self.gotNames)

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
        """
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
        self.wIcon(self.ui.startTracking, PyQt5.QtWidgets.QStyle.SP_DialogYesButton)
        self.wIcon(self.ui.stopTracking, PyQt5.QtWidgets.QStyle.SP_DialogNoButton)
        self.wIcon(self.ui.loadModel, PyQt5.QtWidgets.QStyle.SP_DirOpenIcon)
        self.wIcon(self.ui.saveModel, PyQt5.QtWidgets.QStyle.SP_DialogSaveButton)
        self.wIcon(self.ui.deleteModel, PyQt5.QtWidgets.QStyle.SP_TrashIcon)
        """
        pixmap = PyQt5.QtGui.QPixmap(':/azimuth1.png')
        self.ui.picAZ.setPixmap(pixmap)
        pixmap = PyQt5.QtGui.QPixmap(':/altitude1.png')
        self.ui.picALT.setPixmap(pixmap)

    def updatePointGUI(self):
        """
        updatePointGUI update the gui upon events triggered be the reception of new data
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

        :return:
        """
        obs = self.app.mount.obsSite
        self.ui.timeComputer.setText(datetime.datetime.now().strftime('%H:%M:%S'))

        if obs.Alt is not None:
            self.ui.altitude.setText('{0:5.2f}'.format(obs.Alt.degrees))

        if obs.Az is not None:
            self.ui.azimuth.setText('{0:5.2f}'.format(obs.Az.degrees))

        if obs.raJNow is not None:
            raFormat = '{0:02.0f}:{1:02.0f}:{2:02.0f}'
            raText = raFormat.format(*obs.raJNow.dms())
            self.ui.RA.setText(raText)

        if obs.decJNow is not None:
            decFormat = '{sign}{0:02.0f}:{1:02.0f}:{2:02.0f}'
            decText = decFormat.format(*obs.decJNow.signed_dms()[1:4],
                                       sign='+' if obs.decJNow.degrees > 0 else '-')
            self.ui.DEC.setText(decText)

        if obs.timeJD is not None:
            self.ui.julianDate.setText(obs.timeJD.utc_strftime('%H:%M:%S'))

        if obs.pierside is not None:
            self.ui.pierside.setText('WEST' if obs.pierside == 'W' else 'EAST')

        if obs.timeSidereal is not None:
            self.ui.timeSidereal.setText(obs.timeSidereal[:8])

    def updateSettingGUI(self):
        """
        updateSetGUI update the gui upon events triggered be the reception of new settings
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

        :return:
        """

        sett = self.app.mount.sett

        if sett.slewRate is not None:
            self.ui.slewRate.setText('{0:2.0f}'.format(sett.slewRate))

        if sett.timeToFlip is not None:
            self.ui.timeToFlip.setText('{0:3.0f}'.format(sett.timeToFlip))

        if sett.timeToMeridian() is not None:
            self.ui.timeToMeridian.setText('{0:3.0f}'.format(sett.timeToMeridian()))

        if sett.UTCExpire is not None:
            self.ui.UTCExpire.setText(sett.UTCExpire)
            # coloring if close to end:
            now = datetime.datetime.now()
            expire = datetime.datetime.strptime(sett.UTCExpire, '%Y-%m-%d')
            deltaYellow = datetime.timedelta(days=30)
            if now > expire:
                pass    # red
            elif now > expire - deltaYellow:
                pass    # yellow

        if sett.refractionTemp is not None:
            self.ui.refractionTemp.setText('{0:+4.1f}'.format(sett.refractionTemp))

        if sett.refractionPress is not None:
            self.ui.refractionPress.setText('{0:4.0f}'.format(sett.refractionPress))

        if sett.statusUnattendedFlip is not None:
            self.ui.statusUnattendedFlip.setText('ON' if sett.statusUnattendedFlip else 'OFF')

        if sett.statusDualTracking is not None:
            self.ui.statusDualTracking.setText('ON' if sett.statusDualTracking else 'OFF')

        if sett.statusRefraction is not None:
            self.ui.statusRefraction.setText('ON' if sett.statusRefraction else 'OFF')

    def gotNames(self):
        for name in self.app.mount.model.nameList:
            # print(name)
            pass

    def gotAlign(self):
        for star in self.app.mount.model.starList:
            # print(star)
            pass