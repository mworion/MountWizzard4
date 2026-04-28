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
from queue import Queue

from mw4.base.indiClass import IndiClass
from mw4.logic.cover.cover import Cover
from mw4.logic.cover.coverIndi import CoverIndi
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    cover = Cover(App())
    func = CoverIndi(parent=cover)
    yield func
    func.app.threadPool.waitForDone(5000)


# ---------------------------------------------------------------------------
# writeVectorsToData
# ---------------------------------------------------------------------------


def test_writeVectorsToData_no_cover(function):
    """No 'Cover' key → only super() is called, data not changed."""
    item = mock.MagicMock()
    function.data.pop("CAP_PARK.UNPARK", None)
    with mock.patch.object(IndiClass, "writeVectorsToData") as mock_super:
        function.writeVectorsToData(item, {})
        mock_super.assert_called_once_with(item, {})
    assert "CAP_PARK.UNPARK" not in function.data


def test_writeVectorsToData_with_cover(function):
    """'Cover' key present → data entries populated from members."""
    item = mock.MagicMock()
    vectors = {"Cover": {"name": "Cover", "members": {"OPEN": True, "CLOSE": False}}}
    with mock.patch.object(IndiClass, "writeVectorsToData"):
        function.writeVectorsToData(item, vectors)
    assert function.data["CAP_PARK.UNPARK"] is True
    assert function.data["CAP_PARK.PARK"] is False


def test_writeVectorsToData_cover_missing_members(function):
    """'Cover' with empty members → default False values applied."""
    item = mock.MagicMock()
    vectors = {"Cover": {"name": "Cover", "members": {}}}
    with mock.patch.object(IndiClass, "writeVectorsToData"):
        function.writeVectorsToData(item, vectors)
    assert function.data["CAP_PARK.UNPARK"] is False
    assert function.data["CAP_PARK.PARK"] is False


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


# ---------------------------------------------------------------------------
# lightOn
# ---------------------------------------------------------------------------


def test_lightOn(function):
    """lightOn() puts FLAT_LIGHT_ON='On' into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_cover"
    function.lightOn()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cover", "FLAT_LIGHT_CONTROL", {"FLAT_LIGHT_ON": "On"})


# ---------------------------------------------------------------------------
# lightOff
# ---------------------------------------------------------------------------


def test_lightOff(function):
    """lightOff() puts FLAT_LIGHT_ON='Off' into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_cover"
    function.lightOff()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cover", "FLAT_LIGHT_CONTROL", {"FLAT_LIGHT_ON": "Off"})


# ---------------------------------------------------------------------------
# lightIntensity
# ---------------------------------------------------------------------------


def test_lightIntensity(function):
    """lightIntensity(value) puts the intensity value into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_cover"
    function.lightIntensity(128.0)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == (
        "test_cover",
        "FLAT_LIGHT_INTENSITY",
        {"FLAT_LIGHT_INTENSITY_VALUE": 128.0},
    )
