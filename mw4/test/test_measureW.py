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
    app.measureW.setupButtons()
    assert ' 8 min' == app.measureW.ui.tp0.text()
    assert '16 min' == app.measureW.ui.tp1.text()
    assert '33 min' == app.measureW.ui.tp2.text()
    assert ' 1 hrs' == app.measureW.ui.tp3.text()
    assert ' 2 hrs' == app.measureW.ui.tp4.text()
    assert ' 4 hrs' == app.measureW.ui.tp5.text()
    assert ' 8 hrs' == app.measureW.ui.tp6.text()


def test_setTimeWindow_1():
    app.measureW.setTimeWindow(0)
    assert 0 == app.measureW.timeIndex
    assert 'true' == app.measureW.ui.tp0.property('running')
    assert 'false' == app.measureW.ui.tp1.property('running')
    assert 'false' == app.measureW.ui.tp2.property('running')
    assert 'false' == app.measureW.ui.tp3.property('running')
    assert 'false' == app.measureW.ui.tp4.property('running')
    assert 'false' == app.measureW.ui.tp5.property('running')
    assert 'false' == app.measureW.ui.tp6.property('running')


def test_setTimeWindow_2():
    app.measureW.setTimeWindow(4)
    assert 4 == app.measureW.timeIndex
    assert 'false' == app.measureW.ui.tp0.property('running')
    assert 'false' == app.measureW.ui.tp1.property('running')
    assert 'false' == app.measureW.ui.tp2.property('running')
    assert 'false' == app.measureW.ui.tp3.property('running')
    assert 'true' == app.measureW.ui.tp4.property('running')
    assert 'false' == app.measureW.ui.tp5.property('running')
    assert 'false' == app.measureW.ui.tp6.property('running')


def test_setTimeWindow_3():
    suc = app.measureW.setTimeWindow(10)
    assert not suc


def test_setTimeWindow_4():
    suc = app.measureW.setTimeWindow(-10)
    assert not suc


def test_setMeasureSet_1():
    app.measureW.setMeasureSet(0)
    assert 0 == app.measureW.measureIndex
    assert 'true' == app.measureW.ui.ms0.property('running')
    assert 'false' == app.measureW.ui.ms1.property('running')
    assert 'false' == app.measureW.ui.ms2.property('running')


def test_setMeasureSet_2():
    app.measureW.setMeasureSet(2)
    assert 2 == app.measureW.measureIndex
    assert 'false' == app.measureW.ui.ms0.property('running')
    assert 'false' == app.measureW.ui.ms1.property('running')
    assert 'true' == app.measureW.ui.ms2.property('running')


def test_setMeasureSet_3():
    suc = app.measureW.setMeasureSet(5)
    assert not suc


def test_setMeasureSet_4():
    suc = app.measureW.setMeasureSet(-5)
    assert not suc


def test_openShowMeasureSet_1():
    suc = app.measureW.openShowMeasureSet(0)
    assert suc


def test_openShowMeasureSet_2():
    suc = app.measureW.openShowMeasureSet(9)
    assert not suc
