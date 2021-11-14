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
import pytest
import unittest.mock as mock

# external packages
from astropy.io import fits
from PyQt5.QtTest import QTest
from skyfield.api import wgs84, Angle
import numpy as np

# local import
from logic.camera.cameraSupport import CameraSupport
from base.driverDataClass import Signals
from tests.unit_tests.unitTestAddOns.baseTestSetupMixins import App


@pytest.fixture(autouse=True, scope='function')
def function():
    app = CameraSupport()
    app.data = {'CCD_INFO.CCD_PIXEL_SIZE_X': 1,
                'CCD_INFO.CCD_PIXEL_SIZE_Y': 1,
                'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE': 0,
                }
    app.abortExpose = False
    app.app = App()
    app.signals = Signals()
    yield app


def test_writeHeaderInfo_1(function):
    header = fits.PrimaryHDU(data=np.array([])).header
    obs = function.app.mount.obsSite
    obs.raJNow = Angle(hours=0)
    obs.decJNow = Angle(degrees=0)
    header = function.writeHeaderInfo(header, obs, 1, 1, 0)
    assert header['OBJECT'] == 'SKY_OBJECT'


def test_writeHeaderInfo_2(function):
    header = fits.PrimaryHDU(data=np.array([])).header
    obs = function.app.mount.obsSite
    obs.raJNow = Angle(hours=0)
    obs.decJNow = Angle(degrees=0)
    header = function.writeHeaderInfo(header, obs, 1, 1, 100)
    assert header['OBJECT'] == 'SKY_OBJECT'


def test_writeHeaderInfo_3(function):
    header = fits.PrimaryHDU(data=np.array([])).header
    obs = function.app.mount.obsSite
    obs.location = None
    obs.raJNow = Angle(hours=0)
    obs.decJNow = Angle(degrees=0)
    header = function.writeHeaderInfo(header, obs, 1, 1, 100)
    assert header['OBJECT'] == 'SKY_OBJECT'


def test_saveFits_1(function):
    data = np.array([])
    function.abortExpose = True
    val = function.saveFits('', data, 1, 1, 1)
    assert val == ''


def test_saveFits_2(function):
    data = np.array([])
    hdu = fits.PrimaryHDU(data=np.array([]))
    function.abortExpose = False
    with mock.patch.object(function,
                           'writeHeaderInfo'):
        with mock.patch.object(fits.PrimaryHDU,
                               'writeto'):
            val = function.saveFits('', data, 1, 1, 1)
            assert val == ''


def test_retrieveFits_1(function):
    function.abortExpose = True
    val = function.retrieveFits(None, None)
    assert len(val) == 0


def test_retrieveFits_2(function):
    def func(p):
        return None

    function.abortExpose = False
    val = function.retrieveFits(func, 'test')
    assert len(val) == 0


def test_retrieveFits_3(function):
    def func(p):
        return np.array([1, 2, 3])

    function.abortExpose = False
    val = function.retrieveFits(func, 'test')
    assert len(val) == 3


def test_waitExposed_1(function):
    def func(p):
        return True

    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitExposed(func, 'test', 1)
        assert suc


def test_waitExposed_2(function):
    def func(p):
        return False

    function.abortExpose = True
    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitExposed(func, 'test', 1)
        assert suc


def test_waitExposed_3(function):
    def func(p):
        return False

    function.abortExpose = True
    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitExposed(func, 'test', 0)
        assert suc
