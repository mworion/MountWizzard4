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
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import os

# external packages
import pyqtgraph as pg
from skyfield.api import Angle

# local import
from gui.extWindows.hemisphereW import HemisphereWindow
from tests.unit_tests.unitTestAddOns.baseTestSetupMixins import App


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):
    window = HemisphereWindow(app=App())
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    function.app.config['mainW'] = {}
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        suc = function.mwSuper('initConfig')
        assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_mouseMovedHorizon_1(function):
    with mock.patch.object(function,
                           'mouseMoved'):
        suc = function.mouseMovedHorizon('test')
        assert suc


def test_setIcons(function):
    suc = function.setIcons()
    assert suc


def test_colorChange(function):
    suc = function.colorChangeHorizon()
    assert suc


def test_loadHorizonMaskFile_1(function, qtbot):
    class Test:
        @staticmethod
        def drawHemisphere():
            return

    function.app.uiWindows = {'showHemisphereW': {'classObj': Test()}}
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadHorizonP',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.loadHorizonMask()
                assert suc
            assert ['Horizon mask [test] loaded', 0] == blocker.args


def test_loadHorizonMaskFile_2(function, qtbot):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('', '', '')):
        suc = function.loadHorizonMask()
        assert not suc


def test_loadHorizonMaskFile_3(function, qtbot):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadHorizonP',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.loadHorizonMask()
                assert suc
            assert ['Horizon mask [test] cannot no be loaded', 2] == blocker.args


def test_saveHorizonMaskFile_1(function, qtbot):
    function.ui.horizonMaskFileName.setText('test')
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveHorizonMask()
                assert suc
            assert ['Horizon mask [test] saved', 0] == blocker.args


def test_saveHorizonMaskFile_2(function, qtbot):
    function.ui.horizonMaskFileName.setText('')
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.saveHorizonMask()
        assert not suc
    assert ['Horizon mask file name not given', 2] == blocker.args


def test_saveHorizonMaskFile_3(function, qtbot):
    function.ui.horizonMaskFileName.setText('test')
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveHorizonMask()
                assert suc
            assert ['Horizon mask [test] cannot no be saved', 2] == blocker.args


def test_saveHorizonMaskFileAs_1(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveHorizonMaskAs()
                assert suc
            assert ['Horizon mask [test] saved', 0] == blocker.args


def test_saveHorizonMaskFileAs_2(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('', '', '')):
        suc = function.saveHorizonMaskAs()
        assert not suc


def test_saveHorizonMaskFileAs_3(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveHorizonMaskAs()
                assert suc
            assert ['Horizon mask [test] cannot no be saved', 2] == blocker.args


def test_setOperationModeHor_1(function):
    function.ui.editModeHor.setChecked(True)
    suc = function.setOperationModeHor()
    assert suc


def test_setOperationModeHor_2(function):
    function.ui.editModeHor.setChecked(False)
    suc = function.setOperationModeHor()
    assert suc


def test_updateDataHorizon(function):
    function.horizonPlot = pg.PlotDataItem()
    suc = function.updateDataHorizon([1, 2], [1, 2])
    assert suc


def test_clearHorizonMask(function):
    suc = function.clearHorizonMask()
    assert suc


def test_addActualPosition_1(function):
    suc = function.addActualPosition()
    assert not suc


def test_addActualPosition_2(function):
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=20)
    pd = pg.PlotDataItem(x=[10, 11], y=[10, 100], symbol='o')
    vb = function.ui.horizon.p[0].getViewBox()
    vb.plotDataItem = pd
    suc = function.addActualPosition()
    assert suc


def test_prepareHorizonView(function):
    with mock.patch.object(function,
                           'preparePlotItem'):
        suc = function.prepareHorizonView()
        assert suc


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
    suc = function.prepareHorizonView()
    assert suc


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
    suc = function.setupHorizonView()
    assert suc


def test_setupHorizonView_2(function):
    function.ui.editModeHor.setChecked(False)
    suc = function.setupHorizonView()
    assert suc


def test_drawHorizonTab_1(function):
    function.ui.showTerrain.setChecked(True)
    function.ui.editModeHor.setChecked(True)
    suc = function.drawHorizonTab()
    assert suc


def test_drawHorizonTab_2(function):
    function.ui.showTerrain.setChecked(False)
    function.ui.editModeHor.setChecked(False)
    suc = function.drawHorizonTab()
    assert suc