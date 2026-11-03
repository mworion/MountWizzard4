# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.gui.styles.styles import Styles
from typing import Any


def pierColors(pierside: list[str], styles: Styles) -> list[list[int]]:
    return [styles.M_GREEN if p == "W" else styles.M_YELLOW for p in pierside]


def linkViews(plots: list[Any], isLinked: bool, linkY: bool) -> None:
    views = [plot.p[0].getViewBox() for plot in plots]
    for sourceView in views:
        for targetView in views:
            if sourceView == targetView:
                continue
            sourceView.setXLink(targetView if isLinked else None)
            if linkY:
                sourceView.setYLink(targetView if isLinked else None)
        sourceView.rightMouseRange()
