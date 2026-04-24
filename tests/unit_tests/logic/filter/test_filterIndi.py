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
from queue import Queue

from mw4.logic.filter.filter import Filter
from mw4.logic.filter.filterIndi import FilterIndi
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    filt = Filter(App())
    func = FilterIndi(parent=filt)
    yield func
    func.app.threadPool.waitForDone(5000)


# ---------------------------------------------------------------------------
# sendFilterNumber
# ---------------------------------------------------------------------------

def test_sendFilterNumber_default(function):
    """sendFilterNumber() with default value queues filter slot 1."""
    function.sendQ = Queue()
    function.deviceName = "test_filter"
    function.sendFilterNumber()
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_filter", "FILTER_SLOT", {"FILTER_SLOT_VALUE": 1}
    )


def test_sendFilterNumber_explicit(function):
    """sendFilterNumber(n) queues the given filter number."""
    function.sendQ = Queue()
    function.deviceName = "test_filter"
    function.sendFilterNumber(filterNumber=5)
    assert function.sendQ.qsize() == 1
    assert function.sendQ.get() == (
        "test_filter", "FILTER_SLOT", {"FILTER_SLOT_VALUE": 5}
    )
