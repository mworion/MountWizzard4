############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import glob
import os
import shutil
from unittest import mock

import pytest
from logic.plateSolve.plateSolve import PlateSolve

# external packages
# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    files = glob.glob("tests/work/image/*.fit*")
    for f in files:
        os.remove(f)
    shutil.copy("tests/testData/m51.fit", "tests/work/image/m51.fit")
    shutil.copy("tests/testData/astrometry.cfg", "tests/work/temp/astrometry.cfg")
    func = PlateSolve(app=App())
    yield func


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function):
    def test(a):
        function.solveLoopRunning = False

    monkeypatch.setattr("logic.plateSolve.plateSolve.sleepAndEvents", test)


@pytest.fixture
def mocked_processSolveQueue(monkeypatch, function):
    def test(a, b, c):
        function.solveLoopRunning = False

    monkeypatch.setattr("logic.plateSolve.plateSolve.PlateSolve.processSolveQueue", test)


def test_properties_1(function):
    function.framework = "test"

    function.host = ("localhost", 7624)
    function.apiKey = "test"
    function.indexPath = "test"
    function.deviceName = "test"
    function.timeout = 30
    function.searchRadius = 20
    assert function.host == ("localhost", 7624)
    assert function.apiKey == "test"
    assert function.indexPath == "test"
    assert function.deviceName == "test"
    assert function.timeout == 30
    assert function.searchRadius == 20


def test_properties_2(function):
    function.framework = "astap"

    function.host = ("localhost", 7624)
    function.apiKey = "test"
    function.indexPath = "test"
    function.deviceName = "test"
    function.timeout = 30
    function.searchRadius = 20
    assert function.host == ("localhost", 7624)
    assert function.apiKey == "test"
    assert function.indexPath == "test"
    assert function.deviceName == "test"
    assert function.timeout == 30
    assert function.searchRadius == 20


def test_init_1(function):
    assert "watney" in function.run
    assert "astrometry" in function.run
    assert "astap" in function.run


def test_processSolveQueue_1(function):
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.processSolveQueue("tests/work/image/m51.fit", False)


def test_processSolveQueue_2(function):
    function.framework = "astap"
    with mock.patch.object(os.path, "isfile", return_value=True):
        with mock.patch.object(function.run["astap"], "solve"):
            function.processSolveQueue("tests/work/image/m51.fit", False)


def test_workerSolveLoop_1(function, mocked_sleepAndEvents):
    function.solveLoopRunning = True
    function.workerSolveLoop()


def test_workerSolveLoop_2(function, mocked_processSolveQueue):
    function.solveLoopRunning = True
    function.solveQueue.put(("tests/work/image/m51.fit", False))
    function.workerSolveLoop()


def test_startSolveLoop_1(function):
    with mock.patch.object(function.threadPool, "start"):
        function.startSolveLoop()


def test_checkAvailabilityProgram_1(function):
    function.framework = "astap"
    with mock.patch.object(
        function.run["astap"], "checkAvailabilityProgram", return_value=True
    ):
        assert function.checkAvailabilityProgram("astap")


def test_checkAvailabilityIndex_1(function):
    function.framework = "astap"
    with mock.patch.object(function.run["astap"], "checkAvailabilityIndex", return_value=True):
        assert function.checkAvailabilityIndex("astap")


def test_startCommunication_1(function, mocked_sleepAndEvents):
    function.framework = "astap"
    with mock.patch.object(function, "checkAvailabilityProgram", return_value=True):
        with mock.patch.object(function, "checkAvailabilityIndex", return_value=True):
            function.startCommunication()


def test_startCommunication_2(function, mocked_sleepAndEvents):
    function.framework = "astap"
    with mock.patch.object(function, "checkAvailabilityProgram", return_value=False):
        with mock.patch.object(function, "checkAvailabilityIndex", return_value=True):
            function.startCommunication()


def test_stopCommunication(function):
    function.framework = "astrometry"
    function.stopCommunication()


def test_solve_1(function):
    function.framework = "astap"
    file = "tests/work/image/m51.fit"
    function.solve(imagePath=file)


def test_abort_1(function):
    function.framework = "astap"
    with mock.patch.object(function.run["astap"], "abort", return_value=True):
        function.abort()
