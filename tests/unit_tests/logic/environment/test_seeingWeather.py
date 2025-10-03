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
import json
import os
import shutil
import unittest.mock as mock

import pytest

# external packages
import requests
from base.loggerMW import setupLogging
from logic.environment.seeingWeather import SeeingWeather

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


@pytest.fixture(autouse=True, scope="function")
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
    function.enabled = False
    with mock.patch.object(function, "pollSeeingData"):
        function.startCommunication()
        assert function.enabled


def test_stopCommunication_1(function):
    function.running = True
    function.enabled = True
    function.stopCommunication()
    assert not function.running
    assert not function.enabled


def test_processSeeingData_1(function):
    with mock.patch.object(os.path, "isfile", return_value=False):
        suc = function.processSeeingData()
        assert not suc


def test_processSeeingData_2(function):
    with mock.patch.object(json, "load", return_value={}, side_effect=Exception):
        suc = function.processSeeingData()
        assert not suc


def test_processSeeingData_3(function):
    with mock.patch.object(json, "load", return_value={}):
        suc = function.processSeeingData()
        assert suc


def test_workerGetSeeingData_1(function):
    class Test:
        status_code = 300

    with mock.patch.object(requests, "get", return_value=Test()):
        function.workerGetSeeingData("http://localhost")


def test_workerGetSeeingData_3(function):
    class Test:
        status_code = 300

    with mock.patch.object(requests, "get", side_effect=Exception(), return_value=Test()):
        function.workerGetSeeingData("http://localhost")


def test_workerGetSeeingData_4(function):
    class Test:
        status_code = 300

    with mock.patch.object(requests, "get", side_effect=TimeoutError(), return_value=Test()):
        function.workerGetSeeingData("http://localhost")


def test_workerGetSeeingData_5(function):
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(requests, "get", return_value=Test()):
        function.workerGetSeeingData("http://localhost")


def test_sendStatus_1(function):
    function.running = True
    function.sendStatus(False)


def test_sendStatus_2(function):
    function.running = False
    function.sendStatus(True)


def test_getSeeingData(function):
    with mock.patch.object(function.threadPool, "start"):
        function.getSeeingData("test")


def test_loadingFileNeeded_1(function):
    with mock.patch.object(os.path, "isfile", return_value=False):
        suc = function.loadingFileNeeded("test", 1)
        assert suc


def test_loadingFileNeeded_2(function):
    with mock.patch.object(os.path, "isfile", return_value=True):
        with mock.patch.object(function.app.mount.obsSite.loader, "days_old", return_value=1):
            suc = function.loadingFileNeeded("test", 1)
            assert suc


def test_loadingFileNeeded_3(function):
    with mock.patch.object(os.path, "isfile", return_value=True):
        with mock.patch.object(function.app.mount.obsSite.loader, "days_old", return_value=1):
            suc = function.loadingFileNeeded("test", 25)
            assert not suc


def test_pollSeeingData_1(function):
    function.enabled = False
    function.running = False
    function.online = False
    function.apiKey = ""
    function.pollSeeingData()


def test_pollSeeingData_2(function):
    function.enabled = True
    function.online = False
    function.running = False
    function.apiKey = ""
    function.pollSeeingData()


def test_pollSeeingData_3(function):
    function.enabled = True
    function.online = False
    function.running = True
    function.apiKey = "test"
    function.b = "test"
    function.pollSeeingData()
    assert not function.running


def test_pollSeeingData_4(function):
    function.enabled = True
    function.online = True
    function.running = False
    function.apiKey = "test"
    function.b = "test"
    with mock.patch.object(function, "loadingFileNeeded", return_value=False):
        function.pollSeeingData()


def test_pollSeeingData_5(function):
    function.enabled = True
    function.online = True
    function.running = True
    function.apiKey = "test"
    function.b = "test"
    with mock.patch.object(function, "loadingFileNeeded", return_value=True):
        with mock.patch.object(function, "getSeeingData"):
            function.pollSeeingData()
