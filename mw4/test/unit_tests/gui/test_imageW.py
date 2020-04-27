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
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import os
import glob
import shutil
import faulthandler
faulthandler.enable()

# external packages
import astropy
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
        message = pyqtSignal(str, int)
        mainW = Test1()
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        camera = Camera(app=Test2())
        astrometry = Astrometry(app=Test2())
        uiWindows = {'showImageW': {}}
        mwGlob = {'imageDir': 'mw4/test/image'}
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
    suc = app.showWindow()
    assert suc


def test_closeEvent_1(qtbot):
    with mock.patch.object(MWidget,
                           'closeEvent',
                           return_value=None):
        app.closeEvent(None)
    app.showWindow()


def test_setupDropDownGui():
    app.setupDropDownGui()
    assert app.ui.color.count() == 4
    assert app.ui.zoom.count() == 5
    assert app.ui.stretch.count() == 6


def test_updateWindowsStats_1():
    app.deviceStat['expose'] = True
    app.deviceStat['exposeN'] = True
    app.deviceStat['solve'] = True
    app.deviceStat['imaging'] = True
    app.deviceStat['astrometry'] = True

    suc = app.updateWindowsStats()
    assert suc


def test_updateWindowsStats_2():
    app.deviceStat['expose'] = False
    app.deviceStat['exposeN'] = False
    app.deviceStat['solve'] = False
    app.deviceStat['imaging'] = False
    app.deviceStat['astrometry'] = False

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
            with qtbot.waitSignal(app.signals.showImage):
                suc = app.selectImage()
                assert suc
        assert ['Image [test] selected', 0] == blocker.args
        assert app.folder == 'c:/test'


def test_writeHeaderToGUI_1():
    header = fits.PrimaryHDU().header
    suc = app.writeHeaderToGUI(header=header)
    assert suc == (False, None)


def test_writeHeaderToGUI_2():
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    suc = app.writeHeaderToGUI(header=header)
    assert not suc[0]


def test_zoomImage_1():
    image = None
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    suc = app.zoomImage(image=image, wcsObject=wcsObject)
    assert suc is None


def test_zoomImage_2():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    app.ui.zoom.setCurrentIndex(0)
    suc = app.zoomImage(image=image, wcsObject=wcsObject)
    assert suc.shape == (100, 100)


def test_zoomImage_3():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    app.ui.zoom.setCurrentIndex(1)
    suc = app.zoomImage(image=image, wcsObject=wcsObject)
    assert suc.shape == (50, 50)


def test_stretchImage_1():
    image = None
    suc = app.stretchImage(image=image)
    assert suc is None


def test_stretchImage_2():
    image = np.zeros([100, 100], dtype=np.uint8)
    suc, a, b = app.stretchImage(image=image)
    assert isinstance(suc, astropy.visualization.mpl_normalize.ImageNormalize)


def test_colorImage_1():
    app.ui.color.setCurrentIndex(0)
    suc = app.colorImage()
    assert suc == 'gray'


def test_colorImage_2():
    app.ui.color.setCurrentIndex(1)
    suc = app.colorImage()
    assert suc == 'plasma'


def test_setupDistorted_1():
    header = fits.PrimaryHDU().header
    header['naxis'] = 2

    axe = app.setupDistorted()
    assert not axe


def test_setupDistorted_2():
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageMat.figure

    axe = app.setupDistorted(figure=fig)
    assert not axe


def test_setupDistorted_3():
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    fig = app.imageMat.figure

    axe = app.setupDistorted(figure=fig, wcsObject=wcsObject)
    assert axe


def test_setupNormal_1():
    app.ui.checkShowGrid.setChecked(True)
    app.ui.checkShowCrosshair.setChecked(True)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2

    axe = app.setupNormal()
    assert not axe


def test_setupNormal_2():
    app.ui.checkShowGrid.setChecked(True)
    app.ui.checkShowCrosshair.setChecked(True)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageMat.figure

    axe = app.setupNormal(figure=fig)
    assert not axe


def test_setupNormal_3():
    app.ui.checkShowGrid.setChecked(True)
    app.ui.checkShowCrosshair.setChecked(True)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageMat.figure

    axe = app.setupNormal(figure=fig, header=header)
    assert axe


def test_setupNormal_4():
    app.ui.checkShowGrid.setChecked(False)
    app.ui.checkShowCrosshair.setChecked(False)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageMat.figure

    axe = app.setupNormal(figure=fig, header=header)
    assert axe


def test_stackImages_1():
    val = app.stackImages()
    assert val is None
    assert app.numberStack == 1


def test_stackImages_2():
    val = app.stackImages(5)
    assert val == 5
    assert app.numberStack == 1


def test_stackImages_3():
    app.imageStack = None
    app.stackImages(5)
    val = app.stackImages(3)
    assert val == 4
    assert app.numberStack == 2


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
    app.imageFileName = 'mw4/test/image/m51.fit'
    suc = app.showCurrent()
    assert suc


def test_showImage_4():
    app.ui.checkStackImages.setChecked(True)
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')
    app.imageFileName = 'mw4/test/image/m51.fit'
    suc = app.showCurrent()
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
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.exposeRaw()
            assert suc


def test_exposeImageDone_1(qtbot):
    app.ui.checkAutoSolve.setChecked(False)
    app.app.camera.signals.saved.connect(app.exposeImageDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        with qtbot.waitSignal(app.signals.showImage):
            suc = app.exposeImageDone()
            assert suc
    assert ['Exposed:  []', 0] == blocker.args


def test_exposeImageDone_2(qtbot):
    app.ui.checkAutoSolve.setChecked(True)
    app.app.camera.signals.saved.connect(app.exposeImageDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        with qtbot.waitSignal(app.signals.solveImage):
            suc = app.exposeImageDone()
            assert suc
    assert ['Exposed:  []', 0] == blocker.args


def test_exposeImage_1():
    app.app.camera.data = {}
    suc = app.exposeImage()
    assert suc


def test_exposeImageNDone_1(qtbot):
    app.ui.checkAutoSolve.setChecked(False)
    app.app.camera.signals.saved.connect(app.exposeImageDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        with qtbot.waitSignal(app.signals.showImage):
            suc = app.exposeImageNDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


def test_exposeImageNDone_2(qtbot):
    app.ui.checkAutoSolve.setChecked(True)
    app.app.camera.signals.saved.connect(app.exposeImageDone)
    with qtbot.waitSignal(app.app.message) as blocker:
        with qtbot.waitSignal(app.signals.solveImage):
            suc = app.exposeImageNDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


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
    assert ['Solving error: test', 2] == blocker.args


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
    assert ['Solved : Ra: 10:00:00 (10.000), Dec: +20:00:00 (20.000), ', 0] == blocker.args


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
        'solvedPath': 'test',
        'message': 'test',
    }

    app.app.astrometry.signals.done.connect(app.solveDone)
    with qtbot.waitSignal(app.signals.showImage):
        suc = app.solveDone(result=result)
        assert suc


def test_solveImage_1(qtbot):
    suc = app.solveImage()
    assert not suc


def test_solveImage_2(qtbot):
    suc = app.solveImage('test')
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

