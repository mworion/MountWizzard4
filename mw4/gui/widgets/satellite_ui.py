# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'satellite.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from gui.utilities.tools4pyqtgraph import PlotBase

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
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_273 = QLabel(SatelliteDialog)
        self.label_273.setObjectName(u"label_273")
        self.label_273.setMinimumSize(QSize(0, 25))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(10)
        font1.setBold(False)
        self.label_273.setFont(font1)

        self.horizontalLayout_5.addWidget(self.label_273)

        self.satLatitude = QLineEdit(SatelliteDialog)
        self.satLatitude.setObjectName(u"satLatitude")
        self.satLatitude.setEnabled(True)
        self.satLatitude.setMinimumSize(QSize(0, 25))
        self.satLatitude.setMaximumSize(QSize(60, 16777215))
        self.satLatitude.setFont(font1)
        self.satLatitude.setMouseTracking(False)
        self.satLatitude.setAcceptDrops(False)
        self.satLatitude.setLayoutDirection(Qt.RightToLeft)
        self.satLatitude.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.satLatitude.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.satLatitude)

        self.label_330 = QLabel(SatelliteDialog)
        self.label_330.setObjectName(u"label_330")
        self.label_330.setMinimumSize(QSize(0, 25))
        self.label_330.setFont(font1)
        self.label_330.setAlignment(Qt.AlignCenter)
        self.label_330.setWordWrap(False)

        self.horizontalLayout_5.addWidget(self.label_330)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.label_333 = QLabel(SatelliteDialog)
        self.label_333.setObjectName(u"label_333")
        self.label_333.setMinimumSize(QSize(0, 25))
        self.label_333.setFont(font1)

        self.horizontalLayout_5.addWidget(self.label_333)

        self.satLongitude = QLineEdit(SatelliteDialog)
        self.satLongitude.setObjectName(u"satLongitude")
        self.satLongitude.setEnabled(True)
        self.satLongitude.setMinimumSize(QSize(0, 25))
        self.satLongitude.setMaximumSize(QSize(60, 16777215))
        self.satLongitude.setFont(font1)
        self.satLongitude.setMouseTracking(False)
        self.satLongitude.setAcceptDrops(False)
        self.satLongitude.setLayoutDirection(Qt.RightToLeft)
        self.satLongitude.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.satLongitude.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.satLongitude)

        self.label_205 = QLabel(SatelliteDialog)
        self.label_205.setObjectName(u"label_205")
        self.label_205.setFont(font1)
        self.label_205.setAlignment(Qt.AlignCenter)
        self.label_205.setWordWrap(False)

        self.horizontalLayout_5.addWidget(self.label_205)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_2)

        self.label_238 = QLabel(SatelliteDialog)
        self.label_238.setObjectName(u"label_238")
        self.label_238.setMinimumSize(QSize(0, 25))
        self.label_238.setFont(font1)

        self.horizontalLayout_5.addWidget(self.label_238)

        self.satAzimuth = QLineEdit(SatelliteDialog)
        self.satAzimuth.setObjectName(u"satAzimuth")
        self.satAzimuth.setEnabled(True)
        self.satAzimuth.setMinimumSize(QSize(0, 25))
        self.satAzimuth.setMaximumSize(QSize(60, 16777215))
        self.satAzimuth.setFont(font1)
        self.satAzimuth.setMouseTracking(False)
        self.satAzimuth.setAcceptDrops(False)
        self.satAzimuth.setLayoutDirection(Qt.RightToLeft)
        self.satAzimuth.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.satAzimuth.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.satAzimuth)

        self.label_208 = QLabel(SatelliteDialog)
        self.label_208.setObjectName(u"label_208")
        self.label_208.setMinimumSize(QSize(0, 25))
        self.label_208.setFont(font1)
        self.label_208.setAlignment(Qt.AlignCenter)
        self.label_208.setWordWrap(False)

        self.horizontalLayout_5.addWidget(self.label_208)

        self.horizontalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.label_297 = QLabel(SatelliteDialog)
        self.label_297.setObjectName(u"label_297")
        self.label_297.setMinimumSize(QSize(0, 25))
        self.label_297.setFont(font1)

        self.horizontalLayout_5.addWidget(self.label_297)

        self.satAltitude = QLineEdit(SatelliteDialog)
        self.satAltitude.setObjectName(u"satAltitude")
        self.satAltitude.setEnabled(True)
        self.satAltitude.setMinimumSize(QSize(0, 25))
        self.satAltitude.setMaximumSize(QSize(60, 16777215))
        self.satAltitude.setFont(font1)
        self.satAltitude.setMouseTracking(False)
        self.satAltitude.setAcceptDrops(False)
        self.satAltitude.setLayoutDirection(Qt.RightToLeft)
        self.satAltitude.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.satAltitude.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.satAltitude)

        self.label_331 = QLabel(SatelliteDialog)
        self.label_331.setObjectName(u"label_331")
        self.label_331.setMinimumSize(QSize(0, 25))
        self.label_331.setFont(font1)
        self.label_331.setAlignment(Qt.AlignCenter)
        self.label_331.setWordWrap(False)

        self.horizontalLayout_5.addWidget(self.label_331)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_6)

        self.horizontalLayout_5.setStretch(7, 1)
        self.horizontalLayout_5.setStretch(15, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.groupEarth = QGroupBox(SatelliteDialog)
        self.groupEarth.setObjectName(u"groupEarth")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupEarth.sizePolicy().hasHeightForWidth())
        self.groupEarth.setSizePolicy(sizePolicy1)
        self.groupEarth.setProperty("large", True)
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
        self.groupHorizon.setProperty("large", True)
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
        self.label_273.setText(QCoreApplication.translate("SatelliteDialog", u"Latitude", None))
#if QT_CONFIG(tooltip)
        self.satLatitude.setToolTip(QCoreApplication.translate("SatelliteDialog", u"Actual latitude where the satellite could be seen in zenith.", None))
#endif // QT_CONFIG(tooltip)
        self.satLatitude.setText(QCoreApplication.translate("SatelliteDialog", u"-", None))
        self.label_330.setText(QCoreApplication.translate("SatelliteDialog", u"\u00b0", None))
        self.label_333.setText(QCoreApplication.translate("SatelliteDialog", u"Longitude", None))
#if QT_CONFIG(tooltip)
        self.satLongitude.setToolTip(QCoreApplication.translate("SatelliteDialog", u"Actual longitude where the satellite could be seen in zenith.", None))
#endif // QT_CONFIG(tooltip)
        self.satLongitude.setText(QCoreApplication.translate("SatelliteDialog", u"-", None))
        self.label_205.setText(QCoreApplication.translate("SatelliteDialog", u"\u00b0", None))
        self.label_238.setText(QCoreApplication.translate("SatelliteDialog", u"Azimuth", None))
#if QT_CONFIG(tooltip)
        self.satAzimuth.setToolTip(QCoreApplication.translate("SatelliteDialog", u"Actual azimuth of the satelite from observers position.", None))
#endif // QT_CONFIG(tooltip)
        self.satAzimuth.setText(QCoreApplication.translate("SatelliteDialog", u"-", None))
        self.label_208.setText(QCoreApplication.translate("SatelliteDialog", u"\u00b0", None))
        self.label_297.setText(QCoreApplication.translate("SatelliteDialog", u"Altitude", None))
#if QT_CONFIG(tooltip)
        self.satAltitude.setToolTip(QCoreApplication.translate("SatelliteDialog", u"Actual altitude of the satelite from observers position.", None))
#endif // QT_CONFIG(tooltip)
        self.satAltitude.setText(QCoreApplication.translate("SatelliteDialog", u"-", None))
        self.label_331.setText(QCoreApplication.translate("SatelliteDialog", u"\u00b0", None))
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

