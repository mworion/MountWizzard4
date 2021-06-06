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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import os
import shutil

# external packages
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QCloseEvent
import matplotlib.patches as mpatches
from skyfield.api import Angle
from PIL import Image

# local import
from tests.baseTestSetupExtWindows import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.hemisphereW import HemisphereWindow


@pytest.fixture(scope='module')
def module(qapp):
    yield


@pytest.fixture(scope='function')
def function(module):

    window = HemisphereWindow(app=App())
    yield window
    del window


def test_initConfig_1(function):
    suc = function.initConfig()
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        suc = function.initConfig()
        assert not suc


def test_initConfig_3(function):
    function.app.config['hemisphereW']['winPosX'] = 10000
    function.app.config['hemisphereW']['winPosY'] = 10000
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        suc = function.initConfig()
        assert not suc


def test_initConfig_4(function):
    function.app.config['hemisphereW'] = {}
    function.app.config['hemisphereW']['winPosX'] = 100
    function.app.config['hemisphereW']['winPosY'] = 100
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        suc = function.initConfig()
        assert not suc


def test_initConfig_5(function):
    shutil.copy('tests/testData/terrain.jpg', 'tests/config/terrain.jpg')
    function.app.config['hemisphereW'] = {}
    function.app.config['hemisphereW']['winPosX'] = 100
    function.app.config['hemisphereW']['winPosY'] = 100
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    function.app.config = {}
    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'drawHemisphere'):
        with mock.patch.object(function,
                               'show'):
            with mock.patch.object(MWidget,
                                   'closeEvent'):
                function.showWindow()
                function.closeEvent(QCloseEvent)


def test_resizeEvent_1(function):
    function.ui.showPolar.setChecked(True)
    with mock.patch.object(MWidget,
                           'resizeEvent'):
        function.resizeEvent(QEvent)


def test_showWindow_1(function):
    with mock.patch.object(function,
                           'drawHemisphere'):
        with mock.patch.object(function,
                               'show'):
            suc = function.showWindow()
            assert suc


def test_togglePolar_1(function):
    suc = function.togglePolar()
    assert suc


def test_togglePolar_2(function):
    function.ui.showPolar.setChecked(True)
    suc = function.togglePolar()
    assert suc


def test_updateOnChangedParams_1(function):
    class Test:
        meridianLimitSlew = 0
        meridianLimitTrack = 0
        horizonLimitHigh = 0
        horizonLimitLow = 0

    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.updateOnChangedParams(Test())
        assert suc


def test_updateOnChangedParams_2(function):
    class Test:
        meridianLimitSlew = 0
        meridianLimitTrack = 0
        horizonLimitHigh = 0
        horizonLimitLow = 0

    function.meridianSlewParam = 0
    function.meridianTrackParam = 0
    function.horizonLimitHighParam = 0
    function.horizonLimitLowParam = 0

    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.updateOnChangedParams(Test())
        assert not suc


def test_updatePointerAltAz_1(function):
    function.pointerAltAz = None
    suc = function.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerAltAz, = axe.plot(0, 0)
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = None
    suc = function.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_3(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerAltAz, = axe.plot(0, 0)
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = Angle(degrees=80)
    suc = function.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_4(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerAltAz, = axe.plot(0, 0)
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = Angle(degrees=80)
    suc = function.updatePointerAltAz()
    assert suc


def test_updatePointerPolarAltAz_1(function):
    function.pointerPolarAltAz = None
    suc = function.updatePointerPolarAltAz()
    assert not suc


def test_updatePointerPolarAltAz_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerPolarAltAz, = axe.plot(0, 0)
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = None
    suc = function.updatePointerPolarAltAz()
    assert not suc


def test_updatePointerPolarAltAz_3(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerPolarAltAz, = axe.plot(0, 0)
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = Angle(degrees=80)
    suc = function.updatePointerPolarAltAz()
    assert not suc


def test_updatePointerPolarAltAz_4(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerPolarAltAz, = axe.plot(0, 0)
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = Angle(degrees=80)
    suc = function.updatePointerPolarAltAz()
    assert suc


def test_updateDome_1(function):
    suc = function.updateDome(0)
    assert not suc


def test_updateDome_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerDome, = axe.plot(0, 0)
    suc = function.updateDome('test')
    assert not suc


def test_updateDome_3(function):
    function.pointerDome = mpatches.Rectangle((0, 5), 1, 5)
    function.app.deviceStat['dome'] = True
    suc = function.updateDome(0)
    assert suc


def test_getMarkerStatusParams_1(function):
    val = function.getMarkerStatusParams(True, 0)
    marker, markersize, color, text = val
    assert markersize == 9
    assert color == function.M_GREEN_H
    assert text == ' 1'


def test_getMarkerStatusParams_2(function):
    val = function.getMarkerStatusParams(False, 1)
    marker, markersize, color, text = val
    assert marker == '$\u2714$'
    assert markersize == 11
    assert color == function.M_YELLOW
    assert text == ' 2'


def test_updatePointMarker_1(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.pointsBuild = list()
    function.pointsBuildAnnotate = list()
    p, = axe.plot(0, 0)
    function.pointsBuild.append(p)
    function.pointsBuild.append(p)
    function.pointsBuildAnnotate.append(axe.annotate('test', (0, 0)))
    function.pointsBuildAnnotate.append(axe.annotate('test', (0, 0)))

    function.app.data.buildP = [(0, 0, True), (0, 360, False)]
    suc = function.updatePointMarker()
    assert suc


def test_updatePolarPointMarker_1(function):
    function.pointsPolarBuild = list()
    suc = function.updatePolarPointMarker()
    assert not suc


def test_updatePolarPointMarker_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.pointsPolarBuild = list()
    function.pointsPolarBuildAnnotate = list()
    p, = axe.plot(0, 0)
    function.pointsPolarBuild.append(p)
    function.pointsPolarBuild.append(p)
    function.pointsPolarBuildAnnotate.append(axe.annotate('test', (0, 0)))
    function.pointsPolarBuildAnnotate.append(axe.annotate('test', (0, 0)))

    function.app.data.buildP = [(0, 0, True), (0, 360, False)]
    suc = function.updatePolarPointMarker()
    assert suc


def test_updateAlignStar_1(function):
    function.ui.checkShowAlignStar.setChecked(False)
    suc = function.updateAlignStar()
    assert not suc


def test_updateAlignStar_2(function):
    function.ui.checkShowAlignStar.setChecked(True)
    suc = function.updateAlignStar()
    assert not suc


def test_updateAlignStar_3(function):
    function.ui.checkShowAlignStar.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.starsAlign, = axe.plot(0, 0)
    function.starsAlignAnnotate = None
    suc = function.updateAlignStar()
    assert not suc


def test_updateAlignStar_4(function):
    function.ui.checkShowAlignStar.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.starsAlign, = axe.plot(0, 0)
    function.starsAlignAnnotate = [axe.annotate('test', (0, 0))]
    function.app.hipparcos.alt = [1]
    function.app.hipparcos.az = [1]
    function.app.hipparcos.name = ['test']
    function.mutexDraw.lock()
    suc = function.updateAlignStar()
    assert not suc
    function.mutexDraw.unlock()


def test_updateAlignStar_5(function):
    function.ui.checkShowAlignStar.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.starsAlign, = axe.plot(0, 0)
    function.starsAlignAnnotate = [axe.annotate('test', (0, 0))]
    function.app.hipparcos.alt = [1]
    function.app.hipparcos.az = [1]
    function.app.hipparcos.name = ['test']

    suc = function.updateAlignStar()
    assert suc


def test_clearHemisphere(function):
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.clearHemisphere()
        assert suc


def test_staticHorizon_1(function):
    function.ui.checkUseHorizon.setChecked(False)
    function.app.data.horizonP = list()
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.staticHorizon(axe)
    assert not suc


def test_staticHorizon_2(function):
    function.ui.checkUseHorizon.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.data.horizonP = [(0, 0), (0, 360)]
    suc = function.staticHorizon(axe)
    assert suc


def test_staticHorizon_3(function):
    function.ui.checkUseHorizon.setChecked(False)
    function.app.data.horizonP = list()
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.staticHorizon(axe, polar=True)
    assert not suc


def test_staticHorizon_4(function):
    function.ui.checkUseHorizon.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.data.horizonP = [(0, 0), (0, 360)]
    suc = function.staticHorizon(axe, polar=True)
    assert suc


def test_staticModelData_1(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.data.buildP = list()
    suc = function.staticModelData(axe)
    assert not suc


def test_staticModelData_2(function):
    function.ui.checkShowSlewPath.setChecked(False)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.data.buildP = [(0, 0, True), (0, 360, True)]
    suc = function.staticModelData(axe)
    assert suc


def test_staticModelData_3(function):
    function.ui.checkShowSlewPath.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.data.buildP = [(0, 0, True), (0, 360, False)]
    suc = function.staticModelData(axe)
    assert suc


def test_staticModelData_4(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.data.buildP = list()
    suc = function.staticModelData(axe, polar=True)
    assert not suc


def test_staticModelData_5(function):
    function.ui.checkShowSlewPath.setChecked(False)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.data.buildP = [(0, 0, True), (0, 360, True)]
    suc = function.staticModelData(axe, polar=True)
    assert suc


def test_staticModelData_6(function):
    function.ui.checkShowSlewPath.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.data.buildP = [(0, 0, True), (0, 360, False)]
    suc = function.staticModelData(axe, polar=True)
    assert suc


def test_staticCelestialEquator_1(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.ui.checkShowCelestial.setChecked(True)
    suc = function.staticCelestialEquator(axe)
    assert suc


def test_staticCelestialEquator_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.ui.checkShowCelestial.setChecked(True)
    suc = function.staticCelestialEquator(axe, polar=True)
    assert suc


def test_staticCelestialEquator_3(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.ui.checkShowCelestial.setChecked(True)
    with mock.patch.object(function.app.data,
                           'generateCelestialEquator',
                           return_value=None):
        suc = function.staticCelestialEquator(axe, polar=True)
        assert not suc


def test_staticMeridianLimits_1(function):
    function.app.mount.setting.meridianLimitSlew = None
    function.app.mount.setting.meridianLimitTrack = None
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.staticMeridianLimits(axe)
    assert not suc


def test_staticMeridianLimits_2(function):
    function.app.mount.setting.meridianLimitSlew = 10
    function.app.mount.setting.meridianLimitTrack = 10
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.staticMeridianLimits(axe)
    assert suc


def test_staticHorizonLimits_1(function):
    function.app.mount.setting.horizonLimitHigh = None
    function.app.mount.setting.horizonLimitLow = None
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.staticHorizonLimits(axe)
    assert suc


def test_staticHorizonLimits_2(function):
    function.app.mount.setting.horizonLimitHigh = 10
    function.app.mount.setting.horizonLimitLow = 10
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.staticHorizonLimits(axe)
    assert suc


def test_staticTerrainMask_1(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.imageTerrain = None
    with mock.patch.object(axe,
                           'imshow'):
        suc = function.staticTerrainMask(axe)
        assert not suc


def test_staticTerrainMask_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    img = Image.open('tests/testData/terrain.jpg').convert('LA')
    (w, h) = img.size
    img = img.crop((0, 0, w, h / 2))
    img = img.resize((360, 90))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    function.imageTerrain = Image.new('L', (720, 90))
    function.imageTerrain.paste(img)
    function.imageTerrain.paste(img, (360, 0))
    with mock.patch.object(axe,
                           'imshow'):
        suc = function.staticTerrainMask(axe)
        assert suc


def test_staticTerrainMask_3(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    img = Image.open('tests/testData/terrain.jpg').convert('LA')
    (w, h) = img.size
    img = img.crop((0, 0, w, h / 2))
    img = img.resize((360, 90))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    function.imageTerrain = Image.new('L', (720, 90))
    function.imageTerrain.paste(img)
    function.imageTerrain.paste(img, (360, 0))
    with mock.patch.object(axe,
                           'pcolormesh'):
        suc = function.staticTerrainMask(axe, polar=True)
        assert suc


def test_drawHemisphereStatic_1(function):
    function.ui.checkUseHorizon.setChecked(True)
    function.ui.checkShowCelestial.setChecked(True)
    function.ui.checkShowMeridian.setChecked(True)
    function.ui.checkUseTerrain.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    with mock.patch.object(function,
                           'staticTerrainMask'):
        suc = function.drawHemisphereStatic(axe)
        assert suc


def test_drawHemisphereStatic_2(function):
    function.ui.checkUseHorizon.setChecked(True)
    function.ui.checkShowCelestial.setChecked(True)
    function.ui.checkShowMeridian.setChecked(True)
    function.ui.checkUseTerrain.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.drawHemisphereStatic(axe, polar=True)
    assert suc


def test_drawHemisphereMoving_1(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.drawHemisphereMoving(axe)
    assert suc


def test_drawAlignmentStars_1(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.hipparcos.alt = [1]
    function.app.hipparcos.az = [1]
    function.app.hipparcos.name = ['test']
    function.mutexDraw.lock()
    suc = function.drawAlignmentStars(axe)
    assert not suc
    function.mutexDraw.unlock()


def test_drawAlignmentStars_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.hipparcos.alt = [1]
    function.app.hipparcos.az = [1]
    function.app.hipparcos.name = ['test']

    suc = function.drawAlignmentStars(axe)
    assert suc


def test_drawHemisphere_1(function):
    function.closingWindow = False
    function.ui.checkShowAlignStar.setChecked(True)
    suc = function.drawHemisphere()
    assert suc


def test_drawHemisphere_2(function):
    function.closingWindow = False
    function.ui.checkShowAlignStar.setChecked(False)
    suc = function.drawHemisphere()
    assert suc


def test_drawHemisphere_3(function):
    function.closingWindow = True
    function.ui.checkShowAlignStar.setChecked(False)
    suc = function.drawHemisphere()
    assert not suc
