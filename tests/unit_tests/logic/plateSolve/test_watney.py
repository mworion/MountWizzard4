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
from unittest import mock
import pytest
import subprocess
import os
import glob
import platform
from pathlib import Path

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import logic
from logic.plateSolve.plateSolve import PlateSolve
from logic.plateSolve.watney import Watney


@pytest.fixture(autouse=True, scope="function")
def function():
    files = glob.glob("tests/workDir/image/*.fit*")
    for f in files:
        os.remove(f)
    for file in os.listdir("tests/workDir/temp"):
        fileP = os.path.join("tests/workDir/temp", file)
        if "temp" not in file:
            continue
        os.remove(fileP)

    parent = PlateSolve(app=App())
    func = Watney(parent=parent)
    yield func


def test_saveConfigFile(function):
    function.saveConfigFile()


def test_setDefaultPath_1(function):
    function.setDefaultPath()


def test_runWatney_1(function):
    class Test1:
        @staticmethod
        def decode():
            return "decode"

    class Test:
        returncode = "1"
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess, "Popen", return_value=Test()):
        suc, ret = function.runWatney([])
        assert not suc


def test_runWatney_2(function):
    with mock.patch.object(subprocess, "Popen", return_value=None):
        with mock.patch.object(
            subprocess.Popen,
            "communicate",
            return_value=("", ""),
            side_effect=Exception(),
        ):
            suc, ret = function.runWatney(["test"])
            assert not suc


def test_runWatney_3(function):
    with mock.patch.object(
        subprocess.Popen,
        "communicate",
        return_value=("", ""),
        side_effect=subprocess.TimeoutExpired("run", 1),
    ):
        suc, ret = function.runWatney(["test"])
        assert not suc


def test_solve_1(function):
    function.searchRadius = 10
    with mock.patch.object(function, "runWatney", return_value=(False, 1)):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(os, "remove"):
                res = function.solve(Path("tests/workDir/image/m51.fit"), False)
                assert not res["success"]


def test_solve_2(function):
    function.searchRadius = 180
    with mock.patch.object(function, "runWatney", return_value=(True, 0)):
        with mock.patch.object(Path, "is_file", return_value=False):
            res = function.solve(Path("tests/workDir/image/m51.fit"), False)
            assert not res["success"]


def test_solve_3(function):
    function.searchRadius = 10
    with mock.patch.object(function, "runWatney", return_value=(True, 0)):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(os, "remove", return_value=True):
                with mock.patch.object(logic.plateSolve.watney, "getImageHeader"):
                    with mock.patch.object(logic.plateSolve.watney, "getSolutionFromWCSHeader"):
                        with mock.patch.object(
                            logic.plateSolve.watney, "updateImageFileHeaderWithSolution"
                        ):
                            res = function.solve(Path("tests/workDir/image/m51.fit"), True)
                            assert res["success"]


def test_abort_1(function):
    function.process = None
    suc = function.abort()
    assert not suc


def test_abort_2(function):
    class Test:
        @staticmethod
        def kill():
            return True

    function.framework = "ASTAP"
    function.process = Test()
    suc = function.abort()
    assert suc


def test_checkAvailabilityProgram_1(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(platform, "system", return_value="Linux"):
            suc = function.checkAvailabilityProgram(Path("test"))
            assert suc


def test_checkAvailabilityProgram_2(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(platform, "system", return_value="Darwin"):
            suc = function.checkAvailabilityProgram(Path("test"))
            assert suc


def test_checkAvailabilityProgram_3(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(platform, "system", return_value="Windows"):
            suc = function.checkAvailabilityProgram(Path("test"))
            assert suc


def test_checkAvailabilityProgram_4(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(platform, "system", return_value="test"):
            suc = function.checkAvailabilityProgram(Path("test"))
            assert not suc


def test_checkAvailabilityIndex_1(function):
    with mock.patch.object(Path, "glob", return_value=[]):
        suc = function.checkAvailabilityIndex(Path("test"))
        assert not suc


def test_checkAvailabilityIndex_2(function):
    with mock.patch.object(Path, "glob", return_value=["test"]):
        suc = function.checkAvailabilityIndex(Path("test"))
        assert suc
