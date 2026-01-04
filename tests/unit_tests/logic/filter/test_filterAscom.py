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

import platform
import pytest
import unittest.mock as mock
from mw4.base.ascomClass import AscomClass
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from mw4.logic.filter.filterAscom import FilterAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()

if not platform.system() == "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    signals = Signals()
    deviceType = ""
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    class Test1:
        Names = []
        Position = 1
        Name = "test"
        DriverVersion = "1"
        DriverInfo = "test1"

    func = FilterAscom(parent=Parent())
    func.clientProps = []
    func.client = Test1()
    yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(AscomClass, "workerGetInitialConfig", return_value=True):
        with mock.patch.object(function, "getAscomProperty", return_value=None):
            function.workerGetInitialConfig()


def test_workerGetInitialConfig_2(function):
    with mock.patch.object(AscomClass, "workerGetInitialConfig", return_value=True):
        with mock.patch.object(function, "getAscomProperty", return_value=["test"]):
            with mock.patch.object(function, "storePropertyToData"):
                function.workerGetInitialConfig()


def test_workerPollData_1(function):
    function.client.Position = -1
    function.workerPollData()


def test_workerPollData_2(function):
    function.client.Position = 1
    with mock.patch.object(function, "getAscomProperty", return_value=-1):
        function.workerPollData()


def test_workerPollData_3(function):
    function.client.Position = 1
    with mock.patch.object(function, "getAscomProperty", return_value=1):
        with mock.patch.object(function, "storePropertyToData"):
            function.workerPollData()


def test_sendFilterNumber_1(function):
    function.deviceConnected = True
    with mock.patch.object(function, "setAscomProperty"):
        function.sendFilterNumber(3)


def test_sendFilterNumber_2(function):
    function.deviceConnected = False
    function.sendFilterNumber(3)
