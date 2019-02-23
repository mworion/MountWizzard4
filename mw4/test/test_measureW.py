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
app, spy, mwGlob, test = setupQt()


def test_storeConfig_1():
    app.measureW.storeConfig()


def test_initConfig_1():
    app.config['measureW'] = {}
    suc = app.measureW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['measureW']
    suc = app.measureW.initConfig()
    assert not suc


def test_initConfig_3():
    app.config['measureW'] = {}
    app.config['measureW']['winPosX'] = 10000
    app.config['measureW']['winPosY'] = 10000
    suc = app.measureW.initConfig()
    assert suc


def test_closeEvent(qtbot):
    app.measureW.closeEvent(None)


def test_showWindow_1(qtbot):
    app.measureW.showStatus = False
    app.mainW.ui.checkMeasurement.setChecked(True)
    with mock.patch.object(app.measureW,
                           'show',
                           return_value=None):
        suc = app.measureW.showWindow()
        assert suc
        assert app.measureW.showStatus


def test_showWindow_2(qtbot):
    app.measureW.showStatus = False
    app.mainW.ui.checkMeasurement.setChecked(False)
    with mock.patch.object(app.measureW,
                           'show',
                           return_value=None):
        suc = app.measureW.showWindow()
        assert not suc
        assert not app.measureW.showStatus


def test_setupButtons_1():
    suc = app.measureW.setupButtons()
    assert suc
    assert app.measureW.ui.measureSet.count() == 3
    assert app.measureW.ui.timeSet.count() == 7

