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
    logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

        self.ui = PyQt5.uic.loadUi(os.getcwd() + '/mountwizzard4/gui/main.ui', self)
        self.initUI()
        self.ui.show()

        self.mount = Mount('192.168.2.15')
        self.mount.signals.pointDone.connect(self.updatePointGUI)
        self.mount.signals.setDone.connect(self.updateSetGUI)
        self.mount.startTimers()

    def quit(self):
        self.mount.stopTimers()
        PyQt5.QtCore.QCoreApplication.quit()

    def updatePointGUI(self):
        self.ui.altitude.setText(self.mount.obsSite.Alt)
        self.ui.azimut.setText(self.mount.obsSite.Az)
        self.ui.julianDate.setText(self.mount.obsSite.timeJD)

    def updateSetGUI(self):
        pass
