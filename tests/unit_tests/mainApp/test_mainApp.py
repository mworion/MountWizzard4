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
import pytest
import shutil
from mw4.assets import assetsData
from mw4.mainApp import MountWizzard4
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock
from mw4.gui.mainWindow.mainWindow import MainWindow

assetsData.qInitResources()

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
    if not Path("tests/work/data/de440_mw4.bsp").is_file():
        shutil.copy2("tests/testData/de440_mw4.bsp", Path("tests/work/data/de440_mw4.bsp"))
    if not Path("tests/work/data/finals2000A.all").is_file():
        shutil.copy2("tests/testData/finals2000A.all", Path("tests/work/data/finals2000A.all"))
    if not Path("tests/work/test.run").is_file():
        shutil.copy2("tests/testData/test.run", Path("tests/work/test.run"))

    mock_emit = MagicMock()
    app_instance = MountWizzard4(mwGlob, qapp, 1)
    app_instance.update1s = MagicMock(emit=mock_emit)
    yield app_instance
    app_instance.threadPool.waitForDone(15000)


def test_init_config(app):
    topo = app.initConfig()
    assert topo is not None


def test_store_config(app):
    app.storeConfig()
    assert "topoLat" in app.config


def test_store_status_operation_running(app):
    app.storeStatusOperationRunning(1)
    assert app.statusOperationRunning == 1


def test_sendStart(app):
    for a in [10, 30, 50, 100, 300]:
        app.timerCounter = a
        app.sendStart()


def test_send_cyclic(app):
    for a in [0, 4, 19, 79, 274, 574, 1787, 5986, 17985, 35984]:
        app.timerCounter = a
        app.sendCyclic()


def test_quit(app):
    with mock.patch.object(app, "aboutToQuit"):
        with mock.patch.object(app.application, "quit"):
            app.quit()
