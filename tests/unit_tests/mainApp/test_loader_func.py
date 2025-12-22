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

import ctypes
import glob
import json
import mw4.loader
import os
import platform
import pytest
import socket
import sys
import traceback
import unittest.mock as mock
from mw4.loader import (
    checkIsAdmin,
    except_hook,
    extractDataFiles,
    extractFile,
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
    with mock.patch.object(traceback, "format_exception", return_value=("1", "2", "3")):
        with mock.patch.object(
            sys,
            "__excepthook__",
        ):
            except_hook(1, 2, 3)


def test_setupWorkDirs_1():
    with mock.patch.object(Path, "mkdir"):
            val = setupWorkDirs(Path())
            assert val["modeldata"] == "4.0"


def test_checkIsAdmin_1():
    def getiud():
        return 0

    os.getuid = getiud
    with mock.patch.object(platform, "system", return_value="Darwin"):
        with mock.patch.object(os, "getuid", return_value=0, side_effect=Exception):
            val = checkIsAdmin()
            assert val == "unknown"


def test_checkIsAdmin_2():
    def getiud():
        return 0

    os.getuid = getiud
    with mock.patch.object(platform, "system", return_value="Darwin"):
        with mock.patch.object(os, "getuid", return_value=0):
            val = checkIsAdmin()
            assert val == "yes"


def test_checkIsAdmin_3():
    def getiud():
        return 0

    os.getuid = getiud
    with mock.patch.object(platform, "system", return_value="Darwin"):
        with mock.patch.object(os, "getuid", return_value=1):
            val = checkIsAdmin()
            assert val == "no"


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_checkIsAdmin_4():
    import ctypes

    with mock.patch.object(platform, "system", return_value="Windows"):
        with mock.patch.object(ctypes.windll.shell32, "IsUserAnAdmin", side_effect=Exception):
            val = checkIsAdmin()
            assert val == "unknown"


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_checkIsAdmin_5():
    import ctypes

    with mock.patch.object(platform, "system", return_value="Windows"):
        with mock.patch.object(ctypes.windll.shell32, "IsUserAnAdmin", return_value=1):
            val = checkIsAdmin()
            assert val == "yes"


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_checkIsAdmin_6():
    import ctypes

    with mock.patch.object(platform, "system", return_value="Windows"):
        with mock.patch.object(ctypes.windll.shell32, "IsUserAnAdmin", return_value=0):
            val = checkIsAdmin()
            assert val == "no"


@pytest.mark.skipif(platform.system() != "Windows", reason="need windows")
def test_checkIsAdmin_7():
    with mock.patch.object(platform, "system", return_value="Windows"):
        with mock.patch.object(
            ctypes.windll.shell32,
            "IsUserAnAdmin",
            return_value=0,
            side_effect=Exception,
        ):
            val = checkIsAdmin()
            assert val == "unknown"


@pytest.mark.skipif(platform.system() != "Windows", reason="need windows")
def test_checkIsAdmin_8():
    with mock.patch.object(platform, "system", return_value="Windows"):
        with mock.patch.object(ctypes.windll.shell32, "IsUserAnAdmin", return_value=1):
            val = checkIsAdmin()
            assert val == "yes"


@pytest.mark.skipif(platform.system() != "Windows", reason="need windows")
def test_checkIsAdmin_9():
    with mock.patch.object(platform, "system", return_value="Windows"):
        with mock.patch.object(ctypes.windll.shell32, "IsUserAnAdmin", return_value=0):
            val = checkIsAdmin()
            assert val == "no"


def test_writeSystemInfo_1():
    mwGlob = dict()
    mwGlob["modeldata"] = ""
    mwGlob["workDir"] = ""
    writeSystemInfo(mwGlob=mwGlob)
    mwGlob["WorkDir"] = Path("tests/work")


def test_writeSystemInfo_2():
    mwGlob = dict()
    mwGlob["modeldata"] = ""
    mwGlob["workDir"] = ""
    with mock.patch.object(socket, "gethostbyname_ex", side_effect=Exception()):
        writeSystemInfo(mwGlob=mwGlob)
    mwGlob["WorkDir"] = Path("tests/work")


def test_extractFile_1():
    class MTime:
        st_mtime = 1000000000.0

    filePath = Path("tests/work/data/de440_mw4.bsp")
    with mock.patch.object(Path, "is_file", return_value=False):
        with mock.patch.object(os, "stat", return_value=MTime()):
            extractFile(filePath, "de440_mw4.bsp", 0)


def test_extractFile_2():
    class MTime:
        st_mtime = 1000000000.0

    filePath = Path("tests/work/data/de440_mw4.bsp")
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(os, "stat", return_value=MTime()):
            with mock.patch.object(os, "remove"):
                with mock.patch.object(os, "chmod"):
                    extractFile(filePath, "de440_mw4.bsp", 2000000000.0)


def test_extractFile_3():
    class MTime:
        st_mtime = 1000000000.0

    filePath = Path("tests/work/data/de440_mw4.bsp")
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(os, "stat", return_value=MTime()):
            with mock.patch.object(os, "chmod"):
                extractFile(filePath, "de440_mw4.bsp", 0)


def test_extractDataFiles_1():
    mwGlob = dict()
    mwGlob["dataDir"] = Path("tests/work/data")
    with mock.patch.object(mw4.loader, "extractFile"):
        extractDataFiles(mwGlob=mwGlob)


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_minimizeStartTerminal():
    minimizeStartTerminal()
