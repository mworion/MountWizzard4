# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bigPopup.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QPushButton,
    QSizePolicy, QWidget)

class Ui_BigPopup(object):
    def setupUi(self, BigPopup):
        if not BigPopup.objectName():
            BigPopup.setObjectName(u"BigPopup")
        BigPopup.resize(251, 107)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(BigPopup.sizePolicy().hasHeightForWidth())
        BigPopup.setSizePolicy(sizePolicy)
        BigPopup.setMinimumSize(QSize(200, 100))
        BigPopup.setMaximumSize(QSize(400, 285))
        BigPopup.setSizeIncrement(QSize(10, 10))
        BigPopup.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        BigPopup.setFont(font)
        self.gridLayout_2 = QGridLayout(BigPopup)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(0)
        self.gridLayout_2.setVerticalSpacing(5)
        self.gridLayout_2.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.mountOn = QPushButton(BigPopup)
        self.mountOn.setObjectName(u"mountOn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.mountOn.sizePolicy().hasHeightForWidth())
        self.mountOn.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.mountOn)

        self.mountOff = QPushButton(BigPopup)
        self.mountOff.setObjectName(u"mountOff")
        sizePolicy1.setHeightForWidth(self.mountOff.sizePolicy().hasHeightForWidth())
        self.mountOff.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.mountOff)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.stop = QPushButton(BigPopup)
        self.stop.setObjectName(u"stop")
        sizePolicy1.setHeightForWidth(self.stop.sizePolicy().hasHeightForWidth())
        self.stop.setSizePolicy(sizePolicy1)

        self.gridLayout_2.addWidget(self.stop, 2, 0, 1, 1)


        self.retranslateUi(BigPopup)

        QMetaObject.connectSlotsByName(BigPopup)
    # setupUi

    def retranslateUi(self, BigPopup):
        BigPopup.setWindowTitle(QCoreApplication.translate("BigPopup", u"Device Setup", None))
        self.mountOn.setText(QCoreApplication.translate("BigPopup", u"Mount On", None))
        self.mountOff.setText(QCoreApplication.translate("BigPopup", u"Mount Off", None))
        self.stop.setText(QCoreApplication.translate("BigPopup", u"Mount Stop", None))
    # retranslateUi

