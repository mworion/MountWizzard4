# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'downloadPopup.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QProgressBar,
    QSizePolicy, QWidget)

class Ui_DownloadPopup(object):
    def setupUi(self, DownloadPopup):
        if not DownloadPopup.objectName():
            DownloadPopup.setObjectName(u"DownloadPopup")
        DownloadPopup.resize(400, 90)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DownloadPopup.sizePolicy().hasHeightForWidth())
        DownloadPopup.setSizePolicy(sizePolicy)
        DownloadPopup.setMinimumSize(QSize(400, 0))
        DownloadPopup.setMaximumSize(QSize(400, 90))
        DownloadPopup.setSizeIncrement(QSize(10, 10))
        DownloadPopup.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        DownloadPopup.setFont(font)
        self.progressBar = QProgressBar(DownloadPopup)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(95, 15, 291, 26))
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(Qt.Orientation.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QProgressBar.Direction.TopToBottom)
        self.icon = QLabel(DownloadPopup)
        self.icon.setObjectName(u"icon")
        self.icon.setGeometry(QRect(15, 10, 64, 64))
        self.statusText = QLineEdit(DownloadPopup)
        self.statusText.setObjectName(u"statusText")
        self.statusText.setGeometry(QRect(95, 50, 291, 21))
        self.statusText.setFrame(False)

        self.retranslateUi(DownloadPopup)

        QMetaObject.connectSlotsByName(DownloadPopup)
    # setupUi

    def retranslateUi(self, DownloadPopup):
        DownloadPopup.setWindowTitle(QCoreApplication.translate("DownloadPopup", u"Device Setup", None))
        self.icon.setText(QCoreApplication.translate("DownloadPopup", u"TextLabel", None))
    # retranslateUi

