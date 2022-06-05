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
import pytest
import unittest.mock as mock
import time

# external packages
from PyQt5.QtGui import QCloseEvent, QPixmap
import numpy as np
import cv2

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.videoW import VideoWindow


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    func = VideoWindow(app=App())
    yield func


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'stopVideo'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_colorChange(function):
    suc = function.colorChange()
    assert suc


def test_showWindow_1(function):
    with mock.patch.object(function,
                           'show'):
        suc = function.showWindow()
        assert suc


def test_sendImage(function):
    class Test:
        @staticmethod
        def retrieve():
            return (True, np.ones((10, 10, 1)))

    function.capture = Test()

    with mock.patch.object(cv2,
                           'cvtColor',
                           return_value=np.ones((10, 10, 1))):
        suc = function.sendImage()
        assert suc


def test_calcSkipFactor_1(function):
    function.runningCounter = 10
    with mock.patch.object(time,
                           'time',
                           return_value=3):
        suc = function.calcSkipFactor(1)
        assert suc
        assert function.runningCounter == 11


def test_calcSkipFactor_2(function):
    function.runningCounter = 50
    with mock.patch.object(time,
                           'time',
                           return_value=3):
        suc = function.calcSkipFactor(1)
        assert suc
        assert function.runningCounter == 51


def test_workerVideoStream_1(function):
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

    function.running = True
    with mock.patch.object(cv2,
                           'VideoCapture',
                           return_value=Test()):
        with mock.patch.object(function,
                               'sendImage'):
            with mock.patch.object(function,
                                   'calcSkipFactor'):
                suc = function.workerVideo('test')
                assert suc


def test_workerVideoStream_2(function):
    class Test:
        @staticmethod
        def isOpened():
            return True

        @staticmethod
        def grab():
            function.running = False
            return True

        @staticmethod
        def release():
            return

    function.running = True
    with mock.patch.object(cv2,
                           'VideoCapture',
                           return_value=Test()):
        with mock.patch.object(function,
                               'sendImage'):
            with mock.patch.object(function,
                                   'calcSkipFactor'):
                suc = function.workerVideo('test')
                assert suc


def test_startVideoStream_1(function):
    function.ui.videoURL.setText('')
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.startVideo()
        assert not suc


def test_startVideoStream_2(function):
    function.ui.videoURL.setText('test')
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.startVideo()
        assert suc


def test_stopVideoStream_1(function):
    suc = function.stopVideo()
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
