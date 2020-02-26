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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import zlib
# external packages
from astropy.io import fits
# local import
from mw4.test.test_old.setupQt import setupQt
from mw4.imaging.camera import CameraSignals, Camera
from mw4.base.indiClass import IndiClass


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield
    import shutil
    shutil.rmtree(mwGlob['imageDir'] + 'm-file*', ignore_errors=True)


def test_cameraSignals_1():
    a = CameraSignals()
    assert a.integrated
    assert a.saved
    assert a.message


def test_canSubFrame_1():
    suc = app.camera.canSubFrame()
    assert not suc


def test_canSubFrame_2():
    suc = app.camera.canSubFrame(subFrame=5)
    assert not suc


def test_canSubFrame_3():
    suc = app.camera.canSubFrame(subFrame=110)
    assert not suc


def test_canSubFrame_4():
    app.camera.data['CCD_FRAME.X'] = 1
    suc = app.camera.canSubFrame()
    assert not suc


def test_canSubFrame_5():
    del app.camera.data['CCD_FRAME.X']
    app.camera.data['CCD_FRAME.Y'] = 1
    suc = app.camera.canSubFrame()
    assert not suc


def test_canSubFrame_6():
    app.camera.data['CCD_FRAME.Y'] = 1
    app.camera.data['CCD_FRAME.X'] = 1
    suc = app.camera.canSubFrame()
    assert suc


def test_canBinning_1():
    suc = app.camera.canBinning()
    assert not suc


def test_canBinning_2():
    suc = app.camera.canBinning(binning=0)
    assert not suc


def test_canBinning_3():
    suc = app.camera.canBinning(binning=5)
    assert not suc


def test_canBinning_4():
    app.camera.data['CCD_BINNING.HOR_BIN'] = 1
    suc = app.camera.canBinning()
    assert suc


def test_calcSubFrame_1():
    app.camera.data['CCD_INFO.CCD_MAX_X'] = 1000
    app.camera.data['CCD_INFO.CCD_MAX_Y'] = 1000
    subFrame = 100

    px, py, w, h = app.camera.calcSubFrame(subFrame=subFrame)
    assert py == 0
    assert py == 0
    assert w == 1000
    assert h == 1000


def test_calcSubFrame_2():
    app.camera.data['CCD_INFO.CCD_MAX_X'] = 1000
    app.camera.data['CCD_INFO.CCD_MAX_Y'] = 1000
    subFrame = 50

    px, py, w, h = app.camera.calcSubFrame(subFrame=subFrame)
    assert py == 250
    assert py == 250
    assert w == 500
    assert h == 500


def test_calcSubFrame_3():
    app.camera.data['CCD_INFO.CCD_MAX_X'] = 1001
    app.camera.data['CCD_INFO.CCD_MAX_Y'] = 1001
    subFrame = 50

    px, py, w, h = app.camera.calcSubFrame(subFrame=subFrame)
    assert py == 250
    assert py == 250
    assert w == 500
    assert h == 500


def test_calcSubFrame_4():
    app.camera.data['CCD_INFO.CCD_MAX_X'] = 1001
    app.camera.data['CCD_INFO.CCD_MAX_Y'] = 1001
    subFrame = 10

    px, py, w, h = app.camera.calcSubFrame(subFrame=subFrame)
    assert py == 450
    assert py == 450
    assert w == 100
    assert h == 100


def test_calcSubFrame_5():
    app.camera.data['CCD_INFO.CCD_MAX_X'] = 1001
    app.camera.data['CCD_INFO.CCD_MAX_Y'] = 1001
    subFrame = 5

    px, py, w, h = app.camera.calcSubFrame(subFrame=subFrame)
    assert py == 0
    assert py == 0
    assert w == 1001
    assert h == 1001


def test_expose_1():
    suc = app.camera.expose()
    assert not suc


def test_abort_1():
    class Test:
        @staticmethod
        def getSwitch(name):
            return {}

    class Test1:
        @staticmethod
        def sendNewSwitch(deviceName='',
                          propertyName='',
                          elements=None):
            return True

    app.camera.device = Test()
    app.camera.client = Test1()

    suc = app.camera.abort()
    assert not suc
