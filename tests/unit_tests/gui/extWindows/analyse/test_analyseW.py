# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import gc
import json
import numpy as np
import pytest
from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    func = AnalyseWindow(app=makeApp(), title="Analyse")
    yield func
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    if "WindowAnalyse" in function.app.config:
        del function.app.config["WindowAnalyse"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["WindowAnalyse"] = {}

    function.storeConfig()


def test_closeEvent_1(function):
    with mock.patch.object(function, "show"), mock.patch.object(MWidget, "closeEvent"):
        function.showWindow()
        function.closeEvent(QCloseEvent)


def test_showWindow(function):
    with mock.patch.object(function, "show"):
        function.showWindow()


def test_showWindow_connectsSignalsOnce(function):
    with mock.patch.object(function, "show"), mock.patch.object(function, "drawAll") as drawAll:
        function.showWindow()
        function.showWindow()
        function.ui.showISO.clicked.emit()
        drawAll.assert_called_once()


def test_showWindow_connectsAnalyseSignalOnce(function):
    path = Path("test.model")
    with (
        mock.patch.object(function, "show"),
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(function, "processModel") as processModel,
    ):
        function.showWindow()
        function.showWindow()
        function.app.signals.ui.showAnalyse.emit(path)

    processModel.assert_called_once_with(path)


def test_colorChange(function):
    with mock.patch.object(function, "drawAll"):
        function.colorChange()


def test_loadModel_1(function):
    with (
        mock.patch.object(MWFileDialog, "getOpenFileName", return_value=Path("test.test")),
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(function, "processModel") as processModel,
    ):
        function.loadModel()
        processModel.assert_called_once()


def test_loadModel_2(function):
    with (
        mock.patch.object(MWFileDialog, "getOpenFileName", return_value=Path("test.test")),
        mock.patch.object(Path, "is_file", return_value=False),
        mock.patch.object(function, "processModel") as processModel,
    ):
        function.loadModel()
        processModel.assert_not_called()


def test_showAnalyse_1(function):
    with (
        mock.patch.object(function, "processModel") as processModel,
        mock.patch.object(Path, "is_file", return_value=True),
    ):
        function.showAnalyse(Path("test.test"))
        processModel.assert_called_once()


def test_showAnalyse_2(function):
    with (
        mock.patch.object(function, "processModel") as processModel,
        mock.patch.object(Path, "is_file", return_value=False),
    ):
        function.showAnalyse(Path("test.test"))
        processModel.assert_not_called()


def test_drawAll_1(function):
    with (
        mock.patch.object(function.generalPlots, "drawTab") as general,
        mock.patch.object(function.altAzPlots, "drawTab") as altAz,
        mock.patch.object(function.raDecPlots, "drawTab") as raDec,
        mock.patch.object(function.analyseData, "errorIndex", np.array([0])),
    ):
        function.drawAll()
    general.assert_called_once()
    altAz.assert_called_once()
    raDec.assert_called_once()


def test_composition(function: AnalyseWindow) -> None:
    assert AnalyseWindow.__bases__ == (MWidget,)
    assert not hasattr(function.analyseData, "parentWindow")
    assert not hasattr(function.analyseData, "ui")
    assert not hasattr(function.analyseData, "processModel")
    for tab in function.tabs:
        assert tab.data is function.analyseData
        assert tab.ui is function.ui
    assert len({id(plot) for tab in function.tabs for plot in tab.plots}) == 12


def test_horizonSignal(function: AnalyseWindow) -> None:
    function.ui.showHorizon.setChecked(True)
    with mock.patch.object(function.ui.raErrors, "drawHorizon") as drawHorizon:
        function.app.signals.hemisphere.redrawHorizon.emit()
    drawHorizon.assert_called_once_with(function.app.buildPoint.horizonP)


def test_closeResetsISO(function: AnalyseWindow) -> None:
    with (
        mock.patch.object(function, "storeConfig") as storeConfig,
        mock.patch.object(MWidget, "closeEvent"),
    ):
        function.closeEvent(QCloseEvent())
    storeConfig.assert_called_once()
    assert not function.ui.showISO.isChecked()


def test_loadRedrawsAllTabs(function: AnalyseWindow) -> None:
    function.showAnalyse(Path("tests/testData/test.model"))
    data = function.analyseData
    assert function.titleBar.title.text().endswith("test")
    np.testing.assert_array_equal(function.ui.scaleImage.scatterItem.getData()[0], data.errorIndex)
    np.testing.assert_array_equal(function.ui.raRawErrors.scatterItem.getData()[0], data.azimuth)
    np.testing.assert_array_equal(
        function.ui.raRawErrorsRef.scatterItem.getData()[0], data.angularPosRA
    )
    with mock.patch.object(function, "storeConfig"), mock.patch.object(MWidget, "closeEvent"):
        function.closeEvent(QCloseEvent())
    assert not function.ui.showISO.isChecked()


def test_processModelOrchestratesLoad(function: AnalyseWindow) -> None:
    path = Path("tests/testData/test.model")
    records = json.loads(path.read_text())
    calls = mock.Mock()
    with (
        mock.patch.object(function.analyseData, "loadModel", calls.loadModel),
        mock.patch.object(function, "writeGui", calls.writeGui),
        mock.patch.object(function, "drawAll", calls.drawAll),
    ):
        calls.loadModel.return_value = records
        function.processModel(path)
    assert calls.mock_calls == [
        mock.call.loadModel(path),
        mock.call.writeGui(records, path),
        mock.call.drawAll(),
    ]


def test_writeGui(function: AnalyseWindow) -> None:
    function.writeGui([{"astrometryApp": "ASTAP - version"}], Path("example.model"))
    assert function.ui.solver.text() == "ASTAP"
    assert function.titleBar.title.text().endswith("example")


def test_unloadedEvents(qapp: QApplication, makeApp) -> None:
    window = AnalyseWindow(makeApp(), "Analyse")
    window.app.signals.ui.colorChange.emit()
    window.ui.showISO.click()
    window.ui.showHorizon.click()
    window.ui.linkViews.click()
    window.drawAll()
    assert window.analyseData.errorIndex.size == 0


def test_processModelFailure(function: AnalyseWindow) -> None:
    with (
        mock.patch.object(function.analyseData, "loadModel", return_value=None),
        mock.patch.object(function, "writeGui") as writeGui,
        mock.patch.object(function, "drawAll") as drawAll,
    ):
        function.processModel(Path("missing.model"))
    writeGui.assert_not_called()
    drawAll.assert_not_called()


def test_readFailureDoesNotUpdateGui(function: AnalyseWindow) -> None:
    with (
        mock.patch("builtins.open", side_effect=PermissionError("cannot read")),
        mock.patch.object(function, "writeGui") as writeGui,
        mock.patch.object(function, "drawAll") as drawAll,
    ):
        function.processModel(Path("unreadable.model"))
    writeGui.assert_not_called()
    drawAll.assert_not_called()
