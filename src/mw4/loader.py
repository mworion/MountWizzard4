# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import locale
import sys
from importlib.resources import as_file, files
from mw4.base.bootstrap import (
    configureEnvironment,
    exceptHook,
    extractDataFiles,
    minimizeStartTerminal,
    setupWorkDirs,
    writeSystemInfo,
)
from mw4.gui.extWindows.splashScreen import SplashScreen
from mw4.mainApp import MountWizzard4
from pathlib import Path
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


def setAppIcon(app: QApplication) -> None:
    with as_file(files("mw4").joinpath("assets/icon/mw4.ico")) as iconFile:
        app.setWindowIcon(QIcon(str(iconFile)))


def main(test: int = 0, arguments: str = "") -> None:
    configureEnvironment()
    locale.setlocale(locale.LC_ALL, "")
    app = QApplication(sys.argv)
    minimizeStartTerminal()
    splash = SplashScreen(application=app)
    mwGlob = setupWorkDirs(Path.cwd())
    writeSystemInfo(mwGlob=mwGlob)
    extractDataFiles(mwGlob=mwGlob)
    sys.excepthook = exceptHook
    setAppIcon(app)
    mw4App = MountWizzard4(mwGlob, app, test, arguments)
    splash.close()
    ret = app.exec()
    del mw4App
    del app
    sys.exit(ret)


if __name__ == "__main__":
    main()
