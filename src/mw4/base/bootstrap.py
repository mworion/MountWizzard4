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
import faulthandler
import logging
import os
import platform
import PySide6
import shutil
import socket
import sys
import traceback
import types
import warnings
from astropy.utils import data, iers
from astropy.wcs import FITSFixedWarning
from importlib.metadata import version
from importlib.resources import as_file, files
from mw4.base.loggerMW import setupLogging
from pathlib import Path
from PySide6.QtCore import qVersion
from typing import TypedDict


class MwGlob(TypedDict):
    workDir: Path
    configDir: Path
    dataDir: Path
    imageDir: Path
    tempDir: Path
    modelDir: Path
    measureDir: Path
    logDir: Path


log: logging.Logger = logging.getLogger("MW4")


def configureEnvironment() -> None:
    """Configure warnings, logging, and astropy settings for startup."""
    faulthandler.enable()
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=FITSFixedWarning)
    iers.conf.auto_download = False
    data.conf.allow_internet = False
    setupLogging()


def exceptHook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_tb: types.TracebackType | None) -> None:
    """Log uncaught exceptions before delegating to the default hook."""
    formatted = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log.critical("Uncaught exception:\n%s", formatted)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def setupWorkDirs(workDir: Path) -> MwGlob:
    """Create and return the standard directory structure."""
    mwGlob: MwGlob = {
        "workDir": workDir,
        "configDir": workDir / "config",
        "dataDir": workDir / "data",
        "imageDir": workDir / "image",
        "tempDir": workDir / "temp",
        "modelDir": workDir / "model",
        "measureDir": workDir / "measure",
        "logDir": workDir / "log",
    }
    for path in mwGlob.values():
        path.mkdir(parents=True, exist_ok=True)
    return mwGlob


# noinspection PyUnresolvedReferences
def writeSystemInfo(mwGlob: MwGlob) -> None:
    log.info(f"[SYS] mountwizzard4    : {version('mountwizzard4')}")
    log.info(f"[SYS] platform         : {platform.system()}")
    log.info(f"[SYS] sys.executable   : {sys.executable}")
    log.info(f"[SYS] actual workdir   : {mwGlob['workDir']}")
    log.info(f"[SYS] machine          : {platform.machine()}")
    log.info(f"[SYS] cpu              : {platform.processor()}")
    log.info(f"[SYS] release          : {platform.release()}")
    log.info(f"[SYS] python           : {platform.python_version()}")
    log.info(f"[SYS] python runtime   : {platform.architecture()[0]}")
    log.info(f"[SYS] PySide6 / Qt     : {PySide6.QtCore.__version__} / {qVersion()}")
    log.info(f"[SYS] node / hostname  : {platform.node()} / {socket.gethostname()}")


def extractDataFiles(mwGlob: MwGlob) -> None:
    """Copy bundled asset data files to the work data directory if newer."""
    sourceFiles = files("mw4").joinpath("assets/data").glob("*.*")
    for file in sourceFiles:
        with as_file(file) as src:
            dest = mwGlob["dataDir"] / file.name
            if dest.is_file() and os.stat(src).st_mtime - os.stat(dest).st_mtime < 1:
                continue
            shutil.copy2(src, dest)


def minimizeStartTerminal() -> None:
    """Minimize the console window on Windows."""
    if platform.system() == "Windows":
        import ctypes

        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
