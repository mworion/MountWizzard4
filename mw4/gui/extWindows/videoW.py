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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSizePolicy, QInputDialog, QLineEdit
import cv2
import qimage2ndarray

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets import video_ui
from base.tpool import Worker
from gui.utilities.toolsQtWidget import sleepAndEvents, changeStyleDynamic


class VideoWindow(MWidget):
    """ """

    pixmapReady = Signal(object)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.ui = video_ui.Ui_VideoDialog()
        self.ui.setupUi(self)
        self.running = False
        self.capture = None
        self.user = ""
        self.password = ""
        self.runningCounter = 0
        self.worker: Worker = None

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.stopVideo()
        super().closeEvent(closeEvent)

    def colorChange(self) -> None:
        """ """
        self.setStyleSheet(self.mw4Style)

    def showWindow(self) -> None:
        """ """
        self.pixmapReady.connect(self.receivedImage)
        self.ui.videoStart.clicked.connect(self.startVideo)
        self.ui.videoStop.clicked.connect(self.stopVideo)
        self.ui.videoSource.currentIndexChanged.connect(self.stopVideo)
        self.ui.frameRate.currentIndexChanged.connect(self.restartVideo)
        self.ui.authPopup.clicked.connect(self.authPopup)
        self.app.colorChange.connect(self.colorChange)
        self.app.update0_1s.connect(self.count)
        changeStyleDynamic(self.ui.videoStop, "running", True)
        self.checkAuth()
        self.show()

    def sendImage(self) -> None:
        """ """
        try:
            _, frame = self.capture.retrieve()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except cv2.error as e:
            self.msg.emit(2, "Video", "Compatibility", e)
            return

        image = qimage2ndarray.array2qimage(frame)
        if not self.running:
            return
        self.pixmapReady.emit(QPixmap.fromImage(image))

    def count(self) -> None:
        """ """
        self.runningCounter += 1

    def workerVideo(self, source: str, frameRate: int) -> None:
        """ """
        self.capture = cv2.VideoCapture()
        self.capture.setExceptionMode(True)
        try:
            self.capture.open(source)
            if not self.capture.isOpened():
                self.msg.emit(2, "Video", "Camera", f"[{source}] not available")
                self.running = False
                return
        except cv2.error as e:
            self.msg.emit(2, "Video", "Camera error", f"MSG: {e.err}")
            self.running = False
            return
        except Exception as e:
            self.msg.emit(2, "Video", "Camera error", f"MSG: {e}")
            self.running = False
            return

        self.runningCounter = 0
        while self.running:
            suc = self.capture.grab()
            if not suc:
                break
            if self.runningCounter % frameRate == 0:
                self.sendImage()

        self.capture.release()

    def startVideo(self) -> None:
        """ """
        if self.user and self.password:
            auth = f"{self.user}:{self.password}@"
        else:
            auth = ""
        url = f"{auth}{self.ui.videoURL.text()}"
        sources = ["rtsp://" + url, "http://" + url, "https://" + url, url, 0, 1, 2, 3]
        frameCounter = [2, 5, 10, 20, 50]

        sourceIndex = self.ui.videoSource.currentIndex()
        frameRateIndex = self.ui.frameRate.currentIndex()
        frameRate = frameCounter[frameRateIndex]
        if not self.ui.videoURL.text() and sourceIndex == 0:
            return

        source = sources[sourceIndex]
        self.log.info(f"Video started: source [{source}]")
        changeStyleDynamic(self.ui.videoStart, "running", True)
        changeStyleDynamic(self.ui.videoStop, "running", False)
        self.running = True
        self.worker = Worker(self.workerVideo, source, frameRate)
        self.threadPool.start(self.worker)

    def stopVideo(self) -> None:
        """ """
        changeStyleDynamic(self.ui.videoStart, "running", False)
        changeStyleDynamic(self.ui.videoStop, "running", True)
        self.pixmapReady.emit(None)
        self.running = False

    def restartVideo(self) -> None:
        """ """
        self.stopVideo()
        sleepAndEvents(1000)
        self.startVideo()

    def receivedImage(self, pixmap: QPixmap) -> None:
        """ """
        if not self.running or pixmap is None:
            self.ui.video.clear()
            return

        pixmap = pixmap.scaled(self.ui.video.width(), self.ui.video.height())
        self.ui.video.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.ui.video.setPixmap(pixmap)

    def checkAuth(self) -> None:
        """ """
        hasAuth = self.user != "" and self.password != ""
        changeStyleDynamic(self.ui.authPopup, "running", hasAuth)

    def authPopup(self) -> None:
        """ """
        dlg = QInputDialog()
        value1, ok1 = dlg.getText(
            self,
            "Get authentication",
            "Username: ",
            QLineEdit.EchoMode.Normal,
            self.user,
        )
        value2, ok2 = dlg.getText(
            self,
            "Get authentication",
            "Password: ",
            QLineEdit.EchoMode.Normal,
            self.password,
        )
        if not ok1 or not ok2:
            return
        self.user = value1
        self.password = value2
        self.checkAuth()
        self.restartVideo()
