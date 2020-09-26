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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QCloseEvent
import matplotlib.patches as mpatches
from skyfield.api import Angle

# local import
from tests.baseTestSetupExtWindows import App
from gui.utilities.widget import MWidget
from gui.extWindows.hemisphereW import HemisphereWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = HemisphereWindow(app=App())
    yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_3(function):
    function.app.config['hemisphereW']['winPosX'] = 10000
    function.app.config['hemisphereW']['winPosY'] = 10000
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
    function.startup = False
    with mock.patch.object(MWidget,
                           'resizeEvent'):
        function.resizeEvent(QEvent)


def test_resizeEvent_2(function):
    function.startup = True
    with mock.patch.object(MWidget,
                           'resizeEvent'):
        function.resizeEvent(QEvent)


def test_resizeTimer_1(function):
    function.resizeTimerValue = 3
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.resizeTimer()
        assert suc


def test_resizeTimer_2(function):
    function.resizeTimerValue = 1
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.resizeTimer()
        assert suc


def test_showWindow_1(function):
    with mock.patch.object(function,
                           'drawHemisphere'):
        with mock.patch.object(function,
                               'show'):
            suc = function.showWindow()
            assert suc


def test_drawBlit_1(function):
    function.mutexDraw.lock()
    suc = function.drawBlit()
    assert not suc
    function.mutexDraw.unlock()


def test_drawBlit_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    axe.figure.canvas.blit(axe.bbox)
    function.hemisphereBackStars = axe.figure.canvas.copy_from_bbox(axe.bbox)
    function.pointerAltAz, = axe.plot(0, 0)
    function.pointerDome, = axe.plot(0, 0)
    axe.figure.canvas.draw()
    suc = function.drawBlit()
    assert suc


def test_drawBlit_3(function):
    function.hemisphereBack = None
    suc = function.drawBlit()
    assert suc


def test_drawBlitStars_1(function):
    function.mutexDraw.lock()
    suc = function.drawBlitStars()
    assert not suc
    function.mutexDraw.unlock()


def test_drawBlitStars_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    axe.figure.canvas.blit(axe.bbox)
    function.hemisphereBack = axe.figure.canvas.copy_from_bbox(axe.bbox)
    function.starsAlignAnnotate = [axe.annotate('test', (0, 0))]
    function.starsAlign, = axe.plot(0, 0)
    axe.figure.canvas.draw()
    suc = function.drawBlitStars()
    assert suc


def test_drawBlitStars_3(function):
    function.hemisphereBackStars = None
    suc = function.drawBlitStars()
    assert suc


def test_updateCelestialPath_1(function):
    suc = function.updateCelestialPath()
    assert not suc


def test_updateCelestialPath_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.celestialPath, = axe.plot(0, 0)
    suc = function.updateCelestialPath()
    assert suc


def test_updateMeridian_1(function):
    function.app.mount.setting.meridianLimitSlew = None
    function.app.mount.setting.meridianLimitTrack = 3
    suc = function.updateMeridian(function.app.mount.setting)
    assert not suc


def test_updateMeridian_2(function):
    function.app.mount.setting.meridianLimitSlew = 3
    function.app.mount.setting.meridianLimitTrack = None
    suc = function.updateMeridian(function.app.mount.setting)
    assert not suc


def test_updateMeridian_3(function):
    function.app.mount.setting.meridianLimitSlew = 3
    function.app.mount.setting.meridianLimitTrack = 3
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.meridianTrack, = axe.plot(0, 0)
    suc = function.updateMeridian(function.app.mount.setting)
    assert not suc


def test_updateMeridian_4(function):
    function.app.mount.setting.meridianLimitSlew = 3
    function.app.mount.setting.meridianLimitTrack = 3
    function.meridianTrack = mpatches.Rectangle((0, 5), 1, 5)
    function.meridianSlew = mpatches.Rectangle((0, 5), 1, 5)
    suc = function.updateMeridian(function.app.mount.setting)
    assert suc


def test_updateMeridian_5(function):
    function.app.mount.setting.meridianLimitSlew = 3
    function.app.mount.setting.meridianLimitTrack = 3
    function.meridianTrack = None
    suc = function.updateMeridian(function.app.mount.setting)
    assert not suc


def test_updateMeridian_6(function):
    function.app.mount.setting.meridianLimitSlew = 3
    function.app.mount.setting.meridianLimitTrack = 3
    function.meridianSlew = None
    suc = function.updateMeridian(function.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_1(function):
    function.app.mount.setting.horizonLimitHigh = None
    function.app.mount.setting.horizonLimitLow = 10
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_2(function):
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = None
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_3(function):
    function.drawHemisphere()
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 10
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert suc


def test_updateHorizonLimits_4(function):
    function.drawHemisphere()
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 10
    function.horizonLimitLow = mpatches.Rectangle((0, 5), 1, 5)
    function.horizonLimitHigh = mpatches.Rectangle((0, 5), 1, 5)
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert suc


def test_updateHorizonLimits_5(function):
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 10
    function.horizonLimitHigh = mpatches.Rectangle((0, 5), 1, 5)
    function.horizonLimitLow = None
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_6(function):
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 10
    function.horizonLimitLow = mpatches.Rectangle((0, 5), 1, 5)
    function.horizonLimitHigh = None
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert not suc


def test_updateSettings_1(function):
    with mock.patch.object(function,
                           'updateCelestialPath',
                           return_value=True):
        with mock.patch.object(function,
                               'updateHorizonLimits',
                               return_value=True):
            with mock.patch.object(function,
                                   'updateMeridian',
                                   return_value=True):
                with mock.patch.object(function,
                                       'drawHemisphere'):
                    suc = function.updateSettings()
                    assert suc


def test_updatePointerAltAz_1(function):
    suc = function.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_2(function):
    function.app.mount.obsSite.Alt = 80
    suc = function.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_3(function):
    function.app.mount.obsSite.Alt = 80
    function.app.mount.obsSite.Az = 80
    suc = function.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_4(function):
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = Angle(degrees=80)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.pointerAltAz, = axe.plot(0, 0)
    with mock.patch.object(function,
                           'drawBlit'):
        suc = function.updatePointerAltAz()
        assert suc


def test_updateDome_1(function):
    suc = function.updateDome(0)
    assert not suc


def test_updateDome_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.pointerDome, = axe.plot(0, 0)
    suc = function.updateDome('test')
    assert not suc


def test_updateDome_3(function):
    function.pointerDome = mpatches.Rectangle((0, 5), 1, 5)
    function.app.deviceStat['dome'] = True
    with mock.patch.object(function,
                           'drawBlit'):
        suc = function.updateDome(0)
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
    with mock.patch.object(function,
                           'drawBlitStars'):
        suc = function.updateAlignStar()
        assert suc


def test_clearHemisphere(function):
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.clearHemisphere()
        assert suc


def test_staticHorizon_1(function):
    function.ui.checkUseHorizon.setChecked(False)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.staticHorizon(axe)
    assert not suc


def test_staticHorizon_2(function):
    function.ui.checkUseHorizon.setChecked(True)
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.app.data.horizonP = [(0, 0), (0, 360)]
    suc = function.staticHorizon(axe)
    assert suc


def test_staticModelData_1(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
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


def test_staticCelestialEquator(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.ui.checkShowCelestial.setChecked(True)
    suc = function.staticCelestialEquator(axe)
    assert suc


def test_staticMeridianLimits_1(function):
    function.app.mount.setting.meridianLimitSlew = None
    function.app.mount.setting.meridianLimitTrack = None
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.staticMeridianLimits(axe)
    assert suc


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


def test_drawHemisphereStatic_1(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    function.mutexDraw.lock()
    suc = function.drawHemisphereStatic(axe)
    assert not suc
    function.mutexDraw.unlock()


def test_drawHemisphereStatic_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMat, horizon=False)
    suc = function.drawHemisphereStatic(axe)
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
    with mock.patch.object(function,
                           'drawBlitStars'):
        suc = function.drawAlignmentStars(axe)
        assert suc


def test_drawHemisphere(function):
    suc = function.drawHemisphere()
    assert suc
