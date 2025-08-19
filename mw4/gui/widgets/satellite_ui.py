# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'satellite.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from gui.utilities.gPlotBase import PlotBase

class Ui_SatelliteDialog(object):
    def setupUi(self, SatelliteDialog):
        if not SatelliteDialog.objectName():
            SatelliteDialog.setObjectName(u"SatelliteDialog")
        SatelliteDialog.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SatelliteDialog.sizePolicy().hasHeightForWidth())
        SatelliteDialog.setSizePolicy(sizePolicy)
        SatelliteDialog.setMinimumSize(QSize(800, 285))
        SatelliteDialog.setMaximumSize(QSize(1600, 600))
        SatelliteDialog.setSizeIncrement(QSize(10, 10))
        SatelliteDialog.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        SatelliteDialog.setFont(font)
        self.gridLayout = QGridLayout(SatelliteDialog)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(4, 8, 4, 4)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.groupBox = QGroupBox(SatelliteDialog)
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

        self.horizontalSpacer_4 = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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

        self.label_239 = QLabel(self.groupBox)
        self.label_239.setObjectName(u"label_239")
        self.label_239.setMinimumSize(QSize(0, 25))
        self.label_239.setFont(font1)

        self.horizontalLayout.addWidget(self.label_239)

        self.satAzimuth = QLineEdit(self.groupBox)
        self.satAzimuth.setObjectName(u"satAzimuth")
        self.satAzimuth.setEnabled(True)
        self.satAzimuth.setMinimumSize(QSize(0, 25))
        self.satAzimuth.setMaximumSize(QSize(60, 16777215))
        self.satAzimuth.setFont(font1)
        self.satAzimuth.setMouseTracking(False)
        self.satAzimuth.setAcceptDrops(False)
        self.satAzimuth.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.satAzimuth.setFrame(False)
        self.satAzimuth.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.satAzimuth.setReadOnly(True)

        self.horizontalLayout.addWidget(self.satAzimuth)

        self.label_209 = QLabel(self.groupBox)
        self.label_209.setObjectName(u"label_209")
        self.label_209.setMinimumSize(QSize(0, 25))
        self.label_209.setFont(font1)
        self.label_209.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_209.setWordWrap(False)

        self.horizontalLayout.addWidget(self.label_209)

        self.horizontalSpacer_7 = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_7)

        self.satAltitude = QLineEdit(self.groupBox)
        self.satAltitude.setObjectName(u"satAltitude")
        self.satAltitude.setEnabled(True)
        self.satAltitude.setMinimumSize(QSize(0, 25))
        self.satAltitude.setMaximumSize(QSize(60, 16777215))
        self.satAltitude.setFont(font1)
        self.satAltitude.setMouseTracking(False)
        self.satAltitude.setAcceptDrops(False)
        self.satAltitude.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.satAltitude.setFrame(False)
        self.satAltitude.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.satAltitude.setReadOnly(True)

        self.horizontalLayout.addWidget(self.satAltitude)

        self.label_298 = QLabel(self.groupBox)
        self.label_298.setObjectName(u"label_298")
        self.label_298.setMinimumSize(QSize(0, 25))
        self.label_298.setFont(font1)

        self.horizontalLayout.addWidget(self.label_298)

        self.label_206 = QLabel(self.groupBox)
        self.label_206.setObjectName(u"label_206")
        self.label_206.setFont(font1)
        self.label_206.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_206.setWordWrap(False)

        self.horizontalLayout.addWidget(self.label_206)

        self.horizontalSpacer_8 = QSpacerItem(80, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_8)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.groupEarth = QGroupBox(SatelliteDialog)
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

        self.groupHorizon = QGroupBox(SatelliteDialog)
        self.groupHorizon.setObjectName(u"groupHorizon")
        sizePolicy1.setHeightForWidth(self.groupHorizon.sizePolicy().hasHeightForWidth())
        self.groupHorizon.setSizePolicy(sizePolicy1)
        self.groupHorizon.setProperty(u"large", True)
        self.gridLayout_4 = QGridLayout(self.groupHorizon)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(4, 12, 8, 4)
        self.satHorizon = PlotBase(self.groupHorizon)
        self.satHorizon.setObjectName(u"satHorizon")
        sizePolicy1.setHeightForWidth(self.satHorizon.sizePolicy().hasHeightForWidth())
        self.satHorizon.setSizePolicy(sizePolicy1)

        self.gridLayout_4.addWidget(self.satHorizon, 0, 0, 1, 1)


        self.horizontalLayout_4.addWidget(self.groupHorizon)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(SatelliteDialog)

        QMetaObject.connectSlotsByName(SatelliteDialog)
    # setupUi

    def retranslateUi(self, SatelliteDialog):
        SatelliteDialog.setWindowTitle(QCoreApplication.translate("SatelliteDialog", u"Satellite", None))
        self.groupBox.setTitle(QCoreApplication.translate("SatelliteDialog", u"Coordinates", None))
        self.label_274.setText(QCoreApplication.translate("SatelliteDialog", u"Latitude", None))
#if QT_CONFIG(tooltip)
        self.satLatitude.setToolTip(QCoreApplication.translate("SatelliteDialog", u"Actual latitude where the satellite could be seen in zenith.", None))
#endif // QT_CONFIG(tooltip)
        self.satLatitude.setText(QCoreApplication.translate("SatelliteDialog", u"-", None))
        self.label_332.setText(QCoreApplication.translate("SatelliteDialog", u"\u00b0", None))
        self.label_334.setText(QCoreApplication.translate("SatelliteDialog", u"Longitude", None))
#if QT_CONFIG(tooltip)
        self.satLongitude.setToolTip(QCoreApplication.translate("SatelliteDialog", u"Actual longitude where the satellite could be seen in zenith.", None))
#endif // QT_CONFIG(tooltip)
        self.satLongitude.setText(QCoreApplication.translate("SatelliteDialog", u"-", None))
        self.label_335.setText(QCoreApplication.translate("SatelliteDialog", u"\u00b0", None))
        self.label_239.setText(QCoreApplication.translate("SatelliteDialog", u"Azimuth", None))
#if QT_CONFIG(tooltip)
        self.satAzimuth.setToolTip(QCoreApplication.translate("SatelliteDialog", u"Actual azimuth of the satelite from observers position.", None))
#endif // QT_CONFIG(tooltip)
        self.satAzimuth.setText(QCoreApplication.translate("SatelliteDialog", u"-", None))
        self.label_209.setText(QCoreApplication.translate("SatelliteDialog", u"\u00b0", None))
#if QT_CONFIG(tooltip)
        self.satAltitude.setToolTip(QCoreApplication.translate("SatelliteDialog", u"Actual altitude of the satelite from observers position.", None))
#endif // QT_CONFIG(tooltip)
        self.satAltitude.setText(QCoreApplication.translate("SatelliteDialog", u"-", None))
        self.label_298.setText(QCoreApplication.translate("SatelliteDialog", u"Altitude", None))
        self.label_206.setText(QCoreApplication.translate("SatelliteDialog", u"\u00b0", None))
#if QT_CONFIG(tooltip)
        self.groupEarth.setToolTip(QCoreApplication.translate("SatelliteDialog", u"<html><head/><body><p>Shows the satellite path vertical over ground.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupEarth.setTitle(QCoreApplication.translate("SatelliteDialog", u"Satellite path over earth surface", None))
#if QT_CONFIG(tooltip)
        self.satEarth.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.groupHorizon.setToolTip(QCoreApplication.translate("SatelliteDialog", u"Shows the visible track of the satellite when being observed from the position of the mount. ", None))
#endif // QT_CONFIG(tooltip)
        self.groupHorizon.setTitle(QCoreApplication.translate("SatelliteDialog", u"Satellite path over horizon from observer location", None))
#if QT_CONFIG(tooltip)
        self.satHorizon.setToolTip("")
#endif // QT_CONFIG(tooltip)
    # retranslateUi

