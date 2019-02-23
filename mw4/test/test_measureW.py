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
import datetime
# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
import numpy as np
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


def test_clearPlot_1():
    suc = app.measureW.clearPlot(0)
    assert not suc


def test_clearPlot_2():
    suc = app.measureW.clearPlot(4)
    assert not suc


def test_clearPlot_3():
    suc = app.measureW.clearPlot()
    assert not suc


def test_clearPlot_4():
    suc = app.measureW.clearPlot(1)
    assert suc
    assert len(app.measureW.measureMat.figure.axes) == 3


def test_clearPlot_5():
    suc = app.measureW.clearPlot(3)
    assert suc
    assert len(app.measureW.measureMat.figure.axes) == 3


def test_drawRaDec_1():
    data = app.measure.data
    suc = app.measureW.drawRaDec(data=data, cycle=1)
    assert suc


def test_drawEnvironment_1():
    data = app.measure.data
    suc = app.measureW.drawEnvironment(data=data, cycle=1)
    assert suc


def test_drawSQR_1():
    data = app.measure.data
    suc = app.measureW.drawSQR(data=data, cycle=1)
    assert suc


def test_drawMeasure_1():
    app.measureW.showStatus = False
    suc = app.measureW.drawMeasure()
    assert not suc


def test_drawMeasure_2():
    app.measureW.showStatus = True
    suc = app.measureW.drawMeasure()
    assert not suc


def test_drawMeasure_3():
    value = np.datetime64('2014-12-12 20:20:20')
    app.measure.data = {
        'time': np.empty(shape=[0, 1], dtype='datetime64'),
        'temp': np.zeros(shape=[2, 1]),
        'humidity': np.zeros(shape=[2, 1]),
        'press': np.zeros(shape=[2, 1]),
        'dewTemp': np.zeros(shape=[2, 1]),
        'sqr': np.zeros(shape=[2, 1]),
        'raJNow': np.zeros(shape=[2, 1]),
        'decJNow': np.zeros(shape=[2, 1]),
        'status': np.zeros(shape=[2, 1]),
    }
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measureW.showStatus = True
    suc = app.measureW.drawMeasure()
    assert suc
