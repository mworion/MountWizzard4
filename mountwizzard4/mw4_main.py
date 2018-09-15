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
import mountcontrol
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

    def quit(self):
        pass