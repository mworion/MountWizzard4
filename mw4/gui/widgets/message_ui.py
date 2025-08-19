# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'message.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
    QHeaderView, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MessageDialog(object):
    def setupUi(self, MessageDialog):
        if not MessageDialog.objectName():
            MessageDialog.setObjectName(u"MessageDialog")
        MessageDialog.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MessageDialog.sizePolicy().hasHeightForWidth())
        MessageDialog.setSizePolicy(sizePolicy)
        MessageDialog.setMinimumSize(QSize(800, 285))
        MessageDialog.setMaximumSize(QSize(800, 1200))
        MessageDialog.setSizeIncrement(QSize(10, 10))
        MessageDialog.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        MessageDialog.setFont(font)
        self.verticalLayout = QVBoxLayout(MessageDialog)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, 4, 4, 4)
        self.clear = QPushButton(MessageDialog)
        self.clear.setObjectName(u"clear")
        self.clear.setMinimumSize(QSize(100, 25))
        self.clear.setMaximumSize(QSize(100, 25))

        self.horizontalLayout.addWidget(self.clear)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.line = QFrame(MessageDialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShadow(QFrame.Plain)
        self.line.setLineWidth(2)
        self.line.setMidLineWidth(1)
        self.line.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayout.addWidget(self.line)

        self.messageTable = QTableWidget(MessageDialog)
        self.messageTable.setObjectName(u"messageTable")
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(10)
        font1.setBold(False)
        self.messageTable.setFont(font1)
        self.messageTable.setFrameShape(QFrame.NoFrame)
        self.messageTable.setLineWidth(0)
        self.messageTable.setAutoScrollMargin(0)
        self.messageTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.messageTable.setTabKeyNavigation(False)
        self.messageTable.setProperty(u"showDropIndicator", False)
        self.messageTable.setDragDropOverwriteMode(False)
        self.messageTable.setAlternatingRowColors(False)
        self.messageTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.messageTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.messageTable.setShowGrid(False)
        self.messageTable.setGridStyle(Qt.DotLine)
        self.messageTable.setSortingEnabled(False)
        self.messageTable.setWordWrap(True)
        self.messageTable.setCornerButtonEnabled(False)
        self.messageTable.setColumnCount(0)
        self.messageTable.horizontalHeader().setCascadingSectionResizes(True)
        self.messageTable.horizontalHeader().setMinimumSectionSize(5)
        self.messageTable.horizontalHeader().setDefaultSectionSize(80)
        self.messageTable.horizontalHeader().setHighlightSections(True)
        self.messageTable.horizontalHeader().setProperty(u"showSortIndicator", False)
        self.messageTable.horizontalHeader().setStretchLastSection(True)
        self.messageTable.verticalHeader().setVisible(False)
        self.messageTable.verticalHeader().setCascadingSectionResizes(True)
        self.messageTable.verticalHeader().setMinimumSectionSize(1)
        self.messageTable.verticalHeader().setDefaultSectionSize(10)
        self.messageTable.verticalHeader().setHighlightSections(True)
        self.messageTable.verticalHeader().setProperty(u"showSortIndicator", False)
        self.messageTable.verticalHeader().setStretchLastSection(False)

        self.verticalLayout.addWidget(self.messageTable)


        self.retranslateUi(MessageDialog)

        QMetaObject.connectSlotsByName(MessageDialog)
    # setupUi

    def retranslateUi(self, MessageDialog):
        MessageDialog.setWindowTitle(QCoreApplication.translate("MessageDialog", u"Messages", None))
        self.clear.setText(QCoreApplication.translate("MessageDialog", u"Clear window", None))
#if QT_CONFIG(tooltip)
        self.messageTable.setToolTip(QCoreApplication.translate("MessageDialog", u"<html><head/><body><p>Messages</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

