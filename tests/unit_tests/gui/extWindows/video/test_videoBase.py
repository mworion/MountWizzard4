############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import cv2
import mw4.gui.extWindows.video.videoBase
import numpy as np
import pytest
import unittest.mock as mock
from mw4.gui.extWindows.video.videoBase import VideoWindowBase
from mw4.gui.utilities.nativeQt.qtInputDialog import MWInputDialog
from mw4.gui.utilities.qtMain import MWidget
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = VideoWindowBase(app=App())
    yield func
    QApplication.processEvents()


def test_closeEvent_1(function):
    with mock.patch.object(function, "stopVideo"), mock.patch.object(MWidget, "closeEvent"):
        function.closeEvent(QCloseEvent)


def test_colorChange(function):
    function.colorChange()


def test_showWindow_1(function):
    with mock.patch.object(function, "show"):
        function.showWindow()


def test_sendImage_1(function):
    function.capture = cv2.VideoCapture()
    function.running = False
    with mock.patch.object(cv2, "cvtColor", return_value=np.ones((10, 10, 1))):
        function.sendImage()


def test_sendImage_2(function):
    function.capture = cv2.VideoCapture()
    function.running = False
    with mock.patch.object(
        cv2, "cvtColor", return_value=np.ones((10, 10, 1)), side_effect=cv2.error
    ):
        function.sendImage()


def test_sendImage_3(function):
    function.capture = cv2.VideoCapture()
    function.running = True
    with mock.patch.object(cv2, "cvtColor", return_value=np.ones((10, 10, 1))):
        function.sendImage()


def test_count(function):
    function.runningCounter = 0
    function.count()
    assert function.runningCounter == 1


def test_workerVideoStream_0(function):
    capture = mock.MagicMock()
    capture.isOpened.return_value = True
    capture.open.side_effect = cv2.error
    function.capture = capture
    function.running = True
    function.workerVideo("test", 1)
    assert not function.running


def test_workerVideoStream_1(function):
    capture = mock.MagicMock()
    capture.isOpened.return_value = True
    capture.open.side_effect = Exception
    function.capture = capture
    function.running = True
    function.workerVideo("test", 1)
    assert not function.running


def test_workerVideoStream_2(function):
    capture = mock.MagicMock()
    capture.isOpened.return_value = False
    function.capture = capture
    function.running = True
    function.workerVideo("test", 1)
    assert not function.running


def test_workerVideoStream_3(function):
    capture = mock.MagicMock()
    capture.isOpened.return_value = True
    capture.grab.return_value = False
    function.running = True
    function.capture = capture
    with mock.patch.object(function, "sendImage"):
        function.workerVideo("test", 1)


def test_workerVideoStream_4(function):
    def grabSideEffect():
        function.running = False
        return True

    capture = mock.MagicMock()
    capture.isOpened.return_value = True
    capture.grab.side_effect = grabSideEffect
    function.running = True
    function.capture = capture
    with mock.patch.object(function, "sendImage"):
        function.workerVideo("test", 1)


def test_startVideoStream_1(function):
    function.user = "1"
    function.password = "1"
    function.ui.videoURL.setText("")
    with mock.patch.object(function.threadPool, "start"):
        function.startVideo()


def test_startVideoStream_2(function):
    function.user = ""
    function.password = ""
    function.ui.videoURL.setText("test")
    with mock.patch.object(function.threadPool, "start"):
        function.startVideo()


def test_stopVideoStream_1(function):
    function.stopVideo()


def test_restartVideo(function):
    with (
        mock.patch.object(function, "stopVideo"),
        mock.patch.object(function, "startVideo"),
        mock.patch.object(mw4.gui.extWindows.video.videoBase, "mainThreadSleep"),
    ):
        function.restartVideo()


def test_receivedImage_1(function):
    pixmap = QPixmap(100, 100)
    function.running = False
    function.receivedImage(pixmap)


def test_receivedImage_2(function):
    pixmap = QPixmap(100, 100)
    function.running = True
    function.receivedImage(pixmap)


def test_checkAuth(function):
    function.checkAuth()


def test_authPopup_1(function):
    function.user = "test"
    function.password = "test"
    with (
        mock.patch.object(function, "checkAuth"),
        mock.patch.object(function, "restartVideo"),
        mock.patch.object(MWInputDialog, "getText", return_value=("test", False)),
    ):
        function.authPopup()
        assert function.user == "test"
        assert function.password == "test"


def test_authPopup_2(function):
    function.user = "test"
    function.password = "test"
    with (
        mock.patch.object(function, "checkAuth"),
        mock.patch.object(function, "restartVideo"),
        mock.patch.object(MWInputDialog, "getText", return_value=("test1", True)),
    ):
        function.authPopup()
        assert function.user == "test1"
        assert function.password == "test1"
