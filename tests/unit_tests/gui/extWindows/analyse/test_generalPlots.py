# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import gc
import numpy as np
import pytest
from collections.abc import Callable, Iterator
from mw4.base.appProtocol import AppProtocol
from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow
from mw4.gui.extWindows.analyse.generalPlots import GeneralPlots
from PySide6.QtWidgets import QApplication
from unittest import mock


@pytest.fixture(scope="module")
def function(qapp: QApplication, makeApp: Callable[[], AppProtocol]) -> Iterator[GeneralPlots]:
    window = AnalyseWindow(makeApp(), "Analyse")
    data = window.analyseData
    data.errorRMS = np.array([0.3, 0.1, 0.2])
    data.errorIndex = np.array([4, 1, 7])
    data.pierside = ["E", "W", "E"]
    data.azimuth = np.array([20, 40, 60])
    data.altitude = np.array([30, 45, 70])
    data.errorAngle = np.array([0, 90, 180])
    data.scaleS = np.array([1.2, 1.3, 1.4])
    data.latitude = 48
    yield window.generalPlots
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_drawTab(function: GeneralPlots) -> None:
    function.drawTab()


def test_colorChange(function: GeneralPlots) -> None:
    with (
        mock.patch.object(function.ui.scaleImage, "colorChange") as scale,
        mock.patch.object(function.ui.modelPositions, "colorChange") as positions,
        mock.patch.object(function.ui.errorAscending, "colorChange") as ascending,
        mock.patch.object(function.ui.errorDistribution, "colorChange") as distribution,
    ):
        function.colorChange()
    for changed in (scale, positions, ascending, distribution):
        changed.assert_called_once()


def test_ascendingKeepsPointsAligned(function: GeneralPlots) -> None:
    with mock.patch.object(function.ui.errorAscending, "plot") as plot:
        function.drawErrorAscending()
    assert plot.call_args.args == ([1, 7, 4], [0.1, 0.2, 0.3])
    assert plot.call_args.kwargs["data"] == ["W", "E", "E"]
    window = function.parentWindow
    assert plot.call_args.kwargs["color"] == [window.M_GREEN, window.M_YELLOW, window.M_YELLOW]


def test_modelPositions(function: GeneralPlots) -> None:
    with (
        mock.patch.object(function.ui.modelPositions, "plot") as plot,
        mock.patch.object(function.ui.modelPositions, "plotLoc") as plotLoc,
    ):
        function.drawModelPositions()
    np.testing.assert_array_equal(plot.call_args.args[0], function.data.azimuth)
    np.testing.assert_array_equal(plot.call_args.kwargs["ang"], function.data.errorAngle)
    plotLoc.assert_called_once_with(48)


def test_paletteChange(function: GeneralPlots) -> None:
    function.parentWindow.colorSet = 1
    with mock.patch.object(function.ui.scaleImage, "plot") as plot:
        function.drawScaleImage()
    assert plot.call_args.kwargs["color"][1] == function.parentWindow.M_GREEN
    function.parentWindow.colorSet = 0


def test_misalignedArrays(function: GeneralPlots) -> None:
    with (
        mock.patch.object(function.data, "pierside", ["W"]),
        pytest.raises(ValueError, match="zip"),
    ):
        function.drawErrorAscending()
