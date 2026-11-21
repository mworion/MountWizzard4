# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
import shiboken6
from collections.abc import Iterator
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QWidget


def releaseAddonWindows(existingWindows: set[QWidget]) -> None:
    for window in QApplication.topLevelWidgets():
        if (
            shiboken6.isValid(window)
            and window not in existingWindows
            and window.objectName() == "MainWindow"
            and hasattr(window, "app")
            and hasattr(window, "ui")
        ):
            window.deleteLater()
            QCoreApplication.sendPostedEvents(window, QEvent.Type.DeferredDelete)


@pytest.fixture(scope="module", autouse=True)
def cleanupAddonWindows(qapp: QApplication) -> Iterator[None]:
    existingWindows = set(qapp.topLevelWidgets())
    yield
    releaseAddonWindows(existingWindows)
