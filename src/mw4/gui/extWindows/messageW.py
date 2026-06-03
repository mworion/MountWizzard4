############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import logging
import time
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets import message_ui
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import QTableWidgetItem
from typing import Any


class MessageWindow(MWidget):
    log = logging.getLogger("MW4")
    TEXT_NORMAL = 0
    TEXT_HIGHLIGHT = 1
    TEXT_WARNING = 2
    TEXT_ERROR = 3

    def __init__(self, app: Any, title: str) -> None:
        super().__init__()
        self.app = app
        self.ui = message_ui.Ui_MessageDialog()
        self.ui.setupUi(self.ws)
        self.setWindowTitle("Message")
        self.setMinimumSize(self.FULL_WIDTH, self.HALF_HEIGHT)
        self.setMaximumSize(self.FULL_WIDTH, self.FULL_HEIGHT)
        self.messFont: QFont | None = None
        self.messColor: list = []
        self.setupMessage()
        self.app.msg.connect(self.writeMessageQueue)

    def initConfig(self) -> None:
        config = self.app.config.get("WindowMessage", {})
        self.positionWindow(config)

    def storeConfig(self) -> None:
        configMain = self.app.config
        configMain["WindowMessage"] = {}
        config = configMain["WindowMessage"]
        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()

    def closeEvent(self, closeEvent) -> None:
        self.storeConfig()
        super().closeEvent(closeEvent)

    def clearMessageTable(self) -> None:
        mesTab = self.ui.messageTable
        mesTab.setRowCount(0)
        mesTab.setColumnCount(4)
        hl = [" Time", " Source", " Type", "Message / Value"]
        mesTab.setHorizontalHeaderLabels(hl)
        mesTab.setColumnWidth(0, 75)
        mesTab.setColumnWidth(1, 85)
        mesTab.setColumnWidth(2, 150)
        mesTab.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        mesTab.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        mesTab.verticalHeader().setDefaultSectionSize(16)

    def setupMessage(self) -> None:
        self.messColor = [
            QBrush(QColor(self.M_PRIM)),
            QBrush(QColor(self.M_TER)),
            QBrush(QColor(self.M_YELLOW)),
            QBrush(QColor(self.M_RED)),
        ]

    def updateListColors(self) -> None:
        for row in range(self.ui.messageTable.rowCount()):
            for col in range(self.ui.messageTable.columnCount()):
                item = self.ui.messageTable.item(row, col)
                item.setForeground(self.messColor[0])

    def colorChange(self) -> None:
        self.setStyleSheet(self.mw4Style)
        self.setupMessage()
        self.updateListColors()

    def showWindow(self) -> None:
        self.ui.clear.clicked.connect(self.clearMessageTable)
        self.clearMessageTable()
        self.app.update1s.connect(self.writeMessage)
        self.app.colorChange.connect(self.colorChange)
        self.show()

    def writeMessageQueue(self, prio: int, source: str, mType: str, message: str) -> None:
        self.log.debug(f"Message window:[{source} - {mType} - {message}]")
        self.app.messageQueue.put((prio, source, mType, message))

    def writeMessage(self) -> None:
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
                self.ui.messageTable.setItem(row, self.TEXT_NORMAL, item)

            item = QTableWidgetItem(f"{source}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setForeground(self.messColor[prio])
            self.ui.messageTable.setItem(row, self.TEXT_HIGHLIGHT, item)

            item = QTableWidgetItem(f"{mType}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setForeground(self.messColor[prio])
            self.ui.messageTable.setItem(row, self.TEXT_WARNING, item)

            item = QTableWidgetItem(f"{message}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setForeground(self.messColor[prio])
            self.ui.messageTable.setItem(row, self.TEXT_ERROR, item)

            self.ui.messageTable.scrollToBottom()
