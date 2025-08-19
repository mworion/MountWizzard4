# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'measure.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

from gui.utilities.gMeasure import Measure

class Ui_MeasureDialog(object):
    def setupUi(self, MeasureDialog):
        if not MeasureDialog.objectName():
            MeasureDialog.setObjectName(u"MeasureDialog")
        MeasureDialog.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MeasureDialog.sizePolicy().hasHeightForWidth())
        MeasureDialog.setSizePolicy(sizePolicy)
        MeasureDialog.setMinimumSize(QSize(800, 285))
        MeasureDialog.setMaximumSize(QSize(1600, 1230))
        MeasureDialog.setSizeIncrement(QSize(10, 10))
        MeasureDialog.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        MeasureDialog.setFont(font)
        self.verticalLayout = QVBoxLayout(MeasureDialog)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, 6, 4, 6)
        self.measureGroup = QGroupBox(MeasureDialog)
        self.measureGroup.setObjectName(u"measureGroup")
        self.measureGroup.setProperty(u"large", True)
        self.gridLayout = QGridLayout(self.measureGroup)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 10, 5, 5)
        self.label_2 = QLabel(self.measureGroup)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        self.label_3 = QLabel(self.measureGroup)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 4, 1, 1)

        self.set3 = QComboBox(self.measureGroup)
        self.set3.setObjectName(u"set3")
        self.set3.setMinimumSize(QSize(0, 25))

        self.gridLayout.addWidget(self.set3, 1, 3, 1, 1)

        self.label_4 = QLabel(self.measureGroup)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 3, 1, 1)

        self.set0 = QComboBox(self.measureGroup)
        self.set0.setObjectName(u"set0")
        self.set0.setMinimumSize(QSize(150, 25))

        self.gridLayout.addWidget(self.set0, 1, 0, 1, 1)

        self.label = QLabel(self.measureGroup)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.set1 = QComboBox(self.measureGroup)
        self.set1.setObjectName(u"set1")
        self.set1.setMinimumSize(QSize(150, 25))

        self.gridLayout.addWidget(self.set1, 1, 1, 1, 1)

        self.set4 = QComboBox(self.measureGroup)
        self.set4.setObjectName(u"set4")
        self.set4.setMinimumSize(QSize(150, 25))

        self.gridLayout.addWidget(self.set4, 1, 4, 1, 1)

        self.set2 = QComboBox(self.measureGroup)
        self.set2.setObjectName(u"set2")
        self.set2.setMinimumSize(QSize(0, 25))

        self.gridLayout.addWidget(self.set2, 1, 2, 1, 1)

        self.label_5 = QLabel(self.measureGroup)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 0, 2, 1, 1)


        self.horizontalLayout.addWidget(self.measureGroup)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.measure = Measure(MeasureDialog)
        self.measure.setObjectName(u"measure")
        self.measure.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.measure.sizePolicy().hasHeightForWidth())
        self.measure.setSizePolicy(sizePolicy1)
        self.measure.setMinimumSize(QSize(0, 0))
        self.measure.setMaximumSize(QSize(16777215, 16777215))
        self.measure.setSizeIncrement(QSize(10, 10))
        self.measure.setBaseSize(QSize(10, 10))
        self.measure.setAutoFillBackground(True)
        self.measure.setStyleSheet(u"")

        self.verticalLayout.addWidget(self.measure)

        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(MeasureDialog)

        QMetaObject.connectSlotsByName(MeasureDialog)
    # setupUi

    def retranslateUi(self, MeasureDialog):
        MeasureDialog.setWindowTitle(QCoreApplication.translate("MeasureDialog", u"Measurements", None))
        self.measureGroup.setTitle(QCoreApplication.translate("MeasureDialog", u"Measurement values", None))
        self.label_2.setText(QCoreApplication.translate("MeasureDialog", u"Upper middle chart", None))
        self.label_3.setText(QCoreApplication.translate("MeasureDialog", u"Lower chart", None))
        self.label_4.setText(QCoreApplication.translate("MeasureDialog", u"Lower middle chart", None))
        self.label.setText(QCoreApplication.translate("MeasureDialog", u"Upper chart", None))
        self.label_5.setText(QCoreApplication.translate("MeasureDialog", u"Middle chart", None))
    # retranslateUi

