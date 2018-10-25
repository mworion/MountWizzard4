# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgVal.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_InputValue(object):
    def setupUi(self, InputValue):
        InputValue.setObjectName("InputValue")
        InputValue.setWindowModality(QtCore.Qt.NonModal)
        InputValue.setEnabled(True)
        InputValue.resize(250, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(InputValue.sizePolicy().hasHeightForWidth())
        InputValue.setSizePolicy(sizePolicy)
        InputValue.setMinimumSize(QtCore.QSize(250, 150))
        InputValue.setMaximumSize(QtCore.QSize(250, 150))
        InputValue.setSizeIncrement(QtCore.QSize(9, 0))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        InputValue.setFont(font)
        InputValue.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        InputValue.setFocusPolicy(QtCore.Qt.NoFocus)
        InputValue.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        InputValue.setToolTipDuration(6)
        InputValue.setAutoFillBackground(True)
        self.value = QtWidgets.QDoubleSpinBox(InputValue)
        self.value.setGeometry(QtCore.QRect(35, 55, 171, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.value.setFont(font)
        self.value.setObjectName("value")
        self.ok = QtWidgets.QPushButton(InputValue)
        self.ok.setGeometry(QtCore.QRect(30, 95, 81, 32))
        self.ok.setObjectName("ok")
        self.cancel = QtWidgets.QPushButton(InputValue)
        self.cancel.setGeometry(QtCore.QRect(130, 95, 81, 32))
        self.cancel.setObjectName("cancel")
        self.message = QtWidgets.QLabel(InputValue)
        self.message.setGeometry(QtCore.QRect(40, 20, 171, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.message.setFont(font)
        self.message.setObjectName("message")

        self.retranslateUi(InputValue)
        QtCore.QMetaObject.connectSlotsByName(InputValue)

    def retranslateUi(self, InputValue):
        _translate = QtCore.QCoreApplication.translate
        InputValue.setWindowTitle(_translate("InputValue", "MountWizzard4 (C) MW 2018"))
        self.ok.setText(_translate("InputValue", "OK"))
        self.cancel.setText(_translate("InputValue", "Cancel"))
        self.message.setText(_translate("InputValue", "message"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    InputValue = QtWidgets.QWidget()
    ui = Ui_InputValue()
    ui.setupUi(InputValue)
    InputValue.show()
    sys.exit(app.exec_())

