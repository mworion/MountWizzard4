# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'image.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QFont,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gui.utilities.gImageBar import ImageBar


class Ui_ImageDialog(object):
    def setupUi(self, ImageDialog):
        if not ImageDialog.objectName():
            ImageDialog.setObjectName("ImageDialog")
        ImageDialog.resize(800, 600)
        ImageDialog.setMinimumSize(QSize(800, 600))
        ImageDialog.setMaximumSize(QSize(1600, 1230))
        ImageDialog.setSizeIncrement(QSize(10, 10))
        font = QFont()
        font.setFamilies(["Arial"])
        font.setPointSize(10)
        ImageDialog.setFont(font)
        self.verticalLayout_2 = QVBoxLayout(ImageDialog)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(10)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.groupImageActions = QGroupBox(ImageDialog)
        self.groupImageActions.setObjectName("groupImageActions")
        self.groupImageActions.setProperty("large", True)
        self.gridLayout_4 = QGridLayout(self.groupImageActions)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout_4.setHorizontalSpacing(10)
        self.gridLayout_4.setVerticalSpacing(5)
        self.gridLayout_4.setContentsMargins(5, 10, 5, 5)
        self.solve = QPushButton(self.groupImageActions)
        self.solve.setObjectName("solve")
        self.solve.setEnabled(False)
        self.solve.setMinimumSize(QSize(95, 21))

        self.gridLayout_4.addWidget(self.solve, 3, 0, 1, 1)

        self.exposeN = QPushButton(self.groupImageActions)
        self.exposeN.setObjectName("exposeN")
        self.exposeN.setEnabled(False)
        self.exposeN.setMinimumSize(QSize(95, 21))

        self.gridLayout_4.addWidget(self.exposeN, 1, 1, 1, 1)

        self.expose = QPushButton(self.groupImageActions)
        self.expose.setObjectName("expose")
        self.expose.setEnabled(False)
        self.expose.setMinimumSize(QSize(95, 21))

        self.gridLayout_4.addWidget(self.expose, 1, 0, 1, 1)

        self.load = QPushButton(self.groupImageActions)
        self.load.setObjectName("load")
        self.load.setMinimumSize(QSize(95, 21))

        self.gridLayout_4.addWidget(self.load, 0, 0, 1, 1)

        self.abortExpose = QPushButton(self.groupImageActions)
        self.abortExpose.setObjectName("abortExpose")
        self.abortExpose.setEnabled(False)
        self.abortExpose.setMinimumSize(QSize(95, 21))

        self.gridLayout_4.addWidget(self.abortExpose, 1, 2, 1, 1)

        self.abortSolve = QPushButton(self.groupImageActions)
        self.abortSolve.setObjectName("abortSolve")
        self.abortSolve.setEnabled(False)
        self.abortSolve.setMinimumSize(QSize(95, 21))

        self.gridLayout_4.addWidget(self.abortSolve, 3, 1, 1, 1)

        self.embedData = QCheckBox(self.groupImageActions)
        self.embedData.setObjectName("embedData")
        self.embedData.setMinimumSize(QSize(100, 21))

        self.gridLayout_4.addWidget(self.embedData, 3, 3, 1, 1)

        self.autoSolve = QCheckBox(self.groupImageActions)
        self.autoSolve.setObjectName("autoSolve")
        self.autoSolve.setMinimumSize(QSize(100, 21))

        self.gridLayout_4.addWidget(self.autoSolve, 3, 2, 1, 1)

        self.timeTagImage = QCheckBox(self.groupImageActions)
        self.timeTagImage.setObjectName("timeTagImage")
        self.timeTagImage.setMinimumSize(QSize(105, 0))

        self.gridLayout_4.addWidget(self.timeTagImage, 1, 3, 1, 1)

        self.slewCenter = QPushButton(self.groupImageActions)
        self.slewCenter.setObjectName("slewCenter")
        self.slewCenter.setEnabled(True)
        self.slewCenter.setMinimumSize(QSize(95, 21))

        self.gridLayout_4.addWidget(self.slewCenter, 0, 1, 1, 1)

        self.syncModelToImage = QPushButton(self.groupImageActions)
        self.syncModelToImage.setObjectName("syncModelToImage")
        self.syncModelToImage.setEnabled(True)
        self.syncModelToImage.setMinimumSize(QSize(95, 21))

        self.gridLayout_4.addWidget(self.syncModelToImage, 0, 2, 1, 2)

        self.horizontalLayout_5.addWidget(self.groupImageActions)

        self.groupBox = QGroupBox(ImageDialog)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setProperty("large", True)
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_3.setVerticalSpacing(5)
        self.gridLayout_3.setContentsMargins(5, 15, 15, 5)
        self.aspectLocked = QCheckBox(self.groupBox)
        self.aspectLocked.setObjectName("aspectLocked")
        self.aspectLocked.setMinimumSize(QSize(105, 0))

        self.gridLayout_3.addWidget(self.aspectLocked, 1, 0, 1, 1)

        self.showCrosshair = QCheckBox(self.groupBox)
        self.showCrosshair.setObjectName("showCrosshair")
        self.showCrosshair.setMinimumSize(QSize(105, 21))

        self.gridLayout_3.addWidget(self.showCrosshair, 2, 0, 1, 1)

        self.flipH = QCheckBox(self.groupBox)
        self.flipH.setObjectName("flipH")
        self.flipH.setMinimumSize(QSize(60, 0))

        self.gridLayout_3.addWidget(self.flipH, 1, 1, 1, 1)

        self.flipV = QCheckBox(self.groupBox)
        self.flipV.setObjectName("flipV")
        self.flipV.setMinimumSize(QSize(60, 0))

        self.gridLayout_3.addWidget(self.flipV, 2, 1, 1, 1)

        self.color = QComboBox(self.groupBox)
        self.color.addItem("")
        self.color.addItem("")
        self.color.addItem("")
        self.color.addItem("")
        self.color.addItem("")
        self.color.setObjectName("color")
        self.color.setMinimumSize(QSize(100, 21))

        self.gridLayout_3.addWidget(self.color, 0, 0, 1, 1)

        self.horizontalLayout_5.addWidget(self.groupBox)

        self.photometryGroup = QGroupBox(ImageDialog)
        self.photometryGroup.setObjectName("photometryGroup")
        self.photometryGroup.setCheckable(True)
        self.photometryGroup.setProperty("large", True)
        self.Imageview = QGridLayout(self.photometryGroup)
        self.Imageview.setObjectName("Imageview")
        self.Imageview.setHorizontalSpacing(10)
        self.Imageview.setVerticalSpacing(5)
        self.Imageview.setContentsMargins(10, 15, 15, 5)
        self.snTarget = QComboBox(self.photometryGroup)
        self.snTarget.addItem("")
        self.snTarget.addItem("")
        self.snTarget.addItem("")
        self.snTarget.addItem("")
        self.snTarget.addItem("")
        self.snTarget.setObjectName("snTarget")
        self.snTarget.setMinimumSize(QSize(120, 21))

        self.Imageview.addWidget(self.snTarget, 0, 1, 1, 2)

        self.isoLayer = QCheckBox(self.photometryGroup)
        self.isoLayer.setObjectName("isoLayer")
        self.isoLayer.setMinimumSize(QSize(100, 0))

        self.Imageview.addWidget(self.isoLayer, 1, 1, 1, 2)

        self.showValues = QCheckBox(self.photometryGroup)
        self.showValues.setObjectName("showValues")
        self.showValues.setMinimumSize(QSize(100, 0))

        self.Imageview.addWidget(self.showValues, 2, 1, 1, 2)

        self.horizontalLayout_5.addWidget(self.photometryGroup)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.horizontalLayout_5.setStretch(3, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_2.setContentsMargins(5, 0, 0, 0)
        self.tabImage = QTabWidget(ImageDialog)
        self.tabImage.setObjectName("tabImage")
        self.tabImage.setMinimumSize(QSize(140, 0))
        self.tabImage.setElideMode(Qt.TextElideMode.ElideNone)
        self.tabImage.setMovable(False)
        self.Image = QWidget()
        self.Image.setObjectName("Image")
        self.gridLayout_5 = QGridLayout(self.Image)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.image = ImageBar(self.Image)
        self.image.setObjectName("image")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy)
        self.image.setMinimumSize(QSize(0, 0))

        self.gridLayout_5.addWidget(self.image, 0, 0, 1, 1)

        self.tabImage.addTab(self.Image, "")
        self.HFR = QWidget()
        self.HFR.setObjectName("HFR")
        self.gridLayout_11 = QGridLayout(self.HFR)
        self.gridLayout_11.setSpacing(0)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.gridLayout_11.setContentsMargins(0, 0, 0, 10)
        self.hfr = ImageBar(self.HFR)
        self.hfr.setObjectName("hfr")

        self.gridLayout_11.addWidget(self.hfr, 0, 0, 1, 1)

        self.gridLayout_15 = QGridLayout()
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.gridLayout_15.setHorizontalSpacing(10)
        self.gridLayout_15.setVerticalSpacing(0)
        self.gridLayout_15.setContentsMargins(20, -1, -1, 0)
        self.hfrPercentile = QLineEdit(self.HFR)
        self.hfrPercentile.setObjectName("hfrPercentile")
        self.hfrPercentile.setMaximumSize(QSize(30, 16777215))

        self.gridLayout_15.addWidget(self.hfrPercentile, 0, 1, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout_15.addItem(self.horizontalSpacer_5, 0, 9, 1, 1)

        self.label_13 = QLabel(self.HFR)
        self.label_13.setObjectName("label_13")
        self.label_13.setMinimumSize(QSize(0, 0))

        self.gridLayout_15.addWidget(self.label_13, 1, 2, 1, 1)

        self.medianHFR = QLineEdit(self.HFR)
        self.medianHFR.setObjectName("medianHFR")
        self.medianHFR.setMaximumSize(QSize(60, 16777215))

        self.gridLayout_15.addWidget(self.medianHFR, 0, 3, 1, 1)

        self.label_17 = QLabel(self.HFR)
        self.label_17.setObjectName("label_17")
        self.label_17.setMinimumSize(QSize(0, 0))

        self.gridLayout_15.addWidget(self.label_17, 0, 0, 1, 1)

        self.numberStars = QLineEdit(self.HFR)
        self.numberStars.setObjectName("numberStars")
        self.numberStars.setMaximumSize(QSize(60, 16777215))

        self.gridLayout_15.addWidget(self.numberStars, 1, 3, 1, 1)

        self.label_19 = QLabel(self.HFR)
        self.label_19.setObjectName("label_19")
        self.label_19.setMinimumSize(QSize(0, 0))

        self.gridLayout_15.addWidget(self.label_19, 0, 2, 1, 1)

        self.gridLayout_11.addLayout(self.gridLayout_15, 1, 0, 1, 1)

        self.gridLayout_11.setRowStretch(0, 1)
        self.tabImage.addTab(self.HFR, "")
        self.TiltSquare = QWidget()
        self.TiltSquare.setObjectName("TiltSquare")
        self.gridLayout_9 = QGridLayout(self.TiltSquare)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.gridLayout_9.setHorizontalSpacing(10)
        self.gridLayout_9.setVerticalSpacing(0)
        self.gridLayout_9.setContentsMargins(0, 0, 0, 10)
        self.tiltSquare = ImageBar(self.TiltSquare)
        self.tiltSquare.setObjectName("tiltSquare")

        self.gridLayout_9.addWidget(self.tiltSquare, 0, 0, 1, 1)

        self.gridLayout_13 = QGridLayout()
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.gridLayout_13.setHorizontalSpacing(10)
        self.gridLayout_13.setVerticalSpacing(0)
        self.gridLayout_13.setContentsMargins(20, -1, -1, -1)
        self.label_18 = QLabel(self.TiltSquare)
        self.label_18.setObjectName("label_18")
        self.label_18.setMinimumSize(QSize(0, 0))

        self.gridLayout_13.addWidget(self.label_18, 1, 0, 1, 1)

        self.label_5 = QLabel(self.TiltSquare)
        self.label_5.setObjectName("label_5")

        self.gridLayout_13.addWidget(self.label_5, 1, 3, 1, 1)

        self.textSquareTiltOffAxis = QLineEdit(self.TiltSquare)
        self.textSquareTiltOffAxis.setObjectName("textSquareTiltOffAxis")
        self.textSquareTiltOffAxis.setMinimumSize(QSize(140, 0))

        self.gridLayout_13.addWidget(self.textSquareTiltOffAxis, 1, 1, 1, 1)

        self.textSquareTiltHFR = QLineEdit(self.TiltSquare)
        self.textSquareTiltHFR.setObjectName("textSquareTiltHFR")
        self.textSquareTiltHFR.setMinimumSize(QSize(140, 0))

        self.gridLayout_13.addWidget(self.textSquareTiltHFR, 0, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout_13.addItem(self.horizontalSpacer_2, 0, 7, 1, 1)

        self.label_16 = QLabel(self.TiltSquare)
        self.label_16.setObjectName("label_16")
        self.label_16.setMinimumSize(QSize(0, 0))

        self.gridLayout_13.addWidget(self.label_16, 0, 0, 1, 1)

        self.squareNumberStars = QLineEdit(self.TiltSquare)
        self.squareNumberStars.setObjectName("squareNumberStars")
        self.squareNumberStars.setMinimumSize(QSize(0, 0))
        self.squareNumberStars.setMaximumSize(QSize(60, 16777215))

        self.gridLayout_13.addWidget(self.squareNumberStars, 1, 4, 1, 1)

        self.label_23 = QLabel(self.TiltSquare)
        self.label_23.setObjectName("label_23")

        self.gridLayout_13.addWidget(self.label_23, 0, 3, 1, 1)

        self.squareMedianHFR = QLineEdit(self.TiltSquare)
        self.squareMedianHFR.setObjectName("squareMedianHFR")
        self.squareMedianHFR.setMaximumSize(QSize(60, 16777215))

        self.gridLayout_13.addWidget(self.squareMedianHFR, 0, 4, 1, 1)

        self.gridLayout_13.setColumnStretch(7, 1)

        self.gridLayout_9.addLayout(self.gridLayout_13, 1, 0, 1, 1)

        self.gridLayout_9.setRowStretch(0, 1)
        self.tabImage.addTab(self.TiltSquare, "")
        self.TiltTriangle = QWidget()
        self.TiltTriangle.setObjectName("TiltTriangle")
        self.gridLayout_17 = QGridLayout(self.TiltTriangle)
        self.gridLayout_17.setSpacing(0)
        self.gridLayout_17.setObjectName("gridLayout_17")
        self.gridLayout_17.setContentsMargins(0, 0, 0, 10)
        self.tiltTriangle = ImageBar(self.TiltTriangle)
        self.tiltTriangle.setObjectName("tiltTriangle")

        self.gridLayout_17.addWidget(self.tiltTriangle, 0, 0, 1, 1)

        self.gridLayout_18 = QGridLayout()
        self.gridLayout_18.setObjectName("gridLayout_18")
        self.gridLayout_18.setHorizontalSpacing(10)
        self.gridLayout_18.setVerticalSpacing(0)
        self.gridLayout_18.setContentsMargins(20, -1, -1, 0)
        self.label_14 = QLabel(self.TiltTriangle)
        self.label_14.setObjectName("label_14")

        self.gridLayout_18.addWidget(self.label_14, 1, 2, 1, 1)

        self.label_21 = QLabel(self.TiltTriangle)
        self.label_21.setObjectName("label_21")
        self.label_21.setMinimumSize(QSize(0, 0))

        self.gridLayout_18.addWidget(self.label_21, 0, 0, 1, 1)

        self.triangleNumberStars = QLineEdit(self.TiltTriangle)
        self.triangleNumberStars.setObjectName("triangleNumberStars")
        self.triangleNumberStars.setMinimumSize(QSize(0, 0))
        self.triangleNumberStars.setMaximumSize(QSize(60, 16777215))

        self.gridLayout_18.addWidget(self.triangleNumberStars, 1, 3, 1, 1)

        self.label_22 = QLabel(self.TiltTriangle)
        self.label_22.setObjectName("label_22")
        self.label_22.setMinimumSize(QSize(0, 0))

        self.gridLayout_18.addWidget(self.label_22, 1, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout_18.addItem(self.horizontalSpacer_3, 0, 6, 1, 1)

        self.offsetTiltAngle = QDoubleSpinBox(self.TiltTriangle)
        self.offsetTiltAngle.setObjectName("offsetTiltAngle")
        self.offsetTiltAngle.setMaximumSize(QSize(60, 16777215))
        self.offsetTiltAngle.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.offsetTiltAngle.setDecimals(0)
        self.offsetTiltAngle.setMaximum(120.000000000000000)
        self.offsetTiltAngle.setSingleStep(10.000000000000000)

        self.gridLayout_18.addWidget(self.offsetTiltAngle, 0, 5, 1, 1)

        self.label_20 = QLabel(self.TiltTriangle)
        self.label_20.setObjectName("label_20")
        self.label_20.setMinimumSize(QSize(0, 0))
        self.label_20.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_18.addWidget(self.label_20, 0, 4, 1, 1)

        self.label_24 = QLabel(self.TiltTriangle)
        self.label_24.setObjectName("label_24")

        self.gridLayout_18.addWidget(self.label_24, 0, 2, 1, 1)

        self.triangleMedianHFR = QLineEdit(self.TiltTriangle)
        self.triangleMedianHFR.setObjectName("triangleMedianHFR")
        self.triangleMedianHFR.setMaximumSize(QSize(60, 16777215))

        self.gridLayout_18.addWidget(self.triangleMedianHFR, 0, 3, 1, 1)

        self.textTriangleTiltOffAxis = QLineEdit(self.TiltTriangle)
        self.textTriangleTiltOffAxis.setObjectName("textTriangleTiltOffAxis")
        self.textTriangleTiltOffAxis.setMinimumSize(QSize(140, 0))

        self.gridLayout_18.addWidget(self.textTriangleTiltOffAxis, 1, 1, 1, 1)

        self.textTriangleTiltHFR = QLineEdit(self.TiltTriangle)
        self.textTriangleTiltHFR.setObjectName("textTriangleTiltHFR")
        self.textTriangleTiltHFR.setMinimumSize(QSize(140, 0))

        self.gridLayout_18.addWidget(self.textTriangleTiltHFR, 0, 1, 1, 1)

        self.gridLayout_18.setColumnStretch(6, 1)

        self.gridLayout_17.addLayout(self.gridLayout_18, 1, 0, 1, 1)

        self.gridLayout_17.setRowStretch(0, 1)
        self.tabImage.addTab(self.TiltTriangle, "")
        self.Roundness = QWidget()
        self.Roundness.setObjectName("Roundness")
        self.gridLayout_8 = QGridLayout(self.Roundness)
        self.gridLayout_8.setSpacing(0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.gridLayout_8.setContentsMargins(0, 0, 0, 10)
        self.roundness = ImageBar(self.Roundness)
        self.roundness.setObjectName("roundness")

        self.gridLayout_8.addWidget(self.roundness, 0, 0, 1, 1)

        self.gridLayout_16 = QGridLayout()
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.gridLayout_16.setHorizontalSpacing(10)
        self.gridLayout_16.setVerticalSpacing(0)
        self.gridLayout_16.setContentsMargins(20, -1, -1, 0)
        self.horizontalSpacer_12 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout_16.addItem(self.horizontalSpacer_12, 0, 2, 1, 1)

        self.aspectRatioPercentile = QLineEdit(self.Roundness)
        self.aspectRatioPercentile.setObjectName("aspectRatioPercentile")
        self.aspectRatioPercentile.setMaximumSize(QSize(30, 16777215))

        self.gridLayout_16.addWidget(self.aspectRatioPercentile, 0, 1, 1, 1)

        self.label_15 = QLabel(self.Roundness)
        self.label_15.setObjectName("label_15")

        self.gridLayout_16.addWidget(self.label_15, 0, 0, 1, 1)

        self.gridLayout_8.addLayout(self.gridLayout_16, 1, 0, 1, 1)

        self.gridLayout_8.setRowStretch(0, 1)
        self.tabImage.addTab(self.Roundness, "")
        self.Aberration = QWidget()
        self.Aberration.setObjectName("Aberration")
        self.gridLayout_12 = QGridLayout(self.Aberration)
        self.gridLayout_12.setSpacing(0)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.gridLayout_12.setContentsMargins(0, 0, 0, 0)
        self.aberration = ImageBar(self.Aberration)
        self.aberration.setObjectName("aberration")

        self.gridLayout_12.addWidget(self.aberration, 0, 0, 1, 1)

        self.tabImage.addTab(self.Aberration, "")
        self.Sources = QWidget()
        self.Sources.setObjectName("Sources")
        self.gridLayout_10 = QGridLayout(self.Sources)
        self.gridLayout_10.setSpacing(0)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.imageSource = ImageBar(self.Sources)
        self.imageSource.setObjectName("imageSource")

        self.gridLayout_10.addWidget(self.imageSource, 0, 0, 1, 1)

        self.tabImage.addTab(self.Sources, "")
        self.Back = QWidget()
        self.Back.setObjectName("Back")
        self.gridLayout_6 = QGridLayout(self.Back)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.background = ImageBar(self.Back)
        self.background.setObjectName("background")

        self.gridLayout_6.addWidget(self.background, 0, 0, 1, 1)

        self.tabImage.addTab(self.Back, "")
        self.BackRMS = QWidget()
        self.BackRMS.setObjectName("BackRMS")
        self.gridLayout_7 = QGridLayout(self.BackRMS)
        self.gridLayout_7.setSpacing(0)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.backgroundRMS = ImageBar(self.BackRMS)
        self.backgroundRMS.setObjectName("backgroundRMS")

        self.gridLayout_7.addWidget(self.backgroundRMS, 0, 0, 1, 1)

        self.tabImage.addTab(self.BackRMS, "")

        self.gridLayout_2.addWidget(self.tabImage, 1, 2, 3, 1)

        self.headerGroup = QGroupBox(ImageDialog)
        self.headerGroup.setObjectName("headerGroup")
        self.headerGroup.setMinimumSize(QSize(120, 0))
        self.headerGroup.setMaximumSize(QSize(0, 16777215))
        self.headerGroup.setProperty("large", True)
        self.gridLayout = QGridLayout(self.headerGroup)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setContentsMargins(4, 15, 4, 4)
        self.binX = QLineEdit(self.headerGroup)
        self.binX.setObjectName("binX")
        self.binX.setEnabled(True)
        self.binX.setReadOnly(True)

        self.gridLayout.addWidget(self.binX, 26, 0, 1, 1)

        self.line_7 = QFrame(self.headerGroup)
        self.line_7.setObjectName("line_7")
        self.line_7.setFrameShadow(QFrame.Shadow.Plain)
        self.line_7.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout.addWidget(self.line_7, 16, 0, 1, 2)

        self.line_11 = QFrame(self.headerGroup)
        self.line_11.setObjectName("line_11")
        self.line_11.setFrameShadow(QFrame.Shadow.Plain)
        self.line_11.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout.addWidget(self.line_11, 27, 0, 1, 2)

        self.scale = QLineEdit(self.headerGroup)
        self.scale.setObjectName("scale")
        self.scale.setEnabled(True)
        self.scale.setReadOnly(True)

        self.gridLayout.addWidget(self.scale, 15, 1, 1, 1)

        self.line_3 = QFrame(self.headerGroup)
        self.line_3.setObjectName("line_3")
        self.line_3.setFrameShadow(QFrame.Shadow.Plain)
        self.line_3.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout.addWidget(self.line_3, 2, 0, 1, 2)

        self.line_6 = QFrame(self.headerGroup)
        self.line_6.setObjectName("line_6")
        self.line_6.setFrameShadow(QFrame.Shadow.Plain)
        self.line_6.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout.addWidget(self.line_6, 10, 0, 1, 2)

        self.label_3 = QLabel(self.headerGroup)
        self.label_3.setObjectName("label_3")

        self.gridLayout.addWidget(self.label_3, 7, 0, 1, 2)

        self.sqm = QLineEdit(self.headerGroup)
        self.sqm.setObjectName("sqm")
        self.sqm.setEnabled(True)
        self.sqm.setReadOnly(True)

        self.gridLayout.addWidget(self.sqm, 32, 0, 1, 2)

        self.rotation = QLineEdit(self.headerGroup)
        self.rotation.setObjectName("rotation")
        self.rotation.setEnabled(True)
        self.rotation.setReadOnly(True)

        self.gridLayout.addWidget(self.rotation, 15, 0, 1, 1)

        self.label_6 = QLabel(self.headerGroup)
        self.label_6.setObjectName("label_6")

        self.gridLayout.addWidget(self.label_6, 13, 0, 1, 1)

        self.ccdTemp = QLineEdit(self.headerGroup)
        self.ccdTemp.setObjectName("ccdTemp")
        self.ccdTemp.setEnabled(True)
        self.ccdTemp.setReadOnly(True)

        self.gridLayout.addWidget(self.ccdTemp, 23, 1, 1, 1)

        self.dec = QLineEdit(self.headerGroup)
        self.dec.setObjectName("dec")
        self.dec.setEnabled(True)
        self.dec.setReadOnly(True)

        self.gridLayout.addWidget(self.dec, 8, 0, 1, 2)

        self.exposureTime = QLineEdit(self.headerGroup)
        self.exposureTime.setObjectName("exposureTime")
        self.exposureTime.setEnabled(True)
        self.exposureTime.setReadOnly(True)

        self.gridLayout.addWidget(self.exposureTime, 20, 0, 1, 2)

        self.label = QLabel(self.headerGroup)
        self.label.setObjectName("label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.object = QLineEdit(self.headerGroup)
        self.object.setObjectName("object")
        self.object.setEnabled(True)
        self.object.setReadOnly(True)

        self.gridLayout.addWidget(self.object, 1, 0, 1, 2)

        self.label_2 = QLabel(self.headerGroup)
        self.label_2.setObjectName("label_2")

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)

        self.binY = QLineEdit(self.headerGroup)
        self.binY.setObjectName("binY")
        self.binY.setEnabled(True)
        self.binY.setReadOnly(True)

        self.gridLayout.addWidget(self.binY, 26, 1, 1, 1)

        self.label_4 = QLabel(self.headerGroup)
        self.label_4.setObjectName("label_4")

        self.gridLayout.addWidget(self.label_4, 31, 0, 1, 2)

        self.raFloat = QLineEdit(self.headerGroup)
        self.raFloat.setObjectName("raFloat")
        self.raFloat.setEnabled(True)
        self.raFloat.setReadOnly(True)

        self.gridLayout.addWidget(self.raFloat, 5, 0, 1, 2)

        self.filter = QLineEdit(self.headerGroup)
        self.filter.setObjectName("filter")
        self.filter.setEnabled(True)
        self.filter.setReadOnly(True)

        self.gridLayout.addWidget(self.filter, 23, 0, 1, 1)

        self.label_8 = QLabel(self.headerGroup)
        self.label_8.setObjectName("label_8")

        self.gridLayout.addWidget(self.label_8, 19, 0, 1, 2)

        self.line_5 = QFrame(self.headerGroup)
        self.line_5.setObjectName("line_5")
        self.line_5.setFrameShadow(QFrame.Shadow.Plain)
        self.line_5.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout.addWidget(self.line_5, 6, 0, 1, 2)

        self.line_9 = QFrame(self.headerGroup)
        self.line_9.setObjectName("line_9")
        self.line_9.setFrameShadow(QFrame.Shadow.Plain)
        self.line_9.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout.addWidget(self.line_9, 21, 0, 1, 2)

        self.label_12 = QLabel(self.headerGroup)
        self.label_12.setObjectName("label_12")

        self.gridLayout.addWidget(self.label_12, 25, 1, 1, 1)

        self.label_7 = QLabel(self.headerGroup)
        self.label_7.setObjectName("label_7")

        self.gridLayout.addWidget(self.label_7, 13, 1, 1, 1)

        self.line_10 = QFrame(self.headerGroup)
        self.line_10.setObjectName("line_10")
        self.line_10.setFrameShadow(QFrame.Shadow.Plain)
        self.line_10.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout.addWidget(self.line_10, 24, 0, 1, 2)

        self.ra = QLineEdit(self.headerGroup)
        self.ra.setObjectName("ra")
        self.ra.setEnabled(True)
        self.ra.setReadOnly(True)

        self.gridLayout.addWidget(self.ra, 4, 0, 1, 2)

        self.label_11 = QLabel(self.headerGroup)
        self.label_11.setObjectName("label_11")

        self.gridLayout.addWidget(self.label_11, 25, 0, 1, 1)

        self.label_9 = QLabel(self.headerGroup)
        self.label_9.setObjectName("label_9")

        self.gridLayout.addWidget(self.label_9, 22, 1, 1, 1)

        self.label_10 = QLabel(self.headerGroup)
        self.label_10.setObjectName("label_10")

        self.gridLayout.addWidget(self.label_10, 22, 0, 1, 1)

        self.decFloat = QLineEdit(self.headerGroup)
        self.decFloat.setObjectName("decFloat")
        self.decFloat.setEnabled(True)
        self.decFloat.setReadOnly(True)

        self.gridLayout.addWidget(self.decFloat, 9, 0, 1, 2)

        self.gridLayout_2.addWidget(self.headerGroup, 1, 0, 2, 1)

        self.verticalLayout_2.addLayout(self.gridLayout_2)

        self.verticalLayout_2.setStretch(2, 1)

        self.retranslateUi(ImageDialog)

        self.tabImage.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(ImageDialog)

    # setupUi

    def retranslateUi(self, ImageDialog):
        ImageDialog.setWindowTitle(QCoreApplication.translate("ImageDialog", "Imaging", None))
        self.groupImageActions.setTitle(
            QCoreApplication.translate("ImageDialog", "Image actions", None)
        )
        self.solve.setText(QCoreApplication.translate("ImageDialog", "Solve", None))
        self.exposeN.setText(QCoreApplication.translate("ImageDialog", "Expose N", None))
        self.expose.setText(QCoreApplication.translate("ImageDialog", "Expose 1", None))
        self.load.setText(QCoreApplication.translate("ImageDialog", "Load", None))
        self.abortExpose.setText(QCoreApplication.translate("ImageDialog", "Exp. Abort", None))
        self.abortSolve.setText(QCoreApplication.translate("ImageDialog", "Solve Abort", None))
        self.embedData.setText(QCoreApplication.translate("ImageDialog", "Embed WCS", None))
        self.autoSolve.setText(QCoreApplication.translate("ImageDialog", "Auto Solve", None))
        # if QT_CONFIG(tooltip)
        self.timeTagImage.setToolTip(
            QCoreApplication.translate(
                "ImageDialog",
                "<html><head/><body><p>If checked, the filename of the image is extended with the actual time to make it unique. Otherwise the file get just &quot;exposure&quot; and will be overwritten.</p></body></html>",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.timeTagImage.setText(
            QCoreApplication.translate("ImageDialog", "Add time tags", None)
        )
        self.slewCenter.setText(QCoreApplication.translate("ImageDialog", "Slew Center", None))
        self.syncModelToImage.setText(
            QCoreApplication.translate("ImageDialog", "Sync model to image solution", None)
        )
        self.groupBox.setTitle(QCoreApplication.translate("ImageDialog", "Image View", None))
        self.aspectLocked.setText(
            QCoreApplication.translate("ImageDialog", "Lock aspect", None)
        )
        # if QT_CONFIG(tooltip)
        self.showCrosshair.setToolTip(
            QCoreApplication.translate(
                "ImageDialog",
                "<html><head/><body><p>Showing a red cross hair in the center of the image.</p></body></html>",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.showCrosshair.setText(
            QCoreApplication.translate("ImageDialog", "Crosshair  ", None)
        )
        self.flipH.setText(QCoreApplication.translate("ImageDialog", "Flip H", None))
        self.flipV.setText(QCoreApplication.translate("ImageDialog", "Flip V", None))
        self.color.setItemText(0, QCoreApplication.translate("ImageDialog", "Grey", None))
        self.color.setItemText(1, QCoreApplication.translate("ImageDialog", "Rainbow", None))
        self.color.setItemText(2, QCoreApplication.translate("ImageDialog", "Cividis", None))
        self.color.setItemText(3, QCoreApplication.translate("ImageDialog", "Magma", None))
        self.color.setItemText(4, QCoreApplication.translate("ImageDialog", "Extreme", None))

        self.photometryGroup.setTitle(
            QCoreApplication.translate("ImageDialog", "Photometry", None)
        )
        self.snTarget.setItemText(
            0, QCoreApplication.translate("ImageDialog", "Star norm", None)
        )
        self.snTarget.setItemText(
            1, QCoreApplication.translate("ImageDialog", "Star plus", None)
        )
        self.snTarget.setItemText(
            2, QCoreApplication.translate("ImageDialog", "Star extended", None)
        )
        self.snTarget.setItemText(
            3, QCoreApplication.translate("ImageDialog", "Star max", None)
        )
        self.snTarget.setItemText(
            4, QCoreApplication.translate("ImageDialog", "Star extreme", None)
        )

        self.isoLayer.setText(QCoreApplication.translate("ImageDialog", "2D contour", None))
        self.showValues.setText(QCoreApplication.translate("ImageDialog", "Show values", None))
        self.tabImage.setTabText(
            self.tabImage.indexOf(self.Image),
            QCoreApplication.translate("ImageDialog", "Image", None),
        )
        self.label_13.setText(
            QCoreApplication.translate("ImageDialog", "Number of stars", None)
        )
        self.label_17.setText(
            QCoreApplication.translate("ImageDialog", "10% Percentile [HFR]", None)
        )
        self.label_19.setText(QCoreApplication.translate("ImageDialog", "Median [HFR]", None))
        self.tabImage.setTabText(
            self.tabImage.indexOf(self.HFR),
            QCoreApplication.translate("ImageDialog", "HFR", None),
        )
        self.label_18.setText(
            QCoreApplication.translate("ImageDialog", "Off-Axis aberration [HFR]", None)
        )
        self.label_5.setText(QCoreApplication.translate("ImageDialog", "Number stars", None))
        self.label_16.setText(
            QCoreApplication.translate("ImageDialog", "Tilt square [HFR]", None)
        )
        self.label_23.setText(QCoreApplication.translate("ImageDialog", "Median HFR", None))
        self.tabImage.setTabText(
            self.tabImage.indexOf(self.TiltSquare),
            QCoreApplication.translate("ImageDialog", "Tilt Square", None),
        )
        self.label_14.setText(QCoreApplication.translate("ImageDialog", "Number stars", None))
        self.label_21.setText(
            QCoreApplication.translate("ImageDialog", "Tilt triangle [HFR]", None)
        )
        self.label_22.setText(
            QCoreApplication.translate("ImageDialog", "Off-Axis aberration [HFR]", None)
        )
        self.label_20.setText(
            QCoreApplication.translate("ImageDialog", "Offset tilt angle", None)
        )
        self.label_24.setText(QCoreApplication.translate("ImageDialog", "Median HFR", None))
        self.tabImage.setTabText(
            self.tabImage.indexOf(self.TiltTriangle),
            QCoreApplication.translate("ImageDialog", "Tilt Triangle", None),
        )
        self.label_15.setText(
            QCoreApplication.translate("ImageDialog", "10% Percentile [aspect ratio]", None)
        )
        self.tabImage.setTabText(
            self.tabImage.indexOf(self.Roundness),
            QCoreApplication.translate("ImageDialog", "Roundness", None),
        )
        self.tabImage.setTabText(
            self.tabImage.indexOf(self.Aberration),
            QCoreApplication.translate("ImageDialog", "Aberration Inspect", None),
        )
        self.tabImage.setTabText(
            self.tabImage.indexOf(self.Sources),
            QCoreApplication.translate("ImageDialog", "Image + Source", None),
        )
        self.tabImage.setTabText(
            self.tabImage.indexOf(self.Back),
            QCoreApplication.translate("ImageDialog", "Back", None),
        )
        self.tabImage.setTabText(
            self.tabImage.indexOf(self.BackRMS),
            QCoreApplication.translate("ImageDialog", "Back RMS", None),
        )
        self.headerGroup.setTitle(
            QCoreApplication.translate("ImageDialog", "Fits Header", None)
        )
        self.label_3.setText(QCoreApplication.translate("ImageDialog", "DEC [deg]", None))
        self.label_6.setText(QCoreApplication.translate("ImageDialog", "Rot [deg]", None))
        self.label.setText(QCoreApplication.translate("ImageDialog", "Object Name", None))
        self.label_2.setText(QCoreApplication.translate("ImageDialog", "RA [hours]", None))
        self.label_4.setText(QCoreApplication.translate("ImageDialog", "SQM [mpas]", None))
        self.label_8.setText(
            QCoreApplication.translate("ImageDialog", "Exposure Time [s]", None)
        )
        self.label_12.setText(QCoreApplication.translate("ImageDialog", "Bin Y", None))
        self.label_7.setText(QCoreApplication.translate("ImageDialog", "Scale", None))
        self.label_11.setText(QCoreApplication.translate("ImageDialog", "Bin X", None))
        self.label_9.setText(QCoreApplication.translate("ImageDialog", "Temp", None))
        self.label_10.setText(QCoreApplication.translate("ImageDialog", "Filter", None))

    # retranslateUi
