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
import time

# external packages
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSizePolicy
import cv2
import numpy as np
import qimage2ndarray

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import video_ui
from base.tpool import Worker


class VideoWindow(toolsQtWidget.MWidget):
    """
    the message window class handles
    """

    __all__ = ['VideoWindow']
    pixmapReady = pyqtSignal(object)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool
        self.ui = video_ui.Ui_VideoDialog()
        self.ui.setupUi(self)
        self.running = False
        self.capture = None
        self.runningCounter = 0
        self.imageSkipFactor = 100
        self.targetFrameRate = 1
        self.smoothSkipFactor = np.zeros(50)

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
        self.ui.frameRate.currentIndexChanged.connect(self.stopVideo)
        self.app.colorChange.connect(self.colorChange)
        self.changeStyleDynamic(self.ui.videoStop, 'running', True)
        self.show()
        return True

    def sendImage(self):
        """
        :return:
        """
        _, frame = self.capture.retrieve()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = qimage2ndarray.array2qimage(frame)
        self.pixmapReady.emit(QPixmap.fromImage(image))
        return True

    def calcSkipFactor(self, start):
        """
        :param start:
        :return:
        """
        if self.runningCounter < 50:
            deltaT = (time.time() - start)
            actualSkipFactor = int(1 / (self.targetFrameRate * deltaT))
            self.smoothSkipFactor[self.runningCounter] = actualSkipFactor

        elif self.runningCounter == 50:
            factor = np.maximum(int(np.mean(self.smoothSkipFactor[25:])), 1)
            self.imageSkipFactor = factor

        self.runningCounter += 1
        return True

    def workerVideo(self, source):
        """
        :param source:
        :return:
        """
        self.capture = cv2.VideoCapture(source)
        while self.running and self.capture.isOpened():
            start = time.time()
            suc = self.capture.grab()
            if not suc:
                break

            if self.runningCounter % self.imageSkipFactor == 0:
                self.sendImage()

            self.calcSkipFactor(start)

        self.capture.release()
        return True

    def startVideo(self):
        """
        :return:
        """
        url = self.ui.videoURL.text()
        sources = [url, 0, 1, 2, 3]
        frameRates = [5, 2, 1, 0.5, 0.25]

        sourceIndex = self.ui.videoSource.currentIndex()
        frameRateIndex = self.ui.frameRate.currentIndex()
        self.targetFrameRate = frameRates[frameRateIndex]
        if not self.ui.videoURL.text() and sourceIndex == 0:
            return False

        self.changeStyleDynamic(self.ui.videoStart, 'running', True)
        self.changeStyleDynamic(self.ui.videoStop, 'running', False)
        self.running = True
        worker = Worker(self.workerVideo, sources[sourceIndex])
        self.threadPool.start(worker)
        return True

    def stopVideo(self):
        """
        :return:
        """
        self.changeStyleDynamic(self.ui.videoStart, 'running', False)
        self.changeStyleDynamic(self.ui.videoStop, 'running', True)
        self.running = False
        return True

    def receivedImage(self, pixmap):
        """
        :param pixmap:
        :return:
        """
        if not self.running:
            return False

        pixmap = pixmap.scaled(self.ui.video.width(), self.ui.video.height())
        self.ui.video.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.video.setPixmap(pixmap)
        return True
