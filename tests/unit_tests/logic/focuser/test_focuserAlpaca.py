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
from logic.focuser.focuserAlpaca import FocuserAlpaca
from base.signalsDevices import Signals


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    func = FocuserAlpaca(parent=Parent())
    yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getAlpacaProperty", return_value=1):
        function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=1):
        function.workerPollData()
        assert function.data["ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION"] == 1


def test_move_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "setAlpacaProperty"):
        function.move(position=0)


def test_move_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "setAlpacaProperty"):
        function.move(position=0)


def test_halt_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getAlpacaProperty"):
        function.halt()


def test_halt_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty"):
        function.halt()
