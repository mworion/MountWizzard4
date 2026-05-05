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
    func.device = mock.MagicMock()
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        function.pollData()
        m.assert_called_once_with(
            "Position",
            "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION",
        )


def test_move_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.move(position=100)
    item = function.commandQueue.get_nowait()
    assert item.name == "Move"
    assert item.kwargs == {"Position": 100}


def test_halt_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.halt()
    item = function.commandQueue.get_nowait()
    assert item.name == "Halt"
