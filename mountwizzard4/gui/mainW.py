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
from mountcontrol.mount import Mount


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
            self.ui.timeSidereal.setText(obs.timeSidereal)

    def updateSetGUI(self):
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

        if sett.refractionTemp is not None:
            self.ui.refractionTemp.setText('{0:+4.1f}'.format(sett.refractionTemp))

        if sett.refractionPress is not None:
            self.ui.refractionPress.setText('{0:4.0f}'.format(sett.refractionPress))

        if sett.statusUnattendedFlip is not None:
            self.ui.statusUnattendedFlip.setText('ON' if sett.statusUnattendedFlip else 'OFF')

        if sett.statusDualTracking is not None:
            self.ui.statusDualTracking.setText('ON' if sett.statusDualTracking else 'OFF')
