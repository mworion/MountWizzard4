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
        self.stopVideoStream()
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
        self.ui.streamStart.clicked.connect(self.startVideoStream)
        self.ui.streamStop.clicked.connect(self.stopVideoStream)
        self.app.colorChange.connect(self.colorChange)
        self.changeStyleDynamic(self.ui.streamStop, 'running', True)
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

    def workerVideoStream(self):
        """
        :return:
        """
        streamURL = self.ui.streamURL.text()
        self.capture = cv2.VideoCapture(streamURL)

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

    def startVideoStream(self):
        """
        :return:
        """
        if not self.ui.streamURL.text():
            return False

        self.changeStyleDynamic(self.ui.streamStart, 'running', True)
        self.changeStyleDynamic(self.ui.streamStop, 'running', False)
        self.running = True
        worker = Worker(self.workerVideoStream)
        self.threadPool.start(worker)
        return True

    def stopVideoStream(self):
        """
        :return:
        """
        self.changeStyleDynamic(self.ui.streamStart, 'running', False)
        self.changeStyleDynamic(self.ui.streamStop, 'running', True)
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
