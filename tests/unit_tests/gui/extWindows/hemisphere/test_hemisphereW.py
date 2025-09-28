############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import os
import shutil

# external packages
from PySide6.QtCore import QPointF
from PySide6.QtGui import QCloseEvent
import pyqtgraph as pg

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.hemisphere.hemisphereW import HemisphereWindow


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = HemisphereWindow(app=App())
    yield func
    func.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.initConfig()


def test_initConfig_2(function):
    function.app.config["hemisphereW"] = {"winPosX": 10000}
    function.app.config["hemisphereW"] = {"winPosY": 10000}
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.initConfig()


def test_initConfig_3(function):
    function.app.config["hemisphereW"] = {}
    function.app.config["hemisphereW"] = {"winPosX": 100}
    function.app.config["hemisphereW"] = {"winPosY": 100}
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.initConfig()


def test_initConfig_4(function):
    shutil.copy("tests/testData/terrain.jpg", "tests/work/config/terrain.jpg")
    function.app.config["hemisphereW"] = {}
    function.app.config["hemisphereW"] = {"winPosX": 100}
    function.app.config["hemisphereW"] = {"winPosY": 100}
    function.initConfig()


def test_storeConfig_1(function):
    function.app.config = {}
    function.storeConfig()


def test_enableTabsMovable(function):
    function.enableTabsMovable(True)


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


def test_redrawAll_1(function):
    with mock.patch.object(function.hemisphereDraw, "drawTab"):
        with mock.patch.object(function.horizonDraw, "drawTab"):
            function.redrawAll()
