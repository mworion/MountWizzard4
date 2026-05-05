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

import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.filter.filterAlpaca import FilterAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = FilterAlpaca(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_getInitialConfig_1(function):
    with mock.patch.object(function, "getDeviceProp", return_value=None):
        function.getInitialConfig()


def test_getInitialConfig_2(function):
    with mock.patch.object(function, "getDeviceProp", return_value=["test", "test1"]):
        function.getInitialConfig()
        assert function.data["FILTER_NAME.FILTER_SLOT_NAME_0"] == "test"
        assert function.data["FILTER_NAME.FILTER_SLOT_NAME_1"] == "test1"


def test_getInitialConfig_3(function):
    with mock.patch.object(function, "getDeviceProp", return_value=["test", None]):
        function.getInitialConfig()
        assert function.data["FILTER_NAME.FILTER_SLOT_NAME_0"] == "test"


def test_pollData_1(function):
    with mock.patch.object(function, "getDeviceProp", return_value=-1):
        function.pollData()


def test_pollData_2(function):
    with mock.patch.object(function, "getDeviceProp", return_value=None):
        function.pollData()


def test_pollData_3(function):
    with mock.patch.object(function, "getDeviceProp", return_value=1):
        function.pollData()
        assert function.data["FILTER_SLOT.FILTER_SLOT_VALUE"] == 1


def test_sendFilterNumber_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendFilterNumber(filterNumber=2)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.name == "Position"
    assert item.value == 2
