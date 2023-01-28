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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages
import numpy as np
from PyQt5.QtGui import QCloseEvent
import pyqtgraph as pg

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.measureW import MeasureWindow


@pytest.fixture(autouse=True, scope='function')
def function(qapp):

    func = MeasureWindow(app=App())

    value = np.datetime64('2014-12-12 20:20:20')
    func.app.measure.devices['sensorWeather'] = ''
    func.app.measure.devices['onlineWeather'] = ''
    func.app.measure.devices['directWeather'] = ''
    func.app.measure.devices['power'] = ''
    func.app.measure.devices['skymeter'] = ''
    func.app.measure.devices['camera'] = ''
    func.app.measure.data = {
        'time': np.empty(shape=[0, 1], dtype='datetime64'),
        'sensorWeatherTemp': np.array([1, 1, 1, 1, 1]),
        'sensorWeatherHum': np.array([1, 1, 1, 1, 1]),
        'sensorWeatherPress': np.array([1, 1, 1, 1, 1]),
        'sensorWeatherDew': np.array([1, 1, 1, 1, 1]),
        'onlineWeatherTemp': np.array([1, 1, 1, 1, 1]),
        'onlineWeatherHum': np.array([1, 1, 1, 1, 1]),
        'onlineWeatherPress': np.array([1, 1, 1, 1, 1]),
        'onlineWeatherDew': np.array([1, 1, 1, 1, 1]),
        'directWeatherTemp': np.array([1, 1, 1, 1, 1]),
        'directWeatherHum': np.array([1, 1, 1, 1, 1]),
        'directWeatherPress': np.array([1, 1, 1, 1, 1]),
        'directWeatherDew': np.array([1, 1, 1, 1, 1]),
        'skySQR': np.array([1, 1, 1, 1, 1]),
        'skyTemp': np.array([1, 1, 1, 1, 1]),
        'deltaRaJNow': np.array([1, 1, 1, 1, 1]),
        'deltaDecJNow': np.array([1, 1, 1, 1, 1]),
        'errorAngularPosRA': np.array([1, 1, 1, 1, 1]),
        'errorAngularPosDEC': np.array([1, 1, 1, 1, 1]),
        'status': np.array([1, 1, 1, 1, 1]),
        'powCurr1': np.array([1, 1, 1, 1, 1]),
        'powCurr2': np.array([1, 1, 1, 1, 1]),
        'powCurr3': np.array([1, 1, 1, 1, 1]),
        'powCurr4': np.array([1, 1, 1, 1, 1]),
        'powVolt': np.array([1, 1, 1, 1, 1]),
        'powCurr': np.array([1, 1, 1, 1, 1]),
        'powHum': np.array([1, 1, 1, 1, 1]),
        'powTemp': np.array([1, 1, 1, 1, 1]),
        'powDew': np.array([1, 1, 1, 1, 1]),
        'cameraTemp': np.array([1, 1, 1, 1, 1]),
    }
    func.app.measure.data['time'] = np.append(func.app.measure.data['time'], value)
    func.app.measure.data['time'] = np.append(func.app.measure.data['time'], value)
    func.app.measure.data['time'] = np.append(func.app.measure.data['time'], value)
    func.app.measure.data['time'] = np.append(func.app.measure.data['time'], value)
    func.app.measure.data['time'] = np.append(func.app.measure.data['time'], value)
    yield func


def test_initConfig_1(function):
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
        with mock.patch.object(function.ui.measure,
                               'colorChange'):
            with mock.patch.object(function,
                                   'resetPlotItem'):
                suc = function.colorChange()
        assert suc


def test_setTitle_1(function):
    function.app.measure.framework = ''
    suc = function.setTitle()
    assert suc


def test_setTitle_2(function):
    function.app.measure.framework = 'csv'
    suc = function.setTitle()
    assert suc


def test_setupButtons(function):
    suc = function.setupButtons()
    assert suc


def test_constructPlotItem_1(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots = {'gen': {'range': (0, 1, False)}}
    x = function.app.measure.data['time'].astype('datetime64[s]').astype('int')
    suc = function.constructPlotItem(plotItem, values, x)
    assert suc


def test_plotting_1(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots['Current']
    x = function.app.measure.data['time'].astype('datetime64[s]').astype('int')
    suc = function.plotting(plotItem, values, x)
    assert suc


def test_resetPlotItem(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots['Current']
    suc = function.resetPlotItem(plotItem, values)
    assert suc


def test_triggerUpdate(function):
    suc = function.triggerUpdate()
    assert suc


def test_inUseMessage(function):
    with mock.patch.object(function,
                           'messageDialog'):
        suc = function.inUseMessage()
        assert suc


def test_changeChart_1(function):
    def sender():
        return function.ui.set0

    function.sender = sender
    function.ui.set4.addItem('No chart')
    function.ui.set0.setCurrentIndex(0)
    with mock.patch.object(function,
                           'drawMeasure'):
        with mock.patch.object(function,
                               'inUseMessage'):
            suc = function.changeChart(0)
            assert suc


def test_changeChart_2(function):
    def sender():
        return function.ui.set1

    function.sender = sender
    function.ui.set4.addItem('test')
    function.ui.set0.addItem('No chart')
    function.ui.set0.addItem('test')
    function.ui.set0.setCurrentIndex(1)
    with mock.patch.object(function,
                           'drawMeasure'):
        with mock.patch.object(function,
                               'inUseMessage'):
            suc = function.changeChart(1)
            assert suc


def test_drawMeasure_1(function):
    function.app.measure.data['time'] = np.empty(shape=[0, 1], dtype='datetime64')
    suc = function.drawMeasure()
    assert not suc


def test_drawMeasure_2(function):
    function.drawLock.lock()
    suc = function.drawMeasure()
    function.drawLock.unlock()
    assert not suc


def test_drawMeasure_3(function):
    function.ui.set0.addItem('No chart')
    function.ui.set1.addItem('Current')
    function.ui.set2.addItem('Temperature')
    function.ui.set3.addItem('No chart')
    function.ui.set4.addItem('No chart')
    function.ui.set0.setCurrentIndex(0)
    function.ui.set1.setCurrentIndex(0)
    function.ui.set2.setCurrentIndex(0)
    function.ui.set3.setCurrentIndex(0)
    function.ui.set4.setCurrentIndex(0)
    function.oldTitle = [None, 'Voltage', None, None, None]
    with mock.patch.object(function,
                           'plotting'):
        with mock.patch.object(function,
                               'resetPlotItem'):
            with mock.patch.object(function,
                                   'triggerUpdate'):
                suc = function.drawMeasure()
                assert suc


def test_drawMeasure_4(function):
    function.ui.set0.addItem('No chart')
    function.ui.set1.addItem('No chart')
    function.ui.set2.addItem('No chart')
    function.ui.set3.addItem('No chart')
    function.ui.set4.addItem('Temperature')
    function.ui.set0.setCurrentIndex(0)
    function.ui.set1.setCurrentIndex(0)
    function.ui.set2.setCurrentIndex(0)
    function.ui.set3.setCurrentIndex(0)
    function.ui.set4.setCurrentIndex(0)
    function.oldTitle = [None, None, None, None, None]
    with mock.patch.object(function,
                           'plotting'):
        with mock.patch.object(function,
                               'resetPlotItem'):
            with mock.patch.object(function,
                                   'triggerUpdate'):
                suc = function.drawMeasure()
                assert suc
