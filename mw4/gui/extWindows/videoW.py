############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSizePolicy
import cv2
import qimage2ndarray

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import video_ui
from base.tpool import Worker
from gui.utilities.toolsQtWidget import sleepAndEvents


class VideoWindow(toolsQtWidget.MWidget):
    """
    the message window class handles
    """

    __all__ = ['VideoWindow']
    pixmapReady = pyqtSignal(object)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.ui = video_ui.Ui_VideoDialog()
        self.ui.setupUi(self)
        self.running = False
        self.capture = None
        self.runningCounter = 0

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.stopVideo()
        super().closeEvent(closeEvent)

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        return True

    def showWindow(self):
        """
        :return: true for test purpose
        """
        self.pixmapReady.connect(self.receivedImage)
        self.ui.videoStart.clicked.connect(self.startVideo)
        self.ui.videoStop.clicked.connect(self.stopVideo)
        self.ui.videoSource.currentIndexChanged.connect(self.stopVideo)
        self.ui.frameRate.currentIndexChanged.connect(self.restartVideo)
        self.app.colorChange.connect(self.colorChange)
        self.app.update0_1s.connect(self.count)
        self.changeStyleDynamic(self.ui.videoStop, 'running', True)
        self.show()
        return True

    def sendImage(self):
        """
        :return:
        """
        try:
            _, frame = self.capture.retrieve()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except cv2.error as e:
            self.msg.emit(2, 'Video', 'Compatibility', e)
            return False

        image = qimage2ndarray.array2qimage(frame)
        if not self.running:
            return False
        self.pixmapReady.emit(QPixmap.fromImage(image))
        return True

    def count(self):
        """
        :return:
        """
        self.runningCounter += 1
        return True

    def workerVideo(self, source, frameRate):
        """
        :param source:
        :param frameRate:
        :return:
        """
        try:
            self.capture = cv2.VideoCapture(source)
        except cv2.error as e:
            self.msg.emit(2, 'Video', 'Camera error', e)
            self.running = False
            return False

        if not self.capture.isOpened():
            self.msg.emit(2, 'Video', 'Camera', f'[{source}] could not be started')
            self.running = False
            return False

        self.runningCounter = 0
        while self.running:
            suc = self.capture.grab()
            if not suc:
                break
            if self.runningCounter % frameRate == 0:
                self.sendImage()

        self.capture.release()
        return True

    def startVideo(self):
        """
        :return:
        """
        url = f'rtsp://{self.ui.videoURL.text()}'
        sources = [url, 0, 1, 2, 3]
        frameCounter = [2, 5, 10, 20, 50]

        sourceIndex = self.ui.videoSource.currentIndex()
        frameRateIndex = self.ui.frameRate.currentIndex()
        frameRate = frameCounter[frameRateIndex]
        if not self.ui.videoURL.text() and sourceIndex == 0:
            return False

        source = sources[sourceIndex]
        self.log.info(f'Video started: source [{source}]')
        self.changeStyleDynamic(self.ui.videoStart, 'running', True)
        self.changeStyleDynamic(self.ui.videoStop, 'running', False)
        self.running = True
        worker = Worker(self.workerVideo, source, frameRate)
        self.threadPool.start(worker)
        return True

    def stopVideo(self):
        """
        :return:
        """
        self.changeStyleDynamic(self.ui.videoStart, 'running', False)
        self.changeStyleDynamic(self.ui.videoStop, 'running', True)
        self.pixmapReady.emit(None)
        self.running = False
        return True

    def restartVideo(self):
        """
        :return:
        """
        self.stopVideo()
        sleepAndEvents(1000)
        self.startVideo()
        return True

    def receivedImage(self, pixmap):
        """
        :param pixmap:
        :return:
        """
        if not self.running or pixmap is None:
            self.ui.video.clear()
            return False

        pixmap = pixmap.scaled(self.ui.video.width(), self.ui.video.height())
        self.ui.video.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.video.setPixmap(pixmap)
        return True
