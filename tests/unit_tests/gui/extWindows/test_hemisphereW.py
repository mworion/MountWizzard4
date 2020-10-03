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


def test_showWindow_1(function):
    with mock.patch.object(function,
                           'drawHemisphere'):
        with mock.patch.object(function,
                               'show'):
            suc = function.showWindow()
            assert suc


def test_updatePointerAltAz_1(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerAltAz, = axe.plot(0, 0)
    suc = function.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_2(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerAltAz, = axe.plot(0, 0)
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    suc = function.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_3(function):
    axe, _ = function.generateFlat(widget=function.hemisphereMatMove, horizon=False)
    function.pointerAltAz, = axe.plot(0, 0)
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = Angle(degrees=80)
    suc = function.updatePointerAltAz()
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

    suc = function.drawAlignmentStars(axe)
    assert suc


def test_drawHemisphere(function):
    suc = function.drawHemisphere()
    assert suc
