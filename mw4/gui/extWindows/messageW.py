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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import time

# external packages
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

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
        self.messFont = None
        self.messColor = None
        self.setupMessage()

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'messageW' not in self.app.config:
            self.app.config['messageW'] = {}
        config = self.app.config['messageW']

        self.positionWindow(config)
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        if 'messageW' not in config:
            config['messageW'] = {}
        else:
            config['messageW'].clear()
        config = config['messageW']

        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def clearMessageTable(self):
        """
        :return:
        """
        mesTab = self.ui.messageTable
        mesTab.setRowCount(0)
        mesTab.setColumnCount(4)
        hl = [' Time', ' Source', ' Type', 'Message / Value']
        mesTab.setHorizontalHeaderLabels(hl)
        mesTab.setColumnWidth(0, 65)
        mesTab.setColumnWidth(1, 85)
        mesTab.setColumnWidth(2, 135)
        mesTab.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        mesTab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        mesTab.verticalHeader().setDefaultSectionSize(16)
        return True

    def setupMessage(self):
        """
        :return:
        """
        self.messColor = [QColor(self.M_BLUE),
                          QColor(self.M_WHITE),
                          QColor(self.M_YELLOW),
                          QColor(self.M_RED),
                          ]
        fontFam = self.window().font().family()
        self.messFont = [QFont(fontFam, weight=QFont.Normal),
                         QFont(fontFam, weight=QFont.Bold),
                         QFont(fontFam, weight=QFont.Normal),
                         QFont(fontFam, weight=QFont.Normal),
                         ]
        return True

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.setupMessage()
        self.clearMessageTable()
        return True

    def showWindow(self):
        """
        :return: true for test purpose
        """
        self.ui.clear.clicked.connect(self.clearMessageTable)
        self.clearMessageTable()
        self.app.update1s.connect(self.writeMessage)
        self.app.colorChange.connect(self.colorChange)
        self.show()
        return True

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
            prio, source, mType, message = self.app.messageQueue.get()

            row = self.ui.messageTable.rowCount()
            self.ui.messageTable.insertRow(row)
            timePrefix = time.strftime('%H:%M:%S', time.localtime())

            if source:
                item = QTableWidgetItem(f'{timePrefix}')
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setForeground(self.messColor[prio])
                item.setFont(self.messFont[prio])
                self.ui.messageTable.setItem(row, 0, item)

            item = QTableWidgetItem(f'{source}')
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item.setFont(self.messFont[prio])
            item.setForeground(self.messColor[prio])
            self.ui.messageTable.setItem(row, 1, item)

            item = QTableWidgetItem(f'{mType}')
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item.setFont(self.messFont[prio])
            item.setForeground(self.messColor[prio])
            self.ui.messageTable.setItem(row, 2, item)

            item = QTableWidgetItem(f'{message}')
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item.setFont(self.messFont[prio])
            item.setForeground(self.messColor[prio])
            self.ui.messageTable.setItem(row, 3, item)

            self.ui.messageTable.scrollToBottom()

        return True
