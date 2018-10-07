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
import mw4_global
import base.widget as mWidget
from gui import message_ui


class MessageWindow(mWidget.MWidget):
    logger = logging.getLogger(__name__)

    def __init__(self, app):
        super(MessageWindow, self).__init__()
        self.app = app
        self.showStatus = False
        self.ui = message_ui.Ui_MessageDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.messColor = [self.COLOR_ASTRO,
                          self.COLOR_WHITE,
                          self.COLOR_YELLOW,
                          self.COLOR_RED,
                          ]
        self.messFont = [PyQt5.QtGui.QFont.Normal,
                         PyQt5.QtGui.QFont.Bold,
                         PyQt5.QtGui.QFont.Normal,
                         PyQt5.QtGui.QFont.Normal,
                         ]

        # link gui blocks
        self.app.message.connect(self.writeMessage)
        self.showWindow()

    def initConfig(self):
        x = self.app.config.get('messageWinPosX', 100)
        y = self.app.config.get('messageWinPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)

    def storeConfig(self):
        self.app.config['messageWinPosX'] = self.pos().x()
        self.app.config['messageWinPosY'] = self.pos().y()

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        self.ui.message.setGeometry(10, 10, 780, self.height() - 20)

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)
        self.changeStylesheet(self.app.mainW.ui.openMessageW, 'running', 'false')

    def toggleWindow(self):
        self.showStatus = not self.showStatus
        if self.showStatus:
            self.showWindow()
        else:
            self.close()

    def showWindow(self):
        self.showStatus = True
        self.show()
        self.changeStylesheet(self.app.mainW.ui.openMessageW, 'running', 'true')

    @PyQt5.QtCore.pyqtSlot(str, int)
    def writeMessage(self, message, mType=0):
        prefix = time.strftime('%H:%M:%S - ', time.localtime())
        message = prefix + message
        self.logger.info('Message window: {0}'.format(message))
        self.ui.message.setTextColor(self.messColor[mType])
        self.ui.message.setFontWeight(self.messFont[mType])
        self.ui.message.insertPlainText(message + '\n')
        self.ui.message.moveCursor(PyQt5.QtGui.QTextCursor.End)

