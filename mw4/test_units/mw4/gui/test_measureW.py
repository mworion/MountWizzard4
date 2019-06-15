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
# Python  v3.7.3
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
import numpy as np
# local import
from mw4.test_units.mw4.test_setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.config['showMeasureW'] = True
    app.toggleMeasureWindow()
    yield


@pytest.fixture(autouse=True, scope='function')
def function_setup_teardown():
    value = np.datetime64('2014-12-12 20:20:20')
    app.measure.data = {
        'time': np.empty(shape=[0, 1], dtype='datetime64'),
        'envTemp': np.full([5, 1], 1.0),
        'envHum': np.full([5, 1], 1.0),
        'envPress': np.full([5, 1], 1.0),
        'envDew': np.full([5, 1], 1.0),
        'skySQR': np.full([5, 1], 1.0),
        'skyTemp': np.full([5, 1], 1.0),
        'raJNow': np.full([5, 1], 1.0),
        'decJNow': np.full([5, 1], 1.0),
        'status': np.full([5, 1], 1.0),
        'powCurr1': np.full([5, 1], 1.0),
        'powCurr2': np.full([5, 1], 1.0),
        'powCurr3': np.full([5, 1], 1.0),
        'powCurr4': np.full([5, 1], 1.0),
        'powVolt': np.full([5, 1], 1.0),
        'powCurr': np.full([5, 1], 1.0),
        'powHum': np.full([5, 1], 1.0),
        'powTemp': np.full([5, 1], 1.0),
        'powDew': np.full([5, 1], 1.0),
    }
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    app.measure.data['time'] = np.append(app.measure.data['time'], value)
    yield


def test_initConfig_1():
    with mock.patch.object(app.measureW,
                           'setupButtons'):
        suc = app.measureW.initConfig()
        assert suc


def test_initConfig_1a():
    with mock.patch.object(app.measureW,
                           'setupButtons'):
        suc = app.measureW.initConfig()
        assert suc


def test_initConfig_2():
    with mock.patch.object(app.measureW,
                           'setupButtons'):
        suc = app.measureW.initConfig()
        assert suc


def test_initConfig_3():
    app.config['measureW']['winPosX'] = 10000
    app.config['measureW']['winPosY'] = 10000
    with mock.patch.object(app.measureW,
                           'setupButtons',
                           return_value=True):
        suc = app.measureW.initConfig()
        assert suc


def test_storeConfig_1():
    app.measureW.storeConfig()


def test_setupAxes_1():
    fig = app.measureW.measureMat.figure
    suc = app.measureW.setupAxes(figure=fig, numberPlots=0)
    assert not suc


def test_setupAxes_2():
    fig = app.measureW.measureMat.figure
    suc = app.measureW.setupAxes(figure=fig, numberPlots=4)
    assert not suc


def test_setupAxes_3():
    fig = app.measureW.measureMat.figure
    suc = False
    # suc = app.measureW.setupAxes()
    assert not suc


def test_setupAxes_4():
    fig = app.measureW.measureMat.figure
    suc = app.measureW.setupAxes(figure=fig, numberPlots=1)
    assert suc
    assert len(app.measureW.measureMat.figure.axes) == 1


def test_setupAxes_5():
    fig = app.measureW.measureMat.figure
    suc = app.measureW.setupAxes(figure=fig, numberPlots=4)
    assert not suc


def test_setupAxes_6():
    fig = app.measureW.measureMat.figure
    suc = app.measureW.setupAxes(figure=fig, numberPlots=2)
    assert suc
    assert len(app.measureW.measureMat.figure.axes) == 2


def test_plotRa_1():
    fig = app.measureW.measureMat.figure
    app.measureW.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureW.measureMat.figure.axes[0]
    suc = app.measureW.plotRa(axe=axe,
                              title='test',
                              data=app.measure.data,
                              cycle=1,
                              )
    assert suc


def test_plotDec_1():
    fig = app.measureW.measureMat.figure
    app.measureW.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureW.measureMat.figure.axes[0]
    suc = app.measureW.plotDec(axe=axe,
                               title='test',
                               data=app.measure.data,
                               cycle=1,
                               )
    assert suc


def test_plotTemperature_1():
    fig = app.measureW.measureMat.figure
    app.measureW.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureW.measureMat.figure.axes[0]
    suc = app.measureW.plotTemperature(axe=axe,
                                       title='test',
                                       data=app.measure.data,
                                       cycle=1,
                                       )
    assert suc


def test_plotPressure_1():
    fig = app.measureW.measureMat.figure
    app.measureW.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureW.measureMat.figure.axes[0]
    suc = app.measureW.plotPressure(axe=axe,
                                    title='test',
                                    data=app.measure.data,
                                    cycle=1,
                                    )
    assert suc


def test_plotHumidity_1():
    fig = app.measureW.measureMat.figure
    app.measureW.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureW.measureMat.figure.axes[0]
    suc = app.measureW.plotHumidity(axe=axe,
                                    title='test',
                                    data=app.measure.data,
                                    cycle=1,
                                    )
    assert suc


def test_plotSQR_1():
    fig = app.measureW.measureMat.figure
    app.measureW.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureW.measureMat.figure.axes[0]
    suc = app.measureW.plotSQR(axe=axe,
                               title='test',
                               data=app.measure.data,
                               cycle=1,
                               )
    assert suc


def test_plotVoltage_1():
    fig = app.measureW.measureMat.figure
    app.measureW.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureW.measureMat.figure.axes[0]
    suc = app.measureW.plotVoltage(axe=axe,
                                   title='test',
                                   data=app.measure.data,
                                   cycle=1,
                                   )
    assert suc


def test_plotCurrent_1():
    fig = app.measureW.measureMat.figure
    app.measureW.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureW.measureMat.figure.axes[0]
    suc = app.measureW.plotCurrent(axe=axe,
                                   title='test',
                                   data=app.measure.data,
                                   cycle=1,
                                   )
    assert suc


def test_drawMeasure_1():
    suc = app.measureW.drawMeasure()
    assert not suc


def test_drawMeasure_2():
    app.measureW.ui.measureSet1.setCurrentIndex(1)
    suc = app.measureW.drawMeasure(1)
    assert suc
