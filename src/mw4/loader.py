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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
import locale
import logging
import os
import platform
import PySide6
import socket
import sys
import traceback
import warnings
from astropy.utils import data, iers
from astropy.wcs import FITSFixedWarning
from importlib_metadata import version
from mw4.assets.assetsData import qInitResources
from mw4.base.loggerMW import setupLogging
from mw4.gui.utilities.splashScreen import SplashScreen
from mw4.mainApp import MountWizzard4
from pathlib import Path
from PySide6.QtCore import QEvent, QFile, qVersion
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTabBar,
    QWidget,
)

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FITSFixedWarning)

qInitResources()
iers.conf.auto_download = False
data.conf.allow_internet = False
setupLogging()
log = logging.getLogger("MW4")


class MyApp(QApplication):
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, *argv):
        super().__init__(*argv)
        self.last = None

    # noinspection PyUnresolvedReferences
    def logUserInterface(self, obj: QWidget) -> bool:
        """ """
        if isinstance(obj, QTabBar):
            self.log.ui(f"Click Tab     : [{obj.tabText(obj.currentIndex())}]")
        elif isinstance(obj, QComboBox):
            self.log.ui(f"Click DropDown: [{obj.objectName()}]")
        elif isinstance(obj, QPushButton):
            text = obj.objectName()
            if not text:
                text = f"Popup - {obj.text()}"
            self.log.ui(f"Click Button  : [{text}]")
        elif isinstance(obj, QRadioButton):
            self.log.ui(
                f"Click Radio   : [{obj.objectName()}], value: [{not obj.isChecked()}]"
            )
        elif isinstance(obj, QGroupBox):
            self.log.ui(
                f"Click Group   : [{obj.objectName()}], value: [{not obj.isChecked()}]"
            )
        elif isinstance(obj, QCheckBox):
            self.log.ui(
                f"Click Checkbox: [{obj.objectName()}], value: [{not obj.isChecked()}]"
            )
        elif isinstance(obj, QLineEdit):
            self.log.ui(f"Click EditLine: [{obj.objectName()}]:{obj.text()}")
        else:
            if obj.objectName() not in [
                "qt_scrollarea_viewport",
                "QComboBoxPrivateContainerClassWindow",
                "",
            ]:
                self.log.ui(f"Click Object  : [{obj.objectName()}]")

    def handleButtons(self, obj: QWidget, returnValue: bool) -> bool:
        """ """
        if "Window" not in obj.objectName():
            self.logUserInterface(obj)
        return returnValue

    def notify(self, obj: QWidget, event: QEvent) -> bool:
        """ """
        returnValue = QApplication.notify(self, obj, event)

        if not isinstance(event, QMouseEvent):
            return returnValue
        if not event.button():
            return returnValue
        if event.type() == QEvent.Type.MouseButtonRelease:
            return returnValue
        returnValue = self.handleButtons(obj, returnValue)
        return returnValue


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

    mwGlob["modeldata"] = "4.0"
    return mwGlob


# noinspection PyUnresolvedReferences
def checkIsAdmin() -> str:
    """ """
    if platform.system() == "Windows":
        import ctypes

        try:
            state = ctypes.windll.shell32.IsUserAnAdmin() == 1
        except Exception as e:
            log.error(f"Check admin error: [{e}]")
            state = None
    else:
        try:
            state = os.getuid() == 0
        except Exception as e:
            log.error(f"Check admin error: [{e}]")
            state = None
    if state is None:
        return "unknown"
    elif state:
        return "yes"
    else:
        return "no"


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
    log.header(f"run as admin     : {checkIsAdmin()}")
    log.header("-" * 100)


def extractFile(filePath: Path, file: str, fileTimeStamp: str) -> None:
    """ """
    overwrite = False
    if filePath.is_file():
        mtime = os.stat(filePath).st_mtime
        overwrite = mtime < fileTimeStamp

    if overwrite:
        log.info(f"Writing new file: [{file}]")
        os.remove(filePath)
    else:
        log.info(f"Using existing: [{file}]")

    QFile.copy(f":/data/{file}", str(filePath))
    os.chmod(filePath, 0o666)


def extractDataFiles(mwGlob: dict) -> None:
    """ """
    filesTimes = {
        "de440_mw4.bsp": 0,
        "CDFLeapSeconds.txt": 0,
        "tai-utc.dat": 0,
        "finals2000A.all": 0,
        "finals.data": 0,
    }

    contentFile = QFile(":/data/content.txt")
    contentFile.open(QFile.OpenModeFlag.ReadOnly)
    lines = contentFile.readAll().data().decode().splitlines()
    contentFile.close()

    for line in lines:
        name, date = line.split(" ")
        filesTimes[name] = float(date)

    for file in filesTimes:
        filePath = mwGlob["dataDir"] / file
        extractFile(filePath, file, filesTimes[file])


# noinspection PyUnresolvedReferences
def minimizeStartTerminal() -> None:
    """ """
    if platform.system() == "Windows":
        import ctypes

        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def main(efficient: bool = False) -> None:
    """ """
    locale.setlocale(locale.LC_ALL, "")
    app = QApplication(sys.argv) if efficient else MyApp(sys.argv)
    minimizeStartTerminal()
    splashW = SplashScreen(application=app)
    splashW.showMessage("Start initialising")
    splashW.setValue(0)
    mwGlob = setupWorkDirs(Path.cwd())

    splashW.showMessage("Write system info to log")
    splashW.setValue(40)
    writeSystemInfo(mwGlob=mwGlob)

    splashW.showMessage("Loading star and time data")
    splashW.setValue(60)
    extractDataFiles(mwGlob=mwGlob)

    splashW.showMessage("Initialize Application")
    splashW.setValue(80)
    sys.excepthook = except_hook
    app.setWindowIcon(QIcon(":/icon/mw4.ico"))
    MountWizzard4(mwGlob=mwGlob, application=app)

    splashW.showMessage("Finishing loading")
    splashW.setValue(100)
    splashW.close()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
