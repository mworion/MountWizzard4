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
import unittest.mock as mock
import pytest
import shutil

# external packages
from PyQt5.QtGui import QCloseEvent
import astropy.visualization
from astropy.visualization import AsinhStretch
from astropy.io import fits
from astropy import wcs
from skyfield.api import Angle
import numpy as np

# local import
from tests.baseTestSetupExtWindows import App
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


def test_setupDropDownGui(function):
    function.setupDropDownGui()
    assert function.ui.color.count() == 4
    assert function.ui.zoom.count() == 5
    assert function.ui.stretch.count() == 8


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


def test_selectImage_1(function):
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('test', '', '.fits')):
        suc = function.selectImage()
        assert not suc


def test_selectImage_2(function, qtbot):
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('c:/test/test.fits', 'test', '.fits')):
        with qtbot.waitSignal(function.app.message) as blocker:
            with qtbot.waitSignal(function.app.showImage):
                suc = function.selectImage()
                assert suc
        assert ['Image [test] selected', 0] == blocker.args
        assert function.folder == 'c:/test'


def test_setupDistorted_1(function):
    header = fits.PrimaryHDU().header
    header['naxis'] = 2

    suc = function.setupDistorted()
    assert suc
    assert function.axe is not None
    assert function.axeCB is None


def test_setupDistorted_2(function):
    function.ui.checkShowGrid.setChecked(True)
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2

    suc = function.setupDistorted()
    assert suc
    assert function.axe is not None


def test_setupDistorted_3(function):
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2

    suc = function.setupDistorted()
    assert suc
    assert function.axe is not None
    assert function.axeCB is None


def test_setupNormal_1(function):
    function.ui.zoom.addItem(' 1x Zoom')
    function.ui.checkShowGrid.setChecked(True)
    function.ui.checkShowCrosshair.setChecked(True)
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2

    suc = function.setupNormal()
    assert suc
    assert function.axe is not None
    assert function.axeCB is not None


def test_setupNormal_2(function):
    function.ui.zoom.addItem(' 1x Zoom')
    function.ui.checkShowGrid.setChecked(True)
    function.ui.checkShowCrosshair.setChecked(True)
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2

    suc = function.setupNormal()
    assert suc
    assert function.axe is not None
    assert function.axeCB is not None


def test_setupNormal_3(function):
    function.ui.zoom.addItem(' 1x Zoom')
    function.ui.checkShowGrid.setChecked(True)
    function.ui.checkShowCrosshair.setChecked(True)
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2

    suc = function.setupNormal()
    assert suc
    assert function.axe is not None
    assert function.axeCB is not None


def test_setupNormal_4(function):
    function.ui.zoom.addItem(' 1x Zoom')
    function.ui.checkShowGrid.setChecked(False)
    function.ui.checkShowCrosshair.setChecked(False)
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2

    suc = function.setupNormal()
    assert suc
    assert function.axe is not None
    assert function.axeCB is not None


def test_colorImage_1(function):
    function.ui.color.addItem('Grey')
    function.ui.color.setCurrentIndex(0)
    suc = function.colorImage()
    assert suc
    assert function.colorMap == 'gray'


def test_colorImage_2(function):
    function.ui.color.addItem('Grey')
    function.ui.color.addItem('Cool')
    function.ui.color.setCurrentIndex(1)
    suc = function.colorImage()
    assert suc
    assert function.colorMap == 'plasma'


def test_stretchImage_1(function):
    function.stretchValues = {'Low': 1}
    suc = function.stretchImage()
    assert suc


def test_stretchImage_2(function):
    function.stretchValues = {'Low': 1}
    suc = function.stretchImage()
    assert suc
    assert isinstance(function.stretch, astropy.visualization.AsinhStretch)


def test_imagePlot_0(function):
    function.ui.view.addItem('test')
    function.image = np.random.rand(100, 100)
    function.axe = function.fig.add_subplot(label=0)
    function.axeCB = function.fig.add_subplot(label=1)
    function.stretch = AsinhStretch()
    function.colorMap = 'rainbow'
    function.ui.view.setCurrentIndex(0)
    suc = function.imagePlot()
    assert suc


def test_imagePlot_1(function):
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.axe = function.fig.add_subplot(label=0)
    function.axeCB = function.fig.add_subplot(label=1)
    function.stretch = AsinhStretch()
    function.colorMap = 'rainbow'
    function.objs = np.ones(
        10,
        dtype=[('x', '<f8'), ('y', '<f8'),
               ('a', '<f8'), ('b', '<f8'),
               ('theta', '<f8'), ('flux', '<f8')])
    function.bk_back = np.zeros([100, 100])
    function.ui.view.setCurrentIndex(1)
    suc = function.imagePlot()
    assert suc


def test_imagePlot_2(function):
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.axe = function.fig.add_subplot(label=0)
    function.axeCB = function.fig.add_subplot(label=1)
    function.stretch = AsinhStretch()
    function.colorMap = 'rainbow'
    function.objs = np.ones(
        10,
        dtype=[('x', '<f8'), ('y', '<f8'),
               ('a', '<f8'), ('b', '<f8'),
               ('theta', '<f8'), ('flux', '<f8')])
    function.bk_back = np.zeros([100, 100])
    function.ui.view.setCurrentIndex(2)
    function.radius = np.array([5, 3, 2])
    suc = function.imagePlot()
    assert suc


def test_imagePlot_3(function):
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.axe = function.fig.add_subplot(label=0)
    function.axeCB = function.fig.add_subplot(label=1)
    function.stretch = AsinhStretch()
    function.colorMap = 'rainbow'
    function.objs = np.ones(
        10,
        dtype=[('x', '<f8'), ('y', '<f8'),
               ('a', '<f8'), ('b', '<f8'),
               ('theta', '<f8'), ('flux', '<f8')])
    function.bk_back = np.zeros([100, 100])
    function.ui.view.setCurrentIndex(3)
    suc = function.imagePlot()
    assert suc


def test_imagePlot_4(function):
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.axe = function.fig.add_subplot(label=0)
    function.axeCB = function.fig.add_subplot(label=1)
    function.stretch = AsinhStretch()
    function.colorMap = 'rainbow'
    function.objs = np.ones(
        10,
        dtype=[('x', '<f8'), ('y', '<f8'),
               ('a', '<f8'), ('b', '<f8'),
               ('theta', '<f8'), ('flux', '<f8')])
    function.bk_back = np.zeros([100, 100])
    function.bk_rms = np.zeros([100, 100])
    function.ui.view.setCurrentIndex(4)
    suc = function.imagePlot()
    assert suc


def test_imagePlot_5(function):
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.axe = function.fig.add_subplot(label=0)
    function.axeCB = function.fig.add_subplot(label=1)
    function.stretch = AsinhStretch()
    function.colorMap = 'rainbow'
    function.objs = np.ones(
        10,
        dtype=[('x', '<f8'), ('y', '<f8'),
               ('a', '<f8'), ('b', '<f8'),
               ('theta', '<f8'), ('flux', '<f8')])
    function.bk_back = np.zeros([100, 100])
    function.bk_rms = np.zeros([100, 100])
    function.ui.view.setCurrentIndex(5)
    suc = function.imagePlot()
    assert suc


def test_imagePlot_6(function):
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.axe = function.fig.add_subplot(label=0)
    function.axeCB = function.fig.add_subplot(label=1)
    function.stretch = AsinhStretch()
    function.colorMap = 'rainbow'
    function.objs = np.ones(
        10,
        dtype=[('x', '<f8'), ('y', '<f8'),
               ('a', '<f8'), ('b', '<f8'),
               ('theta', '<f8'), ('flux', '<f8')])
    function.bk_back = np.zeros([100, 100])
    function.flux = np.random.rand(10)
    function.ui.view.setCurrentIndex(6)
    suc = function.imagePlot()
    assert suc


def test_imagePlot_7(function):
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.image = np.random.rand(300, 300)
    function.header = fits.PrimaryHDU().header
    function.axe = function.fig.add_subplot(label=0)
    function.axeCB = function.fig.add_subplot(label=1)
    function.stretch = AsinhStretch()
    function.colorMap = 'rainbow'
    function.objs = np.ones(
        100,
        dtype=[('x', '<f8'), ('y', '<f8'),
               ('a', '<f8'), ('b', '<f8'),
               ('theta', '<f8'), ('flux', '<f8')])
    function.objs['x'] = np.random.rand(100)
    function.objs['y'] = np.random.rand(100)
    function.bk_back = np.zeros([300, 300])
    function.radius = np.random.rand(100)
    function.ui.view.setCurrentIndex(7)
    suc = function.imagePlot()
    assert suc


def test_writeHeaderDataToGUI_1(function):
    function.header = fits.PrimaryHDU().header
    suc = function.writeHeaderDataToGUI()
    assert suc


def test_writeHeaderDataToGUI_2(function):
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2
    suc = function.writeHeaderDataToGUI()
    assert suc


def test_writeHeaderDataToGUI_3(function):
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2
    function.header['OBJCTRA'] = '+08 00 00'
    function.header['OBJCTDEC'] = '90 00 00'
    suc = function.writeHeaderDataToGUI()
    assert suc


def test_writeHeaderDataToGUI_4(function):
    function.header = fits.PrimaryHDU().header
    function.header['naxis'] = 2
    function.header['RA'] = 12.0
    function.header['DEC'] = 80.0
    suc = function.writeHeaderDataToGUI()
    assert suc


def test_preparePlot_1(function):
    function.image = None
    function.header = None
    suc = function.preparePlot()
    assert not suc


def test_preparePlot_2(function):
    function.image = np.random.rand(100, 100)
    function.header = None
    suc = function.preparePlot()
    assert not suc


def test_preparePlot_3(function):
    function.ui.zoom.addItem(' 1x Zoom')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    suc = function.preparePlot()
    assert suc


def test_preparePlot_4(function):
    function.ui.zoom.addItem(' 1x Zoom')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.header['CTYPE1'] = '2'
    function.header['NAXIS'] = 2
    with mock.patch.object(function,
                           'setupNormal'):
        with mock.patch.object(function,
                               'imagePlot'):
            suc = function.preparePlot()
            assert suc


def test_preparePlot_5(function):
    function.ui.view.addItem('test')
    function.ui.view.addItem('test')
    function.ui.zoom.addItem(' 1x Zoom')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.header['CTYPE1'] = '2'
    function.header['NAXIS'] = 2
    function.ui.view.setCurrentIndex(1)
    function.ui.checkUseWCS.setChecked(True)
    with mock.patch.object(wcs.WCS,
                           'has_distortion',
                           return_value=True):
        function.setupDistorted = function.setupNormal
        with mock.patch.object(function,
                               'setupDistorted'):
            with mock.patch.object(function,
                                   'imagePlot'):
                suc = function.preparePlot()
                assert suc


def test_workerPhotometry_1(function):
    function.image = np.random.rand(100, 100) + 1
    function.image[50][50] = 100
    function.image[51][50] = 50
    function.image[50][51] = 50
    function.image[50][49] = 50
    function.image[49][50] = 50
    suc = function.workerPhotometry()
    assert suc
    assert function.bk_back is not None
    assert function.bk_rms is not None
    assert function.flux is not None
    assert function.radius is not None
    assert function.objs is not None


def test_prepareImageForPhotometry_1(function):
    suc = function.prepareImageForPhotometry()
    assert suc


def test_prepareImageForPhotometry_2(function):
    function.sources = None
    with mock.patch.object(function,
                           'workerPhotometry'):
        suc = function.prepareImageForPhotometry()
        assert suc


def test_stackImages_1(function):
    function.ui.checkStackImages.setChecked(False)
    suc = function.stackImages()
    assert not suc
    assert function.imageStack is None
    assert function.ui.numberStacks.text() == 'single'


def test_stackImages_2(function):
    function.image = np.random.rand(100, 100)
    function.imageStack = np.random.rand(50, 50)
    function.header = fits.PrimaryHDU().header
    function.ui.checkStackImages.setChecked(True)

    suc = function.stackImages()
    assert suc
    assert function.imageStack.shape == function.image.shape
    assert function.numberStack == 1


def test_stackImages_3(function):
    function.numberStack = 5
    function.image = np.random.rand(100, 100)
    function.imageStack = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.ui.checkStackImages.setChecked(True)

    suc = function.stackImages()
    assert suc
    assert function.numberStack == 6


def test_clearStack_1(function):
    function.ui.numberStacks.setText('test')
    function.ui.checkStackImages.setChecked(False)
    suc = function.clearStack()
    assert not suc
    assert function.ui.numberStacks.text() == 'single'


def test_clearStack_2(function):
    function.ui.numberStacks.setText('test')
    function.ui.checkStackImages.setChecked(True)
    suc = function.clearStack()
    assert suc
    assert function.ui.numberStacks.text() == 'test'


def test_zoomImage_1(function):
    function.ui.zoom.addItem(' 1x Zoom')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.header['NAXIS'] = 2
    function.ui.zoom.setCurrentIndex(0)
    suc = function.zoomImage()
    assert not suc
    assert function.image.shape == (100, 100)


def test_zoomImage_2(function):
    function.ui.zoom.addItem(' 1x Zoom')
    function.ui.zoom.addItem(' 2x Zoom')
    function.image = np.random.rand(100, 100)
    function.header = fits.PrimaryHDU().header
    function.header['NAXIS'] = 2
    function.ui.zoom.setCurrentIndex(1)
    suc = function.zoomImage()
    assert suc
    assert function.image.shape == (50, 50)


def test_showImage_1(function):
    suc = function.showImage()
    assert not suc


def test_showImage_2(function):
    suc = function.showImage('test')
    assert not suc


def test_showImage_3(function):
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

    function.ui.zoom.addItem(' 1x Zoom')
    shutil.copy('tests/testData/m51.fit', 'tests/image/m51.fit')
    with mock.patch.object(fits,
                           'open',
                           return_value=FitsHandle()):
        suc = function.showImage(imagePath='tests/image/m51.fit')
        assert not suc


def test_showImage_4(function):
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

    function.ui.zoom.addItem(' 1x Zoom')
    shutil.copy('tests/testData/m51.fit', 'tests/image/m51.fit')
    with mock.patch.object(fits,
                           'open',
                           return_value=FitsHandle()):
        suc = function.showImage(imagePath='tests/image/m51.fit')
        assert not suc


def test_showImage_5(function):
    function.ui.zoom.addItem(' 1x Zoom')
    shutil.copy('tests/testData/m51.fit', 'tests/image/m51.fit')
    with mock.patch.object(function,
                           'zoomImage'):
        with mock.patch.object(function,
                               'stackImages'):
            with mock.patch.object(function,
                                   'prepareImageForPhotometry'):
                suc = function.showImage(imagePath='tests/image/m51.fit')
                assert suc


def test_showImage_6(function):
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

    function.ui.zoom.addItem(' 1x Zoom')
    shutil.copy('tests/testData/m51.fit', 'tests/image/m51.fit')
    with mock.patch.object(fits,
                           'open',
                           return_value=FitsHandle()):
        with mock.patch.object(function,
                               'zoomImage'):
            with mock.patch.object(function,
                                   'stackImages'):
                with mock.patch.object(function,
                                       'prepareImageForPhotometry'):
                    suc = function.showImage(imagePath='tests/image/m51.fit')
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
                           ):
        with qtbot.waitSignal(function.app.message):
            suc = function.exposeRaw()
            assert suc


def test_exposeImageDone_1(function, qtbot):
    function.ui.checkAutoSolve.setChecked(False)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with qtbot.waitSignal(function.app.message) as blocker:
        with qtbot.waitSignal(function.app.showImage):
            suc = function.exposeImageDone()
            assert suc
    assert ['Exposed:             []', 0] == blocker.args


def test_exposeImageDone_2(function, qtbot):
    function.ui.checkAutoSolve.setChecked(True)
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
    function.ui.checkAutoSolve.setChecked(False)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with qtbot.waitSignal(function.app.message) as blocker:
        with qtbot.waitSignal(function.app.showImage):
            suc = function.exposeImageNDone()
            assert suc
    assert ['Exposed:             []', 0] == blocker.args


def test_exposeImageNDone_2(function, qtbot):
    function.ui.checkAutoSolve.setChecked(True)
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
    function.ui.checkAutoSolve.setChecked(False)
    function.ui.checkStackImages.setChecked(True)
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


def test_solveDone_4(function, qtbot):
    function.ui.checkAutoSolve.setChecked(True)
    function.ui.checkStackImages.setChecked(False)
    result = {
        'success': True,
        'raJ2000S': Angle(hours=10),
        'decJ2000S': Angle(degrees=20),
        'angleS': 30,
        'scaleS': 1,
        'errorRMS_S': 3,
        'flippedS': False,
        'imagePath': 'test',
        'solvedPath': 'testFile',
        'message': 'test',
    }

    function.app.astrometry.signals.done.connect(function.solveDone)
    with qtbot.waitSignal(function.app.showImage):
        suc = function.solveDone(result=result)
        assert suc


def test_solveImage_1(function, qtbot):
    suc = function.solveImage()
    assert not suc


def test_solveImage_2(function, qtbot):
    suc = function.solveImage(imagePath='testFile')
    assert not suc


def test_solveImage_3(function, qtbot):
    shutil.copy('tests/testData/m51.fit', 'tests/image/m51.fit')
    file = 'tests/image/m51.fit'
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
