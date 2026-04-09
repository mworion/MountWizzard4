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
# Licence APL2.0
#
###########################################################
import faulthandler
import locale
import logging
import os
import platform
import PySide6
import shutil
import socket
import sys
import traceback
import warnings
from astropy.utils import data, iers
from astropy.wcs import FITSFixedWarning
from importlib.metadata import version
from importlib.resources import as_file, files
from mw4.base.loggerMW import setupLogging
from mw4.gui.utilities.splashScreen import SplashScreen
from mw4.mainApp import MountWizzard4
from pathlib import Path
from PySide6.QtCore import qVersion
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

faulthandler.enable()
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FITSFixedWarning)

iers.conf.auto_download = False
data.conf.allow_internet = False
setupLogging()
log = logging.getLogger("MW4")


def except_hook(typeException, valueException, tbackException) -> None:
    """ """
    result = traceback.format_exception(typeException, valueException, tbackException)
    log.critical("")
    log.critical("Logging an uncatched Exception")
    log.critical("")
    for i in range(0, len(result)):
        log.critical(result[i].replace("\n", ""))

    log.critical("")
    sys.__excepthook__(typeException, valueException, tbackException)


def setupWorkDirs(workDir: Path) -> dict:
    """ """
    mwGlob = {
        "workDir": workDir,
        "configDir": workDir / "config",
        "dataDir": workDir / "data",
        "imageDir": workDir / "image",
        "tempDir": workDir / "temp",
        "modelDir": workDir / "model",
        "measureDir": workDir / "measure",
        "logDir": workDir / "log",
    }

    for dirPath in mwGlob:
        mwGlob[dirPath].mkdir(parents=True, exist_ok=True)
    return mwGlob


# noinspection PyUnresolvedReferences
def writeSystemInfo(mwGlob: dict = None) -> None:
    """ """
    log.header("-" * 100)
    log.header(f"mountwizzard4    : {version('mountwizzard4')}")
    log.header(f"platform         : {platform.system()}")
    log.header(f"sys.executable   : {sys.executable}")
    log.header(f"actual workdir   : {mwGlob['workDir']}")
    log.header(f"machine          : {platform.machine()}")
    log.header(f"cpu              : {platform.processor()}")
    log.header(f"release          : {platform.release()}")
    log.header(f"python           : {platform.python_version()}")
    log.header(f"python runtime   : {platform.architecture()[0]}")
    log.header(f"PySide6 / Qt     : {PySide6.QtCore.__version__} / {qVersion()}")
    log.header(f"node / hostname  : {platform.node()} / {socket.gethostname()}")
    log.header("-" * 100)


def extractDataFiles(mwGlob: dict) -> None:
    """ """
    copyFiles = files("mw4").joinpath("assets/data").glob("*.*")
    for file in copyFiles:
        with as_file(file) as src:
            dest = mwGlob["dataDir"] / file.name
            if dest.is_file() and os.stat(src).st_mtime - os.stat(dest).st_mtime < 1:
                continue
            shutil.copy2(src, dest)

    pass


# noinspection PyUnresolvedReferences
def minimizeStartTerminal() -> None:
    """ """
    if platform.system() == "Windows":
        import ctypes

        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def main(test: int = 0) -> None:
    """ """
    locale.setlocale(locale.LC_ALL, "")
    app = QApplication(sys.argv)
    extra = {
        'density_scale': '-4',  # Lower density (more compact layout)
    }
    apply_stylesheet(app, theme="dark_teal.xml", extra=extra)
    minimizeStartTerminal()
    splashW = SplashScreen(application=app)
    splashW.showMessage("Start initialising")
    splashW.setValue(0)
    mwGlob = setupWorkDirs(Path.cwd())

    splashW.showMessage("Write system info to log")
    splashW.setValue(40)
    writeSystemInfo(mwGlob=mwGlob)

    splashW.showMessage("Extracting ephemeris and time data")
    splashW.setValue(60)
    extractDataFiles(mwGlob=mwGlob)

    splashW.showMessage("Initialize Application")
    splashW.setValue(80)
    sys.excepthook = except_hook
    with as_file(files("mw4").joinpath("data/icon/mw4.ico")) as iconFile:
        app.setWindowIcon(QIcon(str(iconFile)))
    MountWizzard4(mwGlob, app, test)
    splashW.showMessage("Finishing loading")
    splashW.setValue(100)
    splashW.close()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
