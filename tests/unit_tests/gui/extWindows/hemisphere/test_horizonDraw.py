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
import unittest.mock as mock
import pytest
import os
import shutil
from pathlib import Path

# external packages
from PySide6.QtCore import QPointF
from skyfield.api import Angle
import pyqtgraph as pg
import cv2
import numpy as np


# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.hemisphere.hemisphereW import HemisphereWindow
from gui.extWindows.hemisphere.horizonDraw import HorizonDraw
from gui.utilities.gCustomViewBox import CustomViewBox


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    shutil.copy("tests/testData/terrain.jpg", "tests/work/config/terrain.jpg")
    func = HorizonDraw(parent=HemisphereWindow(app=App()))
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


def test_mouseMovedHorizon_1(function):
    with mock.patch.object(
        function.ui.hemisphere.p[0].getViewBox(), "posInViewRange", return_value=False
    ):
        function.mouseMovedHorizon(pos=QPointF(1, 1))


def test_mouseMovedHorizon_2(function):
    with mock.patch.object(
        function.ui.hemisphere.p[0].getViewBox(), "posInViewRange", return_value=True
    ):
        function.mouseMovedHorizon(pos=QPointF(0.5, 0.5))


def test_drawTerrainImage_1(function):
    function.imageTerrain = None
    function.drawTerrainImage(pg.PlotItem())


def test_drawTerrainImage_2(function):
    function.imageTerrain = np.ones((1440, 360))
    with mock.patch.object(function, "openFile", return_value=Path("terrain.jpg")):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(cv2, "imread", return_value=np.array([[0, 0], [0, 0]])):
                with mock.patch.object(cv2, "resize", return_value=np.ones((1440, 360))):
                    with mock.patch.object(cv2, "flip", return_value=np.ones((360, 1440))):
                        function.drawTerrainImage(pg.PlotItem())


def test_loadTerrainImage_1(function):
    with mock.patch.object(function, "openFile", return_value=Path("terrain.jpg")):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(cv2, "imread", return_value=np.array([[0, 0], [0, 0]])):
                with mock.patch.object(cv2, "resize", return_value=np.ones((1440, 360))):
                    with mock.patch.object(cv2, "flip", return_value=np.ones((360, 1440))):
                        function.loadTerrainImage(Path("terrain.jpg"))


def test_selectTerrainFile_1(function):
    with mock.patch.object(function, "openFile", return_value=(Path(""))):
        with mock.patch.object(Path, "is_file", return_value=False):
            function.selectTerrainFile()


def test_selectTerrainFile_2(function):
    with mock.patch.object(function, "openFile", return_value=Path("terrain.jpg")):
        with mock.patch.object(function.parent, "redrawAll"):
            with mock.patch.object(Path, "is_file", return_value=True):
                with mock.patch.object(function, "loadTerrainImage"):
                    function.selectTerrainFile()


def test_clearTerrainFile(function):
    with mock.patch.object(function.parent, "redrawAll"):
        function.clearTerrainFile()


def test_loadHorizonMask_1(function):
    with mock.patch.object(function, "openFile", return_value=Path("test.test")):
        with mock.patch.object(Path, "is_file", return_value=False):
            function.loadHorizonMask()


def test_loadHorizonMask_2(function):
    with mock.patch.object(function, "openFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "loadHorizonP", return_value=False):
            with mock.patch.object(Path, "is_file", return_value=True):
                with mock.patch.object(function, "drawTab"):
                    function.loadHorizonMask()


def test_loadHorizonMask_3(function):
    with mock.patch.object(function, "openFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "loadHorizonP", return_value=True):
            with mock.patch.object(Path, "is_file", return_value=True):
                with mock.patch.object(function, "drawTab"):
                    function.loadHorizonMask()


def test_saveHorizonMask_1(function):
    function.ui.horizonMaskFileName.setText("test")
    with mock.patch.object(function, "openFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "saveHorizonP", return_value=True):
            function.saveHorizonMask()


def test_saveHorizonMaskFile_2(function):
    function.ui.horizonMaskFileName.setText("")
    function.saveHorizonMask()


def test_saveHorizonMaskFile_3(function):
    function.ui.horizonMaskFileName.setText("test")
    with mock.patch.object(function, "saveFile", return_value=("build", "test", "bpts")):
        with mock.patch.object(function.app.data, "saveHorizonP", return_value=False):
            function.saveHorizonMask()


def test_saveHorizonMaskFileAs_1(function):
    with mock.patch.object(function, "saveFile", return_value=("build", "test", "bpts")):
        with mock.patch.object(function.app.data, "saveHorizonP", return_value=True):
            function.saveHorizonMaskAs()


def test_saveHorizonMaskFileAs_2(function):
    with mock.patch.object(function, "saveFile", return_value=("", "", "")):
        function.saveHorizonMaskAs()


def test_saveHorizonMaskFileAs_3(function):
    with mock.patch.object(function, "saveFile", return_value=("build", "test", "bpts")):
        with mock.patch.object(function.app.data, "saveHorizonP", return_value=False):
            function.saveHorizonMaskAs()


def test_setOperationMode_1(function):
    function.ui.editModeHor.setChecked(True)
    with mock.patch.object(function, "drawTab"):
        function.setOperationMode()


def test_updateDataHorizon(function):
    function.horizonPlot = pg.PlotDataItem()
    with mock.patch.object(function, "drawTab"):
        function.updateDataHorizon([1, 2], [1, 2])


def test_clearHorizonMask(function):
    with mock.patch.object(function.parent, "redrawAll"):
        function.clearHorizonMask()


def test_addActualPosition_1(function):
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = None
    function.addActualPosition()


def test_addActualPosition_2(function):
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=20)
    with mock.patch.object(CustomViewBox, "getNearestPointIndex", return_value=1):
        with mock.patch.object(CustomViewBox, "addUpdate"):
            function.addActualPosition()


def test_prepareView(function):
    with mock.patch.object(function.parent, "preparePlotItem"):
        function.prepareView()


def test_drawView_1(function):
    function.horizonPlot = pg.PlotDataItem()
    function.drawView()


def test_drawView_2(function):
    function.app.data.horizonP = [(1, 1), (2, 2)]
    function.horizonPlot = pg.PlotDataItem(x=[1], y=[1])
    function.drawView()


def test_setupPointer(function):
    function.setupPointer()


def test_drawPointer_1(function):
    function.pointerHor = None
    function.drawPointer()


def test_drawPointer_2(function):
    function.pointerHor = pg.ScatterPlotItem()
    function.app.mount.obsSite.Alt = None
    function.drawPointer()


def test_drawPointer_3(function):
    function.pointerHor = pg.ScatterPlotItem()
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=20)
    function.drawPointer()


def test_setupView_1(function):
    function.ui.editModeHor.setChecked(True)
    function.setupView()


def test_setupView_2(function):
    function.ui.editModeHor.setChecked(False)
    function.setupView()


def test_drawTab_1(function):
    function.ui.showTerrain.setChecked(True)
    function.ui.editModeHor.setChecked(True)
    with mock.patch.object(function, "prepareView"):
        with mock.patch.object(function, "drawTerrainImage"):
            with mock.patch.object(function, "setupView"):
                with mock.patch.object(function, "drawView"):
                    with mock.patch.object(function, "setupPointer"):
                        with mock.patch.object(function, "drawPointer"):
                            function.drawTab()
