# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'message.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MessageDialog(object):
    def setupUi(self, MessageDialog):
        MessageDialog.setObjectName("MessageDialog")
        MessageDialog.resize(800, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MessageDialog.sizePolicy().hasHeightForWidth())
        MessageDialog.setSizePolicy(sizePolicy)
        MessageDialog.setMinimumSize(QtCore.QSize(800, 200))
        MessageDialog.setMaximumSize(QtCore.QSize(800, 1200))
        MessageDialog.setSizeIncrement(QtCore.QSize(10, 10))
        MessageDialog.setBaseSize(QtCore.QSize(10, 10))
        font = QtGui.QFont()
        font.setFamily("Arial")
        MessageDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(MessageDialog)
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.clear = QtWidgets.QPushButton(MessageDialog)
        self.clear.setMinimumSize(QtCore.QSize(80, 25))
        self.clear.setMaximumSize(QtCore.QSize(100, 25))
        self.clear.setObjectName("clear")
        self.horizontalLayout.addWidget(self.clear)
        self.widget = QtWidgets.QWidget(MessageDialog)
        self.widget.setObjectName("widget")
        self.horizontalLayout.addWidget(self.widget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(MessageDialog)
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(2)
        self.line.setMidLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.message = QtWidgets.QTextBrowser(MessageDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.message.sizePolicy().hasHeightForWidth())
        self.message.setSizePolicy(sizePolicy)
        self.message.setMinimumSize(QtCore.QSize(790, 190))
        self.message.setMaximumSize(QtCore.QSize(790, 1190))
        self.message.setSizeIncrement(QtCore.QSize(10, 10))
        self.message.setBaseSize(QtCore.QSize(10, 10))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.message.setFont(font)
        self.message.setAcceptDrops(False)
        self.message.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.message.setFrameShadow(QtWidgets.QFrame.Plain)
        self.message.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.message.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Courier New\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Arial\'; font-weight:600;\"><br /></p></body></html>")
        self.message.setAcceptRichText(False)
        self.message.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.message.setPlaceholderText("")
        self.message.setSearchPaths([])
        self.message.setOpenLinks(False)
        self.message.setObjectName("message")
        self.verticalLayout.addWidget(self.message)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(MessageDialog)
        QtCore.QMetaObject.connectSlotsByName(MessageDialog)

    def retranslateUi(self, MessageDialog):
        _translate = QtCore.QCoreApplication.translate
        MessageDialog.setWindowTitle(_translate("MessageDialog", "Messages"))
        self.clear.setText(_translate("MessageDialog", "Clear window"))
        self.message.setToolTip(_translate("MessageDialog", "Error Messages from Tool"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MessageDialog = QtWidgets.QWidget()
    ui = Ui_MessageDialog()
    ui.setupUi(MessageDialog)
    MessageDialog.show()
    sys.exit(app.exec_())
