############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import numpy as np
import pyqtgraph as pg
import pytest
import unittest.mock as mock
from mw4.gui.extWindows.measure.measureW import MeasureWindow
from mw4.gui.utilities.toolsQtWidget import MWidget
from pathlib import Path
from PySide6.QtGui import QCloseEvent
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="function")
def function(qapp):
    func = MeasureWindow(app=App())

    value = np.datetime64("2014-12-12 20:20:20")
    func.app.measure.devices["directWeather"] = ""
    func.app.measure.data = {
        "time": np.empty(shape=[0, 1], dtype="datetime64"),
        "directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE": np.array([1, 1, 1, 1, 1]),
        "directWeather-WEATHER_PARAMETERS.WEATHER_PRESSURE": np.array([1, 1, 1, 1, 1]),
        "directWeather-WEATHER_PARAMETERS.WEATHER_DEWPOINT": np.array([1, 1, 1, 1, 1]),
        "directWeather-WEATHER_PARAMETERS.WEATHER_HUMIDITY": np.array([1, 1, 1, 1, 1]),
    }
    func.app.measure.data["time"] = np.append(func.app.measure.data["time"], value)
    func.app.measure.data["time"] = np.append(func.app.measure.data["time"], value)
    func.app.measure.data["time"] = np.append(func.app.measure.data["time"], value)
    func.app.measure.data["time"] = np.append(func.app.measure.data["time"], value)
    func.app.measure.data["time"] = np.append(func.app.measure.data["time"], value)
    yield func
    func.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    with mock.patch.object(function, "setupButtons"):
        with mock.patch.object(function, "drawMeasure"):
            function.initConfig()


def test_storeConfig_1(function):
    if "measureW" in function.app.config:
        del function.app.config["measureW"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["measureW"] = {}
    function.storeConfig()


def test_showWindow_1(function):
    with mock.patch.object(function, "show"):
        function.showWindow()


def test_closeEvent_1(function):
    with mock.patch.object(function, "show"):
        with mock.patch.object(MWidget, "closeEvent"):
            function.showWindow()
            function.closeEvent(QCloseEvent())


def test_colorChange(function):
    with mock.patch.object(function, "drawMeasure"):
        with mock.patch.object(function.ui.measure, "colorChange"):
            with mock.patch.object(function, "resetPlotItem"):
                function.colorChange()


def test_setTitle_1(function):
    function.app.measure.framework = ""
    function.setTitle()


def test_setTitle_2(function):
    function.app.measure.framework = "csv"
    function.app.measure.run["csv"].csvFilename = Path("csv")
    function.setTitle()


def test_setupButtons(function):
    test = function.mSetUI
    function.mSetUI = {
        "set0": function.ui.set0,
    }

    with mock.patch.object(function.ui.set0, "clear"):
        with mock.patch.object(function.ui.set0, "setView"):
            with mock.patch.object(function.ui.set0, "addItem"):
                function.setupButtons()
    function.mSetUI = test


def test_constructPlotItem_1(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots["Current"]
    x = function.app.measure.data["time"].astype("datetime64[s]").astype("int")
    function.constructPlotItem(plotItem, values, x)


def test_plotting_1(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots["Current"]
    x = function.app.measure.data["time"].astype("datetime64[s]").astype("int")
    function.plotting(plotItem, values, x)


def test_resetPlotItem(function):
    class RemoveItem:
        def removeItem(self, item):
            pass

    def scene():
        return RemoveItem()

    plotItem = pg.PlotItem()
    plotItem.scene = scene
    chart = function.dataPlots["Axis Stability"]
    function.resetPlotItem(plotItem, chart)


def test_triggerUpdate(function):
    function.triggerUpdate()


def test_inUseMessage(function):
    with mock.patch.object(function, "messageDialog"):
        function.inUseMessage()


def test_checkInUse_1(function):
    with mock.patch.object(function, "messageDialog"):
        function.ui.set0.clear()
        function.ui.set0.addItem("No chart")
        function.ui.set0.addItem("test1")
        function.ui.set0.addItem("test2")
        function.ui.set0.setCurrentIndex(0)
        function.ui.set1.clear()
        function.ui.set1.addItem("No chart")
        function.ui.set1.addItem("test1")
        function.ui.set1.addItem("test2")
        function.ui.set1.setCurrentIndex(0)
        suc = function.checkInUse("set1", 1)
        assert not suc


def test_checkInUse_2(function):
    with mock.patch.object(function, "messageDialog"):
        function.ui.set0.clear()
        function.ui.set0.addItem("No chart")
        function.ui.set0.addItem("test1")
        function.ui.set0.addItem("test2")
        function.ui.set0.setCurrentIndex(1)
        function.ui.set1.clear()
        function.ui.set1.addItem("No chart")
        function.ui.set1.addItem("test1")
        function.ui.set1.addItem("test2")
        function.ui.set1.setCurrentIndex(0)
        suc = function.checkInUse("set1", 1)
        assert suc


def test_changeChart_1(function):
    with mock.patch.object(function, "inUseMessage"):
        function.ui.set4.clear()
        function.ui.set4.addItem("No chart")
        function.ui.set0.setCurrentIndex(0)
        with mock.patch.object(function, "drawMeasure"):
            with mock.patch.object(function, "checkInUse", return_value=False):
                function.changeChart("set4", 0)


def test_changeChart_2(function):
    with mock.patch.object(function, "inUseMessage"):
        function.ui.set0.clear()
        function.ui.set0.addItem("No chart")
        function.ui.set0.addItem("Voltage")
        function.ui.set0.setCurrentIndex(1)
        with mock.patch.object(function, "drawMeasure"):
            with mock.patch.object(function, "inUseMessage"):
                with mock.patch.object(function, "checkInUse", return_value=True):
                    function.changeChart("set0", 1)
                    function.drawLock.unlock()


def test_processDrawMeasure_1(function):
    with mock.patch.object(function, "inUseMessage"):
        function.ui.set0.clear()
        function.ui.set1.clear()
        function.ui.set2.clear()
        function.ui.set3.clear()
        function.ui.set4.clear()
        function.ui.set0.addItem("No chart")
        function.ui.set1.addItem("Current")
        function.ui.set2.addItem("Temperature")
        function.ui.set3.addItem("No chart")
        function.ui.set4.addItem("No chart")
        function.ui.set0.setCurrentIndex(0)
        function.ui.set1.setCurrentIndex(0)
        function.ui.set2.setCurrentIndex(0)
        function.ui.set3.setCurrentIndex(0)
        function.ui.set4.setCurrentIndex(0)
        function.oldTitle = ["No chart", "Voltage", "No chart", "No chart", "No chart"]
        function.app.measure.data["time"] = np.empty(shape=[0, 1], dtype="datetime64")
        x = function.app.measure.data["time"].astype("datetime64[s]").astype("int")
        with mock.patch.object(function, "plotting"):
            with mock.patch.object(function, "resetPlotItem"):
                with mock.patch.object(function, "triggerUpdate"):
                    function.processDrawMeasure(x, True)


def test_processDrawMeasure_2(function):
    with mock.patch.object(function, "inUseMessage"):
        function.ui.set0.clear()
        function.ui.set1.clear()
        function.ui.set2.clear()
        function.ui.set3.clear()
        function.ui.set4.clear()
        function.ui.set0.addItem("No chart")
        function.ui.set1.addItem("No chart")
        function.ui.set2.addItem("No chart")
        function.ui.set3.addItem("No chart")
        function.ui.set4.addItem("Temperature")
        function.ui.set0.setCurrentIndex(0)
        function.ui.set1.setCurrentIndex(0)
        function.ui.set2.setCurrentIndex(0)
        function.ui.set3.setCurrentIndex(0)
        function.ui.set4.setCurrentIndex(0)
        function.oldTitle = ["No chart"] * 5
        function.app.measure.data["time"] = np.empty(shape=[0, 1], dtype="datetime64")
        x = function.app.measure.data["time"].astype("datetime64[s]").astype("int")
        with mock.patch.object(function, "plotting"):
            with mock.patch.object(function, "resetPlotItem"):
                with mock.patch.object(function, "triggerUpdate"):
                    function.processDrawMeasure(x, False)


def test_drawMeasure_1(function):
    temp = function.app.measure.data["time"]
    function.app.measure.data["time"] = np.empty(shape=[0, 1], dtype="datetime64")
    with mock.patch.object(function, "processDrawMeasure"):
        function.drawMeasure()
    function.app.measure.data["time"] = temp
    function.drawLock.unlock()


def test_drawMeasure_2(function):
    function.drawLock.tryLock()
    with mock.patch.object(function, "processDrawMeasure"):
        function.drawMeasure()
    function.drawLock.unlock()


def test_drawMeasure_3(function):
    with mock.patch.object(function, "processDrawMeasure"):
        function.drawMeasure()
    function.drawLock.unlock()
