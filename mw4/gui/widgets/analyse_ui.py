# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyse.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QVBoxLayout, QWidget)

from gui.utilities.gNormalScatter import NormalScatter
from gui.utilities.gPolarScatter import PolarScatter

class Ui_AnalyseDialog(object):
    def setupUi(self, AnalyseDialog):
        if not AnalyseDialog.objectName():
            AnalyseDialog.setObjectName(u"AnalyseDialog")
        AnalyseDialog.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AnalyseDialog.sizePolicy().hasHeightForWidth())
        AnalyseDialog.setSizePolicy(sizePolicy)
        AnalyseDialog.setMinimumSize(QSize(800, 600))
        AnalyseDialog.setMaximumSize(QSize(1600, 1230))
        AnalyseDialog.setSizeIncrement(QSize(10, 10))
        AnalyseDialog.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        AnalyseDialog.setFont(font)
        self.verticalLayout = QVBoxLayout(AnalyseDialog)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.groupBox_3 = QGroupBox(AnalyseDialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setProperty(u"large", True)
        self.gridLayout_4 = QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setHorizontalSpacing(10)
        self.gridLayout_4.setVerticalSpacing(5)
        self.gridLayout_4.setContentsMargins(5, 10, 5, 5)
        self.label_18 = QLabel(self.groupBox_3)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setMinimumSize(QSize(0, 21))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(10)
        font1.setBold(True)
        self.label_18.setFont(font1)

        self.gridLayout_4.addWidget(self.label_18, 1, 1, 1, 1)

        self.profile = QLineEdit(self.groupBox_3)
        self.profile.setObjectName(u"profile")
        self.profile.setEnabled(True)
        self.profile.setMinimumSize(QSize(0, 21))
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(10)
        font2.setBold(False)
        self.profile.setFont(font2)
        self.profile.setMouseTracking(False)
        self.profile.setAcceptDrops(False)
        self.profile.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.profile.setFrame(False)
        self.profile.setReadOnly(True)

        self.gridLayout_4.addWidget(self.profile, 1, 2, 1, 1)

        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(0, 21))
        self.label_4.setFont(font1)

        self.gridLayout_4.addWidget(self.label_4, 2, 1, 1, 1)

        self.time = QLineEdit(self.groupBox_3)
        self.time.setObjectName(u"time")
        self.time.setEnabled(True)
        self.time.setMinimumSize(QSize(180, 0))
        self.time.setFont(font2)
        self.time.setMouseTracking(False)
        self.time.setAcceptDrops(False)
        self.time.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.time.setFrame(False)
        self.time.setReadOnly(True)

        self.gridLayout_4.addWidget(self.time, 2, 2, 1, 1)

        self.load = QPushButton(self.groupBox_3)
        self.load.setObjectName(u"load")
        self.load.setMinimumSize(QSize(95, 21))
        self.load.setFont(font)
        self.load.setStyleSheet(u"")

        self.gridLayout_4.addWidget(self.load, 1, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.groupBox_4 = QGroupBox(AnalyseDialog)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setProperty(u"large", True)
        self.gridLayout_5 = QGridLayout(self.groupBox_4)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setHorizontalSpacing(20)
        self.gridLayout_5.setVerticalSpacing(5)
        self.gridLayout_5.setContentsMargins(5, 10, 15, 5)
        self.linkViews = QCheckBox(self.groupBox_4)
        self.linkViews.setObjectName(u"linkViews")
        self.linkViews.setMinimumSize(QSize(0, 21))
        self.linkViews.setFont(font)

        self.gridLayout_5.addWidget(self.linkViews, 1, 1, 1, 1)

        self.showISO = QCheckBox(self.groupBox_4)
        self.showISO.setObjectName(u"showISO")
        self.showISO.setMinimumSize(QSize(0, 21))
        self.showISO.setFont(font)

        self.gridLayout_5.addWidget(self.showISO, 1, 2, 1, 1)

        self.pointsWest = QLabel(self.groupBox_4)
        self.pointsWest.setObjectName(u"pointsWest")
        self.pointsWest.setMinimumSize(QSize(0, 21))
        self.pointsWest.setFont(font1)

        self.gridLayout_5.addWidget(self.pointsWest, 0, 1, 1, 1)

        self.pointsEast = QLabel(self.groupBox_4)
        self.pointsEast.setObjectName(u"pointsEast")
        self.pointsEast.setMinimumSize(QSize(0, 21))
        self.pointsEast.setFont(font1)

        self.gridLayout_5.addWidget(self.pointsEast, 0, 2, 1, 1)

        self.showHorizon = QCheckBox(self.groupBox_4)
        self.showHorizon.setObjectName(u"showHorizon")
        self.showHorizon.setMinimumSize(QSize(0, 21))
        self.showHorizon.setFont(font)

        self.gridLayout_5.addWidget(self.showHorizon, 1, 3, 1, 1)


        self.gridLayout.addWidget(self.groupBox_4, 0, 1, 1, 1)

        self.gridLayout.setColumnStretch(2, 1)

        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.gridLayout_9 = QGridLayout()
        self.gridLayout_9.setSpacing(4)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(5, -1, -1, -1)
        self.groupBox_5 = QGroupBox(AnalyseDialog)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setMinimumSize(QSize(120, 0))
        self.groupBox_5.setMaximumSize(QSize(120, 16777215))
        self.groupBox_5.setProperty(u"large", True)
        self.gridLayout_6 = QGridLayout(self.groupBox_5)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setHorizontalSpacing(4)
        self.gridLayout_6.setVerticalSpacing(0)
        self.gridLayout_6.setContentsMargins(4, 15, 4, 4)
        self.goodPoints = QLineEdit(self.groupBox_5)
        self.goodPoints.setObjectName(u"goodPoints")
        self.goodPoints.setEnabled(True)
        self.goodPoints.setMinimumSize(QSize(0, 0))
        self.goodPoints.setFont(font2)
        self.goodPoints.setMouseTracking(False)
        self.goodPoints.setAcceptDrops(False)
        self.goodPoints.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.goodPoints.setFrame(False)
        self.goodPoints.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.goodPoints.setReadOnly(True)

        self.gridLayout_6.addWidget(self.goodPoints, 13, 0, 1, 1)

        self.modelOrthoError = QLineEdit(self.groupBox_5)
        self.modelOrthoError.setObjectName(u"modelOrthoError")
        self.modelOrthoError.setEnabled(True)
        self.modelOrthoError.setMinimumSize(QSize(0, 0))
        self.modelOrthoError.setFont(font2)
        self.modelOrthoError.setMouseTracking(False)
        self.modelOrthoError.setAcceptDrops(False)
        self.modelOrthoError.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.modelOrthoError.setFrame(False)
        self.modelOrthoError.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.modelOrthoError.setReadOnly(True)

        self.gridLayout_6.addWidget(self.modelOrthoError, 7, 0, 1, 2)

        self.version = QLineEdit(self.groupBox_5)
        self.version.setObjectName(u"version")
        self.version.setEnabled(True)
        self.version.setMinimumSize(QSize(0, 0))
        self.version.setFont(font2)
        self.version.setMouseTracking(False)
        self.version.setAcceptDrops(False)
        self.version.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.version.setFrame(False)
        self.version.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.version.setReadOnly(True)

        self.gridLayout_6.addWidget(self.version, 28, 0, 1, 2)

        self.label = QLabel(self.groupBox_5)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 0))
        self.label.setFont(font1)

        self.gridLayout_6.addWidget(self.label, 15, 0, 1, 3)

        self.label_22 = QLabel(self.groupBox_5)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setMinimumSize(QSize(0, 21))
        self.label_22.setFont(font1)

        self.gridLayout_6.addWidget(self.label_22, 13, 1, 1, 1)

        self.label_15 = QLabel(self.groupBox_5)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_6.addWidget(self.label_15, 16, 2, 1, 1)

        self.modelErrorRMS = QLineEdit(self.groupBox_5)
        self.modelErrorRMS.setObjectName(u"modelErrorRMS")
        self.modelErrorRMS.setEnabled(True)
        self.modelErrorRMS.setMinimumSize(QSize(0, 0))
        self.modelErrorRMS.setFont(font2)
        self.modelErrorRMS.setMouseTracking(False)
        self.modelErrorRMS.setAcceptDrops(False)
        self.modelErrorRMS.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.modelErrorRMS.setFrame(False)
        self.modelErrorRMS.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.modelErrorRMS.setReadOnly(True)

        self.gridLayout_6.addWidget(self.modelErrorRMS, 1, 0, 1, 2)

        self.line_2 = QFrame(self.groupBox_5)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShadow(QFrame.Shadow.Plain)
        self.line_2.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_2, 5, 0, 1, 3)

        self.label_19 = QLabel(self.groupBox_5)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setMinimumSize(QSize(0, 0))
        self.label_19.setFont(font1)

        self.gridLayout_6.addWidget(self.label_19, 24, 0, 1, 3)

        self.firmware = QLineEdit(self.groupBox_5)
        self.firmware.setObjectName(u"firmware")
        self.firmware.setEnabled(True)
        self.firmware.setMinimumSize(QSize(0, 0))
        self.firmware.setFont(font2)
        self.firmware.setMouseTracking(False)
        self.firmware.setAcceptDrops(False)
        self.firmware.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.firmware.setFrame(False)
        self.firmware.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.firmware.setReadOnly(True)

        self.gridLayout_6.addWidget(self.firmware, 31, 0, 1, 2)

        self.subframe = QLineEdit(self.groupBox_5)
        self.subframe.setObjectName(u"subframe")
        self.subframe.setEnabled(True)
        self.subframe.setMinimumSize(QSize(0, 0))
        self.subframe.setFont(font2)
        self.subframe.setMouseTracking(False)
        self.subframe.setAcceptDrops(False)
        self.subframe.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.subframe.setFrame(False)
        self.subframe.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.subframe.setReadOnly(True)

        self.gridLayout_6.addWidget(self.subframe, 22, 0, 1, 2)

        self.line_7 = QFrame(self.groupBox_5)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShadow(QFrame.Shadow.Plain)
        self.line_7.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_7, 23, 0, 1, 3)

        self.modelPolarError = QLineEdit(self.groupBox_5)
        self.modelPolarError.setObjectName(u"modelPolarError")
        self.modelPolarError.setEnabled(True)
        self.modelPolarError.setMinimumSize(QSize(0, 0))
        self.modelPolarError.setFont(font2)
        self.modelPolarError.setMouseTracking(False)
        self.modelPolarError.setAcceptDrops(False)
        self.modelPolarError.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.modelPolarError.setFrame(False)
        self.modelPolarError.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.modelPolarError.setReadOnly(True)

        self.gridLayout_6.addWidget(self.modelPolarError, 4, 0, 1, 2)

        self.line_4 = QFrame(self.groupBox_5)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShadow(QFrame.Shadow.Plain)
        self.line_4.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_4, 11, 0, 1, 3)

        self.label_6 = QLabel(self.groupBox_5)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(0, 0))
        self.label_6.setFont(font1)

        self.gridLayout_6.addWidget(self.label_6, 27, 0, 1, 1)

        self.totalPoints = QLineEdit(self.groupBox_5)
        self.totalPoints.setObjectName(u"totalPoints")
        self.totalPoints.setEnabled(True)
        self.totalPoints.setMinimumSize(QSize(0, 0))
        self.totalPoints.setFont(font2)
        self.totalPoints.setMouseTracking(False)
        self.totalPoints.setAcceptDrops(False)
        self.totalPoints.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.totalPoints.setFrame(False)
        self.totalPoints.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.totalPoints.setReadOnly(True)

        self.gridLayout_6.addWidget(self.totalPoints, 13, 2, 1, 1)

        self.label_17 = QLabel(self.groupBox_5)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setMinimumSize(QSize(0, 0))
        self.label_17.setFont(font1)

        self.gridLayout_6.addWidget(self.label_17, 12, 0, 1, 3)

        self.label_3 = QLabel(self.groupBox_5)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(0, 0))
        self.label_3.setFont(font1)

        self.gridLayout_6.addWidget(self.label_3, 18, 0, 1, 3)

        self.label_20 = QLabel(self.groupBox_5)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_6.addWidget(self.label_20, 22, 2, 1, 1)

        self.line_9 = QFrame(self.groupBox_5)
        self.line_9.setObjectName(u"line_9")
        self.line_9.setFrameShadow(QFrame.Shadow.Plain)
        self.line_9.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_9, 29, 0, 1, 3)

        self.line = QFrame(self.groupBox_5)
        self.line.setObjectName(u"line")
        self.line.setFrameShadow(QFrame.Shadow.Plain)
        self.line.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line, 2, 0, 1, 3)

        self.binning = QLineEdit(self.groupBox_5)
        self.binning.setObjectName(u"binning")
        self.binning.setEnabled(True)
        self.binning.setMinimumSize(QSize(0, 0))
        self.binning.setFont(font2)
        self.binning.setMouseTracking(False)
        self.binning.setAcceptDrops(False)
        self.binning.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.binning.setFrame(False)
        self.binning.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.binning.setReadOnly(True)

        self.gridLayout_6.addWidget(self.binning, 19, 0, 1, 2)

        self.line_8 = QFrame(self.groupBox_5)
        self.line_8.setObjectName(u"line_8")
        self.line_8.setFrameShadow(QFrame.Shadow.Plain)
        self.line_8.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_8, 20, 0, 1, 3)

        self.label_2 = QLabel(self.groupBox_5)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 0))
        self.label_2.setFont(font1)

        self.gridLayout_6.addWidget(self.label_2, 33, 0, 1, 1)

        self.label_13 = QLabel(self.groupBox_5)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_6.addWidget(self.label_13, 4, 2, 1, 1)

        self.focalLength = QLineEdit(self.groupBox_5)
        self.focalLength.setObjectName(u"focalLength")
        self.focalLength.setEnabled(True)
        self.focalLength.setMinimumSize(QSize(0, 0))
        self.focalLength.setFont(font2)
        self.focalLength.setMouseTracking(False)
        self.focalLength.setAcceptDrops(False)
        self.focalLength.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.focalLength.setFrame(False)
        self.focalLength.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.focalLength.setReadOnly(True)

        self.gridLayout_6.addWidget(self.focalLength, 25, 0, 1, 2)

        self.label_5 = QLabel(self.groupBox_5)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 0))
        self.label_5.setFont(font1)

        self.gridLayout_6.addWidget(self.label_5, 21, 0, 1, 3)

        self.solver = QLineEdit(self.groupBox_5)
        self.solver.setObjectName(u"solver")
        self.solver.setEnabled(True)
        self.solver.setMinimumSize(QSize(0, 0))
        self.solver.setFont(font2)
        self.solver.setMouseTracking(False)
        self.solver.setAcceptDrops(False)
        self.solver.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.solver.setFrame(False)
        self.solver.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.solver.setReadOnly(True)

        self.gridLayout_6.addWidget(self.solver, 34, 0, 1, 3)

        self.line_6 = QFrame(self.groupBox_5)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShadow(QFrame.Shadow.Plain)
        self.line_6.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_6, 17, 0, 1, 3)

        self.label_21 = QLabel(self.groupBox_5)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_6.addWidget(self.label_21, 19, 2, 1, 1)

        self.line_3 = QFrame(self.groupBox_5)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShadow(QFrame.Shadow.Plain)
        self.line_3.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_3, 8, 0, 1, 3)

        self.label_7 = QLabel(self.groupBox_5)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(0, 0))
        self.label_7.setFont(font1)

        self.gridLayout_6.addWidget(self.label_7, 30, 0, 1, 1)

        self.line_10 = QFrame(self.groupBox_5)
        self.line_10.setObjectName(u"line_10")
        self.line_10.setFrameShadow(QFrame.Shadow.Plain)
        self.line_10.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_10, 26, 0, 1, 3)

        self.label_11 = QLabel(self.groupBox_5)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(0, 0))
        self.label_11.setFont(font1)

        self.gridLayout_6.addWidget(self.label_11, 0, 0, 1, 3)

        self.label_12 = QLabel(self.groupBox_5)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_6.addWidget(self.label_12, 1, 2, 1, 1)

        self.label_8 = QLabel(self.groupBox_5)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(0, 0))
        self.label_8.setFont(font1)

        self.gridLayout_6.addWidget(self.label_8, 9, 0, 1, 3)

        self.line_5 = QFrame(self.groupBox_5)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShadow(QFrame.Shadow.Plain)
        self.line_5.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_5, 14, 0, 1, 3)

        self.label_16 = QLabel(self.groupBox_5)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_6.addWidget(self.label_16, 25, 2, 1, 1)

        self.label_10 = QLabel(self.groupBox_5)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(0, 0))
        self.label_10.setFont(font1)

        self.gridLayout_6.addWidget(self.label_10, 6, 0, 1, 3)

        self.label_9 = QLabel(self.groupBox_5)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(0, 0))
        self.label_9.setFont(font1)

        self.gridLayout_6.addWidget(self.label_9, 3, 0, 1, 3)

        self.label_14 = QLabel(self.groupBox_5)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_6.addWidget(self.label_14, 7, 2, 1, 1)

        self.modelTerms = QLineEdit(self.groupBox_5)
        self.modelTerms.setObjectName(u"modelTerms")
        self.modelTerms.setEnabled(True)
        self.modelTerms.setMinimumSize(QSize(0, 0))
        self.modelTerms.setFont(font2)
        self.modelTerms.setMouseTracking(False)
        self.modelTerms.setAcceptDrops(False)
        self.modelTerms.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.modelTerms.setFrame(False)
        self.modelTerms.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.modelTerms.setReadOnly(True)

        self.gridLayout_6.addWidget(self.modelTerms, 10, 0, 1, 2)

        self.exposureTime = QLineEdit(self.groupBox_5)
        self.exposureTime.setObjectName(u"exposureTime")
        self.exposureTime.setEnabled(True)
        self.exposureTime.setMinimumSize(QSize(25, 0))
        self.exposureTime.setFont(font2)
        self.exposureTime.setMouseTracking(False)
        self.exposureTime.setAcceptDrops(False)
        self.exposureTime.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.exposureTime.setFrame(False)
        self.exposureTime.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.exposureTime.setReadOnly(True)

        self.gridLayout_6.addWidget(self.exposureTime, 16, 0, 1, 2)

        self.line_11 = QFrame(self.groupBox_5)
        self.line_11.setObjectName(u"line_11")
        self.line_11.setFrameShadow(QFrame.Shadow.Plain)
        self.line_11.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout_6.addWidget(self.line_11, 32, 0, 1, 3)


        self.gridLayout_9.addWidget(self.groupBox_5, 0, 0, 1, 1)

        self.tabWidget = QTabWidget(AnalyseDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMinimumSize(QSize(0, 200))
        self.tabWidget.setMovable(False)
        self.General = QWidget()
        self.General.setObjectName(u"General")
        self.gridLayout_2 = QGridLayout(self.General)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.gridLayout_2.setContentsMargins(4, 4, 4, 4)
        self.groupBox = QGroupBox(self.General)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setProperty(u"large", True)
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, 12, 8, 8)
        self.modelPositions = PolarScatter(self.groupBox)
        self.modelPositions.setObjectName(u"modelPositions")
        sizePolicy.setHeightForWidth(self.modelPositions.sizePolicy().hasHeightForWidth())
        self.modelPositions.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.modelPositions)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_14 = QGroupBox(self.General)
        self.groupBox_14.setObjectName(u"groupBox_14")
        self.groupBox_14.setProperty(u"large", True)
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_14)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(4, 12, 8, 8)
        self.errorDistribution = PolarScatter(self.groupBox_14)
        self.errorDistribution.setObjectName(u"errorDistribution")
        sizePolicy.setHeightForWidth(self.errorDistribution.sizePolicy().hasHeightForWidth())
        self.errorDistribution.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.errorDistribution)


        self.gridLayout_2.addWidget(self.groupBox_14, 1, 0, 1, 1)

        self.groupBox_15 = QGroupBox(self.General)
        self.groupBox_15.setObjectName(u"groupBox_15")
        self.groupBox_15.setProperty(u"large", True)
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox_15)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(4, 12, 8, 0)
        self.errorAscending = NormalScatter(self.groupBox_15)
        self.errorAscending.setObjectName(u"errorAscending")
        sizePolicy.setHeightForWidth(self.errorAscending.sizePolicy().hasHeightForWidth())
        self.errorAscending.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.errorAscending)


        self.gridLayout_2.addWidget(self.groupBox_15, 0, 1, 1, 1)

        self.groupBox_16 = QGroupBox(self.General)
        self.groupBox_16.setObjectName(u"groupBox_16")
        self.groupBox_16.setProperty(u"large", True)
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_16)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(4, 12, 8, 0)
        self.scaleImage = NormalScatter(self.groupBox_16)
        self.scaleImage.setObjectName(u"scaleImage")
        sizePolicy.setHeightForWidth(self.scaleImage.sizePolicy().hasHeightForWidth())
        self.scaleImage.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.scaleImage)


        self.gridLayout_2.addWidget(self.groupBox_16, 1, 1, 1, 1)

        self.tabWidget.addTab(self.General, "")
        self.AltAz = QWidget()
        self.AltAz.setObjectName(u"AltAz")
        self.gridLayout_3 = QGridLayout(self.AltAz)
        self.gridLayout_3.setSpacing(4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(4, 4, 4, 4)
        self.groupBox_2 = QGroupBox(self.AltAz)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setProperty(u"large", True)
        self.horizontalLayout_5 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(4, 12, 8, 0)
        self.raRawErrors = NormalScatter(self.groupBox_2)
        self.raRawErrors.setObjectName(u"raRawErrors")
        sizePolicy.setHeightForWidth(self.raRawErrors.sizePolicy().hasHeightForWidth())
        self.raRawErrors.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.raRawErrors)


        self.gridLayout_3.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.groupBox_7 = QGroupBox(self.AltAz)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setProperty(u"large", True)
        self.horizontalLayout_6 = QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(4, 12, 8, 0)
        self.decRawErrors = NormalScatter(self.groupBox_7)
        self.decRawErrors.setObjectName(u"decRawErrors")
        sizePolicy.setHeightForWidth(self.decRawErrors.sizePolicy().hasHeightForWidth())
        self.decRawErrors.setSizePolicy(sizePolicy)

        self.horizontalLayout_6.addWidget(self.decRawErrors)


        self.gridLayout_3.addWidget(self.groupBox_7, 1, 0, 1, 1)

        self.groupBox_8 = QGroupBox(self.AltAz)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.groupBox_8.setProperty(u"large", True)
        self.horizontalLayout_7 = QHBoxLayout(self.groupBox_8)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(4, 12, 8, 0)
        self.raErrors = NormalScatter(self.groupBox_8)
        self.raErrors.setObjectName(u"raErrors")
        sizePolicy.setHeightForWidth(self.raErrors.sizePolicy().hasHeightForWidth())
        self.raErrors.setSizePolicy(sizePolicy)

        self.horizontalLayout_7.addWidget(self.raErrors)


        self.gridLayout_3.addWidget(self.groupBox_8, 0, 1, 1, 1)

        self.groupBox_9 = QGroupBox(self.AltAz)
        self.groupBox_9.setObjectName(u"groupBox_9")
        self.groupBox_9.setProperty(u"large", True)
        self.horizontalLayout_8 = QHBoxLayout(self.groupBox_9)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(4, 12, 8, 0)
        self.decErrors = NormalScatter(self.groupBox_9)
        self.decErrors.setObjectName(u"decErrors")
        sizePolicy.setHeightForWidth(self.decErrors.sizePolicy().hasHeightForWidth())
        self.decErrors.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.decErrors)


        self.gridLayout_3.addWidget(self.groupBox_9, 1, 1, 1, 1)

        self.tabWidget.addTab(self.AltAz, "")
        self.RaDec = QWidget()
        self.RaDec.setObjectName(u"RaDec")
        self.gridLayout_8 = QGridLayout(self.RaDec)
        self.gridLayout_8.setSpacing(4)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(4, 4, 4, 4)
        self.groupBox_18 = QGroupBox(self.RaDec)
        self.groupBox_18.setObjectName(u"groupBox_18")
        self.groupBox_18.setProperty(u"large", True)
        self.horizontalLayout_10 = QHBoxLayout(self.groupBox_18)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(4, 12, 8, 0)
        self.decRawErrorsRef = NormalScatter(self.groupBox_18)
        self.decRawErrorsRef.setObjectName(u"decRawErrorsRef")
        sizePolicy.setHeightForWidth(self.decRawErrorsRef.sizePolicy().hasHeightForWidth())
        self.decRawErrorsRef.setSizePolicy(sizePolicy)

        self.horizontalLayout_10.addWidget(self.decRawErrorsRef)


        self.gridLayout_8.addWidget(self.groupBox_18, 1, 0, 1, 1)

        self.groupBox_17 = QGroupBox(self.RaDec)
        self.groupBox_17.setObjectName(u"groupBox_17")
        self.groupBox_17.setProperty(u"large", True)
        self.horizontalLayout_9 = QHBoxLayout(self.groupBox_17)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(4, 12, 8, 0)
        self.raRawErrorsRef = NormalScatter(self.groupBox_17)
        self.raRawErrorsRef.setObjectName(u"raRawErrorsRef")
        sizePolicy.setHeightForWidth(self.raRawErrorsRef.sizePolicy().hasHeightForWidth())
        self.raRawErrorsRef.setSizePolicy(sizePolicy)

        self.horizontalLayout_9.addWidget(self.raRawErrorsRef)


        self.gridLayout_8.addWidget(self.groupBox_17, 0, 0, 1, 1)

        self.groupBox_19 = QGroupBox(self.RaDec)
        self.groupBox_19.setObjectName(u"groupBox_19")
        self.groupBox_19.setProperty(u"large", True)
        self.horizontalLayout_11 = QHBoxLayout(self.groupBox_19)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(4, 12, 8, 0)
        self.raErrorsRef = NormalScatter(self.groupBox_19)
        self.raErrorsRef.setObjectName(u"raErrorsRef")
        sizePolicy.setHeightForWidth(self.raErrorsRef.sizePolicy().hasHeightForWidth())
        self.raErrorsRef.setSizePolicy(sizePolicy)

        self.horizontalLayout_11.addWidget(self.raErrorsRef)


        self.gridLayout_8.addWidget(self.groupBox_19, 0, 1, 1, 1)

        self.groupBox_20 = QGroupBox(self.RaDec)
        self.groupBox_20.setObjectName(u"groupBox_20")
        self.groupBox_20.setProperty(u"large", True)
        self.horizontalLayout_12 = QHBoxLayout(self.groupBox_20)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(4, 12, 8, 0)
        self.decErrorsRef = NormalScatter(self.groupBox_20)
        self.decErrorsRef.setObjectName(u"decErrorsRef")
        sizePolicy.setHeightForWidth(self.decErrorsRef.sizePolicy().hasHeightForWidth())
        self.decErrorsRef.setSizePolicy(sizePolicy)

        self.horizontalLayout_12.addWidget(self.decErrorsRef)


        self.gridLayout_8.addWidget(self.groupBox_20, 1, 1, 1, 1)

        self.tabWidget.addTab(self.RaDec, "")

        self.gridLayout_9.addWidget(self.tabWidget, 0, 1, 3, 1)


        self.verticalLayout.addLayout(self.gridLayout_9)

        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(AnalyseDialog)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AnalyseDialog)
    # setupUi

    def retranslateUi(self, AnalyseDialog):
        AnalyseDialog.setWindowTitle(QCoreApplication.translate("AnalyseDialog", u"Analyse Model", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("AnalyseDialog", u"Analysis setup", None))
        self.label_18.setText(QCoreApplication.translate("AnalyseDialog", u"Profile", None))
#if QT_CONFIG(tooltip)
        self.profile.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.profile.setText("")
        self.label_4.setText(QCoreApplication.translate("AnalyseDialog", u"Time [UTC]", None))
#if QT_CONFIG(tooltip)
        self.time.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.time.setText("")
#if QT_CONFIG(tooltip)
        self.load.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Loads the model points from file", None))
#endif // QT_CONFIG(tooltip)
        self.load.setText(QCoreApplication.translate("AnalyseDialog", u"Load", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("AnalyseDialog", u"Analysis View", None))
        self.linkViews.setText(QCoreApplication.translate("AnalyseDialog", u"Link Views", None))
        self.showISO.setText(QCoreApplication.translate("AnalyseDialog", u"2D contour", None))
        self.pointsWest.setText(QCoreApplication.translate("AnalyseDialog", u"Pierside West", None))
        self.pointsWest.setProperty(u"color", QCoreApplication.translate("AnalyseDialog", u"green", None))
        self.pointsEast.setText(QCoreApplication.translate("AnalyseDialog", u"Pierside East", None))
        self.pointsEast.setProperty(u"color", QCoreApplication.translate("AnalyseDialog", u"yellow", None))
        self.showHorizon.setText(QCoreApplication.translate("AnalyseDialog", u"Horizon mask", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("AnalyseDialog", u"Model params", None))
#if QT_CONFIG(tooltip)
        self.goodPoints.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.goodPoints.setText("")
#if QT_CONFIG(tooltip)
        self.modelOrthoError.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.modelOrthoError.setText("")
#if QT_CONFIG(tooltip)
        self.version.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.version.setText("")
        self.label.setText(QCoreApplication.translate("AnalyseDialog", u"Exposure", None))
        self.label_22.setText(QCoreApplication.translate("AnalyseDialog", u"/", None))
        self.label_15.setText(QCoreApplication.translate("AnalyseDialog", u"s", None))
#if QT_CONFIG(tooltip)
        self.modelErrorRMS.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.modelErrorRMS.setText("")
        self.label_19.setText(QCoreApplication.translate("AnalyseDialog", u"FocalLength", None))
#if QT_CONFIG(tooltip)
        self.firmware.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.firmware.setText("")
#if QT_CONFIG(tooltip)
        self.subframe.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.subframe.setText("")
#if QT_CONFIG(tooltip)
        self.modelPolarError.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.modelPolarError.setText("")
        self.label_6.setText(QCoreApplication.translate("AnalyseDialog", u"Build", None))
#if QT_CONFIG(tooltip)
        self.totalPoints.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.totalPoints.setText("")
        self.label_17.setText(QCoreApplication.translate("AnalyseDialog", u"Points", None))
        self.label_3.setText(QCoreApplication.translate("AnalyseDialog", u"Binning", None))
        self.label_20.setText(QCoreApplication.translate("AnalyseDialog", u"%", None))
#if QT_CONFIG(tooltip)
        self.binning.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.binning.setText("")
        self.label_2.setText(QCoreApplication.translate("AnalyseDialog", u"Solver", None))
        self.label_13.setText(QCoreApplication.translate("AnalyseDialog", u"arcsec", None))
#if QT_CONFIG(tooltip)
        self.focalLength.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.focalLength.setText("")
        self.label_5.setText(QCoreApplication.translate("AnalyseDialog", u"Subframe", None))
#if QT_CONFIG(tooltip)
        self.solver.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.solver.setText("")
        self.label_21.setText(QCoreApplication.translate("AnalyseDialog", u"x/y", None))
        self.label_7.setText(QCoreApplication.translate("AnalyseDialog", u"FW", None))
        self.label_11.setText(QCoreApplication.translate("AnalyseDialog", u"Error RMS", None))
        self.label_12.setText(QCoreApplication.translate("AnalyseDialog", u"arcsec", None))
        self.label_8.setText(QCoreApplication.translate("AnalyseDialog", u"Terms", None))
        self.label_16.setText(QCoreApplication.translate("AnalyseDialog", u"mm", None))
        self.label_10.setText(QCoreApplication.translate("AnalyseDialog", u"Ortho Error", None))
        self.label_9.setText(QCoreApplication.translate("AnalyseDialog", u"Polar Error", None))
        self.label_14.setText(QCoreApplication.translate("AnalyseDialog", u"arcsec", None))
#if QT_CONFIG(tooltip)
        self.modelTerms.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.modelTerms.setText("")
#if QT_CONFIG(tooltip)
        self.exposureTime.setToolTip(QCoreApplication.translate("AnalyseDialog", u"Name of Model Points file, where the data is stored. ", None))
#endif // QT_CONFIG(tooltip)
        self.exposureTime.setText("")
        self.groupBox.setTitle(QCoreApplication.translate("AnalyseDialog", u"Overview", None))
#if QT_CONFIG(tooltip)
        self.modelPositions.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_14.setTitle(QCoreApplication.translate("AnalyseDialog", u"Model point errors over polar", None))
#if QT_CONFIG(tooltip)
        self.errorDistribution.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_15.setTitle(QCoreApplication.translate("AnalyseDialog", u"Model point errors in ascending order", None))
#if QT_CONFIG(tooltip)
        self.errorAscending.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_16.setTitle(QCoreApplication.translate("AnalyseDialog", u"Image pixel resolution as scale ", None))
#if QT_CONFIG(tooltip)
        self.scaleImage.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.General), QCoreApplication.translate("AnalyseDialog", u"General Analyse", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("AnalyseDialog", u"RA Raw Error (PlateSolve Result, w/o Model)", None))
#if QT_CONFIG(tooltip)
        self.raRawErrors.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_7.setTitle(QCoreApplication.translate("AnalyseDialog", u"DEC Raw Error (PlateSolve Result, w/o Model)", None))
#if QT_CONFIG(tooltip)
        self.decRawErrors.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_8.setTitle(QCoreApplication.translate("AnalyseDialog", u"RA Error (with Model)", None))
#if QT_CONFIG(tooltip)
        self.raErrors.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_9.setTitle(QCoreApplication.translate("AnalyseDialog", u"DEC Error (with Model)", None))
#if QT_CONFIG(tooltip)
        self.decErrors.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.AltAz), QCoreApplication.translate("AnalyseDialog", u"Alt / Az Analyse", None))
        self.groupBox_18.setTitle(QCoreApplication.translate("AnalyseDialog", u"DEC Raw Error (PlateSolve Result, w/o Model)", None))
#if QT_CONFIG(tooltip)
        self.decRawErrorsRef.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_17.setTitle(QCoreApplication.translate("AnalyseDialog", u"RA Raw Error (PlateSolve Result, w/o Model)", None))
#if QT_CONFIG(tooltip)
        self.raRawErrorsRef.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_19.setTitle(QCoreApplication.translate("AnalyseDialog", u"RA Error (with Model)", None))
#if QT_CONFIG(tooltip)
        self.raErrorsRef.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_20.setTitle(QCoreApplication.translate("AnalyseDialog", u"DEC Error (with Model)", None))
#if QT_CONFIG(tooltip)
        self.decErrorsRef.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.RaDec), QCoreApplication.translate("AnalyseDialog", u"RA / DEC Analyse", None))
    # retranslateUi

