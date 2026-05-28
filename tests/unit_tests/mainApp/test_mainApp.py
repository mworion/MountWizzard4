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
import pytest
import runpy
import shutil
from mw4.mainApp import MountWizzard4
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock


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
    with mock.patch("mw4.mainApp.MainWindow") as mock_main_window:
        mock_main_window.return_value = MagicMock()
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
        app.timerMgr.counter = a
        app.timerMgr.emitStart()


def test_send_cyclic(app):
    for a in [0, 4, 19, 79, 274, 574, 1787, 5986, 17985, 35984]:
        app.timerMgr.counter = a
        app.timerMgr.emitCyclic()


def test_aboutToQuit(app):
    """aboutToQuit must stop the timer manager and all mount timers."""
    with (
        mock.patch.object(app.timerMgr, "stop") as mockStop,
        mock.patch.object(app.mount, "stopAllMountTimers") as mockStopMount,
    ):
        app.aboutToQuit()
    mockStop.assert_called_once()
    mockStopMount.assert_called_once()


def test_quit(app):
    with mock.patch.object(app, "aboutToQuit"), mock.patch.object(app.application, "quit"):
        app.quit()


def test_getActiveDrivers(app):
    """getActiveDrivers() returns the drivers dict from the DeviceRegistry."""
    drivers = {"camera": {"class": object()}}
    app.deviceRegistry.update(drivers)
    result = app.getActiveDrivers()
    assert result is drivers


# ---------------------------------------------------------------------------
# __main__.py — entry-point guard
# ---------------------------------------------------------------------------


def test_main_module_entry_point():
    """Running mw4 as __main__ invokes the cli run() entry point."""
    with mock.patch("mw4.cli.run") as mock_run:
        runpy.run_module("mw4", run_name="__main__")
    mock_run.assert_called_once()
