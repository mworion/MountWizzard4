# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import gc
import numpy as np
import pytest
from collections.abc import Callable, Iterator
from contextlib import ExitStack
from mw4.base.appProtocol import AppProtocol
from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow
from mw4.gui.extWindows.analyse.raDecPlots import RaDecPlots
from PySide6.QtWidgets import QApplication
from unittest import mock


@pytest.fixture(scope="module")
def function(qapp: QApplication, makeApp: Callable[[], AppProtocol]) -> Iterator[RaDecPlots]:
    window = AnalyseWindow(makeApp(), "Analyse")
    data = window.analyseData
    data.pierside = ["W", "E"]
    data.angularPosRA = np.array([30, 60])
    data.angularPosDEC = np.array([-20, 40])
    for index, name in enumerate(("errorRA_S", "errorDEC_S", "errorRA", "errorDEC")):
        setattr(data, name, np.array([index + 1, index + 2]))
    yield window.raDecPlots
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


@pytest.mark.parametrize("enabled", [True, False])
def test_drawTab(function: RaDecPlots, enabled: bool) -> None:
    function.ui.linkViews.setChecked(enabled)
    function.drawTab()
    with ExitStack() as stack:
        plots = [stack.enter_context(mock.patch.object(plot, "plot")) for plot in function.plots]
        function.drawTab()
    for index, plot in enumerate(plots):
        expected = [index + 1, -(index + 2) if index % 2 else index + 2]
        np.testing.assert_array_equal(plot.call_args.args[1], expected)
        assert plot.call_args.kwargs["data"] == ["W", "E"]


def test_colorChange(function: RaDecPlots) -> None:
    with ExitStack() as stack:
        plots = [
            stack.enter_context(mock.patch.object(plot, "colorChange")) for plot in function.plots
        ]
        function.colorChange()
    for plot in plots:
        plot.assert_called_once()
