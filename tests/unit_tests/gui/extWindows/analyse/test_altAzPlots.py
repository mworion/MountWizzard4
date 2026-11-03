# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import gc
import numpy as np
import pytest
from collections.abc import Callable, Iterator
from contextlib import ExitStack
from mw4.base.appProtocol import AppProtocol
from mw4.gui.extWindows.analyse.altAzPlots import AltAzPlots
from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow
from PySide6.QtWidgets import QApplication
from unittest import mock


@pytest.fixture(scope="module")
def function(qapp: QApplication, makeApp: Callable[[], AppProtocol]) -> Iterator[AltAzPlots]:
    window = AnalyseWindow(makeApp(), "Analyse")
    data = window.analyseData
    data.azimuth = np.array([20, 40, 60])
    data.altitude = np.array([30, 45, 70])
    for index, name in enumerate(("errorRA_S", "errorDEC_S", "errorRA", "errorDEC")):
        setattr(data, name, np.array([index, index + 1, index + 2]))
    yield window.altAzPlots
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


@pytest.mark.parametrize("enabled", [True, False])
def test_drawTab(function: AltAzPlots, enabled: bool) -> None:
    function.ui.showISO.setChecked(enabled)
    function.ui.linkViews.setChecked(enabled)
    function.ui.showHorizon.setChecked(enabled)
    function.drawTab()
    with ExitStack() as stack:
        plots = [stack.enter_context(mock.patch.object(plot, "plot")) for plot in function.plots]
        function.drawTab()
    for plot, name in zip(plots, ("errorRA_S", "errorDEC_S", "errorRA", "errorDEC"), strict=True):
        np.testing.assert_array_equal(plot.call_args.kwargs["z"], getattr(function.data, name))
        assert plot.call_args.kwargs["isoLevels"] == (20 if enabled else 0)


@pytest.mark.parametrize("enabled", [True, False])
def test_horizon(function: AltAzPlots, enabled: bool) -> None:
    function.ui.showHorizon.setChecked(enabled)
    with ExitStack() as stack:
        plots = [
            stack.enter_context(mock.patch.object(plot, "drawHorizon")) for plot in function.plots
        ]
        function.drawHorizon()
    for plot in plots:
        if enabled:
            plot.assert_called_once_with(function.app.buildPoint.horizonP)
        else:
            plot.assert_not_called()


def test_colorChange(function: AltAzPlots) -> None:
    with ExitStack() as stack:
        plots = [
            stack.enter_context(mock.patch.object(plot, "colorChange")) for plot in function.plots
        ]
        function.colorChange()
    for plot in plots:
        plot.assert_called_once()
