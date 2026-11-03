# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.gui.extWindows.analyse.plotHelpers import linkViews, pierColors
from mw4.gui.styles.styles import Styles
from PySide6.QtWidgets import QApplication
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
    views = [mock.Mock(), mock.Mock()]
    plots = [mock.Mock(), mock.Mock()]
    for plot, view in zip(plots, views, strict=True):
        plot.p = [mock.Mock()]
        plot.p[0].getViewBox.return_value = view
    linkViews(plots, isLinked, linkY)
    for source, target in (views, views[::-1]):
        source.setXLink.assert_called_once_with(target if isLinked else None)
        if linkY:
            source.setYLink.assert_called_once_with(target if isLinked else None)
        else:
            source.setYLink.assert_not_called()
        source.rightMouseRange.assert_called_once()
