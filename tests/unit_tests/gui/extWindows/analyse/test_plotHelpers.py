# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pyqtgraph as pg
import pytest
from mw4.gui.extWindows.analyse.plotHelpers import linkViews, pierColors
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.pyqtgraph.gCustomViewBox import CustomViewBox
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot
from types import SimpleNamespace
from unittest import mock


def test_pierColors(qapp: QApplication) -> None:
    styles = Styles()
    assert pierColors(["W", "E", "W"], styles) == [
        styles.M_GREEN,
        styles.M_YELLOW,
        styles.M_GREEN,
    ]


@pytest.mark.parametrize("isLinked", [True, False])
@pytest.mark.parametrize("linkY", [True, False])
def test_linkViews(isLinked: bool, linkY: bool) -> None:
    views = [mock.Mock() for _ in range(4)]
    plots = [mock.Mock() for _ in range(4)]
    for plot, view in zip(plots, views, strict=True):
        plot.p = [mock.Mock()]
        plot.p[0].getViewBox.return_value = view
    linkViews(plots, isLinked, linkY)
    for index, source in enumerate(views):
        target = views[0] if isLinked and index else None
        source.setXLink.assert_called_once_with(target)
        if linkY:
            source.setYLink.assert_called_once_with(target)
        else:
            source.setYLink.assert_not_called()
        source.rightMouseRange.assert_called_once()


@pytest.mark.parametrize("linkY", [False, True])
def test_linkedRanges(qapp: QApplication, qtbot: QtBot, linkY: bool) -> None:
    widget = pg.GraphicsLayoutWidget()
    qtbot.addWidget(widget)
    items = [widget.addPlot(row=0, col=index, viewBox=CustomViewBox()) for index in range(4)]
    widget.resize(1200, 400)
    widget.show()
    qapp.processEvents()
    plots = [SimpleNamespace(p=[item]) for item in items]
    views = [item.getViewBox() for item in items]
    linkViews(plots, True, linkY)
    for index, view in enumerate(views):
        xRange = [10 * index, 10 * index + 5]
        yRange = [20 * index, 20 * index + 7]
        view.setRange(xRange=xRange, yRange=yRange, padding=0)
        qapp.processEvents()
        for other in views:
            assert other.viewRange()[0] == pytest.approx(xRange)
            if linkY:
                assert other.viewRange()[1] == pytest.approx(yRange)
    linkViews(plots, False, linkY)
    previous = views[0].viewRange()
    views[-1].setRange(xRange=[100, 105], yRange=[200, 207], padding=0)
    qapp.processEvents()
    assert views[0].viewRange() == previous
