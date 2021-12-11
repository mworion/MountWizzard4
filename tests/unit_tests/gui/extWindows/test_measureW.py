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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages
import numpy as np
from PyQt5.QtGui import QCloseEvent

# local import
from tests.unit_tests.unitTestAddOns.baseTestSetupExtWindows import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.measureW import MeasureWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = MeasureWindow(app=App())

    value = np.datetime64('2014-12-12 20:20:20')
    window.app.measure.devices['sensorWeather'] = ''
    window.app.measure.devices['onlineWeather'] = ''
    window.app.measure.devices['directWeather'] = ''
    window.app.measure.devices['power'] = ''
    window.app.measure.devices['skymeter'] = ''
    window.app.measure.devices['camera'] = ''
    window.app.measure.data = {
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
        'deltaRaJNow': np.full([5, 1], 1.0),
        'deltaDecJNow': np.full([5, 1], 1.0),
        'errorAngularPosRA': np.full([5, 1], 1.0),
        'errorAngularPosDEC': np.full([5, 1], 1.0),
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
        'cameraTemp': np.full([5, 1], 1.0),
    }
    window.app.measure.data['time'] = np.append(window.app.measure.data['time'], value)
    window.app.measure.data['time'] = np.append(window.app.measure.data['time'], value)
    window.app.measure.data['time'] = np.append(window.app.measure.data['time'], value)
    window.app.measure.data['time'] = np.append(window.app.measure.data['time'], value)
    window.app.measure.data['time'] = np.append(window.app.measure.data['time'], value)

    yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc

    function.app.config['measureW'] = {'winPosX': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_3(function):
    suc = function.initConfig()
    assert suc

    function.app.config['measureW'] = {'winPosY': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_4(function):
    function.app.config['measureW'] = {}
    function.app.config['measureW']['winPosX'] = 100
    function.app.config['measureW']['winPosY'] = 100
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'measureW' in function.app.config:
        del function.app.config['measureW']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['measureW'] = {}

    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_colorChange(function):
    with mock.patch.object(function,
                           'drawMeasure'):
        suc = function.colorChange()
        assert suc


def test_setupAxes_0(function):
    suc = function.setupAxes(numberPlots=0)
    assert not suc


def test_setupAxes_1(function):
    axe, fig = function.generateFlat(widget=function.measureMat)
    suc = function.setupAxes(figure=fig, numberPlots=-1)
    assert not suc


def test_setupAxes_2(function):
    axe, fig = function.generateFlat(widget=function.measureMat)
    suc = function.setupAxes(figure=fig, numberPlots=4)
    assert not suc


def test_setupAxes_3(function):
    axe, fig = function.generateFlat(widget=function.measureMat)
    suc = function.setupAxes(figure=fig, numberPlots=1)
    assert suc
    assert len(function.measureMat.figure.axes) == 1


def test_setupAxes_4(function):
    axe, fig = function.generateFlat(widget=function.measureMat)
    suc = function.setupAxes(figure=fig, numberPlots=4)
    assert not suc


def test_setupAxes_5(function):
    axe, fig = function.generateFlat(widget=function.measureMat)
    suc = function.setupAxes(figure=fig, numberPlots=2)
    assert suc
    assert len(function.measureMat.figure.axes) == 2


def test_plotRa_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotRa(axe=axe,
                          title='test',
                          data=function.app.measure.data,
                          cycle=1,
                          )
    assert suc


def test_plotDec_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotDec(axe=axe,
                           title='test',
                           data=function.app.measure.data,
                           cycle=1,
                           )
    assert suc


def test_plotErrorAngularPosRA_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotErrorAngularPosRa(axe=axe,
                                         title='test',
                                         data=function.app.measure.data,
                                         cycle=1,
                                         )
    assert suc


def test_plotErrorAngularPosDec_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotErrorAngularPosDec(axe=axe,
                                          title='test',
                                          data=function.app.measure.data,
                                          cycle=1,
                                          )
    assert suc


def test_plotTemperature_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotTemperature(axe=axe,
                                   title='test',
                                   data=function.app.measure.data,
                                   cycle=1,
                                   )
    assert suc


def test_plotTemperature_2(function):
    function.app.measure.devices = {}
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotTemperature(axe=axe,
                                   title='test',
                                   data=function.app.measure.data,
                                   cycle=1,
                                   )
    assert not suc


def test_plotPressure_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotPressure(axe=axe,
                                title='test',
                                data=function.app.measure.data,
                                cycle=1,
                                )
    assert suc


def test_plotPressure_2(function):
    function.app.measure.devices = {}
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotPressure(axe=axe,
                                title='test',
                                data=function.app.measure.data,
                                cycle=1,
                                )
    assert not suc


def test_plotHumidity_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotHumidity(axe=axe,
                                title='test',
                                data=function.app.measure.data,
                                cycle=1,
                                )
    assert suc


def test_plotHumidity_2(function):
    function.app.measure.devices = {}
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotHumidity(axe=axe,
                                title='test',
                                data=function.app.measure.data,
                                cycle=1,
                                )
    assert not suc


def test_plotSQR_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotSQR(axe=axe,
                           title='test',
                           data=function.app.measure.data,
                           cycle=1,
                           )
    assert suc


def test_plotSQR_2(function):
    function.app.measure.devices = {}
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotSQR(axe=axe,
                           title='test',
                           data=function.app.measure.data,
                           cycle=1,
                           )
    assert not suc


def test_plotVoltage_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotVoltage(axe=axe,
                               title='test',
                               data=function.app.measure.data,
                               cycle=1,
                               )
    assert suc


def test_plotVoltage_2(function):
    function.app.measure.devices = {}
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotVoltage(axe=axe,
                               title='test',
                               data=function.app.measure.data,
                               cycle=1,
                               )
    assert not suc


def test_plotCurrent_1(function):
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotCurrent(axe=axe,
                               title='test',
                               data=function.app.measure.data,
                               cycle=1,
                               )
    assert suc


def test_plotCurrent_2(function):
    function.app.measure.devices = {}
    fig = function.measureMat.figure
    function.setupAxes(figure=fig, numberPlots=1)
    axe = function.measureMat.figure.axes[0]
    suc = function.plotCurrent(axe=axe,
                               title='test',
                               data=function.app.measure.data,
                               cycle=1,
                               )
    assert not suc


def test_drawMeasure_1(function):
    function.ui.measureSet1.addItem('No chart')
    function.ui.measureSet2.addItem('No chart')
    function.ui.measureSet3.addItem('No chart')
    suc = function.drawMeasure()
    assert not suc


def test_drawMeasure_2(function):
    function.ui.measureSet1.addItem('No chart')
    function.ui.measureSet1.addItem('Pressure')
    function.ui.measureSet2.addItem('No chart')
    function.ui.measureSet3.addItem('No chart')
    function.ui.measureSet1.setCurrentIndex(1)
    suc = function.drawMeasure(1)
    assert suc


def test_drawMeasure_3(function):
    function.app.measure.data = {}
    function.ui.measureSet1.addItem('No chart')
    function.ui.measureSet2.addItem('No chart')
    function.ui.measureSet3.addItem('No chart')
    suc = function.drawMeasure()
    assert not suc


def test_drawMeasure_4(function):
    function.app.measure.data['time'] = [1, 2, 3]
    function.ui.measureSet1.addItem('No chart')
    function.ui.measureSet2.addItem('No chart')
    function.ui.measureSet3.addItem('No chart')
    suc = function.drawMeasure()
    assert not suc


def test_drawMeasure_5(function):
    function.ui.measureSet1.addItem('No chart')
    function.ui.measureSet2.addItem('No chart')
    function.ui.measureSet3.addItem('No chart')
    with mock.patch.object(function,
                           'setupAxes',
                           return_value=None):
        suc = function.drawMeasure()
        assert not suc


def test_drawMeasure_6(function):
    function.ui.measureSet1.addItem('Pressure')
    function.ui.measureSet2.addItem('No chart')
    function.ui.measureSet3.addItem('Pressure')

    suc = function.drawMeasure()
    assert suc
