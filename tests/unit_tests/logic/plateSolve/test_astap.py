# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import builtins
import glob
import os
import platform
import pytest
from mw4.logic.plateSolve.astap import ASTAP
from mw4.logic.plateSolve.plateSolve import PlateSolve
from pathlib import Path
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(tmp_path_factory):
    files = glob.glob("tests/work/image/*.fit*")
    for f in files:
        os.remove(f)

    app = App()
    app.mwGlob["tempDir"] = tmp_path_factory.mktemp("solverTemp")
    parent = PlateSolve(app=app)
    func = ASTAP(parent=parent)
    yield func


def test_setDefaultPath_1(function):
    with mock.patch.object(platform, "system", return_value="Darwin"):
        function.config.appPath = function.setDefaultAppPath()
        assert function.config.appPath == "/Applications/ASTAP.app/Contents/MacOS"


def test_solve_1(function):
    with (
        mock.patch.object(function.parent, "runSolverBin", return_value=(0, "")),
        mock.patch.object(function.parent, "prepareResult"),
    ):
        res = function.solve(Path("tests/work/image/m51.fit"), True)
        assert res["success"]


def test_checkAvailabilityProgram_1(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        suc = function.checkAvailabilityProgram(Path("test"))
        assert suc


def test_checkAvailabilityProgram_2(function):
    with mock.patch.object(Path, "is_file", return_value=False):
        suc = function.checkAvailabilityProgram(Path("test"))
        assert not suc


def test_checkAvailabilityIndex_1(function):
    with (
        mock.patch.object(builtins, "any", return_value=True),
        mock.patch.object(platform, "system", return_value="Linux"),
    ):
        suc = function.checkAvailabilityIndex(Path("test"))
        assert suc


def test_checkAvailabilityIndex_2(function):
    with (
        mock.patch.object(builtins, "any", return_value=True),
        mock.patch.object(platform, "system", return_value="Darwin"),
    ):
        suc = function.checkAvailabilityIndex(Path("test"))
        assert suc


def test_checkAvailabilityIndex_3(function):
    with (
        mock.patch.object(builtins, "any", return_value=True),
        mock.patch.object(platform, "system", return_value="Windows"),
    ):
        suc = function.checkAvailabilityIndex(Path("test"))
        assert suc
