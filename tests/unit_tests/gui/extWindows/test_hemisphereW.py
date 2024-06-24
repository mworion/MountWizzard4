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
import os
import shutil

# external packages
from PySide6.QtCore import QPointF
from PySide6.QtGui import QCloseEvent
from skyfield.api import Angle, wgs84
import numpy as np
import pyqtgraph as pg

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.utilities.slewInterface import SlewInterface
from gui.extWindows.hemisphereW import HemisphereWindow


@pytest.fixture(scope='module')
def function(qapp):

    func = HemisphereWindow(app=App())
    yield func


def test_initConfig_1(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        with mock.patch.object(function,
                               'mwSuper'):
            suc = function.initConfig()
            assert suc


def test_initConfig_2(function):
    function.app.config['hemisphereW']['winPosX'] = 10000
    function.app.config['hemisphereW']['winPosY'] = 10000
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        with mock.patch.object(function,
                               'mwSuper'):
            suc = function.initConfig()
            assert suc


def test_initConfig_3(function):
    function.app.config['hemisphereW'] = {}
    function.app.config['hemisphereW']['winPosX'] = 100
    function.app.config['hemisphereW']['winPosY'] = 100
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        with mock.patch.object(function,
                               'mwSuper'):
            suc = function.initConfig()
            assert suc


def test_initConfig_4(function):
    shutil.copy('tests/testData/terrain.jpg', 'tests/workDir/config/terrain.jpg')
    function.app.config['hemisphereW'] = {}
    function.app.config['hemisphereW']['winPosX'] = 100
    function.app.config['hemisphereW']['winPosY'] = 100
    with mock.patch.object(function,
                           'mwSuper'):
        suc = function.initConfig()
        assert suc


def test_storeConfig_1(function):
    function.app.config = {}
    with mock.patch.object(function,
                           'mwSuper'):
        suc = function.storeConfig()
        assert suc


def test_enableTabsMovable(function):
    suc = function.enableTabsMovable(True)
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'drawHemisphereTab'):
        with mock.patch.object(function,
                               'show'):
            with mock.patch.object(MWidget,
                                   'closeEvent'):
                function.showWindow()
                function.closeEvent(QCloseEvent)


def test_showWindow_1(function):
    with mock.patch.object(function,
                           'drawHemisphereTab'):
        with mock.patch.object(function,
                               'show'):
            suc = function.showWindow()
            assert suc


def test_mouseMoved_1(function):
    pd = pg.PlotItem(x=[0, 1], y=[0, 1])
    suc = function.mouseMoved(pd, pos=QPointF(1, 1))
    assert suc


def test_mouseMoved_2(function):
    pd = pg.PlotItem()
    suc = function.mouseMoved(pd, pos=QPointF(0.5, 0.5))
    assert suc


def test_mouseMovedHemisphere(function):
    suc = function.mouseMovedHemisphere(pos=QPointF(1, 1))
    assert suc


def test_colorChange(function):
    with mock.patch.object(function,
                           'drawHemisphereTab'):
        suc = function.colorChange()
        assert suc


def test_enableOperationModeChange_1(function):
    suc = function.enableOperationModeChange(True)
    assert suc


def test_setOperationModeHem_1(function):
    function.ui.editModeHem.setChecked(True)
    with mock.patch.object(function,
                           'drawModelPoints'):
        with mock.patch.object(function,
                               'drawHemisphereTab'):
            suc = function.setOperationModeHem()
            assert suc


def test_setOperationModeHem_2(function):
    function.ui.alignmentModeHem.setChecked(True)
    with mock.patch.object(function,
                           'drawModelPoints'):
        with mock.patch.object(function,
                               'drawHemisphereTab'):
            suc = function.setOperationModeHem()
            assert suc


def test_calculateRelevance_1(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=0,
                                                       latitude_degrees=45)
    val = function.calculateRelevance(40, 180)
    assert round(val, 3) == 0.845


def test_calculateRelevance_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=0,
                                                       latitude_degrees=45)
    val = function.calculateRelevance(0, 0)
    assert val == 0


def test_calculateRelevance_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=0,
                                                       latitude_degrees=45)
    val = function.calculateRelevance(30, 180)
    assert val > 0


def test_calculateRelevance_4(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=0,
                                                       latitude_degrees=45)
    val = function.calculateRelevance(40, 10)
    assert val == 0


def test_calculateRelevance_5(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=0,
                                                       latitude_degrees=-45)
    val = function.calculateRelevance(40, 10)
    assert val > 0


def test_selectFontParam_1(function):
    function.colorSet = 0
    col, size = function.selectFontParam(0)
    assert size == 8


def test_selectFontParam_2(function):
    function.colorSet = 0
    col, size = function.selectFontParam(1)
    assert size == 13


def test_updateOnChangedParams_1(function):
    class Test:
        meridianLimitSlew = 0
        meridianLimitTrack = 0
        horizonLimitHigh = 0
        horizonLimitLow = 0

    with mock.patch.object(function,
                           'drawHemisphereTab'):
        suc = function.updateOnChangedParams(Test())
        assert suc


def test_updateOnChangedParams_2(function):
    class Test:
        meridianLimitSlew = 0
        meridianLimitTrack = 0
        horizonLimitHigh = 0
        horizonLimitLow = 0

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0

    with mock.patch.object(function,
                           'drawHemisphereTab'):
        suc = function.updateOnChangedParams(Test())
        assert not suc


def test_preparePlotItem(function):
    pd = pg.PlotItem()
    suc = function.preparePlotItem(pd)
    assert suc


def test_preparePolarItem_1(function):
    pd = pg.PlotItem()
    function.ui.showPolar.setChecked(False)
    suc = function.preparePolarItem(pd)
    assert not suc


def test_preparePolarItem_2(function):
    pd = pg.PlotItem()
    function.ui.showPolar.setChecked(True)
    suc = function.preparePolarItem(pd)
    assert suc


def test_prepareHemisphere(function):
    suc = function.prepareHemisphere()
    assert suc


def test_drawCelestialEquator_1(function):
    with mock.patch.object(function.app.data,
                           'generateCelestialEquator',
                           return_value=None):
        suc = function.drawCelestialEquator()
        assert not suc


def test_drawCelestialEquator_2(function):
    with mock.patch.object(function.app.data,
                           'generateCelestialEquator',
                           return_value=[(1, 1)]):
        suc = function.drawCelestialEquator()
        assert suc


def test_drawHorizonOnHem(function):
    suc = function.drawHorizonOnHem()
    assert suc


def test_drawTerrainMask_1(function):
    pd = pg.PlotItem()
    function.imageTerrain = None
    suc = function.drawTerrainMask(pd)
    assert not suc


def test_drawTerrainMask_2(function):
    pd = pg.PlotItem()
    function.imageTerrain = np.ones((100, 100), dtype=np.uint8)
    suc = function.drawTerrainMask(pd)
    assert suc


def test_drawMeridianLimits_1(function):
    function.app.mount.setting.meridianLimitSlew = None
    function.app.mount.setting.meridianLimitTrack = None
    suc = function.drawMeridianLimits()
    assert not suc


def test_drawMeridianLimits2(function):
    function.app.mount.setting.meridianLimitSlew = 10
    function.app.mount.setting.meridianLimitTrack = 10
    suc = function.drawMeridianLimits()
    assert suc


def test_staticHorizonLimits_1(function):
    function.app.mount.setting.horizonLimitHigh = None
    function.app.mount.setting.horizonLimitLow = None
    suc = function.drawHorizonLimits()
    assert suc


def test_staticHorizonLimits_2(function):
    function.app.mount.setting.horizonLimitHigh = 90
    function.app.mount.setting.horizonLimitLow = 10
    suc = function.drawHorizonLimits()
    assert suc


def test_setupAlignmentStars(function):
    function.app.data.hip = ['test']
    suc = function.setupAlignmentStars()
    assert suc


def test_drawAlignmentStars_1(function):
    function.ui.showAlignStar.setChecked(False)
    suc = function.drawAlignmentStars()
    assert not suc


def test_drawAlignmentStars_2(function):
    function.ui.showAlignStar.setChecked(True)
    function.alignmentStars = None
    suc = function.drawAlignmentStars()
    assert not suc


def test_drawAlignmentStars_3(function):
    function.alignmentStarsText = []
    function.alignmentStarsText.append(pg.TextItem())
    function.ui.showAlignStar.setChecked(True)
    function.alignmentStars = pg.ScatterPlotItem()
    suc = function.drawAlignmentStars()
    assert suc


def test_drawAlignmentStars_4(function):
    function.alignmentStarsText = []
    function.alignmentStarsText.append(pg.TextItem())
    function.ui.showAlignStar.setChecked(True)
    function.ui.alignmentModeHem.setChecked(True)
    function.alignmentStars = pg.ScatterPlotItem()
    suc = function.drawAlignmentStars()
    assert suc


def test_drawModelPoints_1(function):
    function.modelPoints = None
    suc = function.drawModelPoints()
    assert not suc


def test_drawModelPoints_2(function):
    function.modelPoints = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol='o')
    function.app.data.buildP = [(1, 1, True), (2, 2, False)]
    suc = function.drawModelPoints()
    assert suc


def test_drawModelText_1(function):
    function.app.data.buildP = None
    suc = function.drawModelText()
    assert not suc


def test_drawModelText_2(function):
    function.modelPoints = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol='o')
    function.app.data.buildP = [(1, 1, True), (2, 2, False)]
    function.ui.editModeHem.setChecked(True)
    function.modelPointsText.append(pg.TextItem())
    suc = function.drawModelText()
    assert suc


def test_drawModelText_3(function):
    function.modelPoints = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol='o')
    function.app.data.buildP = [(1, 1, True), (2, 2, False)]
    function.ui.editModeHem.setChecked(False)
    suc = function.drawModelText()
    assert suc


def test_updateDataModel(function):
    with mock.patch.object(function,
                           'drawModelPoints'):
        with mock.patch.object(function,
                               'drawModelText'):
            suc = function.updateDataModel([1, 2], [1, 2])
            assert suc


def test_setupModel_1(function):
    function.ui.showSlewPath.setChecked(True)
    function.ui.editModeHem.setChecked(True)
    with mock.patch.object(function,
                           'drawModelPoints'):
        with mock.patch.object(function,
                               'drawModelText'):
            suc = function.setupModel()
            assert suc


def test_setupModel_2(function):
    function.ui.showSlewPath.setChecked(False)
    function.ui.editModeHem.setChecked(False)
    with mock.patch.object(function,
                           'drawModelPoints'):
        with mock.patch.object(function,
                               'drawModelText'):
            suc = function.setupModel()
            assert suc


def test_setupPointerHem(function):
    suc = function.setupPointerHem()
    assert suc


def test_drawPointerHem_1(function):
    function.app.mount.obsSite.Az = None
    function.app.mount.obsSite.Alt = None
    function.setupPointerHem()
    suc = function.drawPointerHem()
    assert not suc


def test_drawPointerHem_2(function):
    function.app.mount.obsSite.Az = Angle(degrees=10)
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.setupPointerHem()
    suc = function.drawPointerHem()
    assert suc


def test_setupDome(function):
    suc = function.setupDome()
    assert suc


def test_drawDome_1(function):
    function.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
    suc = function.drawDome('test')
    assert not suc


def test_drawDome_2(function):
    function.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
    suc = function.drawDome(azimuth=100)
    assert suc


def test_getMountModelData_1(function):
    val = function.getMountModelData()
    assert val[0] is None
    assert val[1] is None
    assert val[2] is None


def test_getMountModelData_2(function):
    class Star:
        alt = Angle(degrees=10)
        az = Angle(degrees=20)
        errorRMS = 5

    function.app.mount.model.starList = [Star()]
    val = function.getMountModelData()
    assert val[0][0] == 20
    assert val[1][0] == 10
    assert val[2][0] == 5


def test_drawModelIsoCurve_1(function):
    with mock.patch.object(function,
                           'getMountModelData',
                           return_value=(None, None, None)):
        suc = function.drawModelIsoCurve()
        assert not suc


def test_drawModelIsoCurve_2(function):
    val = np.array([1])
    data = (val, val, val)
    with mock.patch.object(function,
                           'getMountModelData',
                           return_value=data):
        with mock.patch.object(function.ui.hemisphere,
                               'addIsoItem',
                               return_value=True):
            suc = function.drawModelIsoCurve()
            assert suc


def test_drawHemisphereTab_1(function):
    function.ui.showIsoModel.setChecked(True)
    function.ui.showCelestial.setChecked(True)
    function.ui.showTerrain.setChecked(True)
    function.ui.showMountLimits.setChecked(True)
    function.ui.showHorizon.setChecked(True)
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function,
                           'drawCelestialEquator'):
        with mock.patch.object(function,
                               'drawTerrainMask'):
            with mock.patch.object(function,
                                   'drawMeridianLimits'):
                with mock.patch.object(function,
                                       'drawHorizonLimits'):
                    with mock.patch.object(function,
                                           'drawModelIsoCurve'):
                        with mock.patch.object(function,
                                               'drawHorizonOnHem'):
                            suc = function.drawHemisphereTab()
                            assert suc


def test_slewDirect_1(function):
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.slewDirect(QPointF(1, 1))
        assert not suc


def test_slewDirect_2(function):
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(SlewInterface,
                               'slewTargetAltAz',
                               return_value=False):
            suc = function.slewDirect(QPointF(1, 1))
            assert not suc


def test_slewDirect_3(function):
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(SlewInterface,
                               'slewTargetAltAz',
                               return_value=True):
            suc = function.slewDirect(QPointF(1, 1))
            assert suc


def test_slewStar_1(function):
    function.alignmentStars = pg.ScatterPlotItem()
    with mock.patch.object(function.alignmentStars,
                           'pointsAt',
                           return_value=[]):
        suc = function.slewStar(QPointF(1, 1))
        assert not suc


def test_slewStar_3(function):
    class Spot:
        @staticmethod
        def index():
            return 0

    function.app.hipparcos.name = ['test']
    function.app.mount.model.numberStars = 5
    function.alignmentStars = pg.ScatterPlotItem(x=[0, 1, 2], y=[0, 1, 2])
    with mock.patch.object(function.alignmentStars,
                           'pointsAt',
                           return_value=[Spot()]):
        with mock.patch.object(function,
                               'messageDialog',
                               return_value=0):
            with mock.patch.object(function.app.hipparcos,
                                   'getAlignStarRaDecFromName',
                                   return_value=(0, 0)):
                suc = function.slewStar(QPointF(1, 1))
                assert not suc


def test_slewStar_4(function):
    class Spot:
        @staticmethod
        def index():
            return 0

    function.app.hipparcos.name = ['test']
    function.app.mount.model.numberStars = 5
    function.alignmentStars = pg.ScatterPlotItem(x=[0, 1, 2], y=[0, 1, 2])
    with mock.patch.object(function.alignmentStars,
                           'pointsAt',
                           return_value=[Spot()]):
        with mock.patch.object(function,
                               'messageDialog',
                               return_value=1):
            with mock.patch.object(function.app.hipparcos,
                                   'getAlignStarRaDecFromName',
                                   return_value=(0, 0)):
                with mock.patch.object(SlewInterface,
                                       'slewTargetRaDec',
                                       return_value=False):
                    suc = function.slewStar(QPointF(1, 1))
                    assert not suc


def test_slewStar_5(function):
    class Spot:
        @staticmethod
        def index():
            return 0

    function.app.hipparcos.name = ['test']
    function.app.mount.model.numberStars = 5
    function.alignmentStars = pg.ScatterPlotItem(x=[0, 1, 2], y=[0, 1, 2])
    with mock.patch.object(function.alignmentStars,
                           'pointsAt',
                           return_value=[Spot()]):
        with mock.patch.object(function,
                               'messageDialog',
                               return_value=2):
            with mock.patch.object(function.app.hipparcos,
                                   'getAlignStarRaDecFromName',
                                   return_value=(0, 0)):
                with mock.patch.object(SlewInterface,
                                       'slewTargetRaDec',
                                       return_value=True):
                    suc = function.slewStar(QPointF(1, 1))
                    assert suc


def test_mouseDoubleClick_1(function):
    function.ui.alignmentModeHem.setChecked(True)
    function.ui.normalModeHem.setChecked(False)
    with mock.patch.object(function,
                           'slewStar'):
        suc = function.mouseDoubleClick(1, 2)
        assert suc


def test_mouseDoubleClick_2(function):
    function.ui.alignmentModeHem.setChecked(False)
    function.ui.normalModeHem.setChecked(True)
    with mock.patch.object(function,
                           'slewDirect'):
        suc = function.mouseDoubleClick(1, 2)
        assert suc
