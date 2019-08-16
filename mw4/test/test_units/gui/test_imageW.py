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
# local import
from mw4.test.test_units.setupQt import setupQt
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.config['showImageWindow'] = True
    app.toggleImageWindow()
    yield
    os.remove(mwGlob['imageDir'] + '/test.fit')


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
            suc = app.imageW.selectImage()
            assert suc
            with qtbot.waitSignal(app.imageW.signals.show):
                suc = app.imageW.selectImage()
                assert suc
        assert ['Image [test] selected', 0] == blocker.args
        assert app.imageW.folder == 'c:/test'


def test_solveDone_1(qtbot):
    pass


def test_solveImage_1(qtbot):
    pass


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
    suc = app.imageW.stretchImage(image=image)
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
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupNormal()
    assert not axe


def test_setupNormal_2():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupNormal(figure=fig)
    assert not axe


def test_setupNormal_3():
    image = np.zeros([100, 100], dtype=np.uint8)
    header = fits.PrimaryHDU().header
    header['naxis'] = 2
    fig = app.imageW.imageMat.figure

    axe = app.imageW.setupNormal(figure=fig, header=header)
    assert axe


def test_showFitsImage_1():
    app.imageW.imageFileName = ''
    suc = app.imageW.showFitsImage()
    assert not suc


def test_showFitsImage_2():
    app.imageW.imageFileName = 'test'
    suc = app.imageW.showFitsImage()
    assert not suc


def test_showFitsImage_3():
    app.imageW.imageFileName = mwGlob['imageDir'] + '/m51.fit'
    suc = app.imageW.showFitsImage()
    assert suc


def test_showFitsImageExt_1():
    suc = app.imageW.showFitsFile()
    assert not suc


def test_showFitsImageExt_2():
    suc = app.imageW.showFitsFile(imagePath=mwGlob['imageDir'] + '/m51.fit')
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
        assert ['Exposing   3s  Bin: 2  Sub: 100%', 0] == blocker.args


def test_exposeRaw_2(qtbot):
    app.mainW.ui.expTime.setValue(1)
    app.mainW.ui.binning.setValue(1)
    app.mainW.ui.subFrame.setValue(10)
    with mock.patch.object(app.imaging,
                           'expose',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.imageW.exposeRaw()
            assert suc
        assert ['Exposing   1s  Bin: 1  Sub:  10%', 0] == blocker.args


def test_exposeImagingDone(qtbot):
    app.imaging.signals.saved.connect(app.imageW.exposeImageDone)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.imageW.exposeImageDone()
        assert suc
    assert ['Image exposed', 0] == blocker.args


def test_exposeImage_1():
    app.imaging.data = {}
    suc = app.imageW.exposeImage()
    assert not suc


def test_exposeImage_2():
    app.imaging.data = {'test': 'test'}
    with mock.patch.object(app.imaging,
                           'expose',
                           ):
        suc = app.imageW.exposeImage()
        assert suc


def test_exposeImageN_1():
    app.imaging.data = {}
    suc = app.imageW.exposeImageN()
    assert not suc


def test_exposeImageN_2():
    app.imaging.data = {'test': 'test'}
    with mock.patch.object(app.imaging,
                           'expose',
                           ):
        suc = app.imageW.exposeImageN()
        assert suc


def test_abortImage_1(qtbot):
    with mock.patch.object(app.imaging,
                           'abort',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.imageW.abortImage()
            assert suc
        assert ['Image exposing aborted', 2] == blocker.args


def test_abortImage_2(qtbot):
    app.imaging.signals.saved.connect(app.imageW.showFitsImage)
    app.imageW.ui.exposeN.setEnabled(True)
    app.imageW.ui.expose.setEnabled(False)
    app.imaging.signals.saved.connect(app.imageW.exposeRaw)
    with mock.patch.object(app.imaging,
                           'abort',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.imageW.abortImage()
            assert suc
        assert ['Image exposing aborted', 2] == blocker.args


def test_abortImage_3(qtbot):
    app.imaging.signals.saved.connect(app.imageW.showFitsImage)
    app.imageW.ui.exposeN.setEnabled(False)
    app.imageW.ui.expose.setEnabled(True)
    app.imaging.signals.saved.connect(app.imageW.exposeImageDone)
    with mock.patch.object(app.imaging,
                           'abort',
                           ):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.imageW.abortImage()
            assert suc
        assert ['Image exposing aborted', 2] == blocker.args
