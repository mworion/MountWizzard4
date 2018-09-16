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
import os
import datetime
# external packages
import PyQt5
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
import skyfield.api
from mountcontrol.mount import Mount
# local import
from base import widget
from media import resources


class MountWizzard4(widget.MWidget):
    """
    This is the docstring
    """

    __all__ = ['MountWizzard4',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

        self.ui = PyQt5.uic.loadUi(os.getcwd() + '/mountwizzard4/gui/main.ui', self)
        self.initUI()
        self.ui.show()

        self.mount = Mount('192.168.2.15', pathToTS=os.getcwd() + '/config')
        self.mount.signals.pointDone.connect(self.updatePointGUI)
        self.mount.signals.setDone.connect(self.updateSetGUI)
        self.mount.startTimers()

    def quit(self):
        self.mount.stopTimers()
        PyQt5.QtCore.QCoreApplication.quit()
        pass

    def updatePointGUI(self):
        obs = self.mount.obsSite
        self.ui.computerTime.setText(datetime.datetime.now().strftime('%H:%M:%S'))

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

    def updateSetGUI(self):
        pass