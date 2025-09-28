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
import pytest
import unittest.mock as mock

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.filter.filterAlpaca import FilterAlpaca
from base.signalsDevices import Signals


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    func = FilterAlpaca(parent=Parent())
    yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(function, "getAlpacaProperty"):
        function.workerGetInitialConfig()


def test_workerGetInitialConfig_2(function):
    with mock.patch.object(function, "getAlpacaProperty", return_value=None):
        function.workerGetInitialConfig()


def test_workerGetInitialConfig_3(function):
    with mock.patch.object(function, "getAlpacaProperty", return_value=["test", "test1"]):
        function.workerGetInitialConfig()
        assert function.data["FILTER_NAME.FILTER_SLOT_NAME_0"] == "test"
        assert function.data["FILTER_NAME.FILTER_SLOT_NAME_1"] == "test1"


def test_workerGetInitialConfig_4(function):
    with mock.patch.object(function, "getAlpacaProperty", return_value=["test", None]):
        function.workerGetInitialConfig()
        assert function.data["FILTER_NAME.FILTER_SLOT_NAME_0"] == "test"


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getAlpacaProperty", return_value=-1):
        function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=-1):
        function.workerPollData()


def test_workerPollData_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=1):
        function.workerPollData()
        assert function.data["FILTER_SLOT.FILTER_SLOT_VALUE"] == 1


def test_sendFilterNumber_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "setAlpacaProperty"):
        function.sendFilterNumber()


def test_sendFilterNumber_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "setAlpacaProperty"):
        function.sendFilterNumber()
