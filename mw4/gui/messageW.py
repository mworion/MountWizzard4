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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import time
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import
from mw4.gui import widget
from mw4.gui.widgets import message_ui


class MessageWindow(widget.MWidget):
    """
    the message window class handles

    """

    __all__ = ['MessageWindow',
               ]
    version = '0.2'
    logger = logging.getLogger(__name__)

    def __init__(self, app):
        super().__init__()
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

        self.ui.clear.clicked.connect(self.clearWindow)
        self.app.message.connect(self.writeMessage)
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
        height = config.get('height', 600)
        self.resize(800, height)
        if config.get('showStatus'):
            self.showWindow()

    def storeConfig(self):
        if 'messageW' not in self.app.config:
            self.app.config['messageW'] = {}
        config = self.app.config['messageW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['showStatus'] = self.showStatus

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)

    def toggleWindow(self):
        self.showStatus = not self.showStatus
        if self.showStatus:
            self.showWindow()
        else:
            self.close()

    def showWindow(self):
        self.showStatus = True
        self.show()

    def clearWindow(self):
        """
        clearWindow resets the window and shows empty text.

        :return: true for test purpose
        """

        self.ui.message.clear()
        return True

    def writeMessage(self, message, mType=0):
        """
        writeMessage takes singles with message and writes them to the text browser window.
        types:
            0: normal text
            1: highlighted text
            2: warning text
            3: error text

        :param message: message text
        :param mType: message type
        :return: true for test purpose
        """

        if mType < 0:
            return False
        if mType > len(self.messColor):
            return False
        prefix = time.strftime('%H:%M:%S - ', time.localtime())
        message = prefix + message
        self.logger.info('Message window: [{0}]'.format(message))
        self.ui.message.setTextColor(self.messColor[mType])
        self.ui.message.setFontWeight(self.messFont[mType])
        self.ui.message.insertPlainText(message + '\n')
        self.ui.message.moveCursor(PyQt5.QtGui.QTextCursor.End)
        return True
