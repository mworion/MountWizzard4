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
# external packages
import astropy
from astropy.io import fits
from astropy import wcs
import numpy as np
from skyfield.api import Angle
# local import
from mw4.test.test_units.setupQt import setupQt
from mw4.gui.widget import MWidget
from mw4.definitions import Solution, Solve


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.config['showImageWindow'] = True
    app.toggleImageWindow()
    yield
    file = mwGlob['imageDir'] + '/test.fit'
    if os.path.isfile(file):
        os.remove(file)


def test_storeConfig_1():
    app.imageW.storeConfig()


def test_initConfig_1():
    app.config['imageW'] = {}
    suc = app.imageW.initConfig()
    assert suc


def test_initConfig_3():
    app.config['imageW'] = {}
    app.config['imageW']['winPosX'] = 10000
    app.config['imageW']['winPosY'] = 10000
    suc = app.imageW.initConfig()
    assert suc


def test_showWindow_1(qtbot):
    suc = app.imageW.showWindow()
    assert suc


def test_closeEvent_1(qtbot):
    with mock.patch.object(MWidget,
                           'closeEvent',
                           return_value=None):
        app.imageW.closeEvent(None)
    app.imageW.showWindow()


def test_setupDropDownGui():
    app.imageW.setupDropDownGui()
    assert app.imageW.ui.color.count() == 4
    assert app.imageW.ui.zoom.count() == 5
    assert app.imageW.ui.stretch.count() == 6


def test_updateWindowsStats_1():
    app.imageW.deviceStat['expose'] = True
    app.imageW.deviceStat['exposeN'] = True
    app.imageW.deviceStat['solve'] = True
    app.mainW.deviceStat['imaging'] = True
    app.mainW.deviceStat['astrometry'] = True

    suc = app.imageW.updateWindowsStats()
    assert suc


def test_updateWindowsStats_2():
    app.imageW.deviceStat['expose'] = False
    app.imageW.deviceStat['exposeN'] = False
    app.imageW.deviceStat['solve'] = False
    app.mainW.deviceStat['imaging'] = False
    app.mainW.deviceStat['astrometry'] = False

    suc = app.imageW.updateWindowsStats()
    assert suc


def test_selectImage_1():
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('test', '', '.fits')):
        suc = app.imageW.selectImage()
        assert not suc


def test_selectImage_2(qtbot):
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('c:/test/test.fits', 'test', '.fits')):
        with qtbot.waitSignal(app.message) as blocker:
            with qtbot.waitSignal(app.imageW.signals.showImage):
                suc = app.imageW.selectImage()
                assert suc
        assert ['Image [test] selected', 0] == blocker.args
        assert app.imageW.folder == 'c:/test'


def test_writeHeaderToGUI_1():
    header = fits.PrimaryHDU().header
    suc = app.imageW.writeHeaderToGUI(header=header)
    assert suc == (False, None)


def test_writeHeaderToGUI_2():
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    header['CTYPE1'] = None
    suc = app.imageW.writeHeaderToGUI(header=header)
    assert not suc[0]


def test_zoomImage_1():
    image = None
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    suc = app.imageW.zoomImage(image=image, wcsObject=wcsObject)
    assert suc is None


def test_zoomImage_2():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    app.imageW.ui.zoom.setCurrentIndex(0)
    suc = app.imageW.zoomImage(image=image, wcsObject=wcsObject)
    assert suc.shape == (100, 100)


def test_zoomImage_3():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    app.imageW.ui.zoom.setCurrentIndex(1)
    suc = app.imageW.zoomImage(image=image, wcsObject=wcsObject)
    assert suc.shape == (50, 50)


def test_stretchImage_1():
    image = None
    suc = app.imageW.stretchImage(image=image)
    assert suc is None


def test_stretchImage_2():
    image = np.zeros([100, 100], dtype=np.uint8)
    suc, a, b = app.imageW.stretchImage(image=image)
    assert isinstance(suc, astropy.visualization.mpl_normalize.ImageNormalize)


def test_colorImage_1():
    app.imageW.ui.color.setCurrentIndex(0)
    suc = app.imageW.colorImage()
    assert suc == 'gray'


def test_colorImage_2():
    app.imageW.ui.color.setCurrentIndex(1)
    suc = app.imageW.colorImage()
    assert suc == 'plasma'


def test_setupDistorted_1():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupDistorted()
    assert not axe


def test_setupDistorted_2():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupDistorted(figure=fig)
    assert not axe


def test_setupDistorted_3():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupDistorted(figure=fig, wcsObject=wcsObject)
    assert axe


def test_setupNormal_1():
    app.imageW.ui.checkShowGrid.setChecked(True)
    app.imageW.ui.checkShowCrosshair.setChecked(True)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupNormal()
    assert not axe


def test_setupNormal_2():
    app.imageW.ui.checkShowGrid.setChecked(True)
    app.imageW.ui.checkShowCrosshair.setChecked(True)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupNormal(figure=fig)
    assert not axe


def test_setupNormal_3():
    app.imageW.ui.checkShowGrid.setChecked(True)
    app.imageW.ui.checkShowCrosshair.setChecked(True)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupNormal(figure=fig, header=header)
    assert axe


def test_setupNormal_4():
    app.imageW.ui.checkShowGrid.setChecked(False)
    app.imageW.ui.checkShowCrosshair.setChecked(False)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupNormal(figure=fig, header=header)
    assert axe


def test_stackImages_1():
    val = app.imageW.stackImages()
    assert val is None
    assert app.imageW.numberStack == 1


def test_stackImages_2():
    val = app.imageW.stackImages(5)
    assert val == 5
    assert app.imageW.numberStack == 1


def test_stackImages_3():
    app.imageW.imageStack = None
    app.imageW.stackImages(5)
    val = app.imageW.stackImages(3)
    assert val == 4
    assert app.imageW.numberStack == 2


def test_showImage_1():
    app.imageW.imageFileName = ''
    suc = app.imageW.showImage()
    assert not suc


def test_showImage_2():
    app.imageW.imageFileName = 'test'
    suc = app.imageW.showImage()
    assert not suc


def test_showImage_3():
    app.imageW.imageFileName = mwGlob['imageDir'] + '/m51.fit'
    suc = app.imageW.showCurrent()
    assert suc


def test_showImage_4():
    app.imageW.ui.checkStackImages.setChecked(True)
    app.imageW.imageFileName = mwGlob['imageDir'] + '/m51.fit'
    suc = app.imageW.showCurrent()
    assert suc


def test_showCurrent_1():
    suc = app.imageW.showCurrent()
    assert suc


def test_exposeRaw_1(qtbot):
    app.mainW.ui.expTime.setValue(3)
    app.mainW.ui.binning.setValue(2)
    app.mainW.ui.subFrame.setValue(100)
    with mock.patch.object(app.imaging,
                           'expose',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.imageW.exposeRaw()
            assert suc


def test_exposeImageDone_1(qtbot):
    app.imageW.ui.checkAutoSolve.setChecked(False)
    app.imaging.signals.saved.connect(app.imageW.exposeImageDone)
    with qtbot.waitSignal(app.message) as blocker:
        with qtbot.waitSignal(app.imageW.signals.showImage):
            suc = app.imageW.exposeImageDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


def test_exposeImageDone_2(qtbot):
    app.imageW.ui.checkAutoSolve.setChecked(True)
    app.imaging.signals.saved.connect(app.imageW.exposeImageDone)
    with qtbot.waitSignal(app.message) as blocker:
        with qtbot.waitSignal(app.imageW.signals.solveImage):
            suc = app.imageW.exposeImageDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


def test_exposeImage_1():
    app.imaging.data = {}
    suc = app.imageW.exposeImage()
    assert suc


def test_exposeImageNDone_1(qtbot):
    app.imageW.ui.checkAutoSolve.setChecked(False)
    app.imaging.signals.saved.connect(app.imageW.exposeImageDone)
    with qtbot.waitSignal(app.message) as blocker:
        with qtbot.waitSignal(app.imageW.signals.showImage):
            suc = app.imageW.exposeImageNDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


def test_exposeImageNDone_2(qtbot):
    app.imageW.ui.checkAutoSolve.setChecked(True)
    app.imaging.signals.saved.connect(app.imageW.exposeImageDone)
    with qtbot.waitSignal(app.message) as blocker:
        with qtbot.waitSignal(app.imageW.signals.solveImage):
            suc = app.imageW.exposeImageNDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


def test_exposeImageN_1():
    app.imaging.data = {}
    suc = app.imageW.exposeImageN()
    assert suc


def test_abortImage_1(qtbot):
    with mock.patch.object(app.imaging,
                           'abort',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.imageW.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_abortImage_2(qtbot):
    app.imaging.signals.saved.connect(app.imageW.showImage)
    app.imageW.ui.exposeN.setEnabled(True)
    app.imageW.ui.expose.setEnabled(False)
    app.imaging.signals.saved.connect(app.imageW.exposeRaw)
    with mock.patch.object(app.imaging,
                           'abort',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.imageW.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_abortImage_3(qtbot):
    app.imaging.signals.saved.connect(app.imageW.showImage)
    app.imageW.ui.exposeN.setEnabled(False)
    app.imageW.ui.expose.setEnabled(True)
    app.imaging.signals.saved.connect(app.imageW.exposeImageDone)
    with mock.patch.object(app.imaging,
                           'abort',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.imageW.abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_solveDone_1(qtbot):
    app.astrometry.signals.done.connect(app.imageW.solveDone)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.imageW.solveDone()
        assert not suc
    assert ['Solving error, result missing', 2] == blocker.args


def test_solveDone_2(qtbot):
    result = Solution(success=False,
                      solve=Solve(raJ2000=Angle(hours=10),
                                  decJ2000=Angle(degrees=20),
                                  angle=30,
                                  scale=1,
                                  error=3,
                                  flipped=False,
                                  path='test'),
                      message='test')

    app.astrometry.signals.done.connect(app.imageW.solveDone)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.imageW.solveDone(result=result)
        assert not suc
    assert ['Solving error: test', 2] == blocker.args


def test_solveDone_3(qtbot):
    app.imageW.ui.checkAutoSolve.setChecked(False)
    app.imageW.ui.checkStackImages.setChecked(True)
    result = Solution(success=True,
                      solve=Solve(raJ2000=Angle(hours=10),
                                  decJ2000=Angle(degrees=20),
                                  angle=30,
                                  scale=1,
                                  error=3,
                                  flipped=False,
                                  path='test'),
                      message='test')

    app.astrometry.signals.done.connect(app.imageW.solveDone)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.imageW.solveDone(result=result)
        assert suc
    assert ['Solved: [test]', 0] == blocker.args


def test_solveDone_4(qtbot):
    app.imageW.ui.checkAutoSolve.setChecked(True)
    app.imageW.ui.checkStackImages.setChecked(False)
    result = Solution(success=True,
                      solve=Solve(raJ2000=Angle(hours=10),
                                  decJ2000=Angle(degrees=20),
                                  angle=30,
                                  scale=1,
                                  error=3,
                                  flipped=False,
                                  path='test'),
                      message='test')

    app.astrometry.signals.done.connect(app.imageW.solveDone)
    with qtbot.waitSignal(app.imageW.signals.showImage):
        suc = app.imageW.solveDone(result=result)
        assert suc


def test_solveImage_1(qtbot):
    suc = app.imageW.solveImage()
    assert not suc


def test_solveImage_2(qtbot):
    suc = app.imageW.solveImage('test')
    assert not suc


def test_solveImage_3(qtbot):
    file = mwGlob['imageDir'] + '/m51.fits'
    with mock.patch.object(app.astrometry,
                           'solveThreading'):
        suc = app.imageW.solveImage(imagePath=file)
        assert suc


def test_solveCurrent(qtbot):
    with qtbot.waitSignal(app.imageW.signals.solveImage):
        suc = app.imageW.solveCurrent()
        assert suc


def test_abortSolve_1():
    suc = app.imageW.abortSolve()
    assert not suc

