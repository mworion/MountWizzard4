# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'uploadPopup.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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
from PySide6.QtWidgets import (QApplication, QLineEdit, QProgressBar, QSizePolicy,
    QWidget)

class Ui_UploadPopup(object):
    def setupUi(self, UploadPopup):
        if not UploadPopup.objectName():
            UploadPopup.setObjectName(u"UploadPopup")
        UploadPopup.resize(400, 80)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(UploadPopup.sizePolicy().hasHeightForWidth())
        UploadPopup.setSizePolicy(sizePolicy)
        UploadPopup.setMinimumSize(QSize(400, 0))
        UploadPopup.setMaximumSize(QSize(400, 80))
        UploadPopup.setSizeIncrement(QSize(10, 10))
        UploadPopup.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        UploadPopup.setFont(font)
        self.progressBar = QProgressBar(UploadPopup)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(10, 10, 376, 26))
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QProgressBar.TopToBottom)
        self.statusText = QLineEdit(UploadPopup)
        self.statusText.setObjectName(u"statusText")
        self.statusText.setGeometry(QRect(15, 45, 371, 21))

        self.retranslateUi(UploadPopup)

        QMetaObject.connectSlotsByName(UploadPopup)
    # setupUi

    def retranslateUi(self, UploadPopup):
        UploadPopup.setWindowTitle(QCoreApplication.translate("UploadPopup", u"Device Setup", None))
    # retranslateUi

