# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'video.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_VideoDialog(object):
    def setupUi(self, VideoDialog):
        if not VideoDialog.objectName():
            VideoDialog.setObjectName(u"VideoDialog")
        VideoDialog.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VideoDialog.sizePolicy().hasHeightForWidth())
        VideoDialog.setSizePolicy(sizePolicy)
        VideoDialog.setMinimumSize(QSize(400, 285))
        VideoDialog.setMaximumSize(QSize(800, 600))
        VideoDialog.setSizeIncrement(QSize(10, 10))
        VideoDialog.setBaseSize(QSize(10, 10))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        VideoDialog.setFont(font)
        self.verticalLayout = QVBoxLayout(VideoDialog)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(4, 4, 4, 4)
        self.videoSource = QComboBox(VideoDialog)
        self.videoSource.addItem("")
        self.videoSource.addItem("")
        self.videoSource.addItem("")
        self.videoSource.addItem("")
        self.videoSource.addItem("")
        self.videoSource.addItem("")
        self.videoSource.addItem("")
        self.videoSource.addItem("")
        self.videoSource.setObjectName(u"videoSource")
        self.videoSource.setMinimumSize(QSize(130, 21))
        self.videoSource.setMaximumSize(QSize(16777215, 25))

        self.gridLayout.addWidget(self.videoSource, 0, 4, 1, 1)

        self.frameRate = QComboBox(VideoDialog)
        self.frameRate.addItem("")
        self.frameRate.addItem("")
        self.frameRate.addItem("")
        self.frameRate.addItem("")
        self.frameRate.addItem("")
        self.frameRate.setObjectName(u"frameRate")
        self.frameRate.setMinimumSize(QSize(80, 0))

        self.gridLayout.addWidget(self.frameRate, 0, 5, 1, 1)

        self.videoStop = QPushButton(VideoDialog)
        self.videoStop.setObjectName(u"videoStop")
        self.videoStop.setMinimumSize(QSize(60, 21))
        self.videoStop.setMaximumSize(QSize(100, 25))
        self.videoStop.setProperty(u"running", False)

        self.gridLayout.addWidget(self.videoStop, 0, 3, 1, 1)

        self.videoURL = QLineEdit(VideoDialog)
        self.videoURL.setObjectName(u"videoURL")
        self.videoURL.setMinimumSize(QSize(250, 21))
        self.videoURL.setMaximumSize(QSize(16777215, 25))
        self.videoURL.setFrame(False)
        self.videoURL.setProperty(u"input", True)

        self.gridLayout.addWidget(self.videoURL, 1, 3, 1, 3)

        self.horizontalSpacer = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 6, 2, 2)

        self.videoStart = QPushButton(VideoDialog)
        self.videoStart.setObjectName(u"videoStart")
        self.videoStart.setMinimumSize(QSize(60, 21))
        self.videoStart.setMaximumSize(QSize(100, 25))

        self.gridLayout.addWidget(self.videoStart, 0, 1, 1, 2)

        self.authPopup = QPushButton(VideoDialog)
        self.authPopup.setObjectName(u"authPopup")
        self.authPopup.setMinimumSize(QSize(60, 21))
        self.authPopup.setMaximumSize(QSize(16777215, 25))

        self.gridLayout.addWidget(self.authPopup, 1, 1, 1, 2)

        self.gridLayout.setColumnStretch(7, 1)

        self.verticalLayout.addLayout(self.gridLayout)

        self.line = QFrame(VideoDialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShadow(QFrame.Shadow.Plain)
        self.line.setLineWidth(2)
        self.line.setMidLineWidth(1)
        self.line.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayout.addWidget(self.line)

        self.video = QLabel(VideoDialog)
        self.video.setObjectName(u"video")

        self.verticalLayout.addWidget(self.video)

        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(VideoDialog)

        QMetaObject.connectSlotsByName(VideoDialog)
    # setupUi

    def retranslateUi(self, VideoDialog):
        VideoDialog.setWindowTitle(QCoreApplication.translate("VideoDialog", u"Video Streams", None))
        self.videoSource.setItemText(0, QCoreApplication.translate("VideoDialog", u"RTSP Stream", None))
        self.videoSource.setItemText(1, QCoreApplication.translate("VideoDialog", u"HTTP Stream", None))
        self.videoSource.setItemText(2, QCoreApplication.translate("VideoDialog", u"HTTPS Stream", None))
        self.videoSource.setItemText(3, QCoreApplication.translate("VideoDialog", u"URL", None))
        self.videoSource.setItemText(4, QCoreApplication.translate("VideoDialog", u"Camera 1", None))
        self.videoSource.setItemText(5, QCoreApplication.translate("VideoDialog", u"Camera 2", None))
        self.videoSource.setItemText(6, QCoreApplication.translate("VideoDialog", u"Camera 3", None))
        self.videoSource.setItemText(7, QCoreApplication.translate("VideoDialog", u"Camera 4", None))

        self.frameRate.setItemText(0, QCoreApplication.translate("VideoDialog", u"5.0 fps", None))
        self.frameRate.setItemText(1, QCoreApplication.translate("VideoDialog", u"2.0 fps", None))
        self.frameRate.setItemText(2, QCoreApplication.translate("VideoDialog", u"1.0 fps", None))
        self.frameRate.setItemText(3, QCoreApplication.translate("VideoDialog", u"0.5 fps", None))
        self.frameRate.setItemText(4, QCoreApplication.translate("VideoDialog", u"0.2 fps", None))

        self.videoStop.setText(QCoreApplication.translate("VideoDialog", u"Stop", None))
#if QT_CONFIG(tooltip)
        self.videoURL.setToolTip(QCoreApplication.translate("VideoDialog", u"<html><head/><body><p>Please enter source here. If you have and rtsp url, please leave rtsp:// out, but add the right port if needed.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.videoStart.setText(QCoreApplication.translate("VideoDialog", u"Start", None))
        self.authPopup.setText(QCoreApplication.translate("VideoDialog", u"Auth", None))
        self.video.setText("")
    # retranslateUi

