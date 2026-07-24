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
import glob
import os
import platform
import pytest
import socket
import sys
import traceback
import unittest.mock as mock
from mw4.base.bootstrap import (
    configureEnvironment,
    exceptHook,
    extractDataFiles,
    minimizeStartTerminal,
    setupWorkDirs,
    writeSystemInfo,
)
from pathlib import Path


@pytest.fixture(autouse=True, scope="module")
def module_setup_teardown():
    files = glob.glob("tests/work/config/*.cfg")
    for f in files:
        os.remove(f)
    files = glob.glob("tests/work/config/profile")
    for f in files:
        os.remove(f)
    yield


def test_configure_environment():
    with (
        mock.patch("mw4.base.bootstrap.faulthandler.enable"),
        mock.patch("mw4.base.bootstrap.warnings.filterwarnings"),
        mock.patch("mw4.base.bootstrap.setupLogging"),
    ):
        configureEnvironment()


@pytest.mark.skipif(platform.system() != "Linux", reason="Linux needed")
def test_linux_qt_platform_defaults_to_xcb_when_unset():
    import importlib
    import mw4.base.bootstrap as bootstrapModule

    saved = os.environ.get("QT_QPA_PLATFORM")
    try:
        os.environ.pop("QT_QPA_PLATFORM", None)
        importlib.reload(bootstrapModule)
        assert os.environ.get("QT_QPA_PLATFORM") == "xcb"
    finally:
        if saved is None:
            os.environ.pop("QT_QPA_PLATFORM", None)
        else:
            os.environ["QT_QPA_PLATFORM"] = saved
        importlib.reload(bootstrapModule)


@pytest.mark.skipif(platform.system() != "Linux", reason="Linux needed")
def test_linux_qt_platform_preserved_when_already_set():
    import importlib
    import mw4.base.bootstrap as bootstrapModule

    saved = os.environ.get("QT_QPA_PLATFORM")
    try:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        importlib.reload(bootstrapModule)
        assert os.environ.get("QT_QPA_PLATFORM") == "offscreen"
    finally:
        if saved is None:
            os.environ.pop("QT_QPA_PLATFORM", None)
        else:
            os.environ["QT_QPA_PLATFORM"] = saved
        importlib.reload(bootstrapModule)


def test_except_hook():
    with (
        mock.patch.object(traceback, "format_exception", return_value=("1", "2", "3")),
        mock.patch.object(sys, "__excepthook__"),
    ):
        exceptHook(1, 2, 3)


def test_setup_work_dirs():
    with mock.patch.object(Path, "mkdir"):
        result = setupWorkDirs(Path())
    assert "workDir" in result
    assert "configDir" in result
    assert "dataDir" in result
    assert "imageDir" in result
    assert "tempDir" in result
    assert "modelDir" in result
    assert "measureDir" in result
    assert "logDir" in result


def test_write_system_info():
    mwGlob = {"workDir": Path()}
    writeSystemInfo(mwGlob=mwGlob)


def test_write_system_info_socket_error():
    mwGlob = {"workDir": Path()}
    with (
        mock.patch.object(
            socket, "gethostname", side_effect=Exception("hostname lookup failed")
        ),
        pytest.raises(Exception),
    ):
        writeSystemInfo(mwGlob=mwGlob)


def test_extract_data_files():
    mwGlob = {"dataDir": Path("tests/work/data")}
    extractDataFiles(mwGlob=mwGlob)


def test_extract_data_files_skip_uptodate():
    """continue branch: dest exists with same mtime → shutil.copy2 not called."""
    mwGlob = {"dataDir": Path("tests/work/data")}
    stat_result = mock.MagicMock()
    stat_result.st_mtime = 1000.0
    with (
        mock.patch("mw4.base.bootstrap.os.stat", return_value=stat_result),
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(Path, "is_dir", return_value=True),
        mock.patch("mw4.base.bootstrap.shutil.copy2") as mock_copy,
    ):
        extractDataFiles(mwGlob=mwGlob)
    mock_copy.assert_not_called()


def test_extract_data_files_copy():
    """Test extractDataFiles calls shutil.copy2 when files differ."""
    mwGlob = {"dataDir": Path("tests/work/data")}
    src_stat = mock.MagicMock()
    src_stat.st_mtime = 2000.0
    dest_stat = mock.MagicMock()
    dest_stat.st_mtime = 1000.0
    stat_side_effect = [src_stat, dest_stat]
    with (
        mock.patch("mw4.base.bootstrap.os.stat", side_effect=stat_side_effect),
        mock.patch.object(Path, "is_file", return_value=False),
        mock.patch.object(Path, "is_dir", return_value=True),
        mock.patch("mw4.base.bootstrap.shutil.copy2") as mock_copy,
    ):
        extractDataFiles(mwGlob=mwGlob)
    mock_copy.assert_called()


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_minimize_start_terminal():
    minimizeStartTerminal()


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_minimize_start_terminal_with_mock():
    """Test minimizeStartTerminal with mocked ctypes."""
    with mock.patch("ctypes.windll.user32.ShowWindow") as mock_show_window:
        minimizeStartTerminal()
        mock_show_window.assert_called_once()


@mock.patch("mw4.base.bootstrap.platform.system", return_value="Windows")
def test_minimize_start_terminal_non_windows(mock_platform):
    """Test minimizeStartTerminal when platform reports Windows."""
    mock_ctypes = mock.MagicMock()
    mock_ctypes.windll.user32.ShowWindow = mock.MagicMock()
    mock_ctypes.windll.kernel32.GetConsoleWindow = mock.MagicMock(return_value=12345)
    with mock.patch.dict("sys.modules", {"ctypes": mock_ctypes}):
        minimizeStartTerminal()
        mock_ctypes.windll.user32.ShowWindow.assert_called_once()
