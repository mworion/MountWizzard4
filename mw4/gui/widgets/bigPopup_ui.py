# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './mw4/gui/widgets/bigPopup.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_BigPopup(object):
    def setupUi(self, BigPopup):
        BigPopup.setObjectName("BigPopup")
        BigPopup.resize(251, 107)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(BigPopup.sizePolicy().hasHeightForWidth())
        BigPopup.setSizePolicy(sizePolicy)
        BigPopup.setMinimumSize(QtCore.QSize(200, 100))
        BigPopup.setMaximumSize(QtCore.QSize(400, 285))
        BigPopup.setSizeIncrement(QtCore.QSize(10, 10))
        BigPopup.setBaseSize(QtCore.QSize(10, 10))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        BigPopup.setFont(font)
        self.gridLayout_2 = QtWidgets.QGridLayout(BigPopup)
        self.gridLayout_2.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_2.setHorizontalSpacing(0)
        self.gridLayout_2.setVerticalSpacing(5)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mountOn = QtWidgets.QPushButton(BigPopup)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mountOn.sizePolicy().hasHeightForWidth())
        self.mountOn.setSizePolicy(sizePolicy)
        self.mountOn.setObjectName("mountOn")
        self.horizontalLayout.addWidget(self.mountOn)
        self.mountOff = QtWidgets.QPushButton(BigPopup)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mountOff.sizePolicy().hasHeightForWidth())
        self.mountOff.setSizePolicy(sizePolicy)
        self.mountOff.setObjectName("mountOff")
        self.horizontalLayout.addWidget(self.mountOff)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.stop = QtWidgets.QPushButton(BigPopup)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stop.sizePolicy().hasHeightForWidth())
        self.stop.setSizePolicy(sizePolicy)
        self.stop.setObjectName("stop")
        self.gridLayout_2.addWidget(self.stop, 2, 0, 1, 1)

        self.retranslateUi(BigPopup)
        QtCore.QMetaObject.connectSlotsByName(BigPopup)

    def retranslateUi(self, BigPopup):
        _translate = QtCore.QCoreApplication.translate
        BigPopup.setWindowTitle(_translate("BigPopup", "Device Setup"))
        self.mountOn.setText(_translate("BigPopup", "Mount On"))
        self.mountOff.setText(_translate("BigPopup", "Mount Off"))
        self.stop.setText(_translate("BigPopup", "Mount Stop"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BigPopup = QtWidgets.QWidget()
    ui = Ui_BigPopup()
    ui.setupUi(BigPopup)
    BigPopup.show()
    sys.exit(app.exec_())