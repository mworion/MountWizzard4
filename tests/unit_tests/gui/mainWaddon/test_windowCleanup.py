# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import shiboken6
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QApplication, QWidget
from tests.unit_tests.gui.mainWaddon.conftest import releaseAddonWindows
from types import SimpleNamespace


def test_releaseAddonWindows(qapp: QApplication) -> None:
    existingWindow = QWidget()
    existingWindow.setObjectName("MainWindow")
    existingWindow.app = SimpleNamespace()
    existingWindow.ui = SimpleNamespace()
    existingWindows = set(qapp.topLevelWidgets())

    window = QWidget()
    window.app = SimpleNamespace()
    window.ui = Ui_MainWindow()
    window.ui.setupUi(window)
    plot = window.ui.twilight
    label = plot.p[0].titleLabel

    releaseAddonWindows(existingWindows)

    assert not shiboken6.isValid(window)
    assert not shiboken6.isValid(plot)
    assert not shiboken6.isValid(label)
    assert shiboken6.isValid(existingWindow)
    existingWindow.deleteLater()
