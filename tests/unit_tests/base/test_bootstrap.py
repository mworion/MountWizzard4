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


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_minimize_start_terminal():
    minimizeStartTerminal()
