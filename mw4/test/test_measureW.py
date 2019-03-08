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


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown_data():
    value = np.datetime64('2014-12-12 20:20:20')
    app.measure.data = {
        'time': np.empty(shape=[0, 1], dtype='datetime64'),
        'temp': np.full([5, 1], 1.0),
        'humidity': np.full([5, 1], 1.0),
        'press': np.full([5, 1], 1.0),
        'dewTemp': np.full([5, 1], 1.0),
        'sqr': np.full([5, 1], 1.0),
        'raJNow': np.full([5, 1], 1.0),
        'decJNow': np.full([5, 1], 1.0),
        'status': np.full([5, 1], 1.0),
    }
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measure.data['time'] = np.append(app.measure.data['time'], value)


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
    app.mainW.ui.measureDevice.setCurrentIndex(1)
    with mock.patch.object(app.measureW,
                           'show',
                           return_value=None):
        suc = app.measureW.showWindow()
        assert suc
        assert app.measureW.showStatus


def test_showWindow_2(qtbot):
    app.measureW.showStatus = False
    app.mainW.ui.measureDevice.setCurrentIndex(0)
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
    suc = app.measureW.clearPlot(numberPlots=0)
    assert not suc


def test_clearPlot_2():
    suc = app.measureW.clearPlot(numberPlots=4)
    assert not suc


def test_clearPlot_3():
    suc = app.measureW.clearPlot()
    assert not suc


def test_clearPlot_4():
    suc = app.measureW.clearPlot(numberPlots=1)
    assert suc
    assert len(app.measureW.measureMat.figure.axes) == 1


def test_clearPlot_5():
    suc = app.measureW.clearPlot(numberPlots=2)
    assert suc
    assert len(app.measureW.measureMat.figure.axes) == 2


def test_clearPlot_6():
    suc = app.measureW.clearPlot(numberPlots=3)
    assert not suc


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
    assert suc
