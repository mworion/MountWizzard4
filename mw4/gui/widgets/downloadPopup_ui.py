# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './mw4/gui/widgets/downloadPopup.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DownloadPopup(object):
    def setupUi(self, DownloadPopup):
        DownloadPopup.setObjectName("DownloadPopup")
        DownloadPopup.resize(400, 46)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DownloadPopup.sizePolicy().hasHeightForWidth())
        DownloadPopup.setSizePolicy(sizePolicy)
        DownloadPopup.setMinimumSize(QtCore.QSize(400, 0))
        DownloadPopup.setMaximumSize(QtCore.QSize(400, 80))
        DownloadPopup.setSizeIncrement(QtCore.QSize(10, 10))
        DownloadPopup.setBaseSize(QtCore.QSize(10, 10))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        DownloadPopup.setFont(font)
        self.progressBar = QtWidgets.QProgressBar(DownloadPopup)
        self.progressBar.setGeometry(QtCore.QRect(10, 10, 376, 26))
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")

        self.retranslateUi(DownloadPopup)
        QtCore.QMetaObject.connectSlotsByName(DownloadPopup)

    def retranslateUi(self, DownloadPopup):
        _translate = QtCore.QCoreApplication.translate
        DownloadPopup.setWindowTitle(_translate("DownloadPopup", "Device Setup"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DownloadPopup = QtWidgets.QWidget()
    ui = Ui_DownloadPopup()
    ui.setupUi(DownloadPopup)
    DownloadPopup.show()
    sys.exit(app.exec_())
