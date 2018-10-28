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
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import
from mw4.base import widget
from mw4.gui import message_ui


class HemisphereWindow(widget.MWidget):
    logger = logging.getLogger(__name__)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.showStatus = False
        self.ui = message_ui.Ui_HemisphereDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.initConfig()

    def initConfig(self):
        if 'messageW' not in self.app.config:
            return
        config = self.app.config['messageW']
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        if config.get('showStatus'):
            self.showWindow()

    def storeConfig(self):
        if 'messageW' not in self.app.config:
            self.app.config['messageW'] = {}
        config = self.app.config['messageW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['showStatus'] = self.showStatus

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        self.ui.message.setGeometry(10, 10, 780, self.height() - 20)

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)
        self.changeStylesheet(self.app.mainW.ui.openHemisphereW, 'running', 'false')

    def toggleWindow(self):
        self.showStatus = not self.showStatus
        if self.showStatus:
            self.showWindow()
        else:
            self.close()

    def showWindow(self):
        self.showStatus = True
        self.show()
        self.changeStylesheet(self.app.mainW.ui.openHemisphereW, 'running', 'true')
