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
        return False

    function.abortExpose = True
    suc = function.waitExposed(func, 'test', 1)
    assert suc


def test_waitExposed_2(function):
    function.start = True

    def func(p):
        function.start = not function.start
        return function.start

    function.abortExpose = False
    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitExposed(func, 'test', 0)
        assert suc


def test_waitExposed_3(function):
    function.start = True

    def func(p):
        function.start = not function.start
        return function.start

    function.abortExpose = False
    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitExposed(func, 'test', 1)
        assert suc


def test_waitIntegrate_1(function):
    function.data = {'Device.Message': 'integrating'}
    function.abortExpose = True
    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitIntegrate(1)
        assert suc


def test_waitIntegrate_2(function):
    function.data = {'Device.Message': 'integrating'}

    def func(p):
        function.data = {'Device.Message': 'test'}

    function.abortExpose = False
    QTest.qWait = func
    suc = function.waitIntegrate(1)
    assert suc


def test_waitIntegrate_3(function):
    function.data = {'Device.Message': 'integrating'}

    def func(p):
        function.data = {'Device.Message': 'test'}

    function.abortExpose = False
    QTest.qWait = func
    suc = function.waitIntegrate(0)
    assert suc


def test_waitDownload_1(function):
    function.data = {'Device.Message': 'downloading'}
    function.abortExpose = True
    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitDownload()
        assert suc


def test_waitDownload_2(function):
    function.data = {'Device.Message': 'downloading'}

    def func(p):
        function.data = {'Device.Message': 'test'}

    function.abortExpose = False
    QTest.qWait = func
    suc = function.waitDownload()
    assert suc


def test_waitSave_1(function):
    function.data = {'Device.Message': 'image is ready'}
    function.abortExpose = True
    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitSave()
        assert suc


def test_waitSave_2(function):
    function.data = {'Device.Message': 'image is ready'}

    def func(p):
        function.data = {'Device.Message': 'test'}

    function.abortExpose = False
    QTest.qWait = func
    suc = function.waitSave()
    assert suc


def test_waitFinish_1(function):
    function.start = True

    def func(p):
        function.start = not function.start
        return function.start

    function.abortExpose = True
    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitFinish(func, 0)
        assert suc


def test_waitFinish_2(function):
    function.start = True

    def func(p):
        function.start = not function.start
        return function.start

    function.abortExpose = False
    with mock.patch.object(QTest,
                           'qWait'):
        suc = function.waitFinish(func, 0)
        assert suc


def test_waitCombinedSPro_1(function):
    with mock.patch.object(QTest,
                           'qWait'):
        with mock.patch.object(function,
                               'waitIntegrate'):
            with mock.patch.object(function,
                                   'waitDownload'):
                with mock.patch.object(function,
                                       'waitSave'):
                    with mock.patch.object(function,
                                           'waitFinish'):
                        suc = function.waitCombinedSGPro(0, 0, 0)
                        assert suc


def test_waitCombinedNINA_1(function):
    with mock.patch.object(QTest,
                           'qWait'):
        with mock.patch.object(function,
                               'waitIntegrate'):
            with mock.patch.object(function,
                                   'waitDownload'):
                with mock.patch.object(function,
                                       'waitSave'):
                    suc = function.waitCombinedNINA(0)
                    assert suc

