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

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        if 'messageW' not in self.app.config:
            self.app.config['messageW'] = {}
        config = self.app.config['messageW']
        x = config.get('winPosX', 140)
        y = config.get('winPosY', 140)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        height = config.get('height', 600)
        self.resize(800, height)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

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
        self.storeConfig()

        # gui signals
        self.ui.clear.clicked.disconnect(self.clearWindow)
        self.app.update1s.disconnect(self.writeMessage)

        super().closeEvent(closeEvent)

    def showWindow(self):
        self.show()

        # gui signals
        self.ui.clear.clicked.connect(self.clearWindow)
        self.app.update1s.connect(self.writeMessage)

    def clearWindow(self):
        """
        clearWindow resets the window and shows empty text.

        :return: true for test purpose
        """

        self.ui.message.clear()
        return True

    def writeMessage(self):
        """
        writeMessage takes singles with message and writes them to the text browser window.
        types:
            0: normal text
            1: highlighted text
            2: warning text
            3: error text

        :return: true for test purpose
        """

        while not self.app.messageQueue.empty():
            message, mType = self.app.messageQueue.get()

            if mType < 0:
                continue

            if mType > len(self.messColor):
                continue

            prefix = time.strftime('%H:%M:%S ', time.localtime())

            self.ui.message.setTextColor(self.messColor[mType])
            self.ui.message.setFontWeight(self.messFont[mType])
            self.ui.message.insertPlainText(prefix + message + '\n')
            self.ui.message.moveCursor(QTextCursor.End)

        return True
