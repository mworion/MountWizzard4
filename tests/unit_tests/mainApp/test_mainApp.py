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
import logging
import pytest
import shutil
from mw4.mainApp import MountWizzard4
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock


@pytest.fixture(scope="function")
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
    default_config = {
        "SettingDome": {
            "use10micronDef": True,
            "northOffset": 0.0,
            "eastOffset": 0.0,
            "verticalOffset": 0.0,
            "offGEM": 0.0,
            "offLAT": 0.0,
            "radius": 100.0,
            "settleTime": 0.0,
            "openingHysteresis": 0.0,
            "clearanceZenith": 0.2,
            "clearOpening": 1.0,
            "overshoot": 0.0,
            "useOvershoot": False,
            "useGeometry": False,
            "useDynamicFollowing": False,
            "automaticDome": False,
        },
    }

    def loadProfileStart_mock(config_dir):
        return default_config

    with (
        mock.patch("mw4.mainApp.loadProfileStart", side_effect=loadProfileStart_mock),
        mock.patch("mw4.mainApp.MainWindow") as mock_main_window,
    ):
        mock_main_window.return_value = MagicMock()
        app_instance = MountWizzard4(mwGlob, qapp, 1)
    app_instance.update1s = MagicMock(emit=mock_emit)
    yield app_instance
    try:
        app_instance.shutdown()
    except (AttributeError, RuntimeError) as e:
        logging.getLogger("MW4").debug(f"Fixture cleanup error: {e}")


def test_init_config(app):
    """initConfig() sets up the location from config and custom logging level."""
    app.initConfig()
    assert app.dReg["mount"].obsSite.location is not None


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
    """emitCyclic() must emit correct signals based on counter intervals."""
    # Test signal emissions at various counter values
    # Signals are emitted if counter % interval == 0
    test_cases = [
        (
            0,
            {
                "update0_1s",
                "update0_5s",
                "update1s",
                "update3s",
                "update10s",
                "update30s",
                "update3m",
                "update30m",
            },
        ),
        (4, {"update0_1s"}),
        (5, {"update0_1s", "update0_5s"}),
        (10, {"update0_1s", "update0_5s", "update1s"}),
        (30, {"update0_1s", "update0_5s", "update1s", "update3s"}),
        (100, {"update0_1s", "update0_5s", "update1s", "update10s"}),
        (300, {"update0_1s", "update0_5s", "update1s", "update3s", "update10s", "update30s"}),
        (
            1800,
            {
                "update0_1s",
                "update0_5s",
                "update1s",
                "update3s",
                "update10s",
                "update30s",
                "update3m",
            },
        ),
    ]

    for counter_value, expected_signals in test_cases:
        app.timeMgr.counter = counter_value

        # Mock all cyclic signals to track emissions
        mock_signals = {
            "update0_1s": mock.MagicMock(),
            "update0_5s": mock.MagicMock(),
            "update1s": mock.MagicMock(),
            "update3s": mock.MagicMock(),
            "update10s": mock.MagicMock(),
            "update30s": mock.MagicMock(),
            "update3m": mock.MagicMock(),
            "update30m": mock.MagicMock(),
        }

        # Replace signal emitters with mocks
        with (
            mock.patch.object(app.timeMgr, "update0_1s", mock_signals["update0_1s"]),
            mock.patch.object(app.timeMgr, "update0_5s", mock_signals["update0_5s"]),
            mock.patch.object(app.timeMgr, "update1s", mock_signals["update1s"]),
            mock.patch.object(app.timeMgr, "update3s", mock_signals["update3s"]),
            mock.patch.object(app.timeMgr, "update10s", mock_signals["update10s"]),
            mock.patch.object(app.timeMgr, "update30s", mock_signals["update30s"]),
            mock.patch.object(app.timeMgr, "update3m", mock_signals["update3m"]),
            mock.patch.object(app.timeMgr, "update30m", mock_signals["update30m"]),
        ):
            app.timeMgr.emitCyclic()

        # Verify expected signals were emitted
        for signal_name, mock_signal in mock_signals.items():
            if signal_name in expected_signals:
                mock_signal.emit.assert_called_once()
            else:
                mock_signal.emit.assert_not_called()


def test_writeMessageQueue(app):
    """writeMessageQueue adds messages to the message queue."""
    initial_size = app.messageQueue.qsize()
    app.writeMessageQueue(1, "test", "test", "test")
    assert app.messageQueue.qsize() == initial_size + 1
    while app.messageQueue.qsize() > 1:
        app.messageQueue.get()
    prio, source, mType, message = app.messageQueue.get()
    assert prio == 1
    assert source == "test"
    assert mType == "test"
    assert message == "test"


def test_msg_signal_connects_to_writeMessageQueue(app):
    """msg signal is connected to writeMessageQueue method."""
    initial_size = app.messageQueue.qsize()
    app.msg.emit(1, "source", "type", "message")
    assert app.messageQueue.qsize() == initial_size + 1
    while app.messageQueue.qsize() > 1:
        app.messageQueue.get()
    prio, source, mType, message = app.messageQueue.get()
    assert prio == 1
    assert source == "source"
    assert mType == "type"
    assert message == "message"


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
