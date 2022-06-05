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

# external packages
from PyQt5.QtGui import QCloseEvent, QPixmap

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
                           'stopVideoStream'):
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


def test_workerVideoStream_1(function):
    function.running = False
    suc = function.workerVideoStream()
    assert suc


def test_startVideoStream_1(function):
    function.ui.streamURL.setText('')
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.startVideoStream()
        assert not suc


def test_startVideoStream_2(function):
    function.ui.streamURL.setText('test')
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.startVideoStream()
        assert suc


def test_stopVideoStream_1(function):
    suc = function.stopVideoStream()
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
