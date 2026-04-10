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


@pytest.fixture(autouse=True, scope="function")
def module_setup_teardown():
    files = glob.glob("tests/work/config/*.cfg")
    for f in files:
        os.remove(f)
    files = glob.glob("tests/work/config/profile")
    for f in files:
        os.remove(f)
    yield


def test_except_hook():
    with mock.patch.object(
        traceback,
        "format_exception",
        return_value=("1", "2", "3"),
    ):
        with mock.patch.object(sys, "__excepthook__"):
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
    with mock.patch.object(
        socket, "gethostbyname_ex", side_effect=Exception()
    ):
        writeSystemInfo(mwGlob=mwGlob)


def test_extract_data_files():
    mwGlob = {"dataDir": Path("tests/work/data")}
    extractDataFiles(mwGlob=mwGlob)


@pytest.mark.skipif(
    platform.system() != "Windows", reason="Windows needed"
)
def test_minimize_start_terminal():
    minimizeStartTerminal()
