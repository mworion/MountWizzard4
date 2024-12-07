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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtWidgets import QInputDialog
import numpy as np
import cv2

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.videoW import VideoWindow
import gui.extWindows.videoW


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = VideoWindow(app=App())
    with mock.patch.object(func, "show"):
        yield func


def test_closeEvent_1(function):
    with mock.patch.object(function, "stopVideo"):
        with mock.patch.object(MWidget, "closeEvent"):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_colorChange(function):
    suc = function.colorChange()
    assert suc


def test_showWindow_1(function):
    with mock.patch.object(function, "show"):
        suc = function.showWindow()
        assert suc


def test_sendImage_1(function):
    class Test:
        @staticmethod
        def retrieve():
            return (True, np.ones((10, 10, 1)))

    function.capture = Test()
    function.running = False
    with mock.patch.object(cv2, "cvtColor", return_value=np.ones((10, 10, 1))):
        suc = function.sendImage()
        assert not suc


def test_sendImage_2(function):
    class Test:
        @staticmethod
        def retrieve():
            return (True, np.ones((10, 10, 1)))

    function.capture = Test()
    function.running = False
    with mock.patch.object(
        cv2, "cvtColor", return_value=np.ones((10, 10, 1)), side_effect=cv2.error
    ):
        suc = function.sendImage()
        assert not suc


def test_sendImage_3(function):
    class Test:
        @staticmethod
        def retrieve():
            return (True, np.ones((10, 10, 1)))

    function.capture = Test()
    function.running = True
    with mock.patch.object(cv2, "cvtColor", return_value=np.ones((10, 10, 1))):
        suc = function.sendImage()
        assert suc


def test_count(function):
    function.runningCounter = 0
    suc = function.count()
    assert suc
    assert function.runningCounter == 1


def test_workerVideoStream_0(function):
    class Test:
        @staticmethod
        def isOpened():
            return True

        @staticmethod
        def grab():
            return False

        @staticmethod
        def release():
            return

        @staticmethod
        def open(a):
            return

        @staticmethod
        def setExceptionMode(a):
            return

    function.running = True
    with mock.patch.object(cv2, "VideoCapture", return_value=Test()):
        with mock.patch.object(Test, "open", side_effect=cv2.error):
            suc = function.workerVideo("test", 1)
            assert not suc
            assert not function.running


def test_workerVideoStream_1(function):
    class Test:
        @staticmethod
        def isOpened():
            return True

        @staticmethod
        def open(a):
            return

        @staticmethod
        def grab():
            return False

        @staticmethod
        def release():
            return

        @staticmethod
        def setExceptionMode(a):
            return

    function.running = True
    with mock.patch.object(cv2, "VideoCapture", return_value=Test()):
        with mock.patch.object(Test, "open", side_effect=Exception):
            suc = function.workerVideo("test", 1)
            assert not suc
            assert not function.running


def test_workerVideoStream_2(function):
    class Test:
        @staticmethod
        def isOpened():
            return False

        @staticmethod
        def open(a):
            return

        @staticmethod
        def grab():
            return False

        @staticmethod
        def release():
            return

        @staticmethod
        def setExceptionMode(a):
            return

    function.running = True
    with mock.patch.object(cv2, "VideoCapture", return_value=Test()):
        suc = function.workerVideo("test", 1)
        assert not suc
        assert not function.running


def test_workerVideoStream_3(function):
    class Test:
        @staticmethod
        def isOpened():
            return True

        @staticmethod
        def open(a):
            return

        @staticmethod
        def grab():
            return False

        @staticmethod
        def release():
            return

        @staticmethod
        def setExceptionMode(a):
            return

    function.running = True
    with mock.patch.object(cv2, "VideoCapture", return_value=Test()):
        with mock.patch.object(function, "sendImage"):
            suc = function.workerVideo("test", 1)
            assert suc


def test_workerVideoStream_4(function):
    class Test:
        @staticmethod
        def isOpened():
            return True

        @staticmethod
        def open(a):
            return

        @staticmethod
        def grab():
            function.running = False
            return True

        @staticmethod
        def release():
            return

        @staticmethod
        def setExceptionMode(a):
            return

    function.running = True
    with mock.patch.object(cv2, "VideoCapture", return_value=Test()):
        with mock.patch.object(function, "sendImage"):
            suc = function.workerVideo("test", 1)
            assert suc


def test_startVideoStream_1(function):
    function.user = "1"
    function.password = "1"
    function.ui.videoURL.setText("")
    with mock.patch.object(function.threadPool, "start"):
        suc = function.startVideo()
        assert not suc


def test_startVideoStream_2(function):
    function.user = ""
    function.password = ""
    function.ui.videoURL.setText("test")
    with mock.patch.object(function.threadPool, "start"):
        suc = function.startVideo()
        assert suc


def test_stopVideoStream_1(function):
    suc = function.stopVideo()
    assert suc


def test_restartVideo(function):
    with mock.patch.object(function, "stopVideo"):
        with mock.patch.object(function, "startVideo"):
            with mock.patch.object(gui.extWindows.videoW, "sleepAndEvents"):
                suc = function.restartVideo()
                assert suc


def test_receivedImage_1(function):
    pixmap = QPixmap(100, 100)
    function.running = False
    suc = function.receivedImage(pixmap)
    assert not suc


def test_receivedImage_2(function):
    pixmap = QPixmap(100, 100)
    function.running = True
    suc = function.receivedImage(pixmap)
    assert suc


def test_checkAuth(function):
    suc = function.checkAuth()
    assert suc


def test_authPopup_1(function):
    function.user = "test"
    function.password = "test"
    with mock.patch.object(function, "checkAuth"):
        with mock.patch.object(function, "restartVideo"):
            with mock.patch.object(
                QInputDialog, "getText", return_value=("test", False)
            ):
                suc = function.authPopup()
                assert not suc
                assert function.user == "test"
                assert function.password == "test"


def test_authPopup_2(function):
    function.user = "test"
    function.password = "test"
    with mock.patch.object(function, "checkAuth"):
        with mock.patch.object(function, "restartVideo"):
            with mock.patch.object(
                QInputDialog, "getText", return_value=("test1", True)
            ):
                suc = function.authPopup()
                assert suc
                assert function.user == "test1"
                assert function.password == "test1"
