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
from mw4.logic.focuser.focuser import Focuser
from mw4.logic.focuser.focuserIndi import FocuserIndi
from queue import Queue
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    focuser = Focuser(App())
    func = FocuserIndi(parent=focuser)
    yield func
    func.app.threadPool.waitForDone(5000)


# ---------------------------------------------------------------------------
# move
# ---------------------------------------------------------------------------


def test_move(function):
    """move(position) puts ABS_FOCUS_POSITION command into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_focuser"
    function.move(position=12500)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == (
        "test_focuser",
        "ABS_FOCUS_POSITION",
        {"FOCUS_ABSOLUTE_POSITION": 12500},
    )


# ---------------------------------------------------------------------------
# halt
# ---------------------------------------------------------------------------


def test_halt(function):
    """halt() is a no-op (pass)."""
    function.halt()  # must not raise
