# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'hemisphere.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QTabWidget, QVBoxLayout, QWidget)

from gui.utilities.gHemisphere import Hemisphere
from gui.utilities.gPlotBase import PlotBase

class Ui_HemisphereDialog(object):
    def setupUi(self, HemisphereDialog):
        if not HemisphereDialog.objectName():
            HemisphereDialog.setObjectName(u"HemisphereDialog")
        HemisphereDialog.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(HemisphereDialog.sizePolicy().hasHeightForWidth())
        HemisphereDialog.setSizePolicy(sizePolicy)
        HemisphereDialog.setMinimumSize(QSize(800, 600))
        HemisphereDialog.setMaximumSize(QSize(1600, 1230))
        HemisphereDialog.setSizeIncrement(QSize(10, 10))
        HemisphereDialog.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        HemisphereDialog.setFont(font)
        self.verticalLayout = QVBoxLayout(HemisphereDialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.operationModeGroup = QGroupBox(HemisphereDialog)
        self.operationModeGroup.setObjectName(u"operationModeGroup")
        self.operationModeGroup.setMinimumSize(QSize(120, 0))
        self.operationModeGroup.setProperty(u"large", True)
        self.gridLayout_7 = QGridLayout(self.operationModeGroup)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setHorizontalSpacing(15)
        self.gridLayout_7.setVerticalSpacing(5)
        self.gridLayout_7.setContentsMargins(10, 15, 15, 10)
        self.normalModeHem = QRadioButton(self.operationModeGroup)
        self.normalModeHem.setObjectName(u"normalModeHem")
        self.normalModeHem.setMinimumSize(QSize(0, 21))
        self.normalModeHem.setMaximumSize(QSize(16777215, 20))
        self.normalModeHem.setFont(font)
        self.normalModeHem.setChecked(True)

        self.gridLayout_7.addWidget(self.normalModeHem, 0, 0, 1, 1)

        self.editModeHem = QRadioButton(self.operationModeGroup)
        self.editModeHem.setObjectName(u"editModeHem")
        self.editModeHem.setMinimumSize(QSize(0, 21))
        self.editModeHem.setMaximumSize(QSize(16777215, 20))
        self.editModeHem.setFont(font)

        self.gridLayout_7.addWidget(self.editModeHem, 1, 0, 1, 1)

        self.alignmentModeHem = QRadioButton(self.operationModeGroup)
        self.alignmentModeHem.setObjectName(u"alignmentModeHem")
        self.alignmentModeHem.setEnabled(True)
        self.alignmentModeHem.setMinimumSize(QSize(0, 21))
        self.alignmentModeHem.setMaximumSize(QSize(16777215, 20))
        self.alignmentModeHem.setFont(font)

        self.gridLayout_7.addWidget(self.alignmentModeHem, 2, 0, 1, 1)


        self.horizontalLayout.addWidget(self.operationModeGroup)

        self.groupBox_3 = QGroupBox(HemisphereDialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setProperty(u"large", True)
        self.gridLayout = QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(15)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setContentsMargins(10, 15, 15, 10)
        self.showCelestial = QCheckBox(self.groupBox_3)
        self.showCelestial.setObjectName(u"showCelestial")
        self.showCelestial.setMinimumSize(QSize(0, 21))
        self.showCelestial.setMaximumSize(QSize(16777215, 20))
        self.showCelestial.setFont(font)

        self.gridLayout.addWidget(self.showCelestial, 0, 1, 1, 1)

        self.showMountLimits = QCheckBox(self.groupBox_3)
        self.showMountLimits.setObjectName(u"showMountLimits")
        self.showMountLimits.setMinimumSize(QSize(0, 21))
        self.showMountLimits.setMaximumSize(QSize(16777215, 20))
        self.showMountLimits.setFont(font)

        self.gridLayout.addWidget(self.showMountLimits, 0, 2, 1, 1)

        self.showAlignStar = QCheckBox(self.groupBox_3)
        self.showAlignStar.setObjectName(u"showAlignStar")
        self.showAlignStar.setMinimumSize(QSize(0, 21))
        self.showAlignStar.setMaximumSize(QSize(16777215, 20))
        self.showAlignStar.setFont(font)

        self.gridLayout.addWidget(self.showAlignStar, 0, 0, 1, 1)

        self.showPolar = QCheckBox(self.groupBox_3)
        self.showPolar.setObjectName(u"showPolar")
        self.showPolar.setEnabled(True)
        self.showPolar.setMinimumSize(QSize(0, 21))
        self.showPolar.setMaximumSize(QSize(16777215, 20))

        self.gridLayout.addWidget(self.showPolar, 1, 2, 1, 1)

        self.showSlewPath = QCheckBox(self.groupBox_3)
        self.showSlewPath.setObjectName(u"showSlewPath")
        self.showSlewPath.setMinimumSize(QSize(0, 21))
        self.showSlewPath.setMaximumSize(QSize(16777215, 20))
        self.showSlewPath.setFont(font)

        self.gridLayout.addWidget(self.showSlewPath, 1, 1, 1, 1)

        self.showTerrain = QCheckBox(self.groupBox_3)
        self.showTerrain.setObjectName(u"showTerrain")
        self.showTerrain.setMinimumSize(QSize(0, 21))
        self.showTerrain.setMaximumSize(QSize(16777215, 20))
        self.showTerrain.setFont(font)

        self.gridLayout.addWidget(self.showTerrain, 0, 3, 1, 1)

        self.showHorizon = QCheckBox(self.groupBox_3)
        self.showHorizon.setObjectName(u"showHorizon")
        self.showHorizon.setMinimumSize(QSize(0, 21))
        self.showHorizon.setMaximumSize(QSize(16777215, 20))
        self.showHorizon.setFont(font)
        self.showHorizon.setChecked(True)

        self.gridLayout.addWidget(self.showHorizon, 1, 0, 1, 1)

        self.showIsoModel = QCheckBox(self.groupBox_3)
        self.showIsoModel.setObjectName(u"showIsoModel")
        self.showIsoModel.setMinimumSize(QSize(0, 21))
        self.showIsoModel.setMaximumSize(QSize(16777215, 20))
        self.showIsoModel.setFont(font)

        self.gridLayout.addWidget(self.showIsoModel, 1, 3, 1, 1)


        self.horizontalLayout.addWidget(self.groupBox_3)

        self.operationMode = QGroupBox(HemisphereDialog)
        self.operationMode.setObjectName(u"operationMode")
        self.operationMode.setProperty(u"large", True)
        self.gridLayout_2 = QGridLayout(self.operationMode)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(15)
        self.gridLayout_2.setVerticalSpacing(8)
        self.gridLayout_2.setContentsMargins(10, 15, 15, 10)
        self.label = QLabel(self.operationMode)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setMinimumSize(QSize(50, 21))
        self.label.setMaximumSize(QSize(16777215, 16777215))
        self.label.setFont(font)

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.azimuth = QLineEdit(self.operationMode)
        self.azimuth.setObjectName(u"azimuth")
        self.azimuth.setEnabled(True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.azimuth.sizePolicy().hasHeightForWidth())
        self.azimuth.setSizePolicy(sizePolicy2)
        self.azimuth.setMinimumSize(QSize(0, 21))
        self.azimuth.setMaximumSize(QSize(50, 20))
        self.azimuth.setFrame(False)
        self.azimuth.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.azimuth, 3, 1, 1, 1)

        self.altitude = QLineEdit(self.operationMode)
        self.altitude.setObjectName(u"altitude")
        self.altitude.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.altitude.sizePolicy().hasHeightForWidth())
        self.altitude.setSizePolicy(sizePolicy2)
        self.altitude.setMinimumSize(QSize(0, 21))
        self.altitude.setMaximumSize(QSize(50, 20))
        self.altitude.setFrame(False)
        self.altitude.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.altitude, 0, 1, 1, 1)

        self.label_2 = QLabel(self.operationMode)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setMinimumSize(QSize(50, 21))
        self.label_2.setMaximumSize(QSize(16777215, 16777215))
        self.label_2.setFont(font)

        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)


        self.horizontalLayout.addWidget(self.operationMode)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.horizontalLayout.setStretch(3, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.tabWidget = QTabWidget(HemisphereDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setElideMode(Qt.TextElideMode.ElideNone)
        self.tabWidget.setMovable(False)
        self.HemisphereTab = QWidget()
        self.HemisphereTab.setObjectName(u"HemisphereTab")
        self.gridLayout_4 = QGridLayout(self.HemisphereTab)
        self.gridLayout_4.setSpacing(4)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(8, 12, 8, 8)
        self.hemisphere = Hemisphere(self.HemisphereTab)
        self.hemisphere.setObjectName(u"hemisphere")

        self.gridLayout_4.addWidget(self.hemisphere, 0, 0, 2, 1)

        self.tabWidget.addTab(self.HemisphereTab, "")
        self.HorizonTab = QWidget()
        self.HorizonTab.setObjectName(u"HorizonTab")
        self.gridLayout_5 = QGridLayout(self.HorizonTab)
        self.gridLayout_5.setSpacing(4)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(8, 12, 8, 8)
        self.terrainImageGroup = QGroupBox(self.HorizonTab)
        self.terrainImageGroup.setObjectName(u"terrainImageGroup")
        self.terrainImageGroup.setMinimumSize(QSize(120, 0))
        self.terrainImageGroup.setMaximumSize(QSize(120, 16777215))
        self.terrainImageGroup.setProperty(u"large", True)
        self.gridLayout_6 = QGridLayout(self.terrainImageGroup)
        self.gridLayout_6.setSpacing(5)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(5, 15, 5, 5)
        self.terrainAlpha = QDoubleSpinBox(self.terrainImageGroup)
        self.terrainAlpha.setObjectName(u"terrainAlpha")
        self.terrainAlpha.setMinimumSize(QSize(0, 21))
        self.terrainAlpha.setMaximumSize(QSize(16777215, 20))
        self.terrainAlpha.setDecimals(1)
        self.terrainAlpha.setMaximum(1.000000000000000)
        self.terrainAlpha.setSingleStep(0.100000000000000)
        self.terrainAlpha.setValue(0.300000000000000)

        self.gridLayout_6.addWidget(self.terrainAlpha, 5, 1, 1, 1)

        self.label_4 = QLabel(self.terrainImageGroup)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(0, 21))

        self.gridLayout_6.addWidget(self.label_4, 5, 0, 1, 1)

        self.label_6 = QLabel(self.terrainImageGroup)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(0, 21))

        self.gridLayout_6.addWidget(self.label_6, 4, 0, 1, 1)

        self.terrainFileName = QLineEdit(self.terrainImageGroup)
        self.terrainFileName.setObjectName(u"terrainFileName")
        self.terrainFileName.setMinimumSize(QSize(0, 21))
        self.terrainFileName.setFrame(False)

        self.gridLayout_6.addWidget(self.terrainFileName, 2, 0, 1, 2)

        self.label_3 = QLabel(self.terrainImageGroup)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(60, 21))

        self.gridLayout_6.addWidget(self.label_3, 3, 0, 1, 1)

        self.azimuthShift = QDoubleSpinBox(self.terrainImageGroup)
        self.azimuthShift.setObjectName(u"azimuthShift")
        self.azimuthShift.setMinimumSize(QSize(50, 21))
        self.azimuthShift.setMaximumSize(QSize(16777215, 20))
        self.azimuthShift.setDecimals(0)
        self.azimuthShift.setMinimum(-180.000000000000000)
        self.azimuthShift.setMaximum(180.000000000000000)
        self.azimuthShift.setSingleStep(5.000000000000000)

        self.gridLayout_6.addWidget(self.azimuthShift, 3, 1, 1, 1)

        self.altitudeShift = QDoubleSpinBox(self.terrainImageGroup)
        self.altitudeShift.setObjectName(u"altitudeShift")
        self.altitudeShift.setMinimumSize(QSize(0, 21))
        self.altitudeShift.setMaximumSize(QSize(16777215, 20))
        self.altitudeShift.setDecimals(0)
        self.altitudeShift.setMinimum(-30.000000000000000)
        self.altitudeShift.setMaximum(30.000000000000000)

        self.gridLayout_6.addWidget(self.altitudeShift, 4, 1, 1, 1)

        self.loadTerrainFile = QPushButton(self.terrainImageGroup)
        self.loadTerrainFile.setObjectName(u"loadTerrainFile")
        self.loadTerrainFile.setMinimumSize(QSize(0, 21))

        self.gridLayout_6.addWidget(self.loadTerrainFile, 0, 0, 1, 2)

        self.clearTerrainFile = QPushButton(self.terrainImageGroup)
        self.clearTerrainFile.setObjectName(u"clearTerrainFile")
        self.clearTerrainFile.setMinimumSize(QSize(0, 21))

        self.gridLayout_6.addWidget(self.clearTerrainFile, 1, 0, 1, 2)


        self.gridLayout_5.addWidget(self.terrainImageGroup, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.groupBox_4 = QGroupBox(self.HorizonTab)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setMinimumSize(QSize(120, 0))
        self.groupBox_4.setMaximumSize(QSize(120, 16777215))
        self.groupBox_4.setProperty(u"large", True)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 15, 5, 5)
        self.normalModeHor = QRadioButton(self.groupBox_4)
        self.normalModeHor.setObjectName(u"normalModeHor")
        self.normalModeHor.setMinimumSize(QSize(0, 21))
        self.normalModeHor.setMaximumSize(QSize(16777215, 20))
        self.normalModeHor.setFont(font)
        self.normalModeHor.setChecked(True)

        self.verticalLayout_2.addWidget(self.normalModeHor)

        self.editModeHor = QRadioButton(self.groupBox_4)
        self.editModeHor.setObjectName(u"editModeHor")
        self.editModeHor.setMinimumSize(QSize(0, 21))
        self.editModeHor.setMaximumSize(QSize(16777215, 20))
        self.editModeHor.setFont(font)

        self.verticalLayout_2.addWidget(self.editModeHor)

        self.addPositionToHorizon = QPushButton(self.groupBox_4)
        self.addPositionToHorizon.setObjectName(u"addPositionToHorizon")
        self.addPositionToHorizon.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.addPositionToHorizon.sizePolicy().hasHeightForWidth())
        self.addPositionToHorizon.setSizePolicy(sizePolicy2)
        self.addPositionToHorizon.setMinimumSize(QSize(0, 21))
        self.addPositionToHorizon.setMaximumSize(QSize(16777215, 20))

        self.verticalLayout_2.addWidget(self.addPositionToHorizon)


        self.gridLayout_5.addWidget(self.groupBox_4, 0, 0, 1, 1)

        self.horizonFileGroup = QGroupBox(self.HorizonTab)
        self.horizonFileGroup.setObjectName(u"horizonFileGroup")
        self.horizonFileGroup.setMinimumSize(QSize(120, 0))
        self.horizonFileGroup.setMaximumSize(QSize(120, 16777215))
        self.horizonFileGroup.setProperty(u"large", True)
        self.verticalLayout_3 = QVBoxLayout(self.horizonFileGroup)
        self.verticalLayout_3.setSpacing(5)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(5, 15, 5, 5)
        self.loadHorizonMask = QPushButton(self.horizonFileGroup)
        self.loadHorizonMask.setObjectName(u"loadHorizonMask")
        self.loadHorizonMask.setMinimumSize(QSize(0, 21))

        self.verticalLayout_3.addWidget(self.loadHorizonMask)

        self.saveHorizonMask = QPushButton(self.horizonFileGroup)
        self.saveHorizonMask.setObjectName(u"saveHorizonMask")
        self.saveHorizonMask.setMinimumSize(QSize(0, 21))

        self.verticalLayout_3.addWidget(self.saveHorizonMask)

        self.saveHorizonMaskAs = QPushButton(self.horizonFileGroup)
        self.saveHorizonMaskAs.setObjectName(u"saveHorizonMaskAs")
        self.saveHorizonMaskAs.setMinimumSize(QSize(0, 21))

        self.verticalLayout_3.addWidget(self.saveHorizonMaskAs)

        self.clearHorizonMask = QPushButton(self.horizonFileGroup)
        self.clearHorizonMask.setObjectName(u"clearHorizonMask")
        self.clearHorizonMask.setMinimumSize(QSize(0, 21))

        self.verticalLayout_3.addWidget(self.clearHorizonMask)

        self.horizonMaskFileName = QLineEdit(self.horizonFileGroup)
        self.horizonMaskFileName.setObjectName(u"horizonMaskFileName")
        self.horizonMaskFileName.setMinimumSize(QSize(0, 21))
        self.horizonMaskFileName.setFrame(False)

        self.verticalLayout_3.addWidget(self.horizonMaskFileName)


        self.gridLayout_5.addWidget(self.horizonFileGroup, 1, 0, 1, 1)

        self.horizon = PlotBase(self.HorizonTab)
        self.horizon.setObjectName(u"horizon")

        self.gridLayout_5.addWidget(self.horizon, 0, 1, 4, 1)

        self.tabWidget.addTab(self.HorizonTab, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(HemisphereDialog)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(HemisphereDialog)
    # setupUi

    def retranslateUi(self, HemisphereDialog):
        HemisphereDialog.setWindowTitle(QCoreApplication.translate("HemisphereDialog", u"Hemisphere", None))
        self.operationModeGroup.setTitle(QCoreApplication.translate("HemisphereDialog", u"Operation Mode", None))
#if QT_CONFIG(tooltip)
        self.normalModeHem.setToolTip(QCoreApplication.translate("HemisphereDialog", u"Switching the hemisphere window to normal working mode.", None))
#endif // QT_CONFIG(tooltip)
        self.normalModeHem.setText(QCoreApplication.translate("HemisphereDialog", u"Normal", None))
#if QT_CONFIG(tooltip)
        self.editModeHem.setToolTip(QCoreApplication.translate("HemisphereDialog", u"Enabling the edit mode for model build points.", None))
#endif // QT_CONFIG(tooltip)
        self.editModeHem.setText(QCoreApplication.translate("HemisphereDialog", u"Edit Model", None))
#if QT_CONFIG(tooltip)
        self.alignmentModeHem.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Enabling the polar or ortho align procedure. For starting the procedure, enable align stars and choose a polar align star with mouse double click and chose the type of alignment.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.alignmentModeHem.setText(QCoreApplication.translate("HemisphereDialog", u"Polar / Otho Align", None))
#if QT_CONFIG(tooltip)
        self.groupBox_3.setToolTip(QCoreApplication.translate("HemisphereDialog", u"Showing different elements on the hemisphere diagram.", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_3.setTitle(QCoreApplication.translate("HemisphereDialog", u"Show Elements", None))
#if QT_CONFIG(tooltip)
        self.showCelestial.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Show the celestial circles in the view</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showCelestial.setText(QCoreApplication.translate("HemisphereDialog", u"Celestial paths ", None))
#if QT_CONFIG(tooltip)
        self.showMountLimits.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Show the mount limits</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showMountLimits.setText(QCoreApplication.translate("HemisphereDialog", u"Mount limits ", None))
#if QT_CONFIG(tooltip)
        self.showAlignStar.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Show the align stars in horizin view</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showAlignStar.setText(QCoreApplication.translate("HemisphereDialog", u"Align stars ", None))
#if QT_CONFIG(tooltip)
        self.showPolar.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Show an additional polar diagram on right side in hemisphere view</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showPolar.setText(QCoreApplication.translate("HemisphereDialog", u"Show Polar", None))
#if QT_CONFIG(tooltip)
        self.showSlewPath.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Show the slew path of the mount</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showSlewPath.setText(QCoreApplication.translate("HemisphereDialog", u"Slew path ", None))
#if QT_CONFIG(tooltip)
        self.showTerrain.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Show the terrain image in background</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showTerrain.setText(QCoreApplication.translate("HemisphereDialog", u"Terrain", None))
#if QT_CONFIG(tooltip)
        self.showHorizon.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Use horizon mask in hemisphere window.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showHorizon.setText(QCoreApplication.translate("HemisphereDialog", u"Horizon mask ", None))
#if QT_CONFIG(tooltip)
        self.showIsoModel.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Showing the actual used mount model as reference.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showIsoModel.setText(QCoreApplication.translate("HemisphereDialog", u"Model Error", None))
        self.operationMode.setTitle(QCoreApplication.translate("HemisphereDialog", u"Coordinates", None))
        self.label.setText(QCoreApplication.translate("HemisphereDialog", u"Altitude:", None))
        self.label_2.setText(QCoreApplication.translate("HemisphereDialog", u"Azimuth:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.HemisphereTab), QCoreApplication.translate("HemisphereDialog", u"Hemisphere for Modelling", None))
#if QT_CONFIG(tooltip)
        self.terrainImageGroup.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Adjusting the terrain image to view</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.terrainImageGroup.setTitle(QCoreApplication.translate("HemisphereDialog", u"Terrain Image", None))
        self.label_4.setText(QCoreApplication.translate("HemisphereDialog", u"Alpha", None))
        self.label_6.setText(QCoreApplication.translate("HemisphereDialog", u"Altitude", None))
        self.label_3.setText(QCoreApplication.translate("HemisphereDialog", u"Azimuth", None))
        self.loadTerrainFile.setText(QCoreApplication.translate("HemisphereDialog", u"Load", None))
        self.clearTerrainFile.setText(QCoreApplication.translate("HemisphereDialog", u"Clear ", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("HemisphereDialog", u"Horizon Positions", None))
#if QT_CONFIG(tooltip)
        self.normalModeHor.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Switching the horizon view to normal working mode.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.normalModeHor.setText(QCoreApplication.translate("HemisphereDialog", u"Normal", None))
#if QT_CONFIG(tooltip)
        self.editModeHor.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Enabling the edit mode for horizon mask.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.editModeHor.setText(QCoreApplication.translate("HemisphereDialog", u"Edit Horizon", None))
#if QT_CONFIG(tooltip)
        self.addPositionToHorizon.setToolTip(QCoreApplication.translate("HemisphereDialog", u"<html><head/><body><p>Add actual telescope position (Alt/Az) as point to the horizon.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.addPositionToHorizon.setText(QCoreApplication.translate("HemisphereDialog", u"Add actual pos", None))
        self.horizonFileGroup.setTitle(QCoreApplication.translate("HemisphereDialog", u"Mask File", None))
        self.loadHorizonMask.setText(QCoreApplication.translate("HemisphereDialog", u"Load", None))
        self.saveHorizonMask.setText(QCoreApplication.translate("HemisphereDialog", u"Save", None))
        self.saveHorizonMaskAs.setText(QCoreApplication.translate("HemisphereDialog", u"Save as", None))
        self.clearHorizonMask.setText(QCoreApplication.translate("HemisphereDialog", u"Clear ", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.HorizonTab), QCoreApplication.translate("HemisphereDialog", u"Define Horizon Mask and Terrain Image", None))
    # retranslateUi

