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
import shutil
import os

# external packages
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import QRectF
from astropy.io import fits
from skyfield.api import Angle
import numpy as np
import pyqtgraph as pg

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.imageW import ImageWindow
from logic.photometry.photometry import Photometry
from logic.file.fileHandler import FileHandler
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function(qapp):

    func = ImageWindow(app=App())
    yield func


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc

    function.app.config['imageW'] = {'winPosX': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_3(function):
    suc = function.initConfig()
    assert suc

    function.app.config['imageW'] = {'winPosY': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_4(function):
    function.app.config['imageW'] = {}
    function.app.config['imageW']['winPosX'] = 100
    function.app.config['imageW']['winPosY'] = 100
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'imageW' in function.app.config:
        del function.app.config['imageW']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['imageW'] = {}

    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_colorChange(function):
    with mock.patch.object(function,
                           'showCurrent'):
        suc = function.colorChange()
        assert suc


def test_operationMode_1(function):
    suc = function.operationMode(0)
    assert suc


def test_operationMode_2(function):
    suc = function.operationMode(1)
    assert suc


def test_updateWindowsStats_1(function):
    function.deviceStat['expose'] = True
    function.deviceStat['exposeN'] = False
    function.deviceStat['solve'] = True
    function.app.deviceStat['camera'] = False
    function.app.deviceStat['plateSolve'] = True
    function.deviceStat['imaging'] = True
    function.deviceStat['plateSolve'] = True

    suc = function.updateWindowsStats()
    assert suc


def test_updateWindowsStats_2(function):
    function.deviceStat['expose'] = False
    function.deviceStat['exposeN'] = True
    function.deviceStat['solve'] = False
    function.app.deviceStat['camera'] = True
    function.app.deviceStat['plateSolve'] = False
    function.deviceStat['imaging'] = False
    function.deviceStat['plateSolve'] = False

    suc = function.updateWindowsStats()
    assert suc


def test_updateWindowsStats_3(function):
    function.deviceStat['solve'] = False
    function.app.deviceStat['camera'] = True
    function.app.deviceStat['plateSolve'] = False
    function.deviceStat['imaging'] = False
    function.deviceStat['plateSolve'] = False

    suc = function.updateWindowsStats()
    assert suc


def test_selectImage_1(function):
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('test', '', '.fits')):
        suc = function.selectImage()
        assert not suc


def test_selectImage_2(function):
    function.ui.autoSolve.setChecked(False)
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('c:/test/test.fits', 'test', '.fits')):
        suc = function.selectImage()
        assert suc
        assert function.folder == 'c:/test'


def test_selectImage_3(function):
    function.ui.autoSolve.setChecked(True)
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('c:/test/test.fits', 'test', '.fits')):
        suc = function.selectImage()
        assert suc
        assert function.folder == 'c:/test'


def test_setBarColor_1(function):
    function.ui.color.setCurrentIndex(0)
    with mock.patch.object(function.ui.image,
                           'setColorMap'):
        suc = function.setBarColor()
        assert suc


def test_copyLevels(function):
    suc = function.copyLevels()
    assert suc


def test_setCrosshair_1(function):
    function.ui.color.setCurrentIndex(0)
    with mock.patch.object(function.ui.image,
                           'showCrosshair'):
        suc = function.setCrosshair()
        assert suc


def test_setAspectLocked(function):
    suc = function.setAspectLocked()
    assert suc


def test_getImageSourceRange(function):
    suc = function.getImageSourceRange()
    assert suc


def test_clearImageTab(function):
    suc = function.clearImageTab(function.ui.image)
    assert suc


def test_writeHeaderDataToGUI_1(function):
    function.header = fits.PrimaryHDU().header
    suc = function.writeHeaderDataToGUI(function.header)
    assert suc


def test_writeHeaderDataToGUI_2(function):
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2
    suc = function.writeHeaderDataToGUI(function.header)
    assert suc


def test_writeHeaderDataToGUI_3(function):
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2
    function.header['OBJCTRA'] = '+08 00 00'
    function.header['OBJCTDEC'] = '90 00 00'
    suc = function.writeHeaderDataToGUI(function.header)
    assert suc


def test_writeHeaderDataToGUI_4(function):
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2
    function.header['RA'] = 12.0
    function.header['DEC'] = 80.0
    suc = function.writeHeaderDataToGUI(function.header)
    assert suc


def test_showTabImage_1(function):
    function.fileHandler = FileHandler(function)
    function.fileHandler.image = np.random.rand(100, 100) + 1
    with mock.patch.object(function,
                           'setBarColor'):
        with mock.patch.object(function,
                               'setCrosshair'):
            with mock.patch.object(function,
                                   'writeHeaderDataToGUI'):
                suc = function.showTabImage()
                assert suc


def test_showTabImage_2(function):
    function.fileHandler = FileHandler(function)
    function.fileHandler.image = None
    suc = function.showTabImage()
    assert not suc


def test_showTabHFR(function):
    function.ui.isoLayer.setChecked(True)
    function.photometry = Photometry(function)
    function.photometry.hfr = np.random.rand(100, 100) + 1
    function.photometry.hfrPercentile = 0
    function.photometry.hfrMedian = 0
    with mock.patch.object(function.ui.hfr,
                           'addIsoBasic'):
        suc = function.showTabHFR()
        assert suc


def test_showTabTiltSquare(function):
    function.photometry = Photometry(function)
    function.photometry.hfr = np.linspace(20, 30, 20)
    function.photometry.hfrMedian = 1
    function.photometry.hfrInner = 1
    function.photometry.hfrOuter = 1
    function.photometry.w = 100
    function.photometry.h = 100
    function.photometry.hfrSegSquare = np.ones((3, 3))
    function.photometry.image = np.random.rand(100, 100) + 1
    suc = function.showTabTiltSquare()
    assert suc


def test_showTabTiltTriangle(function):
    function.photometry = Photometry(function)
    function.photometry.hfr = np.linspace(20, 30, 20)
    function.photometry.hfrMedian = 1
    function.photometry.hfrInner = 1
    function.photometry.hfrOuter = 1
    function.photometry.w = 100
    function.photometry.h = 100
    function.photometry.hfrSegTriangle = np.ones(72)
    function.image = np.random.rand(100, 100) + 1
    suc = function.showTabTiltTriangle()
    assert suc


def test_showTabRoundness(function):
    function.ui.isoLayer.setChecked(True)
    function.photometry = Photometry(function)
    function.photometry.roundnessMin = 1
    function.photometry.roundnessMax = 10
    function.photometry.roundnessPercentile = 10
    function.photometry.roundnessGrid = np.random.rand(100, 100) + 1
    with mock.patch.object(function.ui.roundness,
                           'addIsoBasic'):
        suc = function.showTabRoundness()
    assert suc


def test_showTabAberrationInspect(function):
    function.photometry = Photometry(function)
    function.photometry.image = np.random.rand(100, 100) + 1
    function.photometry.roundnessPercentile = 1
    suc = function.showTabAberrationInspect()
    assert suc


def test_showTabImageSources(function):
    function.photometry = Photometry(function)
    function.imageSourceRange = QRectF(1, 2, 3, 4)
    function.photometry.objs = {'x': np.linspace(0, 50, 20),
                          'y': np.linspace(50, 100, 20),
                          'theta': np.random.rand(20, 1) + 10,
                          'a': np.random.rand(20, 1) + 10,
                          'b': np.random.rand(20, 1) + 10}
    function.photometry.image = np.random.rand(100, 100) + 1
    function.photometry.hfr = np.random.rand(20, ) + 10.0

    function.ui.showValues.setChecked(True)
    with mock.patch.object(function.ui.imageSource,
                           'addEllipse',
                           return_value=pg.PlotItem()):
        suc = function.showTabImageSources()
        assert suc


def test_showTabBackground(function):
    function.photometry = Photometry(function)
    function.photometry.background = np.random.rand(100, 100) + 1
    suc = function.showTabBackground()
    assert suc


def test_showTabBackgroundRMS(function):
    function.photometry = Photometry(function)
    function.photometry.backgroundRMS = np.random.rand(100, 100) + 1
    suc = function.showTabBackgroundRMS()
    assert suc


def test_clearGui(function):
    suc = function.clearGui()
    assert suc


def test_resultPhotometry_1(function):
    function.photometry = Photometry(function)
    function.photometry.objs = None
    suc = function.resultPhotometry()
    assert suc


def test_resultPhotometry_2(function):
    function.photometry = Photometry(function)
    function.photometry.objs = 1
    suc = function.resultPhotometry()
    assert suc


def test_processPhotometry_1(function):
    function.ui.photometryGroup.setChecked(True)
    function.fileHandler = FileHandler(function)
    function.fileHandler.image = 1
    with mock.patch.object(function.photometry,
                           'processPhotometry'):
        suc = function.processPhotometry()
        assert suc


def test_processPhotometry_2(function):
    function.ui.photometryGroup.setChecked(False)
    function.fileHandler = FileHandler(function)
    function.fileHandler.image = None
    with mock.patch.object(function,
                           'clearGui'):
        suc = function.processPhotometry()
        assert not suc


def test_showImage_1(function):
    function.deviceStat['expose'] = True
    with mock.patch.object(function,
                           'clearGui'):
        suc = function.showImage()
        assert not suc


def test_showImage_2(function):
    function.deviceStat['expose'] = False
    suc = function.showImage('test')
    assert not suc


def test_showImage_3(function):
    function.deviceStat['expose'] = False
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(function.fileHandler,
                               'loadImage'):
            suc = function.showImage('tests')
            assert suc


def test_showCurrent_1(function):
    suc = function.showCurrent()
    assert suc


def test_exposeRaw_1(function):
    function.app.camera.expTime = 3
    function.app.camera.binning = 3
    function.app.camera.subFrame = 100
    function.ui.timeTagImage.setChecked(True)
    with mock.patch.object(function.app.camera,
                           'expose',
                           return_value=True):
        suc = function.exposeRaw()
        assert suc


def test_exposeRaw_2(function):
    function.app.camera.expTime = 3
    function.app.camera.binning = 3
    function.app.camera.subFrame = 100
    function.ui.timeTagImage.setChecked(False)
    with mock.patch.object(function.app.camera,
                           'expose',
                           return_value=True):
        suc = function.exposeRaw()
        assert suc


def test_exposeRaw_3(function):
    function.app.camera.expTime = 3
    function.app.camera.binning = 3
    function.app.camera.subFrame = 100
    with mock.patch.object(function.app.camera,
                           'expose',
                           return_value=False):
        suc = function.exposeRaw()
        assert not suc


def test_exposeImageDone_1(function):
    function.ui.autoSolve.setChecked(False)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    suc = function.exposeImageDone()
    assert suc


def test_exposeImageDone_2(function):
    function.ui.autoSolve.setChecked(True)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    suc = function.exposeImageDone()
    assert suc


def test_exposeImage_1(function):
    function.app.camera.data = {}
    suc = function.exposeImage()
    assert suc


def test_exposeImageNDone_1(function):
    function.ui.autoSolve.setChecked(False)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    suc = function.exposeImageNDone()
    assert suc


def test_exposeImageNDone_2(function):
    function.ui.autoSolve.setChecked(True)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    suc = function.exposeImageNDone()
    assert suc


def test_exposeImageN_1(function):
    function.app.camera.data = {}
    suc = function.exposeImageN()
    assert suc


def test_abortExpose_1(function):
    with mock.patch.object(function.app.camera,
                           'abort',
                           ):
        suc = function.abortExpose()
        assert suc


def test_abortExpose_2(function):
    function.app.camera.signals.saved.connect(function.showImage)
    function.ui.exposeN.setEnabled(True)
    function.ui.expose.setEnabled(False)
    function.app.camera.signals.saved.connect(function.exposeRaw)
    with mock.patch.object(function.app.camera,
                           'abort',
                           ):
        suc = function.abortExpose()
        assert suc


def test_abortExpose_3(function):
    function.deviceStat['expose'] = True
    function.deviceStat['exposeN'] = False
    function.app.camera.signals.saved.connect(function.showImage)
    function.ui.exposeN.setEnabled(False)
    function.ui.expose.setEnabled(True)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with mock.patch.object(function.app.camera,
                           'abort',
                           ):
        suc = function.abortExpose()
        assert suc


def test_abortExpose_4(function):
    function.deviceStat['expose'] = False
    function.deviceStat['exposeN'] = True
    function.app.camera.signals.saved.connect(function.showImage)
    function.ui.exposeN.setEnabled(False)
    function.ui.expose.setEnabled(True)
    function.app.camera.signals.saved.connect(function.exposeImageNDone)
    with mock.patch.object(function.app.camera,
                           'abort',
                           ):
        suc = function.abortExpose()
        assert suc


def test_solveDone_1(function):
    function.app.plateSolve.signals.done.connect(function.solveDone)
    suc = function.solveDone()
    assert not suc


def test_solveDone_2(function):
    result = {
        'success': False,
        'raJ2000S': Angle(hours=10),
        'decJ2000S': Angle(degrees=20),
        'angleS': 30,
        'scaleS': 1,
        'errorRMS_S': 3,
        'flippedS': False,
        'imagePath': 'test',
        'message': 'test',
    }

    function.app.plateSolve.signals.done.connect(function.solveDone)
    suc = function.solveDone(result=result)
    assert not suc


def test_solveDone_3(function):
    function.ui.embedData.setChecked(True)
    result = {
        'success': True,
        'raJ2000S': Angle(hours=10),
        'decJ2000S': Angle(degrees=20),
        'angleS': 30,
        'scaleS': 1,
        'errorRMS_S': 3,
        'flippedS': False,
        'imagePath': 'test',
        'message': 'test',
    }

    function.app.plateSolve.signals.done.connect(function.solveDone)
    suc = function.solveDone(result=result)
    assert suc


def test_solveImage_1(function):
    suc = function.solveImage()
    assert not suc


def test_solveImage_2(function):
    suc = function.solveImage(imagePath='testFile')
    assert not suc


def test_solveImage_3(function):
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    file = 'tests/workDir/image/m51.fit'
    with mock.patch.object(function.app.plateSolve,
                           'solveThreading'):
        suc = function.solveImage(imagePath=file)
        assert suc


def test_solveCurrent(function):
    suc = function.solveCurrent()
    assert suc


def test_abortSolve_1(function):
    suc = function.abortSolve()
    assert not suc


def test_slewSelectedTargetWithDome_1(function):
    function.app.mount.obsSite.AltTarget = None
    function.app.mount.obsSite.AzTarget = None
    function.app.deviceStat['dome'] = False
    suc = function.slewSelectedTargetWithDome()
    assert not suc


def test_slewSelectedTargetWithDome_2(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=10)
    function.app.mount.obsSite.AzTarget = Angle(degrees=10)
    function.app.deviceStat['dome'] = False
    with mock.patch.object(function.app.mount.obsSite,
                           'startSlewing',
                           return_value=True):
        suc = function.slewSelectedTargetWithDome()
        assert suc


def test_slewSelectedTargetWithDome_3(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=10)
    function.app.mount.obsSite.AzTarget = Angle(degrees=10)
    function.app.deviceStat['dome'] = False
    with mock.patch.object(function.app.mount.obsSite,
                           'startSlewing',
                           return_value=False):
        suc = function.slewSelectedTargetWithDome()
        assert not suc


def test_slewSelectedTargetWithDome_4(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=10)
    function.app.mount.obsSite.AzTarget = Angle(degrees=10)
    function.app.deviceStat['dome'] = True
    with mock.patch.object(function.app.mount.obsSite,
                           'startSlewing',
                           return_value=False):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=10):
            suc = function.slewSelectedTargetWithDome()
            assert not suc


def test_moveRaDecAbsolute_1(function):
    a = function.app.mount.obsSite.timeJD
    function.app.mount.obsSite.timeJD = None
    suc = function.moveRaDecAbsolute(Angle(degrees=10), Angle(degrees=10))
    assert not suc
    function.app.mount.obsSite.timeJD = a


def test_moveRaDecAbsolute_2(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec'):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=False):
            suc = function.moveRaDecAbsolute(Angle(degrees=10), Angle(degrees=10))
            assert not suc


def test_moveRaDecAbsolute_3(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec'):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.moveRaDecAbsolute(Angle(degrees=10), Angle(degrees=10))
            assert suc


def test_solveCenterDone_1(function):
    function.app.plateSolve.signals.done.connect(function.solveCenterDone)
    suc = function.solveCenterDone()
    assert not suc


def test_solveCenterDone_2(function):
    result = {
        'success': False,
        'raJ2000S': Angle(hours=10),
        'decJ2000S': Angle(degrees=20),
        'angleS': 30,
        'scaleS': 1,
        'errorRMS_S': 3,
        'flippedS': False,
        'imagePath': 'test',
        'message': 'test',
    }

    function.app.plateSolve.signals.done.connect(function.solveCenterDone)
    suc = function.solveCenterDone(result=result)
    assert not suc


def test_solveCenterDone_3(function):
    function.ui.embedData.setChecked(True)
    result = {
        'success': True,
        'raJ2000S': Angle(hours=10),
        'decJ2000S': Angle(degrees=20),
        'angleS': 30,
        'scaleS': 1,
        'errorRMS_S': 3,
        'flippedS': False,
        'imagePath': 'test',
        'message': 'test',
    }
    function.app.plateSolve.signals.done.connect(function.solveCenterDone)
    with mock.patch.object(function,
                           'moveRaDecAbsolute',
                           return_value=False):
        suc = function.solveCenterDone(result=result)
        assert not suc


def test_solveCenterDone_4(function):
    function.ui.embedData.setChecked(True)
    result = {
        'success': True,
        'raJ2000S': Angle(hours=10),
        'decJ2000S': Angle(degrees=20),
        'angleS': 30,
        'scaleS': 1,
        'errorRMS_S': 3,
        'flippedS': False,
        'imagePath': 'test',
        'message': 'test',
    }
    function.app.plateSolve.signals.done.connect(function.solveCenterDone)
    with mock.patch.object(function,
                           'moveRaDecAbsolute',
                           return_value=True):
        suc = function.solveCenterDone(result=result)
        assert suc


def test_solveCenter_1(function):
    suc = function.solveCenter()
    assert not suc


def test_solveCenter_2(function):
    function.imageFileName = 'test'
    suc = function.solveCenter()
    assert not suc


def test_solveCenter_3(function):
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    function.imageFileName = 'tests/workDir/image/m51.fit'
    with mock.patch.object(function.app.plateSolve,
                           'solveThreading'):
        suc = function.solveCenter()
        assert suc
