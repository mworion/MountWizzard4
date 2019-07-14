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
                           return_value=('test_mountwizzard', '', '.fits')):
        suc = app.imageW.selectImage()
        assert not suc


def test_selectImage_2(qtbot):
    with mock.patch.object(MWidget,
                           'openFile',
                           return_value=('c:/test_mountwizzard/test_mountwizzard.fits', 'test_mountwizzard', '.fits')):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.imageW.selectImage()
            assert suc
            with qtbot.waitSignal(app.imageW.signals.show):
                suc = app.imageW.selectImage()
                assert suc
        assert ['Image [test_mountwizzard] selected', 0] == blocker.args
        assert app.imageW.folder == 'c:/test_mountwizzard'


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
