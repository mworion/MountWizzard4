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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import shutil

# external packages
from astropy.io import fits
import numpy as np
from xisf import XISF


# local import
from logic.file.fileHandler import FileHandler, FileHandlerSignals
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope='function')
def function(qapp):

    func = FileHandler(App())
    yield func


def test_signals(function):
    sig = FileHandlerSignals()


def test_debayerImage_1(function):
    function.w = 100
    function.h = 100
    function.image = np.random.rand(100, 100)
    suc = function.debayerImage('GBRG')
    assert suc
    assert function.image.shape == (100, 100)


def test_debayerImage_2(function):
    function.w = 100
    function.h = 100
    function.image = np.random.rand(100, 100)
    suc = function.debayerImage('RGGB')
    assert suc
    assert function.image.shape == (100, 100)


def test_debayerImage_3(function):
    function.w = 100
    function.h = 100
    function.image = np.random.rand(100, 100)
    suc = function.debayerImage('GRBG')
    assert suc
    assert function.image.shape == (100, 100)


def test_debayerImage_4(function):
    function.w = 100
    function.h = 100
    function.image = np.random.rand(100, 100)
    suc = function.debayerImage('BGGR')
    assert suc
    assert function.image.shape == (100, 100)


def test_debayerImage_5(function):
    function.w = 100
    function.h = 100
    function.image = np.random.rand(100, 100)
    suc = function.debayerImage('test')
    assert not suc
    assert function.image.shape == (100, 100)


def test_cleanImageFormat_1(function):
    function.image = np.random.rand(100, 100) + 1
    function.flipV = False
    function.flipH = True
    suc = function.cleanImageFormat()
    assert suc
    assert function.image.dtype == np.dtype('float32')


def test_checkValidImageFormat_1(function):
    function.image = None
    suc = function.checkValidImageFormat()
    assert not suc


def test_checkValidImageFormat_2(function):
    function.image = np.random.rand(100, 100)
    function.header = None
    suc = function.checkValidImageFormat()
    assert not suc


def test_checkValidImageFormat_3(function):
    function.image = np.random.rand(100, 100)
    function.header = {}
    suc = function.checkValidImageFormat()
    assert not suc


def test_checkValidImageFormat_4(function):
    function.image = np.random.rand(100, 100)
    function.header = {'NAXIS': 2}
    suc = function.checkValidImageFormat()
    assert suc


def test_convHeaderXISF2FITS(function):
    header = {
        'FITSKeywords': {
            'COMMENT': [{'value': 'test', 'comment': 'test'}],
            'SIMPLE': [{'value': 'T', 'comment': 'test'}]
        },
        'geometry': (1000, 2000, 3)
    }
    h = function.convHeaderXISF2FITS(header)
    assert h['NAXIS'] == 2
    assert h['NAXIS1'] == 1000
    assert h['NAXIS2'] == 2000
    assert 'SIMPLE' in h
    assert 'EXTEND' in h


def test_loadXSIF(function):
    img = np.ones((100, 100, 1))
    with mock.patch.object(XISF,
                           'read',
                           return_value=img):
        with mock.patch.object(function,
                               'convHeaderXISF2FITS'):
            suc = function.loadXISF()
            assert suc


def test_loadFITS_1(function):
    class Data:
        data = np.random.rand(100, 100)
        header = None

    class FitsHandle:
        @staticmethod
        def __enter__():
            return [Data(), Data()]

        @staticmethod
        def __exit__(a, b, c):
            return
    with mock.patch.object(fits,
                           'open',
                           return_value=FitsHandle()):
        suc = function.loadFITS()
        assert suc


def test_workerLoadImage_1(function):
    imageFileName = 'tests/workDir/image/m51.fit'
    with mock.patch.object(function,
                           'loadFITS'):
        with mock.patch.object(function,
                               'checkValidImageFormat',
                               return_value=False):
            suc = function.workerLoadImage(imageFileName)
            assert not suc


def test_workerLoadImage_2(function):
    imageFileName = 'tests/workDir/image/m51.xisf'
    with mock.patch.object(function,
                           'loadXISF'):
        with mock.patch.object(function,
                               'checkValidImageFormat',
                               return_value=False):
            suc = function.workerLoadImage(imageFileName)
            assert not suc


def test_workerLoadImage_3(function):
    function.header = {'BAYERPAT': 'RGGB  ',
                       'CTYPE1': 'DEF',
                       'CTYPE2': 'DEF',
                       'NAXIS': 2,
                       'NAXIS1': 100,
                       'NAXIS2': 200,
                      }

    imageFileName = 'tests/workDir/image/m51.fit'
    with mock.patch.object(function,
                           'loadFITS'):
        with mock.patch.object(function,
                               'checkValidImageFormat',
                               return_value=True):
            with mock.patch.object(function,
                                   'cleanImageFormat'):
                with mock.patch.object(function,
                                       'debayerImage'):
                    suc = function.workerLoadImage(imageFileName)
                    assert suc


def test_loadImage_1(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.loadImage()
        assert not suc


def test_loadImage_2(function):
    imageFileName = 'tests/workDir/image/m51.fit'
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.loadImage(imageFileName)
        assert suc
