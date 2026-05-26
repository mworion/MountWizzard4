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
from mw4.logic.cover.cover import Cover
from mw4.logic.cover.coverIndi import CoverIndi
from queue import Queue
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    cover = Cover(App())
    func = CoverIndi(parent=cover)
    yield func
    func.app.threadPool.waitForDone(5000)


# ---------------------------------------------------------------------------
# closeCover
# ---------------------------------------------------------------------------


def test_closeCover(function):
    """closeCover() puts one CAP_PARK/PARK command into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_cover"
    function.closeCover()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cover", "CAP_PARK", {"PARK": "On"})


# ---------------------------------------------------------------------------
# openCover
# ---------------------------------------------------------------------------


def test_openCover(function):
    """openCover() puts one CAP_PARK/UNPARK command into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_cover"
    function.openCover()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cover", "CAP_PARK", {"UNPARK": "On"})


# ---------------------------------------------------------------------------
# haltCover
# ---------------------------------------------------------------------------


def test_haltCover(function):
    """haltCover() is a no-op (pass)."""
    function.haltCover()  # must not raise
