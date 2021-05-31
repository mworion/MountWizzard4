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
#
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import time

# external packages
from PyQt5.QtGui import QTextCursor
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import message_ui


class MessageWindow(toolsQtWidget.MWidget):
    """
    the message window class handles

    """

    __all__ = ['MessageWindow',
               ]

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.ui = message_ui.Ui_MessageDialog()
        self.ui.setupUi(self)

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

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'messageW' not in self.app.config:
            self.app.config['messageW'] = {}
        config = self.app.config['messageW']
        height = config.get('height', 600)
        width = 800
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'messageW' not in self.app.config:
            self.app.config['messageW'] = {}
        config = self.app.config['messageW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.storeConfig()
        self.ui.clear.clicked.disconnect(self.clearWindow)
        self.app.update1s.disconnect(self.writeMessage)
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        :return: true for test purpose
        """
        self.ui.clear.clicked.connect(self.clearWindow)
        self.app.update1s.connect(self.writeMessage)
        self.show()
        return True

    def clearWindow(self):
        """
        :return: true for test purpose
        """
        self.ui.message.clear()
        return True

    @staticmethod
    def splitByN(seq, n):
        """
        A generator to divide a sequence into chunks of n units.
        :param n:
        :return:
        """
        while seq:
            yield seq[:n]
            seq = seq[n:]

    def writeMessage(self):
        """
        writeMessage takes singles with message and writes them to the text
        browser window. types:
            0: normal text
            1: highlighted text
            2: warning text
            3: error text

        setting bit8 means without prefix
        :return: true for test purpose
        """
        while not self.app.messageQueue.empty():
            message, mType = self.app.messageQueue.get()

            withoutPrefix = mType & 0x100
            mType = mType % 256

            if mType > len(self.messColor):
                continue

            if withoutPrefix:
                prefix = ' ' * 9
            else:
                prefix = time.strftime('%H:%M:%S ', time.localtime())

            self.ui.message.setTextColor(self.messColor[mType])
            self.ui.message.setFontWeight(self.messFont[mType])

            for line in self.splitByN(message, 87):
                self.ui.message.insertPlainText(prefix + line + '\n')
            self.ui.message.moveCursor(QTextCursor.End)

        return True
