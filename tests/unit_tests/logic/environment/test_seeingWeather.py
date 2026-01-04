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
import json
import pytest
import requests
import shutil
from pathlib import Path
import unittest.mock as mock
from mw4.base.loggerMW import setupLogging
from mw4.logic.environment.seeingWeather import SeeingWeather
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


@pytest.fixture(autouse=True, scope="module")
def function():
    class Test1:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    shutil.copy("tests/testData/meteoblue.data", "tests/work/data/meteoblue.data")

    with mock.patch.object(requests, "get", return_value=Test1()):
        func = SeeingWeather(app=App())
        yield func


def test_properties(function):
    with mock.patch.object(function, "pollSeeingData"):
        function.keyAPI = "test"
        assert function.keyAPI == "test"
        function.online = True
        assert function.online


def test_startCommunication_(function):
    with mock.patch.object(function, "pollSeeingData"):
        function.startCommunication()


def test_stopCommunication_1(function):
    function.running = True
    function.stopCommunication()
    assert not function.running


def test_processSeeingData_1(function):
    with mock.patch.object(Path, "is_file", return_value=False):
        function.processSeeingData()


def test_processSeeingData_2(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(json, "load", return_value={}, side_effect=Exception):
            function.processSeeingData()


def test_processSeeingData_3(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(json, "load", return_value={}):
            function.processSeeingData()


def test_workerGetSeeingData_0(function):
    class Test:
        status_code = 300

    function.app.onlineMode = False
    with mock.patch.object(requests, "get", return_value=Test()):
        function.workerGetSeeingData("http://localhost")


def test_workerGetSeeingData_1(function):
    class Test:
        status_code = 300

    function.app.onlineMode = True
    with mock.patch.object(requests, "get", return_value=Test()):
        function.workerGetSeeingData("http://localhost")


def test_workerGetSeeingData_3(function):
    class Test:
        status_code = 300

    function.app.onlineMode = True
    with mock.patch.object(requests, "get", side_effect=Exception(), return_value=Test()):
        function.workerGetSeeingData("http://localhost")


def test_workerGetSeeingData_4(function):
    class Test:
        status_code = 300

    function.app.onlineMode = True
    with mock.patch.object(requests, "get", side_effect=TimeoutError(), return_value=Test()):
        function.workerGetSeeingData("http://localhost")


def test_workerGetSeeingData_5(function):
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    function.app.onlineMode = True
    with mock.patch.object(requests, "get", return_value=Test()):
        function.workerGetSeeingData("http://localhost")


def test_sendStatus_1(function):
    function.running = True
    function.sendStatus(False)


def test_sendStatus_2(function):
    function.running = False
    function.sendStatus(True)


def test_getSeeingData_1(function):
    with mock.patch.object(function, "loadingFileNeeded", return_value=False):
        with mock.patch.object(function, "processSeeingData"):
            with mock.patch.object(function, "sendStatus"):
                with mock.patch.object(function.threadPool, "start"):
                    function.getSeeingData("test")


def test_getSeeingData_2(function):
    with mock.patch.object(function, "loadingFileNeeded", return_value=True):
        with mock.patch.object(function, "processSeeingData"):
            with mock.patch.object(function, "sendStatus"):
                with mock.patch.object(function.threadPool, "start"):
                    function.getSeeingData("test")


def test_loadingFileNeeded_1(function):
    with mock.patch.object(Path, "is_file", return_value=False):
        suc = function.loadingFileNeeded("test", 1)
        assert suc


def test_loadingFileNeeded_2(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function.app.mount.obsSite.loader, "days_old", return_value=1):
            suc = function.loadingFileNeeded("test", 1)
            assert suc


def test_loadingFileNeeded_3(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function.app.mount.obsSite.loader, "days_old", return_value=1):
            suc = function.loadingFileNeeded("test", 25)
            assert not suc


def test_pollSeeingData_1(function):
    function.app.mwGlob["dataDir"] = Path("tests/work/data")
    function.apiKey = ""
    function.pollSeeingData()


def test_pollSeeingData_2(function):
    function.app.mwGlob["dataDir"] = Path("tests/work/data")
    function.apiKey = "test"
    function.b = "test"
    function.app.onlineMode = False
    function.running = True
    function.pollSeeingData()


def test_pollSeeingData_3(function):
    function.app.mwGlob["dataDir"] = Path("tests/work/data")
    function.apiKey = "test"
    function.b = "test"
    function.app.onlineMode = True
    function.pollSeeingData()


def test_pollSeeingData_4(function):
    function.app.mwGlob["dataDir"] = Path("tests/work/data")
    function.apiKey = "test"
    function.b = "test"
    function.app.onlineMode = True
    with mock.patch.object(function, "loadingFileNeeded", return_value=False):
        function.pollSeeingData()


def test_pollSeeingData_5(function):
    function.app.mwGlob["dataDir"] = Path("tests/work/data")
    function.apiKey = "test"
    function.b = "test"
    function.app.onlineMode = True
    with mock.patch.object(function, "loadingFileNeeded", return_value=True):
        with mock.patch.object(function, "getSeeingData"):
            function.pollSeeingData()
