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
# Licence APL2.0
#
###########################################################
import cv2
import numpy as np
from pathlib import Path
import os
import pyqtgraph as pg
import pytest
import shutil
import unittest.mock as mock
from mw4.gui.extWindows.hemisphere.hemisphereW import HemisphereWindow
from mw4.gui.utilities.toolsQtWidget import MWidget
from PySide6.QtCore import QPointF
from PySide6.QtGui import QCloseEvent
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = HemisphereWindow(app=App())
    yield func
    func.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    with mock.patch.object(function.horizonDraw, "initConfig"):
        with mock.patch.object(function.hemisphereDraw, "initConfig"):
            function.initConfig()


def test_storeConfig_1(function):
    function.app.config = {}
    function.storeConfig()


def test_closeEvent_1(function):
    with mock.patch.object(function, "storeConfig"):
        with mock.patch.object(function.hemisphereDraw, "close"):
            with mock.patch.object(MWidget, "closeEvent"):
                function.closeEvent(QCloseEvent)


def test_showWindow_1(function):
    with mock.patch.object(function.hemisphereDraw, "drawTab"):
        with mock.patch.object(function.horizonDraw, "drawTab"):
            with mock.patch.object(function, "setIcons"):
                with mock.patch.object(function, "show"):
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
    with mock.patch.object(function.hemisphereDraw, "drawTab"):
        with mock.patch.object(function.horizonDraw, "drawTab"):
            with mock.patch.object(function, "setIcons"):
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
    function.app.mount.setting.meridianLimitSlew = 10
    function.app.mount.setting.meridianLimitTrack = 10
    function.drawMeridianLimits(pg.PlotItem())


def test_staticHorizonLimits_2(function):
    function.app.mount.setting.horizonLimitHigh = 90
    function.app.mount.setting.horizonLimitLow = 10
    function.drawHorizonLimits(pg.PlotItem())


def test_drawTerrainImage_1(function):
    function.horizonDraw.imageTerrain = None
    function.drawTerrainImage(pg.PlotItem())


def test_drawTerrainImage_2(function):
    function.horizonDraw.imageTerrain = np.ones((1440, 360))
    with mock.patch.object(function, "openFile", return_value=Path("terrain.jpg")):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(cv2, "imread", return_value=np.array([[0, 0], [0, 0]])):
                with mock.patch.object(cv2, "resize", return_value=np.ones((1440, 360))):
                    with mock.patch.object(cv2, "flip", return_value=np.ones((360, 1440))):
                        function.drawTerrainImage(pg.PlotItem())


def test_redrawAll_1(function):
    with mock.patch.object(function.hemisphereDraw, "drawTab"):
        with mock.patch.object(function.horizonDraw, "drawTab"):
            function.redrawAll()
