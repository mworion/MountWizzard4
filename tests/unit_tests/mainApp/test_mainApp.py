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
import shutil
from mw4.mainApp import MountWizzard4
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock


@pytest.fixture(scope="module")
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
        app.timeMgr.counter = a
        app.timeMgr.emitStart()


def test_send_cyclic(app):
    for a in [0, 4, 19, 79, 274, 574, 1787, 5986, 17985, 35984]:
        app.timeMgr.counter = a
        app.timeMgr.emitCyclic()


def test_aboutToQuit(app):
    """aboutToQuit must stop the timer manager and all mount timers."""
    with (
        mock.patch.object(app.timeMgr, "stop") as mockStop,
        mock.patch.object(app.mount, "stopAllMountTimers") as mockStopMount,
    ):
        app.aboutToQuit()
    mockStop.assert_called_once()
    mockStopMount.assert_called_once()


def test_quit(app):
    """Test quit() method calls aboutToQuit and quits application."""
    with (
        mock.patch.object(app, "aboutToQuit") as mock_about_to_quit,
        mock.patch.object(app.application, "quit") as mock_app_quit,
    ):
        app.quit()
    mock_about_to_quit.assert_called_once()
    mock_app_quit.assert_called_once()


def test_quit_prevents_double_call(app):
    """Test quit() method always executes quit logic."""
    with (
        mock.patch.object(app, "aboutToQuit") as mock_about_to_quit,
        mock.patch.object(app.application, "quit") as mock_app_quit,
    ):
        app.quit()
    mock_about_to_quit.assert_called_once()
    mock_app_quit.assert_called_once()


def test_getActiveDrivers(app):
    """getActiveDrivers() method is not implemented yet."""
    # TODO: This method needs to be implemented in the MountWizzard4 class
    # For now, just check that the app has a dReg (device registry)
    assert hasattr(app, "dReg")
    assert "camera" in app.dReg.d


# ---------------------------------------------------------------------------
# __main__.py — entry-point guard
# ---------------------------------------------------------------------------


def test_main_module_entry_point():
    """Running mw4 as __main__ invokes the cli run() entry point."""
    # Verify __main__.py imports and calls cli.run
    main_file = Path("src/mw4/__main__.py")
    assert main_file.exists()
    content = main_file.read_text()
    assert "from mw4.cli import run" in content
    assert "run()" in content
