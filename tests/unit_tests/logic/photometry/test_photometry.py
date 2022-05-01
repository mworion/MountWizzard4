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
from astropy.io import fits
from skyfield.api import Angle
import numpy as np
import sep

# local import
import gui.extWindows.imageW
from tests.unit_tests.unitTestAddOns.baseTestSetupExtWindows import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.imageW import ImageWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = ImageWindow(app=App())
    yield window
    window.app.threadPool.waitForDone(3000)


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


def test_updateWindowsStats_1(function):
    function.deviceStat['expose'] = True
    function.deviceStat['exposeN'] = False
    function.deviceStat['solve'] = True
    function.app.deviceStat['camera'] = False
    function.app.deviceStat['astrometry'] = True
    function.deviceStat['imaging'] = True
    function.deviceStat['astrometry'] = True

    suc = function.updateWindowsStats()
    assert suc


def test_updateWindowsStats_2(function):
    function.deviceStat['expose'] = False
    function.deviceStat['exposeN'] = True
    function.deviceStat['solve'] = False
    function.app.deviceStat['camera'] = True
    function.app.deviceStat['astrometry'] = False
    function.deviceStat['imaging'] = False
    function.deviceStat['astrometry'] = False

    suc = function.updateWindowsStats()
    assert suc


def test_showTitle(function):
    suc = function.showTitle('test')
    assert suc


def test_selectImage_1(function):
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('test', '', '.fits')):
        suc = function.selectImage()
        assert not suc


def test_selectImage_2(function, qtbot):
    function.ui.autoSolve.setChecked(False)
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('c:/test/test.fits', 'test', '.fits')):
        with qtbot.waitSignal(function.app.message) as blocker:
            with qtbot.waitSignal(function.app.showImage):
                suc = function.selectImage()
                assert suc
        assert function.folder == 'c:/test'


def test_selectImage_3(function, qtbot):
    function.ui.autoSolve.setChecked(True)
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('c:/test/test.fits', 'test', '.fits')):
        with qtbot.waitSignal(function.app.message) as blocker:
            with qtbot.waitSignal(function.app.showImage):
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


def test_calcAberrationInspectView_1(function):
    imgIn = np.random.rand(1000, 1000) + 1
    img = function.calcAberrationInspectView(imgIn)
    h, w = img.shape
    assert w == function.aberrationSize * 3
    assert h == function.aberrationSize * 3


def test_calcAberrationInspectView_2(function):
    imgIn = np.random.rand(100, 100) + 1
    img = function.calcAberrationInspectView(imgIn)
    h, w = img.shape
    assert w == imgIn.shape[0]
    assert h == imgIn.shape[1]


def test_workerCalcTiltValuesTriangle(function):
    function.objs = {'x': np.linspace(0, 50, 20),
                     'y': np.linspace(50, 100, 20)}
    function.image = np.random.rand(100, 100) + 1
    function.HFR = np.linspace(20, 30, 20)
    suc = function.workerCalcTiltValuesTriangle()
    assert suc


def test_workerCalcTiltValuesSquare(function):
    function.objs = {'x': np.linspace(0, 50, 20),
                     'y': np.linspace(50, 100, 20)}
    function.image = np.random.rand(100, 100) + 1
    function.HFR = np.linspace(20, 30, 20)
    suc = function.workerCalcTiltValuesSquare()
    assert suc


def test_baseCalcTabInfo(function):
    function.objs = {'x': np.linspace(0, 50, 20),
                     'y': np.linspace(50, 100, 20)}
    function.HFR = np.linspace(20, 30, 20)
    function.image = np.random.rand(100, 100) + 1
    suc = function.baseCalcTabInfo()
    assert suc


def test_showTabRaw(function):
    suc = function.showTabRaw()
    assert suc


def test_showTabBackground(function):
    img = np.random.rand(100, 100) + 1
    function.filterConst = 5
    function.bkg = sep.Background(img)
    suc = function.showTabBackground()
    assert suc


def test_workerShowTabHFR(function):
    function.filterConst = 5
    function.xm = np.linspace(0, 100, 100)
    function.ym = np.linspace(0, 100, 100)
    function.objs = {'x': np.linspace(0, 50, 20),
                     'y': np.linspace(50, 100, 20)}
    function.HFR = np.linspace(20, 30, 20)
    img = function.workerShowTabHFR()
    assert img.shape[0] == 100


def test_showTabHFR(function):
    function.HFR = np.linspace(20, 30, 20)
    img = np.random.rand(100, 100) + 1
    suc = function.showTabHFR(img)
    assert suc


def test_clearImageTab(function):
    widget = function.ui.tiltSquare
    suc = function.clearImageTab(widget)
    assert suc


def test_showTabTiltSquare(function):
    function.HFR = np.linspace(20, 30, 20)
    function.medianHFR = 1
    function.innerHFR = 1
    function.outerHFR = 1
    function.segSquareHFR = np.ones((3, 3))
    function.image = np.random.rand(100, 100) + 1
    suc = function.showTabTiltSquare()
    assert suc


def test_showTabTiltTriangle(function):
    function.HFR = np.linspace(20, 30, 20)
    function.innerHFR = 1
    function.outerHFR = 1
    function.medianHFR = 1
    function.segTriangleHFR = np.ones(72)
    function.image = np.random.rand(100, 100) + 1
    suc = function.showTabTiltTriangle()
    assert suc


def test_workerShowTabRoundness(function):
    img = np.random.rand(100, 100) + 1
    function.filterConst = 5
    function.xm = np.linspace(0, 100, 100)
    function.ym = np.linspace(0, 100, 100)
    function.objs = {'x': np.linspace(0, 50, 20),
                     'y': np.linspace(50, 100, 20),
                     'a': np.random.rand(20, 1) + 10,
                     'b': np.random.rand(20, 1) + 10}
    with mock.patch.object(gui.extWindows.imageW,
                           'griddata',
                           return_value=img):
        with mock.patch.object(gui.extWindows.imageW,
                               'uniform_filter',
                               return_value=img):
            val = function.workerShowTabRoundness()
            assert len(val) == 4


def test_showTabRoundness(function):
    result = (np.random.rand(20, 1),
              np.random.rand(100, 100) + 1,
              1, 2)
    suc = function.showTabRoundness(result)
    assert suc


def test_showTabAberrationInspect(function):
    function.image = np.random.rand(100, 100) + 1
    suc = function.showTabAberrationInspect()
    assert suc


def test_showTabImageSources(function):
    function.objs = {'x': np.linspace(0, 50, 20),
                     'y': np.linspace(50, 100, 20),
                     'theta': np.random.rand(20, 1) + 10,
                     'a': np.random.rand(20, 1) + 10,
                     'b': np.random.rand(20, 1) + 10}
    function.image = np.random.rand(100, 100) + 1
    with mock.patch.object(function.ui.imageSource,
                           'addEllipse'):
        suc = function.showTabImageSources()
        assert suc


def test_showTabBackgroundRMS(function):
    img = np.random.rand(100, 100) + 1
    function.filterConst = 5
    function.bkg = sep.Background(img)
    suc = function.showTabBackgroundRMS()
    assert suc


def test_showTabImages_1(function):
    with mock.patch.object(function,
                           'showTabRaw'):
        suc = function.showTabImages()
        assert not suc


def test_showTabImages_2(function):
    function.HFR = np.linspace(20, 30, 20)
    with mock.patch.object(function,
                           'showTabRaw'):
        with mock.patch.object(function,
                               'baseCalcTabInfo'):
            with mock.patch.object(function.threadPool,
                                   'start'):
                with mock.patch.object(function,
                                       'showTabBackground'):
                    with mock.patch.object(function,
                                           'showTabAberrationInspect'):
                        with mock.patch.object(function,
                                               'showTabImageSources'):
                            with mock.patch.object(function,
                                                   'showTabBackgroundRMS'):
                                suc = function.showTabImages()
                                assert suc


def test_workerPreparePhotometry_1(function):
    function.image = np.random.rand(100, 100) + 1
    function.image[50][50] = 100
    function.image[51][50] = 50
    function.image[50][51] = 50
    function.image[50][49] = 50
    function.image[49][50] = 50
    suc = function.workerPreparePhotometry()
    assert suc
    assert function.bkg is not None
    assert function.HFR is not None
    assert function.objs is not None


def test_preparePhotometry_1(function):
    function.ui.enablePhotometry.setChecked(True)
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.preparePhotometry()
        assert suc


def test_preparePhotometry_2(function):
    function.ui.enablePhotometry.setChecked(False)
    with mock.patch.object(function,
                           'showTabImages'):
        suc = function.preparePhotometry()
        assert suc


def test_stackImages_1(function):
    function.ui.stackImages.setChecked(False)
    suc = function.stackImages()
    assert not suc
    assert function.imageStack is None


def test_stackImages_2(function):
    function.image = np.random.rand(100, 100)
    function.imageStack = np.random.rand(50, 50)
    function.header = fits.PrimaryHDU().header
    function.ui.stackImages.setChecked(True)

    suc = function.stackImages()
    assert suc
    assert function.imageStack.shape == function.image.shape
    assert function.numberStack == 1


def test_stackImages_3(function):
    function.numberStack = 5
    function.image = np.random.rand(100, 100)
    function.imageStack = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.ui.stackImages.setChecked(True)

    suc = function.stackImages()
    assert suc
    assert function.numberStack == 6


def test_clearStack_1(function):
    function.ui.stackImages.setChecked(False)
    suc = function.clearStack()
    assert not suc


def test_clearStack_2(function):
    function.ui.stackImages.setChecked(True)
    suc = function.clearStack()
    assert suc


def test_debayerImage_1(function):
    img = np.random.rand(100, 100)
    img = function.debayerImage(img, 'GBRG')
    assert img.shape == (100, 100)


def test_debayerImage_2(function):
    img = np.random.rand(100, 100)
    img = function.debayerImage(img, 'RGGB')
    assert img.shape == (100, 100)


def test_debayerImage_3(function):
    img = np.random.rand(100, 100)
    img = function.debayerImage(img, 'GRBG')
    assert img.shape == (100, 100)


def test_debayerImage_4(function):
    img = np.random.rand(100, 100)
    img = function.debayerImage(img, 'BGGR')
    assert img.shape == (100, 100)


def test_debayerImage_5(function):
    img = np.random.rand(100, 100)
    img = function.debayerImage(img, 'test')
    assert img.shape == (100, 100)


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


def test_checkFormatImage(function):
    img = np.random.rand(100, 100) + 1
    img = function.checkFormatImage(img)
    assert img.dtype == np.dtype('float32')


def test_workerLoadImage_1(function):
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

    function.imageFileName = 'tests/workDir/image/m51.fit'
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    with mock.patch.object(fits,
                           'open',
                           return_value=FitsHandle()):
        suc = function.workerLoadImage()
        assert not suc


def test_workerLoadImage_2(function):
    class Data:
        data = None
        header = 2

    class FitsHandle:
        @staticmethod
        def __enter__():
            return [Data(), Data()]

        @staticmethod
        def __exit__(a, b, c):
            return

    function.imageFileName = 'tests/workDir/image/m51.fit'
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    with mock.patch.object(fits,
                           'open',
                           return_value=FitsHandle()):
        suc = function.workerLoadImage()
        assert not suc


def test_workerLoadImage_3(function):
    class Data:
        data = np.random.rand(100, 100)
        header = {'BAYERPAT': 1,
                  'CTYPE1': 'DEF',
                  'CTYPE2': 'DEF',
                  }

    class FitsHandle:
        @staticmethod
        def __enter__():
            return [Data(), Data()]

        @staticmethod
        def __exit__(a, b, c):
            return

    function.imageFileName = 'tests/workDir/image/m51.fit'
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    with mock.patch.object(fits,
                           'open',
                           return_value=FitsHandle()):
        with mock.patch.object(function,
                               'stackImages'):
            suc = function.workerLoadImage()
            assert suc


def test_showImage_1(function):
    suc = function.showImage()
    assert not suc


def test_showImage_2(function):
    suc = function.showImage('test')
    assert not suc


def test_showImage_3(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(function.threadPool,
                               'start'):
            suc = function.showImage('tests')
            assert suc


def test_showCurrent_1(function):
    suc = function.showCurrent()
    assert suc


def test_exposeRaw_1(function, qtbot):
    function.app.camera.expTime = 3
    function.app.camera.binning = 3
    function.app.camera.subFrame = 100
    with mock.patch.object(function.app.camera,
                           'expose',
                           return_value=True):
        with qtbot.waitSignal(function.app.message):
            suc = function.exposeRaw()
            assert suc


def test_exposeRaw_2(function, qtbot):
    function.app.camera.expTime = 3
    function.app.camera.binning = 3
    function.app.camera.subFrame = 100
    with mock.patch.object(function.app.camera,
                           'expose',
                           return_value=False):
        with qtbot.waitSignal(function.app.message):
            suc = function.exposeRaw()
            assert not suc


def test_exposeImageDone_1(function, qtbot):
    function.ui.autoSolve.setChecked(False)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with qtbot.waitSignal(function.app.message) as blocker:
        with qtbot.waitSignal(function.app.showImage):
            suc = function.exposeImageDone()
            assert suc
    assert ['Exposed:             []', 0] == blocker.args


def test_exposeImageDone_2(function, qtbot):
    function.ui.autoSolve.setChecked(True)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with qtbot.waitSignal(function.app.message) as blocker:
        with qtbot.waitSignal(function.signals.solveImage):
            suc = function.exposeImageDone()
            assert suc
    assert ['Exposed:             []', 0] == blocker.args


def test_exposeImage_1(function):
    function.app.camera.data = {}
    suc = function.exposeImage()
    assert suc


def test_exposeImageNDone_1(function, qtbot):
    function.ui.autoSolve.setChecked(False)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with qtbot.waitSignal(function.app.message) as blocker:
        with qtbot.waitSignal(function.app.showImage):
            suc = function.exposeImageNDone()
            assert suc
    assert ['Exposed:             []', 0] == blocker.args


def test_exposeImageNDone_2(function, qtbot):
    function.ui.autoSolve.setChecked(True)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with qtbot.waitSignal(function.app.message) as blocker:
        with qtbot.waitSignal(function.signals.solveImage):
            suc = function.exposeImageNDone()
            assert suc
    assert ['Exposed:             []', 0] == blocker.args


def test_exposeImageN_1(function):
    function.app.camera.data = {}
    suc = function.exposeImageN()
    assert suc


def test_abortImage_1(function, qtbot):
    with mock.patch.object(function.app.camera,
                           'abort',
                           ):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_abortImage_2(function, qtbot):
    function.app.camera.signals.saved.connect(function.showImage)
    function.ui.exposeN.setEnabled(True)
    function.ui.expose.setEnabled(False)
    function.app.camera.signals.saved.connect(function.exposeRaw)
    with mock.patch.object(function.app.camera,
                           'abort',
                           ):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_abortImage_3(function, qtbot):
    function.deviceStat['expose'] = True
    function.deviceStat['exposeN'] = False
    function.app.camera.signals.saved.connect(function.showImage)
    function.ui.exposeN.setEnabled(False)
    function.ui.expose.setEnabled(True)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with mock.patch.object(function.app.camera,
                           'abort',
                           ):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_abortImage_4(function, qtbot):
    function.deviceStat['expose'] = False
    function.deviceStat['exposeN'] = True
    function.app.camera.signals.saved.connect(function.showImage)
    function.ui.exposeN.setEnabled(False)
    function.ui.expose.setEnabled(True)
    function.app.camera.signals.saved.connect(function.exposeImageNDone)
    with mock.patch.object(function.app.camera,
                           'abort',
                           ):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_solveDone_1(function, qtbot):
    function.app.astrometry.signals.done.connect(function.solveDone)
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.solveDone()
        assert not suc
    assert ['Solving error, result missing', 2] == blocker.args


def test_solveDone_2(function, qtbot):
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

    function.app.astrometry.signals.done.connect(function.solveDone)
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.solveDone(result=result)
        assert not suc
    assert ['Solving error:       test', 2] == blocker.args


def test_solveDone_3(function, qtbot):
    function.ui.embedData.setChecked(True)
    function.ui.stackImages.setChecked(True)
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

    function.app.astrometry.signals.done.connect(function.solveDone)
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.solveDone(result=result)
        assert suc
    assert ['Solved :             RA: 10:00:00 (10.000), DEC: +20:00:00 (20.000), ', 0] == blocker.args


def test_solveImage_1(function, qtbot):
    suc = function.solveImage()
    assert not suc


def test_solveImage_2(function, qtbot):
    suc = function.solveImage(imagePath='testFile')
    assert not suc


def test_solveImage_3(function, qtbot):
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    file = 'tests/workDir/image/m51.fit'
    with mock.patch.object(function.app.astrometry,
                           'solveThreading'):
        suc = function.solveImage(imagePath=file)
        assert suc


def test_solveCurrent(function, qtbot):
    with qtbot.waitSignal(function.signals.solveImage):
        suc = function.solveCurrent()
        assert suc


def test_abortSolve_1(function):
    suc = function.abortSolve()
    assert not suc
