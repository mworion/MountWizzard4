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
import gc
import numpy as np
import pyqtgraph as pg
import pytest
import unittest.mock as mock
from mw4.gui.extWindows.hemisphere.hemisphereW import HemisphereWindow
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtCore import QPointF
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = HemisphereWindow(app=App(), title="Hemisphere")
    yield func
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_initConfig_1(function):
    with (
        mock.patch.object(function.horizonDraw, "initConfig"),
        mock.patch.object(function.hemisphereDraw, "initConfig"),
    ):
        function.initConfig()


def test_storeConfig_1(function):
    function.app.config = {}
    function.storeConfig()


def test_closeEvent_1(function):
    with (
        mock.patch.object(function, "storeConfig"),
        mock.patch.object(function.hemisphereDraw, "closeTab"),
        mock.patch.object(function.horizonDraw, "closeTab"),
        mock.patch.object(MWidget, "closeEvent"),
    ):
        function.closeEvent(QCloseEvent)


def test_showWindow_1(function):
    with (
        mock.patch.object(function.hemisphereDraw, "drawTab"),
        mock.patch.object(function.horizonDraw, "drawTab"),
        mock.patch.object(function, "setIcons"),
        mock.patch.object(function, "show"),
    ):
        function.showWindow()


def test_setIcons(function):
    function.setIcons()


def test_mouseMoved_1(function):
    with mock.patch.object(
        function.ui.hemisphere.p[0].getViewBox(), "posInViewRange", return_value=False
    ):
        function.mouseMoved(pos=QPointF(1, 1))


def test_mouseMoved_2(function):
    with mock.patch.object(
        function.ui.hemisphere.p[0].getViewBox(), "posInViewRange", return_value=True
    ):
        function.mouseMoved(pos=QPointF(0.5, 0.5))


def test_colorChange(function):
    with (
        mock.patch.object(function.hemisphereDraw, "drawTab"),
        mock.patch.object(function.horizonDraw, "drawTab"),
        mock.patch.object(function, "setIcons"),
    ):
        function.colorChange()


def test_preparePlotItem(function):
    pd = pg.PlotItem()
    function.preparePlotItem(pd)


def test_preparePolarItem_1(function):
    pd = pg.PlotItem()
    function.ui.showPolar.setChecked(False)
    function.preparePolarItem(pd)


def test_preparePolarItem_2(function):
    pd = pg.PlotItem()
    function.ui.showPolar.setChecked(True)
    function.preparePolarItem(pd)


def test_drawMeridianLimits2(function):
    function.app.dReg.drivers["mount"]["class"].setting.meridianLimitSlew = 10
    function.app.dReg.drivers["mount"]["class"].setting.meridianLimitTrack = 10
    function.drawMeridianLimits(pg.PlotItem())


def test_staticHorizonLimits_2(function):
    function.app.dReg.drivers["mount"]["class"].setting.horizonLimitHigh = 90
    function.app.dReg.drivers["mount"]["class"].setting.horizonLimitLow = 10
    function.drawHorizonLimits(pg.PlotItem())


def test_drawTerrainImage_1(function):
    function.horizonDraw.imageTerrain = np.ones((0, 0))
    function.drawTerrainImage(pg.PlotItem())


def test_drawTerrainImage_2(function):
    function.horizonDraw.imageTerrain = np.ones((1440, 360))
    with (
        mock.patch.object(function, "openFile", return_value=Path("terrain.jpg")),
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(cv2, "imread", return_value=np.array([[0, 0], [0, 0]])),
        mock.patch.object(cv2, "resize", return_value=np.ones((1440, 360))),
        mock.patch.object(cv2, "flip", return_value=np.ones((360, 1440))),
    ):
        function.drawTerrainImage(pg.PlotItem())


def test_redrawAll_1(function):
    with (
        mock.patch.object(function.hemisphereDraw, "drawTab"),
        mock.patch.object(function.horizonDraw, "drawTab"),
    ):
        function.redrawAll()
