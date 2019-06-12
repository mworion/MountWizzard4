# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'satellite.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SatelliteDialog(object):
    def setupUi(self, SatelliteDialog):
        SatelliteDialog.setObjectName("SatelliteDialog")
        SatelliteDialog.resize(800, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SatelliteDialog.sizePolicy().hasHeightForWidth())
        SatelliteDialog.setSizePolicy(sizePolicy)
        SatelliteDialog.setMinimumSize(QtCore.QSize(800, 600))
        SatelliteDialog.setMaximumSize(QtCore.QSize(1600, 1200))
        SatelliteDialog.setSizeIncrement(QtCore.QSize(10, 10))
        SatelliteDialog.setBaseSize(QtCore.QSize(10, 10))
        font = QtGui.QFont()
        font.setFamily("Arial")
        SatelliteDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(SatelliteDialog)
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.clear = QtWidgets.QPushButton(SatelliteDialog)
        self.clear.setMinimumSize(QtCore.QSize(80, 25))
        self.clear.setMaximumSize(QtCore.QSize(100, 25))
        self.clear.setObjectName("clear")
        self.horizontalLayout.addWidget(self.clear)
        self.widget = QtWidgets.QWidget(SatelliteDialog)
        self.widget.setObjectName("widget")
        self.horizontalLayout.addWidget(self.widget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(SatelliteDialog)
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(2)
        self.line.setMidLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.satSphere = QtWidgets.QWidget(SatelliteDialog)
        self.satSphere.setObjectName("satSphere")
        self.horizontalLayout_3.addWidget(self.satSphere)
        self.line_3 = QtWidgets.QFrame(SatelliteDialog)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setMidLineWidth(1)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout_3.addWidget(self.line_3)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.satEarth = QtWidgets.QWidget(SatelliteDialog)
        self.satEarth.setObjectName("satEarth")
        self.verticalLayout_3.addWidget(self.satEarth)
        self.line_2 = QtWidgets.QFrame(SatelliteDialog)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setMidLineWidth(1)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_3.addWidget(self.line_2)
        self.satHorizon = QtWidgets.QWidget(SatelliteDialog)
        self.satHorizon.setObjectName("satHorizon")
        self.verticalLayout_3.addWidget(self.satHorizon)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(SatelliteDialog)
        QtCore.QMetaObject.connectSlotsByName(SatelliteDialog)

    def retranslateUi(self, SatelliteDialog):
        _translate = QtCore.QCoreApplication.translate
        SatelliteDialog.setWindowTitle(_translate("SatelliteDialog", "Satellite"))
        self.clear.setText(_translate("SatelliteDialog", "Clear window"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SatelliteDialog = QtWidgets.QWidget()
    ui = Ui_SatelliteDialog()
    ui.setupUi(SatelliteDialog)
    SatelliteDialog.show()
    sys.exit(app.exec_())
