# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'satelliteMap.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from mw4.gui.utilities.gPlotBase import PlotBase

class Ui_SatelliteMapDialog(object):
    def setupUi(self, SatelliteMapDialog):
        if not SatelliteMapDialog.objectName():
            SatelliteMapDialog.setObjectName(u"SatelliteMapDialog")
        SatelliteMapDialog.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SatelliteMapDialog.sizePolicy().hasHeightForWidth())
        SatelliteMapDialog.setSizePolicy(sizePolicy)
        SatelliteMapDialog.setMinimumSize(QSize(400, 285))
        SatelliteMapDialog.setMaximumSize(QSize(1600, 1230))
        SatelliteMapDialog.setSizeIncrement(QSize(10, 10))
        SatelliteMapDialog.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        SatelliteMapDialog.setFont(font)
        self.gridLayout = QGridLayout(SatelliteMapDialog)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(4, 8, 4, 4)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.groupBox = QGroupBox(SatelliteMapDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(0, 0))
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, 3, 4, 0)
        self.label_274 = QLabel(self.groupBox)
        self.label_274.setObjectName(u"label_274")
        self.label_274.setMinimumSize(QSize(0, 25))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(10)
        font1.setBold(False)
        self.label_274.setFont(font1)

        self.horizontalLayout.addWidget(self.label_274)

        self.satLatitude = QLineEdit(self.groupBox)
        self.satLatitude.setObjectName(u"satLatitude")
        self.satLatitude.setEnabled(True)
        self.satLatitude.setMinimumSize(QSize(0, 25))
        self.satLatitude.setMaximumSize(QSize(60, 16777215))
        self.satLatitude.setFont(font1)
        self.satLatitude.setMouseTracking(False)
        self.satLatitude.setAcceptDrops(False)
        self.satLatitude.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.satLatitude.setFrame(False)
        self.satLatitude.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.satLatitude.setReadOnly(True)

        self.horizontalLayout.addWidget(self.satLatitude)

        self.label_332 = QLabel(self.groupBox)
        self.label_332.setObjectName(u"label_332")
        self.label_332.setMinimumSize(QSize(0, 25))
        self.label_332.setFont(font1)
        self.label_332.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_332.setWordWrap(False)

        self.horizontalLayout.addWidget(self.label_332)

        self.horizontalSpacer_4 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.label_334 = QLabel(self.groupBox)
        self.label_334.setObjectName(u"label_334")
        self.label_334.setMinimumSize(QSize(0, 25))
        self.label_334.setFont(font1)

        self.horizontalLayout.addWidget(self.label_334)

        self.satLongitude = QLineEdit(self.groupBox)
        self.satLongitude.setObjectName(u"satLongitude")
        self.satLongitude.setEnabled(True)
        self.satLongitude.setMinimumSize(QSize(0, 25))
        self.satLongitude.setMaximumSize(QSize(60, 16777215))
        self.satLongitude.setFont(font1)
        self.satLongitude.setMouseTracking(False)
        self.satLongitude.setAcceptDrops(False)
        self.satLongitude.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.satLongitude.setFrame(False)
        self.satLongitude.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.satLongitude.setReadOnly(True)

        self.horizontalLayout.addWidget(self.satLongitude)

        self.label_335 = QLabel(self.groupBox)
        self.label_335.setObjectName(u"label_335")
        self.label_335.setMinimumSize(QSize(0, 25))
        self.label_335.setFont(font1)
        self.label_335.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_335.setWordWrap(False)

        self.horizontalLayout.addWidget(self.label_335)

        self.horizontalSpacer_5 = QSpacerItem(70, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_5)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.groupEarth = QGroupBox(SatelliteMapDialog)
        self.groupEarth.setObjectName(u"groupEarth")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupEarth.sizePolicy().hasHeightForWidth())
        self.groupEarth.setSizePolicy(sizePolicy1)
        self.groupEarth.setProperty(u"large", True)
        self.gridLayout_5 = QGridLayout(self.groupEarth)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(4, 12, 8, 4)
        self.satEarth = PlotBase(self.groupEarth)
        self.satEarth.setObjectName(u"satEarth")
        sizePolicy1.setHeightForWidth(self.satEarth.sizePolicy().hasHeightForWidth())
        self.satEarth.setSizePolicy(sizePolicy1)

        self.gridLayout_5.addWidget(self.satEarth, 0, 0, 1, 1)


        self.horizontalLayout_4.addWidget(self.groupEarth)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(SatelliteMapDialog)

        QMetaObject.connectSlotsByName(SatelliteMapDialog)
    # setupUi

    def retranslateUi(self, SatelliteMapDialog):
        SatelliteMapDialog.setWindowTitle(QCoreApplication.translate("SatelliteMapDialog", u"Satellite Map", None))
        self.groupBox.setTitle(QCoreApplication.translate("SatelliteMapDialog", u"Coordinates", None))
        self.label_274.setText(QCoreApplication.translate("SatelliteMapDialog", u"Latitude", None))
#if QT_CONFIG(tooltip)
        self.satLatitude.setToolTip(QCoreApplication.translate("SatelliteMapDialog", u"Actual latitude where the satellite could be seen in zenith.", None))
#endif // QT_CONFIG(tooltip)
        self.satLatitude.setText(QCoreApplication.translate("SatelliteMapDialog", u"-", None))
        self.label_332.setText(QCoreApplication.translate("SatelliteMapDialog", u"\u00b0", None))
        self.label_334.setText(QCoreApplication.translate("SatelliteMapDialog", u"Longitude", None))
#if QT_CONFIG(tooltip)
        self.satLongitude.setToolTip(QCoreApplication.translate("SatelliteMapDialog", u"Actual longitude where the satellite could be seen in zenith.", None))
#endif // QT_CONFIG(tooltip)
        self.satLongitude.setText(QCoreApplication.translate("SatelliteMapDialog", u"-", None))
        self.label_335.setText(QCoreApplication.translate("SatelliteMapDialog", u"\u00b0", None))
#if QT_CONFIG(tooltip)
        self.groupEarth.setToolTip(QCoreApplication.translate("SatelliteMapDialog", u"<html><head/><body><p>Shows the satellite path vertical over ground.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupEarth.setTitle(QCoreApplication.translate("SatelliteMapDialog", u"Satellite path over earth surface", None))
#if QT_CONFIG(tooltip)
        self.satEarth.setToolTip("")
#endif // QT_CONFIG(tooltip)
    # retranslateUi

