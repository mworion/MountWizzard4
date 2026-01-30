import pytest
import shutil
from mw4.mainApp import MountWizzard4
from pathlib import Path
from unittest.mock import MagicMock
from mw4.assets.assetsData import qInitResources

qInitResources()


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

    shutil.copy("./tests/testData/de440_mw4.bsp", Path("./tests/work/data/de440_mw4.bsp"))
    shutil.copy("./tests/testData/finals2000A.all", Path("./tests/work/data/finals2000A.all"))
    shutil.copy("./tests/testData/test.run", Path("./tests/work/test.run"))

    mock_emit = MagicMock()
    app_instance = MountWizzard4(mwGlob, qapp, 0)
    app_instance.update1s = MagicMock(emit=mock_emit)
    app_instance.update3s = MagicMock(emit=mock_emit)
    yield app_instance
    app_instance.threadPool.waitForDone(15000)
    app_instance.aboutToQuit()
    app_instance.deleteLater()
    qapp.processEvents()


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
