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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import astropy

# external packages
import numpy as np
from PySide6.QtGui import QCloseEvent
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
    with mock.patch.object(function,
                           'setupButtons'):
        with mock.patch.object(function,
                               'drawMeasure'):
            function.initConfig()


def test_storeConfig_1(function):
    if 'measureW' in function.app.config:
        del function.app.config['measureW']

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config['measureW'] = {}
    function.storeConfig()


def test_showWindow_1(function):
    with mock.patch.object(function,
                           'show'):
        function.showWindow()


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.showWindow()
            function.closeEvent(QCloseEvent())


def test_colorChange(function):
    with mock.patch.object(function,
                           'drawMeasure'):
        with mock.patch.object(function.ui.measure,
                               'colorChange'):
            with mock.patch.object(function,
                                   'resetPlotItem'):
                function.colorChange()


def test_setTitle_1(function):
    function.app.measure.framework = ''
    function.setTitle()


def test_setTitle_2(function):
    function.app.measure.framework = 'csv'
    function.setTitle()


def test_setupButtons(function):
    function.setupButtons()


def test_constructPlotItem_1(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots['Axis Stability']
    x = function.app.measure.data['time'].astype('datetime64[s]').astype('int')
    function.constructPlotItem(plotItem, values, x)


def test_plotting_1(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots['Axis Stability']
    x = function.app.measure.data['time'].astype('datetime64[s]').astype('int')
    function.plotting(plotItem, values, x)


def test_resetPlotItem(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots['Axis Stability']
    function.resetPlotItem(plotItem, values)


def test_triggerUpdate(function):
    function.triggerUpdate()


def test_inUseMessage(function):
    with mock.patch.object(function,
                           'messageDialog'):
        function.inUseMessage()


def test_checkInUse_1(function):
    function.ui.set0.clear()
    function.ui.set0.addItem('No chart')
    function.ui.set0.addItem('test1')
    function.ui.set0.addItem('test2')
    function.ui.set0.setCurrentIndex(0)
    function.ui.set1.clear()
    function.ui.set1.addItem('No chart')
    function.ui.set1.addItem('test1')
    function.ui.set1.addItem('test2')
    function.ui.set1.setCurrentIndex(0)
    suc = function.checkInUse('set1', 1)
    assert not suc


def test_checkInUse_2(function):
    function.ui.set0.clear()
    function.ui.set0.addItem('No chart')
    function.ui.set0.addItem('test1')
    function.ui.set0.addItem('test2')
    function.ui.set0.setCurrentIndex(1)
    function.ui.set1.clear()
    function.ui.set1.addItem('No chart')
    function.ui.set1.addItem('test1')
    function.ui.set1.addItem('test2')
    suc = function.checkInUse('set1', 1)
    function.ui.set1.setCurrentIndex(0)
    assert suc


def test_changeChart_1(function):
    function.ui.set4.clear()
    function.ui.set4.addItem('No chart')
    function.ui.set0.setCurrentIndex(0)
    with mock.patch.object(function,
                           'drawMeasure'):
        with mock.patch.object(function,
                               'checkInUse',
                               return_value=False):
            function.changeChart('set4', 0)


def test_changeChart_2(function):
    function.ui.set0.clear()
    function.ui.set0.addItem('No chart')
    function.ui.set0.addItem('Voltage')
    function.ui.set0.setCurrentIndex(1)
    with mock.patch.object(function,
                           'inUseMessage'):
        with mock.patch.object(function,
                               'checkInUse',
                               return_value=True):
            function.changeChart('set0', 1)


def test_drawMeasure_1(function):
    temp = function.app.measure.data['time']
    function.app.measure.data['time'] = np.empty(shape=[0, 1], dtype='datetime64')
    suc = function.drawMeasure()
    assert not suc
    function.app.measure.data['time'] = temp


def test_drawMeasure_2(function):
    function.drawLock.lock()
    suc = function.drawMeasure()
    function.drawLock.unlock()
    assert not suc


def test_drawMeasure_3(function):
    function.ui.set0.clear()
    function.ui.set1.clear()
    function.ui.set2.clear()
    function.ui.set3.clear()
    function.ui.set4.clear()
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
    function.ui.set0.clear()
    function.ui.set1.clear()
    function.ui.set2.clear()
    function.ui.set3.clear()
    function.ui.set4.clear()
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
