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
# License APL2.0
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
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = FilterAlpaca(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_getInitialConfig_namesNone(function):
    with mock.patch.object(function, "getDeviceProp", return_value=None):
        function.getInitialConfig()


def test_getInitialConfig_namesPresent(function):
    with mock.patch.object(
        function, "getDeviceProp", return_value=["Red", "Green"]
    ):
        function.getInitialConfig()
        assert function.data["FILTER_NAME.FILTER_SLOT_NAME_0"] == "Red"
        assert function.data["FILTER_NAME.FILTER_SLOT_NAME_1"] == "Green"


def test_getInitialConfig_nameNoneEntry(function):
    with mock.patch.object(
        function, "getDeviceProp", return_value=["Red", None]
    ):
        function.getInitialConfig()
        assert function.data["FILTER_NAME.FILTER_SLOT_NAME_0"] == "Red"


def test_pollData_positionMinusOne(function):
    with mock.patch.object(function, "getDeviceProp", return_value=-1):
        function.pollData()


def test_pollData_positionNone(function):
    with mock.patch.object(function, "getDeviceProp", return_value=None):
        function.pollData()


def test_pollData_positionValid(function):
    with mock.patch.object(function, "getDeviceProp", return_value=2):
        function.pollData()
        assert function.data["FILTER_SLOT.FILTER_SLOT_VALUE"] == 2


def test_sendFilterNumber(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendFilterNumber(filterNumber=3)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "Position"
    assert item.value == 3
