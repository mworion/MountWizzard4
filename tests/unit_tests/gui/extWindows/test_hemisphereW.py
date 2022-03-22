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
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QCloseEvent
from skyfield.api import Angle, wgs84
import numpy as np
import pyqtgraph as pg
from PIL import Image

# local import
from tests.unit_tests.unitTestAddOns.baseTestSetupExtWindows import App
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
    pd = pg.PlotItem()
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


def test_setOperationModeHem_1(function):
    function.ui.editModeHem.setChecked(True)
    suc = function.setOperationModeHem()
    assert suc


def test_setOperationModeHem_2(function):
    function.ui.alignmentModeHem.setChecked(True)
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
    function.imageTerrain = Image.fromarray(np.array([[1, 2], [1, 2]],
                                                     dtype=np.uint8))
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
    function.app.mount.setting.horizonLimitHigh = 10
    function.app.mount.setting.horizonLimitLow = 10
    suc = function.drawHorizonLimits()
    assert suc


def test_setupAlignmentStars(function):
    suc = function.setupAlignmentStars()
    assert suc


def test_drawAlignmentStars_1(function):
    function.ui.showAlignStar.setChecked(False)
    suc = function.drawAlignmentStars()
    assert not suc


def test_drawAlignmentStars_2(function):
    function.ui.showAlignStar.setChecked(True)
    suc = function.drawAlignmentStars()
    assert not suc


def test_drawAlignmentStars_3(function):
    function.ui.showAlignStar.setChecked(True)
    function.alignmentStars = pg.ScatterPlotItem()
    suc = function.drawAlignmentStars()
    assert suc


def test_slewSelectedTarget_1(function):
    function.app.deviceStat['dome'] = False
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=0):
            suc = function.slewSelectedTarget('test')
            assert not suc


def test_slewSelectedTarget_2(function):
    function.app.deviceStat['dome'] = False
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=5):
            suc = function.slewSelectedTarget('test')
            assert not suc


def test_slewSelectedTarget_3(function):
    function.app.deviceStat['dome'] = True
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=5):
            with mock.patch.object(function.app.mount.obsSite,
                                   'startSlewing',
                                   return_value=True):
                suc = function.slewSelectedTarget('test')
                assert suc


def test_onMouseStar_1(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = False
        dblclick = False
        button = 0

    suc = function.onMouseStar(Event())
    assert not suc


def test_onMouseStar_2(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    suc = function.onMouseStar(Event())
    assert not suc


def test_onMouseStar_2b(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 3

    function.app.mount.model.numberStars = 3
    suc = function.onMouseStar(Event())
    assert not suc


def test_onMouseStar_3(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 3

    function.app.mount.model.numberStars = 3
    suc = function.onMouseStar(Event())
    assert not suc


def test_onMouseStar_4(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=None):
            suc = function.onMouseStar(Event())
            assert not suc


def test_onMouseStar_5(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 3

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=None):
            suc = function.onMouseStar(Event())
            assert not suc


def test_onMouseStar_6(function):
    function.app.hipparcos.name = ['test']

    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=0):
            with mock.patch.object(function.app.hipparcos,
                                   'getAlignStarRaDecFromName',
                                   return_value=(0, 0)):
                suc = function.onMouseStar(Event())
                assert not suc


def test_onMouseStar_7(function):
    function.app.hipparcos.name = ['test']

    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=0):
            with mock.patch.object(function.app.hipparcos,
                                   'getAlignStarRaDecFromName',
                                   return_value=(0, 0)):
                with mock.patch.object(function,
                                       'slewSelectedTarget',
                                       return_value=False):
                    suc = function.onMouseStar(Event())
                    assert not suc


def test_onMouseStar_8(function):
    function.app.hipparcos.name = ['test']

    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.app.mount.model.numberStars = 3
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=0):
            with mock.patch.object(function.app.hipparcos,
                                   'getAlignStarRaDecFromName',
                                   return_value=(0, 0)):
                with mock.patch.object(function,
                                       'slewSelectedTarget',
                                       return_value=True):
                    with mock.patch.object(function.app.mount.obsSite,
                                           'setTargetRaDec',
                                           return_value=True):
                        suc = function.onMouseStar(Event())
                        assert suc


def test_onMouseNormal_1(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = False
        dblclick = False
        button = 0

    suc = function.onMouseNormal(Event())
    assert not suc


def test_onMouseNormal_2(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 0

    suc = function.onMouseNormal(Event())
    assert not suc


def test_onMouseNormal_3(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    suc = function.onMouseNormal(Event())
    assert not suc


def test_onMouseNormal_4(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.onMouseNormal(Event())
        assert not suc


def test_onMouseNormal_5(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTarget',
                               return_value=False):
            suc = function.onMouseNormal(Event())
            assert not suc


def test_onMouseNormal_6(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTarget',
                               return_value=True):
            with mock.patch.object(function.app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                suc = function.onMouseNormal(Event())
                assert suc
