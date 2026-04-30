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
from mw4.base.indiClass import IndiClass
from mw4.base.signalsDevices import Signals
from mw4.logic.dome.domeIndi import DomeIndi
from queue import Queue
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = DomeIndi(parent=Parent())
    yield func


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


def test_init_lastAzimuth(function):
    """DomeIndi initialises lastAzimuth to None."""
    assert function.lastAzimuth is None


# ---------------------------------------------------------------------------
# sendDomePosition
# ---------------------------------------------------------------------------


def test_sendDomePosition_absent(function):
    """No ABS_DOME_POSITION key → early return, no crash."""
    function.sendDomePosition({})


def test_sendDomePosition_no_member(function):
    """ABS_DOME_POSITION present but DOME_ABSOLUTE_POSITION missing → early return."""
    vectors = {
        "ABS_DOME_POSITION": {
            "state": "Ok",
            "members": {},
        }
    }
    slot = mock.MagicMock()
    function.signals.azimuth.connect(slot)
    function.sendDomePosition(vectors)
    slot.assert_not_called()
    function.signals.azimuth.disconnect(slot)


def test_sendDomePosition_busy(function):
    """ABS_DOME_POSITION with state Busy → Slewing=True, azimuth emitted."""
    vectors = {
        "ABS_DOME_POSITION": {
            "state": "Busy",
            "members": {"DOME_ABSOLUTE_POSITION": {"value": "180.0", "floatvalue": 180.0}},
        }
    }
    slot = mock.MagicMock()
    function.signals.azimuth.connect(slot)
    function.sendDomePosition(vectors)
    assert function.data["Slewing"] is True
    slot.assert_called_once_with(180.0)
    function.signals.azimuth.disconnect(slot)


def test_sendDomePosition_ok(function):
    """ABS_DOME_POSITION with state Ok → Slewing=False, azimuth emitted."""
    vectors = {
        "ABS_DOME_POSITION": {
            "state": "Ok",
            "members": {"DOME_ABSOLUTE_POSITION": {"value": "90.0", "floatvalue": 90.0}},
        }
    }
    slot = mock.MagicMock()
    function.signals.azimuth.connect(slot)
    function.sendDomePosition(vectors)
    assert function.data["Slewing"] is False
    slot.assert_called_once_with(90.0)
    function.signals.azimuth.disconnect(slot)


# ---------------------------------------------------------------------------
# addShutterStatus
# ---------------------------------------------------------------------------


def test_addShutterStatus_absent(function):
    """No DOME_SHUTTER key → early return, Shutter.Status not set."""
    function.data.pop("Shutter.Status", None)
    function.addShutterStatus({})
    assert "Shutter.Status" not in function.data


def test_addShutterStatus_busy(function):
    """DOME_SHUTTER state Busy → Shutter.Status = 'Moving'."""
    vectors = {
        "DOME_SHUTTER": {
            "state": "Busy",
            "members": {},
        }
    }
    function.addShutterStatus(vectors)
    assert function.data["Shutter.Status"] == "Moving"


def test_addShutterStatus_ok(function):
    """DOME_SHUTTER state Ok → Shutter.Status = '-'."""
    vectors = {
        "DOME_SHUTTER": {
            "state": "Ok",
            "members": {},
        }
    }
    function.addShutterStatus(vectors)
    assert function.data["Shutter.Status"] == "-"


# ---------------------------------------------------------------------------
# writeVectorsToData
# ---------------------------------------------------------------------------


def test_writeVectorsToData(function):
    """super(), sendDomePosition and addShutterStatus are all called."""
    item = mock.MagicMock()
    vectors = {}
    with mock.patch.object(IndiClass, "writeVectorsToData") as mock_super:
        with mock.patch.object(function, "sendDomePosition") as mock_pos:
            with mock.patch.object(function, "addShutterStatus") as mock_shut:
                function.writeVectorsToData(item, vectors)
                mock_super.assert_called_once_with(item, vectors)
                mock_pos.assert_called_once_with(vectors)
                mock_shut.assert_called_once_with(vectors)


# ---------------------------------------------------------------------------
# slewToAltAz
# ---------------------------------------------------------------------------


def test_slewToAltAz(function):
    """slewToAltAz puts DOME_ABSOLUTE_POSITION with azimuth into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_dome"
    function.slewToAltAz(altitude=30, azimuth=180)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == (
        "test_dome",
        "ABS_DOME_POSITION",
        {"DOME_ABSOLUTE_POSITION": 180},
    )


# ---------------------------------------------------------------------------
# openShutter
# ---------------------------------------------------------------------------


def test_openShutter(function):
    """openShutter puts SHUTTER_OPEN=On into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_dome"
    function.openShutter()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_dome", "DOME_SHUTTER", {"SHUTTER_OPEN": "On"})


# ---------------------------------------------------------------------------
# closeShutter
# ---------------------------------------------------------------------------


def test_closeShutter(function):
    """closeShutter puts SHUTTER_CLOSE=On into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_dome"
    function.closeShutter()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_dome", "DOME_SHUTTER", {"SHUTTER_CLOSE": "On"})


# ---------------------------------------------------------------------------
# slewCW
# ---------------------------------------------------------------------------


def test_slewCW(function):
    """slewCW puts DOME_CW=On into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_dome"
    function.slewCW()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_dome", "DOME_MOTION", {"DOME_CW": "On"})


# ---------------------------------------------------------------------------
# slewCCW
# ---------------------------------------------------------------------------


def test_slewCCW(function):
    """slewCCW puts DOME_CCW=On into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_dome"
    function.slewCCW()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_dome", "DOME_MOTION", {"DOME_CCW": "On"})


# ---------------------------------------------------------------------------
# abortSlew
# ---------------------------------------------------------------------------


def test_abortSlew(function):
    """abortSlew puts ABORT=On into txQ."""
    function.txQ = Queue()
    function.deviceName = "test_dome"
    function.abortSlew()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_dome", "DOME_ABORT_MOTION", {"ABORT": "On"})
