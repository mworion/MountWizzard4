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


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.config['showImageWindow'] = True
    app.toggleWindow(windowTag='showImageW')
    yield
    file = mwGlob['imageDir'] + '/test.fit'
    if os.path.isfile(file):
        os.remove(file)


def test_storeConfig_1():
    app.uiWindows['showImageW']['classObj'].storeConfig()


def test_initConfig_1():
    app.config['imageW'] = {}
    suc = app.uiWindows['showImageW']['classObj'].initConfig()
    assert suc


def test_initConfig_3():
    app.config['imageW'] = {}
    app.config['imageW']['winPosX'] = 10000
    app.config['imageW']['winPosY'] = 10000
    suc = app.uiWindows['showImageW']['classObj'].initConfig()
    assert suc


def test_showWindow_1(qtbot):
    suc = app.uiWindows['showImageW']['classObj'].showWindow()
    assert suc


def test_closeEvent_1(qtbot):
    with mock.patch.object(MWidget,
                           'closeEvent',
                           return_value=None):
        app.uiWindows['showImageW']['classObj'].closeEvent(None)
    app.uiWindows['showImageW']['classObj'].showWindow()


def test_setupDropDownGui():
    app.uiWindows['showImageW']['classObj'].setupDropDownGui()
    assert app.uiWindows['showImageW']['classObj'].ui.color.count() == 4
    assert app.uiWindows['showImageW']['classObj'].ui.zoom.count() == 5
    assert app.uiWindows['showImageW']['classObj'].ui.stretch.count() == 6


def test_updateWindowsStats_1():
    app.uiWindows['showImageW']['classObj'].deviceStat['expose'] = True
    app.uiWindows['showImageW']['classObj'].deviceStat['exposeN'] = True
    app.uiWindows['showImageW']['classObj'].deviceStat['solve'] = True
    app.mainW.deviceStat['imaging'] = True
    app.mainW.deviceStat['astrometry'] = True

    suc = app.uiWindows['showImageW']['classObj'].updateWindowsStats()
    assert suc


def test_updateWindowsStats_2():
    app.uiWindows['showImageW']['classObj'].deviceStat['expose'] = False
    app.uiWindows['showImageW']['classObj'].deviceStat['exposeN'] = False
    app.uiWindows['showImageW']['classObj'].deviceStat['solve'] = False
    app.mainW.deviceStat['imaging'] = False
    app.mainW.deviceStat['astrometry'] = False

    suc = app.uiWindows['showImageW']['classObj'].updateWindowsStats()
    assert suc


def test_selectImage_1():
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('test', '', '.fits')):
        suc = app.uiWindows['showImageW']['classObj'].selectImage()
        assert not suc


def test_selectImage_2(qtbot):
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('c:/test/test.fits', 'test', '.fits')):
        with qtbot.waitSignal(app.message) as blocker:
            with qtbot.waitSignal(app.uiWindows['showImageW']['classObj'].signals.showImage):
                suc = app.uiWindows['showImageW']['classObj'].selectImage()
                assert suc
        assert ['Image [test] selected', 0] == blocker.args
        assert app.uiWindows['showImageW']['classObj'].folder == 'c:/test'


def test_writeHeaderToGUI_1():
    header = fits.PrimaryHDU().header
    suc = app.uiWindows['showImageW']['classObj'].writeHeaderToGUI(header=header)
    assert suc == (False, None)


def test_writeHeaderToGUI_2():
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    header['CTYPE1'] = None
    suc = app.uiWindows['showImageW']['classObj'].writeHeaderToGUI(header=header)
    assert not suc[0]


def test_zoomImage_1():
    image = None
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    suc = app.uiWindows['showImageW']['classObj'].zoomImage(image=image, wcsObject=wcsObject)
    assert suc is None


def test_zoomImage_2():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    app.uiWindows['showImageW']['classObj'].ui.zoom.setCurrentIndex(0)
    suc = app.uiWindows['showImageW']['classObj'].zoomImage(image=image, wcsObject=wcsObject)
    assert suc.shape == (100, 100)


def test_zoomImage_3():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    app.uiWindows['showImageW']['classObj'].ui.zoom.setCurrentIndex(1)
    suc = app.uiWindows['showImageW']['classObj'].zoomImage(image=image, wcsObject=wcsObject)
    assert suc.shape == (50, 50)


def test_stretchImage_1():
    image = None
    suc = app.uiWindows['showImageW']['classObj'].stretchImage(image=image)
    assert suc is None


def test_stretchImage_2():
    image = np.zeros([100, 100], dtype=np.uint8)
    suc, a, b = app.uiWindows['showImageW']['classObj'].stretchImage(image=image)
    assert isinstance(suc, astropy.visualization.mpl_normalize.ImageNormalize)


def test_colorImage_1():
    app.uiWindows['showImageW']['classObj'].ui.color.setCurrentIndex(0)
    suc = app.uiWindows['showImageW']['classObj'].colorImage()
    assert suc == 'gray'


def test_colorImage_2():
    app.uiWindows['showImageW']['classObj'].ui.color.setCurrentIndex(1)
    suc = app.uiWindows['showImageW']['classObj'].colorImage()
    assert suc == 'plasma'


def test_setupDistorted_1():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    fig = app.uiWindows['showImageW']['classObj'].imageMat.figure

    axe = app.uiWindows['showImageW']['classObj'].setupDistorted()
    assert not axe


def test_setupDistorted_2():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    fig = app.uiWindows['showImageW']['classObj'].imageMat.figure

    axe = app.uiWindows['showImageW']['classObj'].setupDistorted(figure=fig)
    assert not axe


def test_setupDistorted_3():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    wcsObject = wcs.WCS(header)
    fig = app.uiWindows['showImageW']['classObj'].imageMat.figure

    axe = app.uiWindows['showImageW']['classObj'].setupDistorted(figure=fig, wcsObject=wcsObject)
    assert axe


def test_setupNormal_1():
    app.uiWindows['showImageW']['classObj'].ui.checkShowGrid.setChecked(True)
    app.uiWindows['showImageW']['classObj'].ui.checkShowCrosshair.setChecked(True)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.uiWindows['showImageW']['classObj'].imageMat.figure

    axe = app.uiWindows['showImageW']['classObj'].setupNormal()
    assert not axe


def test_setupNormal_2():
    app.uiWindows['showImageW']['classObj'].ui.checkShowGrid.setChecked(True)
    app.uiWindows['showImageW']['classObj'].ui.checkShowCrosshair.setChecked(True)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.uiWindows['showImageW']['classObj'].imageMat.figure

    axe = app.uiWindows['showImageW']['classObj'].setupNormal(figure=fig)
    assert not axe


def test_setupNormal_3():
    app.uiWindows['showImageW']['classObj'].ui.checkShowGrid.setChecked(True)
    app.uiWindows['showImageW']['classObj'].ui.checkShowCrosshair.setChecked(True)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.uiWindows['showImageW']['classObj'].imageMat.figure

    axe = app.uiWindows['showImageW']['classObj'].setupNormal(figure=fig, header=header)
    assert axe


def test_setupNormal_4():
    app.uiWindows['showImageW']['classObj'].ui.checkShowGrid.setChecked(False)
    app.uiWindows['showImageW']['classObj'].ui.checkShowCrosshair.setChecked(False)
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.uiWindows['showImageW']['classObj'].imageMat.figure

    axe = app.uiWindows['showImageW']['classObj'].setupNormal(figure=fig, header=header)
    assert axe


def test_stackImages_1():
    val = app.uiWindows['showImageW']['classObj'].stackImages()
    assert val is None
    assert app.uiWindows['showImageW']['classObj'].numberStack == 1


def test_stackImages_2():
    val = app.uiWindows['showImageW']['classObj'].stackImages(5)
    assert val == 5
    assert app.uiWindows['showImageW']['classObj'].numberStack == 1


def test_stackImages_3():
    app.uiWindows['showImageW']['classObj'].imageStack = None
    app.uiWindows['showImageW']['classObj'].stackImages(5)
    val = app.uiWindows['showImageW']['classObj'].stackImages(3)
    assert val == 4
    assert app.uiWindows['showImageW']['classObj'].numberStack == 2


def test_showImage_1():
    app.uiWindows['showImageW']['classObj'].imageFileName = ''
    suc = app.uiWindows['showImageW']['classObj'].showImage()
    assert not suc


def test_showImage_2():
    app.uiWindows['showImageW']['classObj'].imageFileName = 'test'
    suc = app.uiWindows['showImageW']['classObj'].showImage()
    assert not suc


def test_showImage_3():
    app.uiWindows['showImageW']['classObj'].imageFileName = mwGlob['imageDir'] + '/m51.fit'
    suc = app.uiWindows['showImageW']['classObj'].showCurrent()
    assert suc


def test_showImage_4():
    app.uiWindows['showImageW']['classObj'].ui.checkStackImages.setChecked(True)
    app.uiWindows['showImageW']['classObj'].imageFileName = mwGlob['imageDir'] + '/m51.fit'
    suc = app.uiWindows['showImageW']['classObj'].showCurrent()
    assert suc


def test_showCurrent_1():
    suc = app.uiWindows['showImageW']['classObj'].showCurrent()
    assert suc


def test_exposeRaw_1(qtbot):
    app.mainW.ui.expTime.setValue(3)
    app.mainW.ui.binning.setValue(2)
    app.mainW.ui.subFrame.setValue(100)
    with mock.patch.object(app.imaging,
                           'expose',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.uiWindows['showImageW']['classObj'].exposeRaw()
            assert suc


def test_exposeImageDone_1(qtbot):
    app.uiWindows['showImageW']['classObj'].ui.checkAutoSolve.setChecked(False)
    app.imaging.signals.saved.connect(app.uiWindows['showImageW']['classObj'].exposeImageDone)
    with qtbot.waitSignal(app.message) as blocker:
        with qtbot.waitSignal(app.uiWindows['showImageW']['classObj'].signals.showImage):
            suc = app.uiWindows['showImageW']['classObj'].exposeImageDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


def test_exposeImageDone_2(qtbot):
    app.uiWindows['showImageW']['classObj'].ui.checkAutoSolve.setChecked(True)
    app.imaging.signals.saved.connect(app.uiWindows['showImageW']['classObj'].exposeImageDone)
    with qtbot.waitSignal(app.message) as blocker:
        with qtbot.waitSignal(app.uiWindows['showImageW']['classObj'].signals.solveImage):
            suc = app.uiWindows['showImageW']['classObj'].exposeImageDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


def test_exposeImage_1():
    app.imaging.data = {}
    suc = app.uiWindows['showImageW']['classObj'].exposeImage()
    assert suc


def test_exposeImageNDone_1(qtbot):
    app.uiWindows['showImageW']['classObj'].ui.checkAutoSolve.setChecked(False)
    app.imaging.signals.saved.connect(app.uiWindows['showImageW']['classObj'].exposeImageDone)
    with qtbot.waitSignal(app.message) as blocker:
        with qtbot.waitSignal(app.uiWindows['showImageW']['classObj'].signals.showImage):
            suc = app.uiWindows['showImageW']['classObj'].exposeImageNDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


def test_exposeImageNDone_2(qtbot):
    app.uiWindows['showImageW']['classObj'].ui.checkAutoSolve.setChecked(True)
    app.imaging.signals.saved.connect(app.uiWindows['showImageW']['classObj'].exposeImageDone)
    with qtbot.waitSignal(app.message) as blocker:
        with qtbot.waitSignal(app.uiWindows['showImageW']['classObj'].signals.solveImage):
            suc = app.uiWindows['showImageW']['classObj'].exposeImageNDone()
            assert suc
    assert ['Exposed: []', 0] == blocker.args


def test_exposeImageN_1():
    app.imaging.data = {}
    suc = app.uiWindows['showImageW']['classObj'].exposeImageN()
    assert suc


def test_abortImage_1(qtbot):
    with mock.patch.object(app.imaging,
                           'abort',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.uiWindows['showImageW']['classObj'].abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_abortImage_2(qtbot):
    app.imaging.signals.saved.connect(app.uiWindows['showImageW']['classObj'].showImage)
    app.uiWindows['showImageW']['classObj'].ui.exposeN.setEnabled(True)
    app.uiWindows['showImageW']['classObj'].ui.expose.setEnabled(False)
    app.imaging.signals.saved.connect(app.uiWindows['showImageW']['classObj'].exposeRaw)
    with mock.patch.object(app.imaging,
                           'abort',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.uiWindows['showImageW']['classObj'].abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_abortImage_3(qtbot):
    app.imaging.signals.saved.connect(app.uiWindows['showImageW']['classObj'].showImage)
    app.uiWindows['showImageW']['classObj'].ui.exposeN.setEnabled(False)
    app.uiWindows['showImageW']['classObj'].ui.expose.setEnabled(True)
    app.imaging.signals.saved.connect(app.uiWindows['showImageW']['classObj'].exposeImageDone)
    with mock.patch.object(app.imaging,
                           'abort',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.uiWindows['showImageW']['classObj'].abortImage()
            assert suc
        assert ['Exposing aborted', 2] == blocker.args


def test_solveDone_1(qtbot):
    app.astrometry.signals.done.connect(app.uiWindows['showImageW']['classObj'].solveDone)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.uiWindows['showImageW']['classObj'].solveDone()
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

    app.astrometry.signals.done.connect(app.uiWindows['showImageW']['classObj'].solveDone)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.uiWindows['showImageW']['classObj'].solveDone(result=result)
        assert not suc
    assert ['Solving error: test', 2] == blocker.args


def test_solveDone_3(qtbot):
    app.uiWindows['showImageW']['classObj'].ui.checkAutoSolve.setChecked(False)
    app.uiWindows['showImageW']['classObj'].ui.checkStackImages.setChecked(True)
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

    app.astrometry.signals.done.connect(app.uiWindows['showImageW']['classObj'].solveDone)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.uiWindows['showImageW']['classObj'].solveDone(result=result)
        assert suc
    assert ['Solved : Ra: 10:00:00 (10.000), Dec: +20:00:00 (20.000), ', 0] == blocker.args


def test_solveDone_4(qtbot):
    app.uiWindows['showImageW']['classObj'].ui.checkAutoSolve.setChecked(True)
    app.uiWindows['showImageW']['classObj'].ui.checkStackImages.setChecked(False)
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

    app.astrometry.signals.done.connect(app.uiWindows['showImageW']['classObj'].solveDone)
    with qtbot.waitSignal(app.uiWindows['showImageW']['classObj'].signals.showImage):
        suc = app.uiWindows['showImageW']['classObj'].solveDone(result=result)
        assert suc


def test_solveImage_1(qtbot):
    suc = app.uiWindows['showImageW']['classObj'].solveImage()
    assert not suc


def test_solveImage_2(qtbot):
    suc = app.uiWindows['showImageW']['classObj'].solveImage('test')
    assert not suc


def test_solveImage_3(qtbot):
    file = mwGlob['imageDir'] + '/m51.fits'
    with mock.patch.object(app.astrometry,
                           'solveThreading'):
        suc = app.uiWindows['showImageW']['classObj'].solveImage(imagePath=file)
        assert suc


def test_solveCurrent(qtbot):
    with qtbot.waitSignal(app.uiWindows['showImageW']['classObj'].signals.solveImage):
        suc = app.uiWindows['showImageW']['classObj'].solveCurrent()
        assert suc


def test_abortSolve_1():
    suc = app.uiWindows['showImageW']['classObj'].abortSolve()
    assert not suc

