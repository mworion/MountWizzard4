# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'simulator.ui'
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
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_SimulatorDialog(object):
    def setupUi(self, SimulatorDialog):
        if not SimulatorDialog.objectName():
            SimulatorDialog.setObjectName(u"SimulatorDialog")
        SimulatorDialog.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SimulatorDialog.sizePolicy().hasHeightForWidth())
        SimulatorDialog.setSizePolicy(sizePolicy)
        SimulatorDialog.setMinimumSize(QSize(800, 600))
        SimulatorDialog.setMaximumSize(QSize(1600, 1230))
        SimulatorDialog.setSizeIncrement(QSize(10, 10))
        SimulatorDialog.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        SimulatorDialog.setFont(font)
        self.horizontalLayout = QHBoxLayout(SimulatorDialog)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout.setContentsMargins(0, -1, -1, -1)
        self.groupBox_2 = QGroupBox(SimulatorDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setProperty(u"large", True)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(8, 10, 16, 4)
        self.domeTransparent = QCheckBox(self.groupBox_2)
        self.domeTransparent.setObjectName(u"domeTransparent")
        sizePolicy.setHeightForWidth(self.domeTransparent.sizePolicy().hasHeightForWidth())
        self.domeTransparent.setSizePolicy(sizePolicy)
        self.domeTransparent.setMinimumSize(QSize(0, 25))
        self.domeTransparent.setFont(font)

        self.verticalLayout_2.addWidget(self.domeTransparent)

        self.showPointer = QCheckBox(self.groupBox_2)
        self.showPointer.setObjectName(u"showPointer")
        self.showPointer.setMinimumSize(QSize(0, 25))
        self.showPointer.setFont(font)

        self.verticalLayout_2.addWidget(self.showPointer)

        self.showLaser = QCheckBox(self.groupBox_2)
        self.showLaser.setObjectName(u"showLaser")
        self.showLaser.setMinimumSize(QSize(0, 25))

        self.verticalLayout_2.addWidget(self.showLaser)

        self.showBuildPoints = QCheckBox(self.groupBox_2)
        self.showBuildPoints.setObjectName(u"showBuildPoints")
        self.showBuildPoints.setMinimumSize(QSize(0, 25))
        self.showBuildPoints.setFont(font)

        self.verticalLayout_2.addWidget(self.showBuildPoints)

        self.showNumbers = QCheckBox(self.groupBox_2)
        self.showNumbers.setObjectName(u"showNumbers")
        self.showNumbers.setMinimumSize(QSize(0, 25))
        self.showNumbers.setFont(font)

        self.verticalLayout_2.addWidget(self.showNumbers)

        self.showSlewPath = QCheckBox(self.groupBox_2)
        self.showSlewPath.setObjectName(u"showSlewPath")
        self.showSlewPath.setMinimumSize(QSize(0, 25))
        self.showSlewPath.setFont(font)

        self.verticalLayout_2.addWidget(self.showSlewPath)

        self.showHorizon = QCheckBox(self.groupBox_2)
        self.showHorizon.setObjectName(u"showHorizon")
        self.showHorizon.setMinimumSize(QSize(0, 25))
        self.showHorizon.setFont(font)

        self.verticalLayout_2.addWidget(self.showHorizon)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.groupBox = QGroupBox(SimulatorDialog)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy1)
        self.groupBox.setMaximumSize(QSize(150, 16777215))
        self.groupBox.setProperty(u"large", True)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(8, 10, 16, 4)
        self.topView = QPushButton(self.groupBox)
        self.topView.setObjectName(u"topView")
        self.topView.setMinimumSize(QSize(0, 25))

        self.verticalLayout.addWidget(self.topView)

        self.topWestView = QPushButton(self.groupBox)
        self.topWestView.setObjectName(u"topWestView")
        self.topWestView.setMinimumSize(QSize(0, 25))

        self.verticalLayout.addWidget(self.topWestView)

        self.westView = QPushButton(self.groupBox)
        self.westView.setObjectName(u"westView")
        self.westView.setMinimumSize(QSize(0, 25))

        self.verticalLayout.addWidget(self.westView)

        self.topEastView = QPushButton(self.groupBox)
        self.topEastView.setObjectName(u"topEastView")
        self.topEastView.setMinimumSize(QSize(0, 25))

        self.verticalLayout.addWidget(self.topEastView)

        self.eastView = QPushButton(self.groupBox)
        self.eastView.setObjectName(u"eastView")
        self.eastView.setMinimumSize(QSize(0, 25))

        self.verticalLayout.addWidget(self.eastView)

        self.telescopeView = QPushButton(self.groupBox)
        self.telescopeView.setObjectName(u"telescopeView")
        self.telescopeView.setMinimumSize(QSize(0, 25))

        self.verticalLayout.addWidget(self.telescopeView)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(45, 16777215))

        self.horizontalLayout_2.addWidget(self.label)

        self.lightIntensity = QDoubleSpinBox(self.groupBox)
        self.lightIntensity.setObjectName(u"lightIntensity")
        self.lightIntensity.setDecimals(1)
        self.lightIntensity.setMinimum(0.000000000000000)
        self.lightIntensity.setMaximum(1.000000000000000)
        self.lightIntensity.setSingleStep(0.050000000000000)
        self.lightIntensity.setValue(1.000000000000000)

        self.horizontalLayout_2.addWidget(self.lightIntensity)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.simulator = QHBoxLayout()
        self.simulator.setSpacing(0)
        self.simulator.setObjectName(u"simulator")
        self.simulator.setSizeConstraint(QLayout.SetMinimumSize)

        self.gridLayout.addLayout(self.simulator, 0, 1, 2, 1)


        self.horizontalLayout.addLayout(self.gridLayout)


        self.retranslateUi(SimulatorDialog)

        QMetaObject.connectSlotsByName(SimulatorDialog)
    # setupUi

    def retranslateUi(self, SimulatorDialog):
        SimulatorDialog.setWindowTitle(QCoreApplication.translate("SimulatorDialog", u"Mount Simulation View", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SimulatorDialog", u"Show Settings", None))
#if QT_CONFIG(tooltip)
        self.domeTransparent.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>Show dome transparent.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.domeTransparent.setText(QCoreApplication.translate("SimulatorDialog", u"Dome transp.", None))
#if QT_CONFIG(tooltip)
        self.showPointer.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>Show intersection point from line of sight and dome sphere.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showPointer.setText(QCoreApplication.translate("SimulatorDialog", u"Intersect Point", None))
#if QT_CONFIG(tooltip)
        self.showLaser.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>Show line of sight from telescope.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showLaser.setText(QCoreApplication.translate("SimulatorDialog", u"Laser", None))
#if QT_CONFIG(tooltip)
        self.showBuildPoints.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>Show build points on outer sphere.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showBuildPoints.setText(QCoreApplication.translate("SimulatorDialog", u"Build Points", None))
#if QT_CONFIG(tooltip)
        self.showNumbers.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>Show build point number close to build point.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showNumbers.setText(QCoreApplication.translate("SimulatorDialog", u"Numbers", None))
#if QT_CONFIG(tooltip)
        self.showSlewPath.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>Show slew path between build points.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showSlewPath.setText(QCoreApplication.translate("SimulatorDialog", u"Slew Path", None))
#if QT_CONFIG(tooltip)
        self.showHorizon.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>Show horizon in scene.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.showHorizon.setText(QCoreApplication.translate("SimulatorDialog", u"Horizon", None))
#if QT_CONFIG(tooltip)
        self.groupBox.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body>\n"
"<p>Left mouse button:<br> \n"
"While the left mouse button is pressed, mouse movement along x-axis moves the camera left and right and movement along y-axis moves it up and down.</p>\n"
"<p>Right mouse button:<br> \n"
"While the right mouse button is pressed, mouse movement along x-axis pans the camera around the camera view center and movement along y-axis tilts it around the camera view center.</p>\n"
"<p>Both left and right mouse button: <br>\n"
"While both the left and the right mouse button are pressed, mouse movement along y-axis zooms the camera in and out without changing the view center.</p>\n"
"<p>Mouse scroll wheel:<br> \n"
"Zooms the camera in and out without changing the view center.</p>\n"
"<p>Arrow keys:<br> \n"
"Move the camera vertically and horizontally relative to camera viewport.</p>\n"
"<p>Page up and page down keys: <br>\n"
"Move the camera forwards and backwards.</p>\n"
"<p>Shift key: <br>\n"
"Changes the behavior of the up and down arrow keys to zoom the camera i"
                        "n and out without changing the view center. The other movement keys are disabled.</p>\n"
"<p>Alt key: <br>\n"
"Changes the behovior of the arrow keys to pan and tilt the camera around the view center. Disables the page up and page down keys.</p>\n"
"<p>Escape: <br>\n"
"Moves the camera so that entire scene is visible in the camera viewport.</p>\n"
"</html></head/></body>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox.setTitle(QCoreApplication.translate("SimulatorDialog", u"Select View", None))
#if QT_CONFIG(tooltip)
        self.topView.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>When pressed, show top view of scene.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.topView.setText(QCoreApplication.translate("SimulatorDialog", u"Top View", None))
#if QT_CONFIG(tooltip)
        self.topWestView.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>When pressed, show view from top west to telecope scene.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.topWestView.setText(QCoreApplication.translate("SimulatorDialog", u"Top West View", None))
#if QT_CONFIG(tooltip)
        self.westView.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>When pressed, show view from west to telecope scene.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.westView.setText(QCoreApplication.translate("SimulatorDialog", u"West View", None))
#if QT_CONFIG(tooltip)
        self.topEastView.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>When pressed, show view from top east to telecope scene.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.topEastView.setText(QCoreApplication.translate("SimulatorDialog", u"Top East View", None))
#if QT_CONFIG(tooltip)
        self.eastView.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>When pressed, show view from east to telecope scene.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.eastView.setText(QCoreApplication.translate("SimulatorDialog", u"East View", None))
#if QT_CONFIG(tooltip)
        self.telescopeView.setToolTip(QCoreApplication.translate("SimulatorDialog", u"<html><head/><body><p>When pressed, show view from telecope to sphere.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.telescopeView.setText(QCoreApplication.translate("SimulatorDialog", u"Telescope View", None))
        self.label.setText(QCoreApplication.translate("SimulatorDialog", u"Light", None))
    # retranslateUi

