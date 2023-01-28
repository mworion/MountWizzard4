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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages
from PyQt5.QtCore import QRectF
import pyqtgraph as pg
from astropy import wcs
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.imageW import ImageWindow
from logic.photometry.photometry import Photometry
from logic.file.fileHandler import FileHandler


@pytest.fixture(autouse=True, scope='function')
def function(qapp):

    func = ImageWindow(app=App())
    yield func


def test_showTabImage_1(function):
    function.fileHandler = FileHandler(function)
    function.fileHandler.image = np.random.rand(100, 100) + 1
    function.fileHandler.wcs = wcs.WCS()
    with mock.patch.object(function,
                           'setBarColor'):
        with mock.patch.object(function,
                               'setCrosshair'):
            with mock.patch.object(function,
                                   'writeHeaderDataToGUI'):
                suc = function.showTabImage()
                assert suc


def test_showTabImage_2(function):
    function.fileHandler = FileHandler(function)
    function.fileHandler.image = None
    suc = function.showTabImage()
    assert not suc


def test_showTabHFR(function):
    function.ui.isoLayer.setChecked(True)
    function.photometry = Photometry(function)
    function.photometry.hfr = np.random.rand(100, 100) + 1
    function.photometry.hfrPercentile = 0
    function.photometry.hfrMedian = 0
    with mock.patch.object(function.ui.hfr,
                           'addIsoBasic'):
        suc = function.showTabHFR()
        assert suc


def test_showTabTiltSquare(function):
    function.photometry = Photometry(function)
    function.photometry.hfr = np.linspace(20, 30, 20)
    function.photometry.hfrMedian = 1
    function.photometry.hfrInner = 1
    function.photometry.hfrOuter = 1
    function.photometry.w = 100
    function.photometry.h = 100
    function.photometry.hfrSegSquare = np.ones((3, 3))
    function.photometry.image = np.random.rand(100, 100) + 1
    suc = function.showTabTiltSquare()
    assert suc


def test_showTabTiltTriangle(function):
    function.photometry = Photometry(function)
    function.photometry.hfr = np.linspace(20, 30, 20)
    function.photometry.hfrMedian = 1
    function.photometry.hfrInner = 1
    function.photometry.hfrOuter = 1
    function.photometry.w = 100
    function.photometry.h = 100
    function.photometry.hfrSegTriangle = np.ones(72)
    function.image = np.random.rand(100, 100) + 1
    suc = function.showTabTiltTriangle()
    assert suc


def test_showTabRoundness(function):
    function.ui.isoLayer.setChecked(True)
    function.photometry = Photometry(function)
    function.photometry.roundnessMin = 1
    function.photometry.roundnessMax = 10
    function.photometry.roundnessPercentile = 10
    function.photometry.roundnessGrid = np.random.rand(100, 100) + 1
    with mock.patch.object(function.ui.roundness,
                           'addIsoBasic'):
        suc = function.showTabRoundness()
    assert suc


def test_showTabAberrationInspect(function):
    function.photometry = Photometry(function)
    function.photometry.image = np.random.rand(100, 100) + 1
    function.photometry.roundnessPercentile = 1
    suc = function.showTabAberrationInspect()
    assert suc


def test_showTabImageSources(function):
    function.photometry = Photometry(function)
    function.imageSourceRange = QRectF(1, 2, 3, 4)
    function.photometry.objs = {'x': np.linspace(0, 50, 20),
                                'y': np.linspace(50, 100, 20),
                                'theta': np.random.rand(20, 1) + 10,
                                'a': np.random.rand(20, 1) + 10,
                                'b': np.random.rand(20, 1) + 10}
    function.photometry.image = np.random.rand(100, 100) + 1
    function.photometry.hfr = np.random.rand(20, ) + 10.0

    function.ui.showValues.setChecked(True)
    with mock.patch.object(function.ui.imageSource,
                           'addEllipse',
                           return_value=pg.PlotItem()):
        suc = function.showTabImageSources()
        assert suc


def test_showTabBackground(function):
    function.photometry = Photometry(function)
    function.photometry.background = np.random.rand(100, 100) + 1
    suc = function.showTabBackground()
    assert suc


def test_showTabBackgroundRMS(function):
    function.photometry = Photometry(function)
    function.photometry.backgroundRMS = np.random.rand(100, 100) + 1
    suc = function.showTabBackgroundRMS()
    assert suc
