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
from mw4.logic.focuser.focuserAlpaca import FocuserAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = FocuserAlpaca(parent=Parent())
    yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(
        function, "getAndStoreDeviceProp"
    ) as m:
        function.workerPollData()
        m.assert_called_once_with(
            "Position", "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION"
        )


def test_move_1(function):
    function.deviceConnected = False
    function.move(position=0)


def test_move_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.move(position=100)
        m.assert_called_once_with("Move", Position=100)


def test_halt_1(function):
    function.deviceConnected = False
    function.halt()


def test_halt_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.halt()
        m.assert_called_once_with("Halt")
