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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import unittest.mock as mock

import pytest

from mw4.base.signalsDevices import Signals
from mw4.logic.focuser.focuserAlpaca import FocuserAlpaca



from tests.unit_tests.unitTestAddOns.baseTestApp import App


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
