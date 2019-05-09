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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp
from mw4.test_units.test_setupQt import setupQt
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
        suc = app.imageW.closeEvent(None)
        assert suc
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
            with qtbot.waitSignal(app.imageW.signalShowImage):
                suc = app.imageW.selectImage()
                assert suc
        assert ['Image [test] selected', 0] == blocker.args
        assert app.imageW.folder == 'c:/test'


def test_solveDone_1(qtbot):
    app.astrometry.signals.done.connect(app.imageW.solveDone)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.imageW.solveDone(('', 1))
        assert not suc
    assert ['Solving error', 2] == blocker.args


def test_solveDone_2(qtbot):
    app.astrometry.signals.done.connect(app.imageW.solveDone)
    with qtbot.assertNotEmitted(app.message):
        with qtbot.assertNotEmitted(app.imageW.signalShowImage):
            suc = app.imageW.solveDone(('test', 1))
            assert not suc


def test_solveImage_1(qtbot):
    suc = app.imageW.solveImage()
    assert suc
    app.astrometry.signals.done.disconnect(app.imageW.solveDone)
