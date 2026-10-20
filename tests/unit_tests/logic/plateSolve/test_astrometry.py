# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import glob
import mw4.logic
import os
import pytest
from mw4.logic.plateSolve.astrometry import Astrometry
from mw4.logic.plateSolve.plateSolve import PlateSolve
from pathlib import Path
from skyfield.units import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from tests.unit_tests.unitTestAddOns.platformStub import patchPlatform
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(tmp_path_factory):
    files = glob.glob("tests/work/image/*.fit*")
    for f in files:
        os.remove(f)

    app = App()
    app.mwGlob["tempDir"] = tmp_path_factory.mktemp("solverTemp")
    parent = PlateSolve(app=app)
    func = Astrometry(parent=parent)
    yield func


def test_setDefaultPath_1(function):
    with patchPlatform("Darwin"):
        function.config.appPath = function.setDefaultAppPath()
        assert function.config.appPath == "/Applications/KStars.app/Contents/MacOS/astrometry/bin"


def test_setDefaultPath_2(function):
    with patchPlatform("Linux"):
        function.config.appPath = function.setDefaultAppPath()
        assert function.config.appPath == "/usr/bin"


def test_setDefaultPath_3(function):
    with patchPlatform("Windows"):
        function.config.appPath = function.setDefaultAppPath()
        assert function.config.appPath == ""


def test_saveConfigFile(function):
    function.saveConfigFile()


def test_solve_1(function):
    with (
        mock.patch.object(function.parent, "runSolverBin", return_value=(False, "")),
        mock.patch.object(function.parent, "prepareResult"),
    ):
        res = function.solve(Path("tests/work/image/m51.fit"), True)
        assert not res["success"]


def test_solve_2(function):
    function.config.appPath = "test/Astrometry.app"
    with (
        mock.patch.object(function.parent, "runSolverBin", return_value=(True, "")),
        mock.patch.object(function.parent, "prepareResult"),
        mock.patch.object(
            mw4.logic.plateSolve.astrometry,
            "getHintFromImageFile",
            return_value=(Angle(hours=1), Angle(degrees=1), 1),
        ),
    ):
        res = function.solve(Path("tests/work/image/m51.fit"), True)
        assert res["success"]


def test_checkAvailabilityProgram_1(function):
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        patchPlatform("Linux"),
    ):
        suc = function.checkAvailabilityProgram(Path("test"))
        assert suc


def test_checkAvailabilityProgram_2(function):
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        patchPlatform("Darwin"),
    ):
        suc = function.checkAvailabilityProgram(Path("test"))
        assert suc


def test_checkAvailabilityProgram_3(function):
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        patchPlatform("Windows"),
    ):
        suc = function.checkAvailabilityProgram(Path("test"))
        assert not suc


def test_checkAvailabilityProgram_4(function):
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        patchPlatform("test"),
    ):
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


def test_solve_3(function):
    function.config.appPath = "/usr/bin"
    with (
        mock.patch.object(function.parent, "runSolverBin", return_value=(True, "")) as runBin,
        mock.patch.object(function.parent, "prepareResult"),
        mock.patch.object(
            mw4.logic.plateSolve.astrometry,
            "getHintFromImageFile",
            return_value=(Angle(hours=1), Angle(degrees=1), 1),
        ),
    ):
        function.solve(Path("tests/work/image/m51.fit"), True)
        assert "--no-fits2fits" not in runBin.call_args[0][0]
