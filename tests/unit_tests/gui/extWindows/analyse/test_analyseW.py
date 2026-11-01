# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import gc
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
    def test():
        pass

    function.errorIndex = np.array([])
    function.charts = [test]
    with (
        mock.patch.object(function, "linkViewsAltAz"),
        mock.patch.object(function, "linkViewsRa"),
        mock.patch.object(function, "linkViewsDec"),
    ):
        function.drawAll()
