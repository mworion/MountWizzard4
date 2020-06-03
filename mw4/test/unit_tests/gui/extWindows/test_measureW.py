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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
from queue import Queue
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
import numpy as np

# local import
from mw4.gui.measureW import MeasureWindow
from mw4.measure.measure import MeasureData


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app

    class Test1():
        pass

    class Test(QObject):
        config = {'mainW': {}}
        update1s = pyqtSignal()
        messageQueue = Queue()
        measure = MeasureData(app=Test1())
        uiWindows = {'showMeasureW': {}}

    with mock.patch.object(MeasureWindow,
                           'show'):
        app = MeasureWindow(app=Test())

    value = np.datetime64('2014-12-12 20:20:20')
    app.app.measure.devices['sensorWeather'] = ''
    app.app.measure.devices['onlineWeather'] = ''
    app.app.measure.devices['directWeather'] = ''
    app.app.measure.devices['power'] = ''
    app.app.measure.devices['skymeter'] = ''
    app.app.measure.data = {
        'time': np.empty(shape=[0, 1], dtype='datetime64'),
        'sensorWeatherTemp': np.full([5, 1], 1.0),
        'sensorWeatherHum': np.full([5, 1], 1.0),
        'sensorWeatherPress': np.full([5, 1], 1.0),
        'sensorWeatherDew': np.full([5, 1], 1.0),
        'onlineWeatherTemp': np.full([5, 1], 1.0),
        'onlineWeatherHum': np.full([5, 1], 1.0),
        'onlineWeatherPress': np.full([5, 1], 1.0),
        'onlineWeatherDew': np.full([5, 1], 1.0),
        'directWeatherTemp': np.full([5, 1], 1.0),
        'directWeatherHum': np.full([5, 1], 1.0),
        'directWeatherPress': np.full([5, 1], 1.0),
        'directWeatherDew': np.full([5, 1], 1.0),
        'skySQR': np.full([5, 1], 1.0),
        'skyTemp': np.full([5, 1], 1.0),
        'raJNow': np.full([5, 1], 1.0),
        'decJNow': np.full([5, 1], 1.0),
        'angularPosRA': np.full([5, 1], 1.0),
        'angularPosDEC': np.full([5, 1], 1.0),
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
    app.app.measure.data['time'] = np.append(app.app.measure.data['time'], value)
    app.app.measure.data['time'] = np.append(app.app.measure.data['time'], value)
    app.app.measure.data['time'] = np.append(app.app.measure.data['time'], value)
    app.app.measure.data['time'] = np.append(app.app.measure.data['time'], value)
    app.app.measure.data['time'] = np.append(app.app.measure.data['time'], value)

    app.app.config['showMeasureW'] = True

    qtbot.addWidget(app)

    yield


def test_initConfig_1(qtbot):
    with mock.patch.object(app,
                           'setupButtons'):
        suc = app.initConfig()
        assert suc


def test_initConfig_1a():
    with mock.patch.object(app,
                           'setupButtons'):
        suc = app.initConfig()
        assert suc


def test_initConfig_2():
    with mock.patch.object(app,
                           'setupButtons'):
        suc = app.initConfig()
        assert suc


def test_initConfig_3():
    app.app.config['measureW']['winPosX'] = 10000
    app.app.config['measureW']['winPosY'] = 10000
    with mock.patch.object(app,
                           'setupButtons',
                           return_value=True):
        suc = app.initConfig()
        assert suc


def test_storeConfig_1():
    app.storeConfig()


def test_setupAxes_1():
    fig = app.measureMat.figure
    suc = app.setupAxes(figure=fig, numberPlots=0)
    assert not suc


def test_setupAxes_2():
    fig = app.measureMat.figure
    suc = app.setupAxes(figure=fig, numberPlots=4)
    assert not suc


def test_setupAxes_4():
    fig = app.measureMat.figure
    suc = app.setupAxes(figure=fig, numberPlots=1)
    assert suc
    assert len(app.measureMat.figure.axes) == 1


def test_setupAxes_5():
    fig = app.measureMat.figure
    suc = app.setupAxes(figure=fig, numberPlots=4)
    assert not suc


def test_setupAxes_6():
    fig = app.measureMat.figure
    suc = app.setupAxes(figure=fig, numberPlots=2)
    assert suc
    assert len(app.measureMat.figure.axes) == 2


def test_plotRa_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotRa(axe=axe,
                     title='test',
                     data=app.app.measure.data,
                     cycle=1,
                     )
    assert suc


def test_plotDec_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotDec(axe=axe,
                      title='test',
                      data=app.app.measure.data,
                      cycle=1,
                      )
    assert suc


def test_plotAngularPosRA_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotAngularPosRa(axe=axe,
                               title='test',
                               data=app.app.measure.data,
                               cycle=1,
                               )
    assert suc


def test_plotAngularPosDec_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotAngularPosDec(axe=axe,
                                title='test',
                                data=app.app.measure.data,
                                cycle=1,
                                )
    assert suc


def test_plotTemperature_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotTemperature(axe=axe,
                              title='test',
                              data=app.app.measure.data,
                              cycle=1,
                              )
    assert suc


def test_plotPressure_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotPressure(axe=axe,
                           title='test',
                           data=app.app.measure.data,
                           cycle=1,
                           )
    assert suc


def test_plotHumidity_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotHumidity(axe=axe,
                           title='test',
                           data=app.app.measure.data,
                           cycle=1,
                           )
    assert suc


def test_plotSQR_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotSQR(axe=axe,
                      title='test',
                      data=app.app.measure.data,
                      cycle=1,
                      )
    assert suc


def test_plotVoltage_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotVoltage(axe=axe,
                          title='test',
                          data=app.app.measure.data,
                          cycle=1,
                          )
    assert suc


def test_plotCurrent_1():
    fig = app.measureMat.figure
    app.setupAxes(figure=fig, numberPlots=1)
    axe = app.measureMat.figure.axes[0]
    suc = app.plotCurrent(axe=axe,
                          title='test',
                          data=app.app.measure.data,
                          cycle=1,
                          )
    assert suc


def test_drawMeasure_1():
    suc = app.drawMeasure()
    assert not suc


def test_drawMeasure_2():
    app.ui.measureSet1.setCurrentIndex(1)
    suc = app.drawMeasure(1)
    assert suc
