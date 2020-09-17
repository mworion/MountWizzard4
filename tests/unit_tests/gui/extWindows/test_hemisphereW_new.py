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

# local import
from tests.baseTestSetup import App
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
    function.storeConfig()


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


def test_drawBlit_1(function):
    function.mutexDraw.lock()
    suc = function.drawBlit()
    assert not suc


def test_drawBlit_2(function):
    suc = function.drawBlit()
    assert suc


def test_drawBlit_3(function):
    function.hemisphereBack = None
    suc = function.drawBlit()
    assert suc


def test_drawBlitStars_1(function):
    suc = function.drawBlitStars()
    assert suc


def test_drawBlitStars_2(function):
    function.mutexDraw.lock()
    suc = function.drawBlitStars()
    assert not suc


def test_drawBlitStars_3(function):
    function.hemisphereBackStars = None
    suc = function.drawBlitStars()
    assert suc


def test_updateCelestialPath_1(function):
    function.drawHemisphere()
    suc = function.updateCelestialPath()
    assert not suc


def test_updateCelestialPath_3(function):
    function.drawHemisphere()
    function.celestialPath = None
    suc = function.updateCelestialPath()
    assert not suc


def test_updateMeridian_1(function):
    function.drawHemisphere()
    function.app.mount.setting.meridianLimitSlew = 3
    function.app.mount.setting.meridianLimitTrack = 3
    suc = function.updateMeridian(function.app.mount.setting)
    assert suc


def test_updateMeridian_3(function):
    function.drawHemisphere()
    function.app.mount.setting.meridianLimitSlew = None
    function.app.mount.setting.meridianLimitTrack = 3
    suc = function.updateMeridian(function.app.mount.setting)
    assert not suc


def test_updateMeridian_4(function):
    function.drawHemisphere()
    function.app.mount.setting.meridianLimitSlew = 3
    function.app.mount.setting.meridianLimitTrack = None
    suc = function.updateMeridian(function.app.mount.setting)
    assert not suc


def test_updateMeridian_5(function):
    function.drawHemisphere()
    function.app.mount.setting.meridianLimitSlew = 3
    function.app.mount.setting.meridianLimitTrack = 3
    function.meridianTrack = None
    suc = function.updateMeridian(function.app.mount.setting)
    assert not suc


def test_updateMeridian_6(function):
    function.drawHemisphere()
    function.app.mount.setting.meridianLimitSlew = 3
    function.app.mount.setting.meridianLimitTrack = 3
    function.meridianSlew = None
    suc = function.updateMeridian(function.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_1(function):
    function.drawHemisphere()
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 10
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert suc


def test_updateHorizonLimits_3(function):
    function.drawHemisphere()
    function.app.mount.setting.horizonLimitHigh = None
    function.app.mount.setting.horizonLimitLow = 10
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_4(function):
    function.drawHemisphere()
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = None
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_5(function):
    function.drawHemisphere()
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 10
    function.horizonLimitLow = None
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_6(function):
    function.drawHemisphere()
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 10
    function.horizonLimitHigh = None
    suc = function.updateHorizonLimits(function.app.mount.setting)
    assert not suc
