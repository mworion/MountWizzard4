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
from mw4.logic.plateSolve.plateSolve import PlateSolve
from mw4.logic.plateSolve.watney import Watney
from pathlib import Path
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="function")
def function():
    files = glob.glob("tests/work/image/*.fit*")
    for f in files:
        os.remove(f)
    for file in os.listdir("tests/work/temp"):
        fileP = os.path.join("tests/work/temp", file)
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


def test_solve_1(function):
    with mock.patch.object(function.parent, "runSolverBin", return_value=(0, "")):
        with mock.patch.object(function.parent, "prepareResult"):
            res = function.solve(Path("tests/work/image/m51.fit"), True)
            assert res["success"]


def test_solve_2(function):
    function.searchRadius = 180
    with mock.patch.object(function.parent, "runSolverBin", return_value=(0, "")):
        with mock.patch.object(function.parent, "prepareResult"):
            res = function.solve(Path("tests/work/image/m51.fit"), True)
            assert res["success"]


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
