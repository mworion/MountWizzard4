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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import shutil

# external packages
import pyqtgraph as pg
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.hemisphereW import HemisphereWindow
from gui.utilities.tools4pyqtgraph import CustomViewBox


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    shutil.copy('tests/testData/terrain.jpg', 'tests/workDir/config/terrain.jpg')
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):
    window = HemisphereWindow(app=App())
    yield window


def test_mouseMovedHorizon_1(function):
    with mock.patch.object(function,
                           'mouseMoved'):
        suc = function.mouseMovedHorizon('test')
        assert suc


def test_setIcons(function):
    function.setIcons()


def test_colorChangeHorizon(function):
    function.colorChangeHorizon()


def test_setTerrainFile_1(function):
    suc = function.setTerrainFile('test')
    assert not suc
    assert function.imageTerrain is None


def test_setTerrainFile_2(function):
    suc = function.setTerrainFile('terrain')
    assert suc
    assert function.imageTerrain is not None


def test_loadTerrainFile_1(function):
    class Test:
        @staticmethod
        def drawHemisphere():
            return

    function.app.uiWindows = {'showHemisphereW': {'classObj': Test()}}
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'jpg')):
        with mock.patch.object(function,
                               'setTerrainFile',
                               return_value=True):
            with mock.patch.object(function,
                                   'drawHorizonTab'):
                suc = function.loadTerrainFile()
                assert suc


def test_loadTerrainFile_2(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('', '', '')):
        suc = function.loadTerrainFile()
        assert not suc


def test_loadTerrainFile_3(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'jpg')):
        with mock.patch.object(function,
                               'setTerrainFile',
                               return_value=False):
            with mock.patch.object(function,
                                   'drawHorizonTab'):
                suc = function.loadTerrainFile()
                assert suc


def test_clearTerrainFile(function):
    with mock.patch.object(function,
                           'setTerrainFile'):
        with mock.patch.object(function,
                               'drawHorizonTab'):
            function.clearTerrainFile()


def test_loadHorizonMask_1(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('', '', '')):
        suc = function.loadHorizonMask()
        assert not suc


def test_loadHorizonMask_2(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadHorizonP',
                               return_value=False):
            with mock.patch.object(function,
                                   'drawHorizonTab'):
                suc = function.loadHorizonMask()
                assert suc


def test_loadHorizonMaskFile_3(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadHorizonP',
                               return_value=True):
            with mock.patch.object(function,
                                   'drawHorizonTab'):
                suc = function.loadHorizonMask()
                assert suc


def test_saveHorizonMask_1(function):
    function.ui.horizonMaskFileName.setText('test')
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=True):
            suc = function.saveHorizonMask()
            assert suc


def test_saveHorizonMaskFile_2(function):
    function.ui.horizonMaskFileName.setText('')
    suc = function.saveHorizonMask()
    assert not suc


def test_saveHorizonMaskFile_3(function):
    function.ui.horizonMaskFileName.setText('test')
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=False):
            suc = function.saveHorizonMask()
            assert suc


def test_saveHorizonMaskFileAs_1(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=True):
            suc = function.saveHorizonMaskAs()
            assert suc


def test_saveHorizonMaskFileAs_2(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('', '', '')):
        suc = function.saveHorizonMaskAs()
        assert not suc


def test_saveHorizonMaskFileAs_3(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=False):
            suc = function.saveHorizonMaskAs()
            assert suc


def test_setOperationModeHor_1(function):
    function.ui.editModeHor.setChecked(True)
    function.setOperationModeHor()


def test_setOperationModeHor_2(function):
    function.ui.editModeHor.setChecked(False)
    function.setOperationModeHor()


def test_updateDataHorizon(function):
    function.horizonPlot = pg.PlotDataItem()
    function.updateDataHorizon([1, 2], [1, 2])


def test_clearHorizonMask(function):
    function.clearHorizonMask()


def test_addActualPosition_1(function):
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = None
    suc = function.addActualPosition()
    assert not suc


def test_addActualPosition_2(function):
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=20)
    with mock.patch.object(CustomViewBox,
                           'getNearestPointIndex',
                           return_value=1):
        with mock.patch.object(CustomViewBox,
                               'addUpdate'):
            suc = function.addActualPosition()
            assert suc


def test_prepareHorizonView(function):
    with mock.patch.object(function,
                           'preparePlotItem'):
        function.prepareHorizonView()


def test_drawHorizonView_1(function):
    function.horizonPlot = pg.PlotDataItem()
    suc = function.drawHorizonView()
    assert not suc


def test_drawHorizonView_2(function):
    function.app.data.horizonP = [(1, 1), (2, 2)]
    function.horizonPlot = pg.PlotDataItem(x=[1], y=[1])
    suc = function.drawHorizonView()
    assert suc


def test_setupPointerHor(function):
    function.prepareHorizonView()


def test_drawPointerHor_1(function):
    function.pointerHor = None
    suc = function.drawPointerHor()
    assert not suc


def test_drawPointerHor_2(function):
    function.pointerHor = pg.ScatterPlotItem()
    function.app.mount.obsSite.Alt = None
    suc = function.drawPointerHor()
    assert not suc


def test_drawPointerHor_3(function):
    function.pointerHor = pg.ScatterPlotItem()
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=20)
    suc = function.drawPointerHor()
    assert suc


def test_setupHorizonView_1(function):
    function.ui.editModeHor.setChecked(True)
    function.setupHorizonView()


def test_setupHorizonView_2(function):
    function.ui.editModeHor.setChecked(False)
    function.setupHorizonView()


def test_drawHorizonTab_1(function):
    function.ui.showTerrain.setChecked(True)
    function.ui.editModeHor.setChecked(True)
    function.drawHorizonTab()


def test_drawHorizonTab_2(function):
    function.ui.showTerrain.setChecked(False)
    function.ui.editModeHor.setChecked(False)
    function.drawHorizonTab()
