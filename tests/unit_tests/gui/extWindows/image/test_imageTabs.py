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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import numpy as np
import pyqtgraph as pg
import pytest
import unittest.mock as mock
from astropy import wcs
from astropy.io import fits
from mw4.gui.extWindows.image.imageTabs import ImageTabs
from mw4.gui.extWindows.image.imageW import ImageWindow
from mw4.gui.utilities.gCustomViewBox import CustomViewBox
from mw4.logic.file.fileHandler import FileHandler
from mw4.logic.photometry.photometry import Photometry
from PySide6.QtCore import QRectF
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    CustomViewBox._previousGeometry = None
    parent = ImageWindow(app=App())
    func = ImageTabs(parent)
    yield func
    parent.app.threadPool.waitForDone(10000)


def test_colorChange(function):
    function.colorChange()


def test_getImageSourceRange(function):
    function.getImageSourceRange()


def test_setBarColor_1(function):
    function.ui.color.setCurrentIndex(0)
    with mock.patch.object(function.ui.image, "setColorMap"):
        function.setBarColor()


def test_setCrosshair_1(function):
    function.ui.color.setCurrentIndex(0)
    with mock.patch.object(function.ui.image, "showCrosshair"):
        function.setCrosshair()


def test_writeHeaderDataToGUI_3(function):
    function.header = fits.PrimaryHDU().header
    function.header["naxis"] = 2
    function.header["OBJCTRA"] = "+08 00 00"
    function.header["OBJCTDEC"] = "90 00 00"
    function.writeHeaderDataToGUI(function.header)


def test_writeHeaderDataToGUI_4(function):
    function.header = fits.PrimaryHDU().header
    function.header["naxis"] = 2
    function.header["RA"] = 12.0
    function.header["DEC"] = 80.0
    function.writeHeaderDataToGUI(function.header)


def test_clearImageTab(function):
    function.clearImageTab(function.ui.image)


def test_showTabImage_1(function):
    function.fileHandler = FileHandler(function)
    function.fileHandler.image = np.random.rand(100, 100) + 1
    function.fileHandler.wcs = wcs.WCS()
    with mock.patch.object(function, "setBarColor"):
        with mock.patch.object(function, "setCrosshair"):
            with mock.patch.object(function, "writeHeaderDataToGUI"):
                function.showImage()


def test_showTabImage_2(function):
    function.fileHandler = FileHandler(function)
    function.fileHandler.image = None
    function.showImage()


def test_showTabHFR(function):
    function.ui.isoLayer.setChecked(True)
    function.photometry = Photometry(function)
    function.photometry.hfr = np.random.rand(100, 100) + 1
    function.photometry.hfrPercentile = 0
    function.photometry.hfrMedian = 0
    with mock.patch.object(function.ui.hfr, "addIsoBasic"):
        function.showHFR()


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
    function.showTiltSquare()


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
    function.showTiltTriangle()


def test_showTabRoundness(function):
    function.ui.isoLayer.setChecked(True)
    function.photometry = Photometry(function)
    function.photometry.roundnessMin = 1
    function.photometry.roundnessMax = 10
    function.photometry.roundnessPercentile = 10
    function.photometry.roundnessGrid = np.random.rand(100, 100) + 1
    with mock.patch.object(function.ui.roundness, "addIsoBasic"):
        function.showRoundness()


def test_showTabAberrationInspect(function):
    function.photometry = Photometry(function)
    function.photometry.image = np.random.rand(100, 100) + 1
    function.photometry.roundnessPercentile = 1
    function.showAberrationInspect()


def test_showTabImageSources(function):
    function.photometry = Photometry(function)
    function.imageSourceRange = QRectF(1, 2, 3, 4)
    function.photometry.objs = {
        "x": np.linspace(0, 50, 20),
        "y": np.linspace(50, 100, 20),
        "theta": np.random.rand(20, 1) + 10,
        "a": np.random.rand(20, 1) + 10,
        "b": np.random.rand(20, 1) + 10,
    }
    function.photometry.image = np.random.rand(100, 100) + 1
    function.photometry.hfr = (
        np.random.rand(
            20,
        )
        + 10.0
    )

    function.ui.showValues.setChecked(True)
    with mock.patch.object(function.ui.imageSource, "addEllipse", return_value=pg.PlotItem()):
        with mock.patch.object(function.ui.tabImage, "setTabEnabled"):
            function.showImageSources()


def test_showTabBackground(function):
    function.photometry = Photometry(function)
    function.photometry.background = np.random.rand(100, 100) + 1
    function.showBackground()


def test_showTabBackgroundRMS(function):
    function.photometry = Photometry(function)
    function.photometry.backgroundRMS = np.random.rand(100, 100) + 1
    function.showBackgroundRMS()
