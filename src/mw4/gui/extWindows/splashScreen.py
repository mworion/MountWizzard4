# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from importlib.resources import as_file, files
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen, QWidget


class SplashScreen:
    def __init__(self, application: QApplication | None = None) -> None:
        self._qapp = application
        with as_file(files("mw4").joinpath("assets/icon/mw4.png")) as imageFile:
            self._pxm = QPixmap(str(imageFile))
        flags = Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.X11BypassWindowManagerHint
        self.qss = QSplashScreen(self._pxm, flags)
        self.qss.show()
        self.qss.raise_()
        QApplication.processEvents()

    def close(self) -> None:
        self.qss.close()

    def finish(self, qwid: QWidget) -> None:
        self.qss.finish(qwid)
