############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import shutil
import unittest.mock as mock
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# external packages
from PySide6.QtCore import QBasicTimer, QCoreApplication, QTimer
from PySide6.QtWidgets import QWidget

from mw4.assets import assetsData as res
from mw4.base.loggerMW import setupLogging
from mw4.gui.mainWaddon.astroObjects import AstroObjects

# local import
from mw4.mainApp import MountWizzard4

res.qInitResources()
setupLogging()


@pytest.fixture(autouse=True, scope="module")
def app(qapp):
    mwGlob = {
        "configDir": Path("tests/work/config"),
        "dataDir": Path("tests/work/data"),
        "tempDir": Path("tests/work/temp"),
        "imageDir": Path("tests/work/image"),
        "modelDir": Path("tests/work/model"),
        "workDir": Path("tests/work"),
    }

    shutil.copy("tests/testData/de440_mw4.bsp", Path("tests/work/data/de440_mw4.bsp"))
    shutil.copy("tests/testData/finals2000A.all", Path("tests/work/data/finals2000A.all"))
    shutil.copy("tests/testData/test.run", Path("tests/work/test.run"))

    class Test:
        def emit(self):
            return

    with mock.patch.object(QWidget, "show"):
        with mock.patch.object(QTimer, "start"):
            with mock.patch.object(QBasicTimer, "start"):
                with mock.patch.object(AstroObjects, "loadSourceUrl"):
                    app = MountWizzard4(mwGlob=mwGlob, application=MagicMock())
                    app.update1s = Test()
                    yield app
                    app.threadPool.waitForDone(15000)


def test_storeStatusOperationRunning(app):
    app.storeStatusOperationRunning(4)
    assert app.statusOperationRunning == 4


def test_initConfig_1(app):
    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_initConfig_2(app):
    app.config["mainW"] = {}
    app.config["mainW"]["loglevelDebug"] = True

    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_initConfig_4(app):
    app.config["mainW"] = {}
    app.config["mainW"]["loglevelTrace"] = True

    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_storeConfig_1(app):
    app.storeConfig()


def test_sendStart_1(app):
    app.timerCounter = 10
    app.sendStart()


def test_sendStart_2(app):
    app.timerCounter = 30
    app.sendStart()


def test_sendStart_3(app):
    app.timerCounter = 50
    app.sendStart()


def test_sendStart_4(app):
    app.timerCounter = 100
    app.sendStart()


def test_sendStart_5(app):
    app.timerCounter = 300
    app.sendStart()


def test_sendCyclic_1(app):
    app.timerCounter = 0
    app.sendCyclic()


def test_sendCyclic_2(app):
    app.timerCounter = 4
    app.sendCyclic()


def test_sendCyclic_3(app):
    app.timerCounter = 19
    app.sendCyclic()


def test_sendCyclic_4(app):
    app.timerCounter = 79
    app.sendCyclic()


def test_sendCyclic_5(app):
    app.timerCounter = 574
    app.sendCyclic()


def test_sendCyclic_6(app):
    app.timerCounter = 1800 - 12 - 1
    app.sendCyclic()


def test_sendCyclic_7(app):
    app.timerCounter = 6000 - 13 - 1
    app.sendCyclic()


def test_sendCyclic_8(app):
    app.timerCounter = 18000 - 14 - 1
    app.sendCyclic()


def test_sendCyclic_9(app):
    app.timerCounter = 36000 - 15 - 1
    app.sendCyclic()


def test_aboutToQuit_1(app):
    app.aboutToQuit()


def test_quit_1(app):
    with mock.patch.object(QCoreApplication, "quit"):
        with mock.patch.object(app.mount, "stopAllMountTimers"):
            app.quit()
