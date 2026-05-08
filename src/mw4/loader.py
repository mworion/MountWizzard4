############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
"""Entry point for the MountWizzard4 application."""

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


def _setAppIcon(app: QApplication) -> None:
    """Load and set the application window icon."""
    with as_file(files("mw4").joinpath("data/icon/mw4.ico")) as iconFile:
        app.setWindowIcon(QIcon(str(iconFile)))


def main(test: int = 0) -> None:
    """Bootstrap and launch the MountWizzard4 application."""
    configureEnvironment()
    locale.setlocale(locale.LC_ALL, "")

    app = QApplication(sys.argv)
    minimizeStartTerminal()

    splash = SplashScreen(application=app)
    splash.showMessage("Start initialising")
    splash.setValue(0)

    mwGlob = setupWorkDirs(Path.cwd())

    splash.showMessage("Write system info to log")
    splash.setValue(40)
    writeSystemInfo(mwGlob=mwGlob)

    splash.showMessage("Extracting ephemeris and time data")
    splash.setValue(60)
    extractDataFiles(mwGlob=mwGlob)

    splash.showMessage("Initialize Application")
    splash.setValue(80)
    sys.excepthook = exceptHook
    _setAppIcon(app)

    MountWizzard4(mwGlob, app, test)

    splash.showMessage("Finishing loading")
    splash.setValue(100)
    splash.close()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
