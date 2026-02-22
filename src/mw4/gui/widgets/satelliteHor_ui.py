# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'satelliteHor.ui'
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

class Ui_SatelliteHorizonDialog(object):
    def setupUi(self, SatelliteHorizonDialog):
        if not SatelliteHorizonDialog.objectName():
            SatelliteHorizonDialog.setObjectName(u"SatelliteHorizonDialog")
        SatelliteHorizonDialog.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SatelliteHorizonDialog.sizePolicy().hasHeightForWidth())
        SatelliteHorizonDialog.setSizePolicy(sizePolicy)
        SatelliteHorizonDialog.setMinimumSize(QSize(400, 285))
        SatelliteHorizonDialog.setMaximumSize(QSize(1600, 1230))
        SatelliteHorizonDialog.setSizeIncrement(QSize(10, 10))
        SatelliteHorizonDialog.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        SatelliteHorizonDialog.setFont(font)
        self.gridLayout = QGridLayout(SatelliteHorizonDialog)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(4, 8, 4, 4)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.groupBox = QGroupBox(SatelliteHorizonDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(0, 0))
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, 3, 4, 0)
        self.label_239 = QLabel(self.groupBox)
        self.label_239.setObjectName(u"label_239")
        self.label_239.setMinimumSize(QSize(0, 25))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(10)
        font1.setBold(False)
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

        self.horizontalSpacer_7 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_7)

        self.label_298 = QLabel(self.groupBox)
        self.label_298.setObjectName(u"label_298")
        self.label_298.setMinimumSize(QSize(0, 25))
        self.label_298.setFont(font1)

        self.horizontalLayout.addWidget(self.label_298)

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
        self.groupHorizon = QGroupBox(SatelliteHorizonDialog)
        self.groupHorizon.setObjectName(u"groupHorizon")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
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


        self.retranslateUi(SatelliteHorizonDialog)

        QMetaObject.connectSlotsByName(SatelliteHorizonDialog)
    # setupUi

    def retranslateUi(self, SatelliteHorizonDialog):
        SatelliteHorizonDialog.setWindowTitle(QCoreApplication.translate("SatelliteHorizonDialog", u"Satellite Horizon", None))
        self.groupBox.setTitle(QCoreApplication.translate("SatelliteHorizonDialog", u"Coordinates", None))
        self.label_239.setText(QCoreApplication.translate("SatelliteHorizonDialog", u"Azimuth", None))
#if QT_CONFIG(tooltip)
        self.satAzimuth.setToolTip(QCoreApplication.translate("SatelliteHorizonDialog", u"Actual azimuth of the satelite from observers position.", None))
#endif // QT_CONFIG(tooltip)
        self.satAzimuth.setText(QCoreApplication.translate("SatelliteHorizonDialog", u"-", None))
        self.label_209.setText(QCoreApplication.translate("SatelliteHorizonDialog", u"\u00b0", None))
        self.label_298.setText(QCoreApplication.translate("SatelliteHorizonDialog", u"Altitude", None))
#if QT_CONFIG(tooltip)
        self.satAltitude.setToolTip(QCoreApplication.translate("SatelliteHorizonDialog", u"Actual altitude of the satelite from observers position.", None))
#endif // QT_CONFIG(tooltip)
        self.satAltitude.setText(QCoreApplication.translate("SatelliteHorizonDialog", u"-", None))
        self.label_206.setText(QCoreApplication.translate("SatelliteHorizonDialog", u"\u00b0", None))
#if QT_CONFIG(tooltip)
        self.groupHorizon.setToolTip(QCoreApplication.translate("SatelliteHorizonDialog", u"Shows the visible track of the satellite when being observed from the position of the mount. ", None))
#endif // QT_CONFIG(tooltip)
        self.groupHorizon.setTitle(QCoreApplication.translate("SatelliteHorizonDialog", u"Satellite path over horizon from observer location", None))
#if QT_CONFIG(tooltip)
        self.satHorizon.setToolTip("")
#endif // QT_CONFIG(tooltip)
    # retranslateUi

