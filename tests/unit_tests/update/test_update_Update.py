############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import sys
import unittest.mock as mock
import pytest
import subprocess
import builtins
import platform

# external packages

# local import
from mw4.update import Update
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope="function")
def update():
    def writer(text, color):
        return

    update = Update(runnable="python", writer=writer)
    yield update


def test_formatPIP_1(update):
    line = update.formatPIP()
    assert line == ""


def test_formatPIP_2(update):
    line = update.formatPIP("   ")
    assert line == ""


def test_formatPIP_3(update):
    line = update.formatPIP("Requirement already satisfied: mountcontrol in /Users (0.157)")
    assert line == "Requirement already satisfied : mountcontrol"


def test_formatPIP_4(update):
    line = update.formatPIP("Collecting mountcontrol==0.157")
    assert line == "Collecting mountcontrol"


def test_formatPIP_5(update):
    line = update.formatPIP("Installing collected packages: mountcontrol")
    assert line == "Installing collected packages"


def test_formatPIP_6(update):
    line = update.formatPIP("Successfully installed mountcontrol-0.156")
    assert line == "Successfully installed mountcontrol-0.156"


def test_isVenv_1(update):
    setattr(sys, "real_prefix", "")
    setattr(sys, "base_prefix", "")
    update.isVenv()


def test_runInstall_1(update):
    class Test1:
        @staticmethod
        def decode():
            return "decode"

        @staticmethod
        def readline():
            return ""

        @staticmethod
        def replace(a, b):
            return ""

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess, "Popen", return_value=Test()):
        with mock.patch.object(update, "isVenv", return_value=True):
            with mock.patch.object(builtins, "iter", return_value=["1", "2"]):
                suc = update.runInstall()
                assert suc


def test_runInstall_2(update):
    class Test1:
        @staticmethod
        def decode():
            return "decode"

        @staticmethod
        def readline():
            return

        @staticmethod
        def replace(a, b):
            return ""

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess, "Popen", return_value=Test(), side_effect=Exception()):
        with mock.patch.object(update, "formatPIP", return_value=""):
            with mock.patch.object(update, "isVenv", return_value=True):
                suc = update.runInstall()
                assert not suc


def test_runInstall_3(update):
    with mock.patch.object(update, "isVenv", return_value=False):
        suc = update.runInstall()
        assert not suc


def test_runInstall_4(update):
    class Test1:
        @staticmethod
        def decode():
            return "decode"

        @staticmethod
        def readline():
            return

        @staticmethod
        def replace(a, b):
            return ""

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(
        subprocess,
        "Popen",
        return_value=Test(),
        side_effect=subprocess.TimeoutExpired("res", 2),
    ):
        with mock.patch.object(update, "isVenv", return_value=True):
            with mock.patch.object(update, "formatPIP", return_value=""):
                suc = update.runInstall()
                assert not suc


def test_restart_1(update):
    with mock.patch.object(platform, "system", return_value="Windows"):
        with mock.patch.object(os, "execl"):
            update.restart("test")


def test_restart_2(update):
    with mock.patch.object(platform, "system", return_value="Darwin"):
        with mock.patch.object(os, "execl"):
            update.restart("test")
