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
    logging.getLogger('apscheduler').setLevel(logging.WARNING)

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
        obsSite = self.mount.obsSite

        self.ui.altitude.setText('{0:5.2f}'.format(obsSite.Alt.degrees))
        self.ui.azimuth.setText('{0:5.2f}'.format(obsSite.Az.degrees))

        raFormat = '{0:02.0f}:{1:02.0f}:{2:02.0f}'
        raText = raFormat.format(*obsSite.raJNow.dms())
        self.ui.RA.setText(raText)

        decFormat = '{sign}{0:02.0f}:{1:02.0f}:{2:02.0f}'
        decText = decFormat.format(*obsSite.decJNow.signed_dms()[1:4],
                                   sign='+' if obsSite.decJNow.degrees > 0 else '-')
        self.ui.DEC.setText(decText)
        self.ui.julianDate.setText(obsSite.timeJD.utc_strftime('%H:%M:%S'))

    def updateSetGUI(self):
        pass