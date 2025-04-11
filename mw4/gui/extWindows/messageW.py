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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import time
import logging

# external packages
from PySide6.QtGui import QColor, QFont, QBrush
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import message_ui


class MessageWindow(toolsQtWidget.MWidget):
    """ """

    log = logging.getLogger("MW4")

    TEXT_NORMAL = 0
    TEXT_HIGHLIGHT = 1
    TEXT_WARNING = 2
    TEXT_ERROR = 3

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = message_ui.Ui_MessageDialog()
        self.ui.setupUi(self)
        self.messFont = None
        self.messColor = None
        self.setupMessage()
        self.app.msg.connect(self.writeMessageQueue)

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("messageW", {})
        self.positionWindow(config)

    def storeConfig(self) -> None:
        """ """
        configMain = self.app.config
        configMain["messageW"] = {}
        config = configMain["messageW"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def clearMessageTable(self) -> None:
        """ """
        mesTab = self.ui.messageTable
        mesTab.setRowCount(0)
        mesTab.setColumnCount(4)
        hl = [" Time", " Source", " Type", "Message / Value"]
        mesTab.setHorizontalHeaderLabels(hl)
        mesTab.setColumnWidth(0, 65)
        mesTab.setColumnWidth(1, 85)
        mesTab.setColumnWidth(2, 150)
        mesTab.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        mesTab.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        mesTab.verticalHeader().setDefaultSectionSize(16)

    def setupMessage(self) -> None:
        """ """
        self.messColor = [
            QBrush(QColor(self.M_PRIM)),
            QBrush(QColor(self.M_TER)),
            QBrush(QColor(self.M_YELLOW)),
            QBrush(QColor(self.M_RED)),
        ]
        fontFam = self.window().font().family()
        self.messFont = [
            QFont(fontFam, weight=QFont.Weight.Normal),
            QFont(fontFam, weight=QFont.Weight.Bold),
            QFont(fontFam, weight=QFont.Weight.Normal),
            QFont(fontFam, weight=QFont.Weight.Normal),
        ]

    def updateListColors(self) -> None:
        """ """
        for row in range(self.ui.messageTable.rowCount()):
            for col in range(self.ui.messageTable.columnCount()):
                item = self.ui.messageTable.item(row, col)
                item.setForeground(self.messColor[0])
                item.setFont(self.messFont[0])

    def colorChange(self) -> None:
        """ """
        self.setStyleSheet(self.mw4Style)
        self.setupMessage()
        self.updateListColors()

    def showWindow(self) -> None:
        """ """
        self.ui.clear.clicked.connect(self.clearMessageTable)
        self.clearMessageTable()
        self.app.update1s.connect(self.writeMessage)
        self.app.colorChange.connect(self.colorChange)
        self.show()

    def writeMessageQueue(self, prio: int, source: str, mType: str, message: str) -> None:
        """ """
        self.log.ui(f"Message window: [{source} - {mType} - {message}]")
        self.app.messageQueue.put((prio, source, mType, message))

    def writeMessage(self) -> None:
        """ """
        while not self.app.messageQueue.empty():
            prio, source, mType, message = self.app.messageQueue.get()

            row = self.ui.messageTable.rowCount()
            self.ui.messageTable.insertRow(row)
            timePrefix = time.strftime("%H:%M:%S", time.localtime())

            if source:
                item = QTableWidgetItem(f"{timePrefix}")
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                item.setForeground(self.messColor[prio])
                item.setFont(self.messFont[prio])
                self.ui.messageTable.setItem(row, self.TEXT_NORMAL, item)

            item = QTableWidgetItem(f"{source}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setFont(self.messFont[prio])
            item.setForeground(self.messColor[prio])
            self.ui.messageTable.setItem(row, self.TEXT_HIGHLIGHT, item)

            item = QTableWidgetItem(f"{mType}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setFont(self.messFont[prio])
            item.setForeground(self.messColor[prio])
            self.ui.messageTable.setItem(row, self.TEXT_WARNING, item)

            item = QTableWidgetItem(f"{message}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setFont(self.messFont[prio])
            item.setForeground(self.messColor[prio])
            self.ui.messageTable.setItem(row, self.TEXT_ERROR, item)

            self.ui.messageTable.scrollToBottom()
