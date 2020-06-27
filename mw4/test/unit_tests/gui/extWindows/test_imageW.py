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
import mw4.base.packageConfig as Config
# standard libraries
import unittest.mock as mock
import pytest
import os
import glob
import shutil
import faulthandler
faulthandler.enable()

# external packages
import astropy.visualization
from astropy.visualization import AsinhStretch
from astropy.io import fits
from astropy import wcs
from skyfield.api import Angle
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QCheckBox
import numpy as np
from mountcontrol.qtmount import Mount

# local import
from mw4.gui.widget import MWidget
from mw4.gui.imageW import ImageWindow
from mw4.imaging.camera import Camera
from mw4.astrometry.astrometry import Astrometry


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app

    class Test2(QObject):
        threadPool = QThreadPool()

    class Test1a:
        expTime = QDoubleSpinBox()
        binning = QDoubleSpinBox()
        expTimeN = QDoubleSpinBox()
        binningN = QDoubleSpinBox()
        subFrame = QDoubleSpinBox()
        focalLength = QDoubleSpinBox()
        checkFastDownload = QCheckBox()
        solveTimeout = QDoubleSpinBox()
        searchRadius = QDoubleSpinBox()

    class Test1:
        ui = Test1a()

    class Test(QObject):
        config = {'mainW': {},
                  'showImageW': True}
        update1s = pyqtSignal()
        showImage = pyqtSignal(str)
        message = pyqtSignal(str, int)
        mainW = Test1()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', expire=False, verbose=False,
                      pathToData='mw4/test/data')
        camera = Camera(app=Test2())
        astrometry = Astrometry(app=Test2())
        uiWindows = {'showImageW': {}}
        mwGlob = {'imageDir': 'mw4/test/image'}
        threadPool = QThreadPool()
        deviceStat = {'camera': True,
                      'astrometry': True}

    with mock.patch.object(ImageWindow,
                           'show'):
        app = ImageWindow(app=Test())
        qtbot.addWidget(app)
        yield

    files = glob.glob('mw4/test/image/*.fit*')
    for f in files:
        os.remove(f)


def test_storeConfig_1():
    app.storeConfig()


def test_initConfig_1():
    app.app.config['imageW'] = {}
    suc = app.initConfig()
    assert suc


def test_initConfig_3():
    app.app.config['imageW'] = {}
    app.app.config['imageW']['winPosX'] = 10000
    app.app.config['imageW']['winPosY'] = 10000
    suc = app.initConfig()
    assert suc


def test_showWindow_1(qtbot):
    with mock.patch.object(app,
                           'show'):
        suc = app.showWindow()
        assert suc


def test_closeEvent_1(qtbot):
    with mock.patch.object(app,
                           'show'):
        app.showWindow()
        with mock.patch.object(MWidget,
                               'closeEvent',
                               return_value=None):
            app.closeEvent(None)


def test_setupDropDownGui():
    app.setupDropDownGui()
    assert app.ui.color.count() == 4
    assert app.ui.zoom.count() == 5
    assert app.ui.stretch.count() == 6


def test_updateWindowsStats_1():
    app.deviceStat['expose'] = True
    app.deviceStat['exposeN'] = False
    app.deviceStat['solve'] = True
    app.app.deviceStat['camera'] = False
    app.app.deviceStat['astrometry'] = True
    app.deviceStat['imaging'] = True
    app.deviceStat['astrometry'] = True

    suc = app.updateWindowsStats()
    assert suc


def test_updateWindowsStats_2():
    app.deviceStat['expose'] = False
    app.deviceStat['exposeN'] = True
    app.deviceStat['solve'] = False
    app.app.deviceStat['camera'] = True
    app.app.deviceStat['astrometry'] = False
    app.deviceStat['imaging'] = False
    app.deviceStat['astrometry'] = False

    suc = app.updateWindowsStats()
    assert suc


def test_updateWindowsStats_3():
    app.ui.checkShowFlux.setChecked(True)

    suc = app.updateWindowsStats()
    assert suc


def test_selectImage_1():
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('test', '', '.fits')):
        suc = app.selectImage()
        assert not suc


def test_selectImage_2(qtbot):
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('c:/test/test.fits', 'test', '.fits')):
        with qtbot.waitSignal(app.app.message) as blocker:
            with qtbot.waitSignal(app.app.showImage):
                suc = app.selectImage()
                assert suc
        assert ['Image [test] selected', 0] == blocker.args
        assert app.folder == 'c:/test'


def test_setupDistorted_1():
    header = fits.PrimaryHDU().header
    header['naxis'] = 2

    suc = app.setupDistorted()
    assert suc
    assert app.axe is not None
    assert app.axeCB is None


def test_setupDistorted_3():
    app.header = fits.PrimaryHDU().header
    app.header['naxis'] = 2

    suc = app.setupDistorted()
    assert suc
    assert app.axe is not None
    assert app.axeCB is None


def test_setupNormal_1():
    app.ui.checkShowGrid.setChecked(True)
    app.ui.checkShowCrosshair.setChecked(True)
    app.header = fits.PrimaryHDU().header
    app.header['naxis'] = 2

    suc = app.setupNormal()
    assert suc
    assert app.axe is not None
    assert app.axeCB is not None


def test_setupNormal_2():
    app.ui.checkShowGrid.setChecked(True)
    app.ui.checkShowCrosshair.setChecked(True)
    app.header = fits.PrimaryHDU().header
    app.header['naxis'] = 2

    suc = app.setupNormal()
    assert suc
    assert app.axe is not None
    assert app.axeCB is not None


def test_setupNormal_3():
    app.ui.checkShowGrid.setChecked(True)
    app.ui.checkShowCrosshair.setChecked(True)
    app.header = fits.PrimaryHDU().header
    app.header['naxis'] = 2

    suc = app.setupNormal()
    assert suc
    assert app.axe is not None
    assert app.axeCB is not None


def test_setupNormal_4():
    app.ui.checkShowGrid.setChecked(False)
    app.ui.checkShowCrosshair.setChecked(False)
    app.header = fits.PrimaryHDU().header
    app.header['naxis'] = 2

    suc = app.setupNormal()
    assert suc
    assert app.axe is not None
    assert app.axeCB is not None


def test_colorImage_1():
    app.ui.color.setCurrentIndex(0)
    suc = app.colorImage()
    assert suc
    assert app.colorMap == 'gray'


def test_colorImage_2():
    app.ui.color.setCurrentIndex(1)
    suc = app.colorImage()
    assert suc
    assert app.colorMap == 'plasma'


def test_stretchImage_1():
    suc = app.stretchImage()
    assert suc


def test_stretchImage_2():
    suc = app.stretchImage()
    assert suc
    assert isinstance(app.stretch, astropy.visualization.AsinhStretch)


def test_imagePlot_1():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.axe = app.fig.add_subplot()
    app.axeCB = app.fig.add_axes()
    app.stretch = AsinhStretch()
    app.colorMap = 'rainbow'
    suc = app.imagePlot()
    assert suc


def test_imagePlot_2():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.axe = app.fig.add_subplot()
    app.axeCB = app.fig.add_axes()
    app.stretch = AsinhStretch()
    app.colorMap = 'rainbow'
    app.sources = {'xcentroid': 50 * np.ones([1]),
                   'ycentroid': 50 * np.ones([1]),
                   'sharpness': 0.5 * np.ones([1]),
                   'roundness1': 0.5 * np.ones([1]),
                   'roundness2': 0.5 * np.ones([1]),
                   'flux': 5 * np.ones([1]),
                   }
    app.mean = np.zeros([100, 100], dtype=np.uint8)
    app.ui.checkShowSources.setChecked(True)
    suc = app.imagePlot()
    assert suc


def test_imagePlot_3():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.axe = app.fig.add_subplot()
    app.axeCB = app.fig.add_axes()
    app.stretch = AsinhStretch()
    app.colorMap = 'rainbow'
    app.sources = {'xcentroid': 50 * np.ones([1]),
                   'ycentroid': 50 * np.ones([1]),
                   'sharpness': 0.5 * np.ones([1]),
                   'roundness1': 0.5 * np.ones([1]),
                   'roundness2': 0.5 * np.ones([1]),
                   'flux': 5 * np.ones([1]),
                   }
    app.mean = np.zeros([100, 100], dtype=np.uint8)
    app.ui.checkShowSharp.setChecked(True)
    suc = app.imagePlot()
    assert suc


def test_imagePlot_4():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.axe = app.fig.add_subplot()
    app.axeCB = app.fig.add_axes()
    app.stretch = AsinhStretch()
    app.colorMap = 'rainbow'
    app.sources = {'xcentroid': 50 * np.ones([1]),
                   'ycentroid': 50 * np.ones([1]),
                   'sharpness': 0.5 * np.ones([1]),
                   'roundness1': 0.5 * np.ones([1]),
                   'roundness2': 0.5 * np.ones([1]),
                   'flux': 5 * np.ones([1]),
                   }
    app.mean = np.zeros([100, 100], dtype=np.uint8)
    app.ui.checkShowRound.setChecked(True)
    suc = app.imagePlot()
    assert suc


def test_imagePlot_5():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.axe = app.fig.add_subplot()
    app.axeCB = app.fig.add_axes()
    app.stretch = AsinhStretch()
    app.colorMap = 'rainbow'
    app.sources = {'xcentroid': 50 * np.ones([1]),
                   'ycentroid': 50 * np.ones([1]),
                   'sharpness': 0.5 * np.ones([1]),
                   'roundness1': 0.5 * np.ones([1]),
                   'roundness2': 0.5 * np.ones([1]),
                   'flux': 5 * np.ones([1]),
                   }
    app.mean = np.zeros([100, 100], dtype=np.uint8)
    app.ui.checkShowFlux.setChecked(True)
    suc = app.imagePlot()
    assert suc


def test_writeHeaderDataToGUI_1():
    app.header = fits.PrimaryHDU().header
    suc = app.writeHeaderDataToGUI()
    assert suc


def test_writeHeaderDataToGUI_2():
    app.header = fits.PrimaryHDU().header
    app.header['naxis'] = 2
    suc = app.writeHeaderDataToGUI()
    assert suc


def test_preparePlot_1():
    app.image = None
    app.header = None
    suc = app.preparePlot()
    assert not suc


def test_preparePlot_2():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = None
    suc = app.preparePlot()
    assert not suc


def test_preparePlot_3():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    suc = app.preparePlot()
    assert suc


def test_preparePlot_4():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.header['CTYPE1'] = '2'
    suc = app.preparePlot()
    assert suc


def test_preparePlot_5():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.header['CTYPE1'] = '2'
    app.ui.checkUseWCS.setChecked(True)
    with mock.patch.object(wcs.WCS,
                           'has_distortion',
                           return_value=True):
        app.setupDistorted = app.setupNormal
        suc = app.preparePlot()
        assert suc


def test_workerPhotometry_1():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    suc = app.workerPhotometry()
    assert suc
    assert app.mean is not None
    assert app.std is not None
    assert app.median is not None
    assert app.sources is None


def test_prepareImage_1():
    Config.featureFlags['imageAdv'] = False
    suc = app.prepareImage()
    assert suc


def test_prepareImage_2():
    Config.featureFlags['imageAdv'] = True
    app.sources = None
    with mock.patch.object(app,
                           'workerPhotometry'):
        suc = app.prepareImage()
        assert suc


def test_stackImages_1():
    app.ui.checkStackImages.setChecked(False)
    suc = app.stackImages()
    assert not suc
    assert app.imageStack is None
    assert app.ui.numberStacks.text() == 'single'


def test_stackImages_2():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.imageStack = np.zeros([50, 50], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.ui.checkStackImages.setChecked(True)

    suc = app.stackImages()
    assert suc
    assert app.imageStack.shape == app.image.shape
    assert app.numberStack == 1


def test_stackImages_3():
    app.numberStack = 5
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.imageStack = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.ui.checkStackImages.setChecked(True)

    suc = app.stackImages()
    assert suc
    assert app.numberStack == 6


def test_zoomImage_1():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.header['naxis'] = 2
    app.ui.zoom.setCurrentIndex(0)
    suc = app.zoomImage()
    assert not suc
    assert app.image.shape == (100, 100)


def test_zoomImage_2():
    app.image = np.zeros([100, 100], dtype=np.uint8)
    app.header = fits.PrimaryHDU().header
    app.header['naxis'] = 2
    app.ui.zoom.setCurrentIndex(1)
    suc = app.zoomImage()
    assert suc
    assert app.image.shape == (50, 50)


def test_showImage_1():
    app.imageFileName = ''
    suc = app.showImage()
    assert not suc


def test_showImage_2():
    app.imageFileName = 'test'
    suc = app.showImage()
    assert not suc


def test_showImage_3():
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')
    suc = app.showImage(imagePath='mw4/test/image/m51.fit')
    assert suc


def test_showCurrent_1():
    suc = app.showCurrent()
    assert suc


def test_exposeRaw_1(qtbot):
    app.app.mainW.ui.expTime.setValue(3)
    app.app.mainW.ui.binning.setValue(2)
    app.app.mainW.ui.subFrame.setValue(100)
    with mock.patch.object(app.app.camera,
                           'expose',
                           ):
        with qtbot.waitSignal(app.app.message):
            suc = app.exposeRaw()
            assert suc


def test_exposeImageDone_1(qtbot):
    app.ui.checkAutoSolve.setChecked(False)
    app.app.camera.signals.saved.connect(app.exposeImageDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        with qtbot.waitSignal(app.app.showImage):
            suc = app.exposeImageDone()
            assert suc
    assert ['Exposed:             []', 0] == blocker.args


def test_exposeImageDone_2(qtbot):
    app.ui.checkAutoSolve.setChecked(True)
    app.app.camera.signals.saved.connect(app.exposeImageDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        with qtbot.waitSignal(app.signals.solveImage):
            suc = app.exposeImageDone()
            assert suc
    assert ['Exposed:             []', 0] == blocker.args


def test_exposeImage_1():
    app.app.camera.data = {}
    suc = app.exposeImage()
    assert suc


def test_exposeImageNDone_1(qtbot):
    app.ui.checkAutoSolve.setChecked(False)
    app.app.camera.signals.saved.connect(app.exposeImageDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        with qtbot.waitSignal(app.app.showImage):
            suc = app.exposeImageNDone()
            assert suc
    assert ['Exposed:            []', 0] == blocker.args


def test_exposeImageNDone_2(qtbot):
    app.ui.checkAutoSolve.setChecked(True)
    app.app.camera.signals.saved.connect(app.exposeImageDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        with qtbot.waitSignal(app.signals.solveImage):
            suc = app.exposeImageNDone()
            assert suc
    assert ['Exposed:            []', 0] == blocker.args


def test_exposeImageN_1():
    app.app.camera.data = {}
    suc = app.exposeImageN()
    assert suc


def test_abortImage_1(qtbot):
    with mock.patch.object(app.app.camera,
                           'abort',
                           ):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_abortImage_2(qtbot):
    app.app.camera.signals.saved.connect(app.showImage)
    app.ui.exposeN.setEnabled(True)
    app.ui.expose.setEnabled(False)
    app.app.camera.signals.saved.connect(app.exposeRaw)
    with mock.patch.object(app.app.camera,
                           'abort',
                           ):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_abortImage_3(qtbot):
    app.app.camera.signals.saved.connect(app.showImage)
    app.ui.exposeN.setEnabled(False)
    app.ui.expose.setEnabled(True)
    app.app.camera.signals.saved.connect(app.exposeImageDone)
    with mock.patch.object(app.app.camera,
                           'abort',
                           ):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_solveDone_1(qtbot):
    app.app.astrometry.signals.done.connect(app.solveDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.solveDone()
        assert not suc
    assert ['Solving error, result missing', 2] == blocker.args


def test_solveDone_2(qtbot):
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

    app.app.astrometry.signals.done.connect(app.solveDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.solveDone(result=result)
        assert not suc
    assert ['Solving error:       test', 2] == blocker.args


def test_solveDone_3(qtbot):
    app.ui.checkAutoSolve.setChecked(False)
    app.ui.checkStackImages.setChecked(True)
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

    app.app.astrometry.signals.done.connect(app.solveDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.solveDone(result=result)
        assert suc
    assert ['Solved :             RA: 10:00:00 (10.000), DEC: +20:00:00 (20.000), ', 0] == blocker.args


def test_solveDone_4(qtbot):
    app.ui.checkAutoSolve.setChecked(True)
    app.ui.checkStackImages.setChecked(False)
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

    app.app.astrometry.signals.done.connect(app.solveDone)
    with qtbot.waitSignal(app.app.showImage):
        suc = app.solveDone(result=result)
        assert suc


def test_solveImage_1(qtbot):
    suc = app.solveImage()
    assert not suc


def test_solveImage_2(qtbot):
    suc = app.solveImage(imagePath='testFile')
    assert not suc


def test_solveImage_3(qtbot):
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')
    file = 'mw4/test/image/m51.fit'
    with mock.patch.object(app.app.astrometry,
                           'solveThreading'):
        suc = app.solveImage(imagePath=file)
        assert suc


def test_solveCurrent(qtbot):
    with qtbot.waitSignal(app.signals.solveImage):
        suc = app.solveCurrent()
        assert suc


def test_abortSolve_1():
    suc = app.abortSolve()
    assert not suc
