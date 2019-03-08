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
from mw4.test.test_setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_storeConfig_1():
    app.imageW.storeConfig()


def test_initConfig_1():
    app.config['imageW'] = {}
    suc = app.imageW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['imageW']
    suc = app.imageW.initConfig()
    assert not suc


def test_initConfig_3():
    app.config['imageW'] = {}
    app.config['imageW']['winPosX'] = 10000
    app.config['imageW']['winPosY'] = 10000
    suc = app.imageW.initConfig()
    assert suc


def test_closeEvent(qtbot):
    app.imageW.closeEvent(None)


def test_toggleWindow1(qtbot):
    app.imageW.showStatus = True
    with mock.patch.object(app.imageW,
                           'close',
                           return_value=None):
        app.imageW.toggleWindow()
        assert not app.imageW.showStatus


def test_toggleWindow2(qtbot):
    app.imageW.showStatus = False
    with mock.patch.object(app.imageW,
                           'showWindow',
                           return_value=None):
        app.imageW.toggleWindow()
        assert app.imageW.showStatus


def test_showWindow_1(qtbot):
    with mock.patch.object(app.imageW,
                           'show',
                           return_value=None):
        suc = app.imageW.showWindow()
        assert suc
        assert app.imageW.showStatus


def test_setupDropDownGui():
    app.imageW.setupDropDownGui()
