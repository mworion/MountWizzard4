# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import contextlib
import gc
import numpy as np
import pyqtgraph as pg
import pytest
import warnings
from mw4.gui.extWindows.measure.measureW import MeasureWindow
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = MeasureWindow(app=App(), title="Measure")
    yield func
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


@pytest.fixture(autouse=True)
def prepareFunctionState(function):
    value = np.datetime64("2014-12-12 20:20:20")
    measure = function.app.dReg["measure"].instance
    measure.framework = ""
    measure.data.clear()
    measure.data.update(
        {
            "time": np.array([value] * 5, dtype="datetime64[s]"),
            "directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE": np.array([1] * 5),
            "directWeather-WEATHER_PARAMETERS.WEATHER_PRESSURE": np.array([1] * 5),
            "directWeather-WEATHER_PARAMETERS.WEATHER_DEWPOINT": np.array([1] * 5),
            "directWeather-WEATHER_PARAMETERS.WEATHER_HUMIDITY": np.array([1] * 5),
        }
    )

    warningFilters = warnings.filters[:]
    warnings.simplefilter("ignore", RuntimeWarning)
    try:
        for setName in function.mSetUI:
            with contextlib.suppress(TypeError, RuntimeError):
                function.mSetUI[setName].currentIndexChanged.disconnect()

        for signal, slot in (
            (function.app.colorChange, function.colorChange),
            (function.app.timeMgr.update1s, function.drawMeasure),
            (function.app.timeMgr.update1s, function.setTitle),
        ):
            with contextlib.suppress(TypeError, RuntimeError):
                signal.disconnect(slot)
    finally:
        warnings.filters = warningFilters

    function.setupButtons()
    for setName in function.mSetUI:
        function.mSetUI[setName].setCurrentIndex(0)
    function.oldTitle = ["No chart"] * len(function.mSetUI)

    for chart in function.dataPlots.values():
        if not chart:
            continue
        chart["template"]["legendRef"] = None
        for line in chart["lineItems"].values():
            line["plotItemRef"] = None

    if function.drawLock.tryLock():
        function.drawLock.unlock()
    yield
    if function.drawLock.tryLock():
        function.drawLock.unlock()


def test_initConfig_1(function):
    with (
        mock.patch.object(function, "setupButtons"),
        mock.patch.object(function, "drawMeasure"),
    ):
        function.initConfig()


def test_storeConfig_1(function):
    if "WindowMeasure" in function.app.config:
        del function.app.config["WindowMeasure"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["WindowMeasure"] = {}
    function.storeConfig()


def test_showWindow_1(function):
    with mock.patch.object(function, "show"):
        function.showWindow()


def test_closeEvent_1(function):
    function.app.timeMgr.update1s.connect(function.drawMeasure)
    function.app.timeMgr.update1s.connect(function.setTitle)
    with (
        mock.patch.object(function, "show"),
        mock.patch.object(MWidget, "closeEvent"),
    ):
        function.closeEvent(QCloseEvent())


def test_colorChange(function):
    with (
        mock.patch.object(function, "drawMeasure"),
        mock.patch.object(function.ui.measure, "colorChange"),
        mock.patch.object(function, "resetPlotItem"),
    ):
        function.colorChange()


def test_setTitle_1(function):
    function.app.dReg["measure"].instance.framework = ""
    function.setTitle()


def test_setTitle_2(function):
    function.app.dReg["measure"].instance.framework = "csv"
    function.app.dReg["measure"].run["csv"].csvFilename = Path("csv")
    with mock.patch.object(function, "setWindowTitle") as mockTitle:
        function.setTitle()
    mockTitle.assert_called_once_with("Measuring:   csv")


def test_setupButtons(function):
    test = function.mSetUI
    function.mSetUI = {
        "set0": function.ui.set0,
    }

    with (
        mock.patch.object(function.ui.set0, "clear"),
        mock.patch.object(function.ui.set0, "setView"),
        mock.patch.object(function.ui.set0, "addItem"),
    ):
        function.setupButtons()
    function.mSetUI = test


def test_constructPlotItem_1(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots["Pressure"]
    x = function.app.dReg["measure"].data["time"].astype("datetime64[s]").astype("int")
    function.constructPlotItem(plotItem, values, x)


def test_plotting_1(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots["Pressure"]
    x = function.app.dReg["measure"].data["time"].astype("datetime64[s]").astype("int")
    function.plotting(plotItem, values, x)


def test_resetPlotItem_1(function):
    plotItem = pg.PlotItem()
    function.resetPlotItem(plotItem, {})


def test_resetPlotItem_2(function):
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
    with mock.patch("mw4.gui.extWindows.measure.measureW.MWMessageDialog.question"):
        function.inUseMessage()


def test_checkInUse_1(function):
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
        with (
            mock.patch.object(function, "drawMeasure"),
            mock.patch.object(function, "checkInUse", return_value=False),
        ):
            function.changeChart("set4", 0)


def test_changeChart_2(function):
    with mock.patch.object(function, "inUseMessage"):
        function.ui.set0.clear()
        function.ui.set0.addItem("No chart")
        function.ui.set0.addItem("Voltage")
        function.ui.set0.setCurrentIndex(1)
        with (
            mock.patch.object(function, "drawMeasure"),
            mock.patch.object(function, "inUseMessage"),
            mock.patch.object(function, "checkInUse", return_value=True),
        ):
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
        x = function.app.dReg["measure"].data["time"].astype("datetime64[s]").astype("int")
        with (
            mock.patch.object(function, "plotting"),
            mock.patch.object(function, "resetPlotItem"),
            mock.patch.object(function, "triggerUpdate"),
        ):
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
        x = function.app.dReg["measure"].data["time"].astype("datetime64[s]").astype("int")
        with (
            mock.patch.object(function, "plotting"),
            mock.patch.object(function, "resetPlotItem"),
            mock.patch.object(function, "triggerUpdate"),
        ):
            function.processDrawMeasure(x, False)


def test_drawMeasure_1(function):
    with mock.patch.object(function, "processDrawMeasure"):
        function.drawMeasure()
    function.drawLock.unlock()


def test_drawMeasure_2(function):
    function.drawLock.tryLock()
    with mock.patch.object(function, "processDrawMeasure"):
        function.drawMeasure()
    function.drawLock.unlock()


def test_drawMeasure_3(function):
    function.app.dReg["measure"].data["time"] = np.empty(shape=[0, 1], dtype="datetime64")
    with mock.patch.object(function, "processDrawMeasure"):
        function.drawMeasure()
    function.drawLock.unlock()


def test_setTitle_csvFramework(function):
    measureClass = function.app.dReg.d["measure"].instance
    measureClass.framework = "csv"
    measureClass.run["csv"].csvFilename = Path("test_data.csv")
    with mock.patch.object(function, "setWindowTitle") as mockTitle:
        function.setTitle()
    mockTitle.assert_called_once_with("Measuring:   test_data")
    measureClass.framework = ""


def test_plotting_withExistingPlotItem(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots["Pressure"]
    x = function.app.dReg["measure"].data["time"].astype("datetime64[s]").astype("int")
    values["template"]["legendRef"] = pg.LegendItem()
    firstKey = next(iter(values["lineItems"].keys()))
    values["lineItems"][firstKey]["plotItemRef"] = plotItem.plot()
    function.plotting(plotItem, values, x)


def test_plotting_newPlotItemWithLegend(function):
    plotItem = pg.PlotItem()
    values = function.dataPlots["Pressure"]
    x = function.app.dReg["measure"].data["time"].astype("datetime64[s]").astype("int")
    values["template"]["legendRef"] = pg.LegendItem()
    for line in values["lineItems"].values():
        line["plotItemRef"] = None
    function.plotting(plotItem, values, x)


def test_drawMeasure_realData(function):
    function.drawLock.tryLock()
    function.drawLock.unlock()
    with mock.patch.object(function, "processDrawMeasure"):
        function.drawMeasure()
    if function.drawLock.tryLock():
        function.drawLock.unlock()
