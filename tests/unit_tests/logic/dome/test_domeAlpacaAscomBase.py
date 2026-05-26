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
from mw4.logic.dome.domeAlpaca import DomeAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    DEVICE_TYPE = "dome"
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = DomeAlpaca(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_shutterStates(function):
    assert function.SHUTTER_STATES == [
        "Open",
        "Closed",
        "Opening",
        "Closing",
        "Error",
    ]


def test_getInitialConfig(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp") as m,
        mock.patch.object(function, "getDeviceProp"),
    ):
        function.getInitialConfig()
        # 3 from base (Name, DriverVersion, DriverInfo) + 3 dome-specific
        assert m.call_count == 6


def test_pollData_shutterOpen(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=0),
    ):
        function.pollData()
        assert function.data.get("DOME_SHUTTER.SHUTTER_OPEN") is True
        assert function.data.get("DOME_SHUTTER.SHUTTER_CLOSED") is False


def test_pollData_shutterClosed(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=1),
    ):
        function.pollData()
        assert function.data.get("DOME_SHUTTER.SHUTTER_OPEN") is False
        assert function.data.get("DOME_SHUTTER.SHUTTER_CLOSED") is True


def test_pollData_shutterElse(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=3),
    ):
        function.pollData()
        assert function.data.get("DOME_SHUTTER.SHUTTER_OPEN") is None
        assert function.data.get("DOME_SHUTTER.SHUTTER_CLOSED") is None


def test_pollData_shutterNone(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=None),
    ):
        function.pollData()
        assert function.data.get("DOME_SHUTTER.SHUTTER_OPEN") is None
        assert function.data.get("DOME_SHUTTER.SHUTTER_CLOSED") is None


def test_slewToAltAz_noFlags(function):
    function.data.pop("CanSetAzimuth", None)
    function.data.pop("CanSetAltitude", None)
    function.slewToAltAz(0, 0)
    assert function.commandQueue.empty()


def test_slewToAltAz_bothFlags(function):
    function.data["CanSetAzimuth"] = True
    function.data["CanSetAltitude"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.slewToAltAz(10, 45)
    assert function.commandQueue.qsize() == 2


def test_openShutter_noFlag(function):
    function.data.pop("CanSetShutter", None)
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.openShutter()
    assert function.commandQueue.empty()


def test_openShutter_withFlag(function):
    function.data["CanSetShutter"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.openShutter()
    assert not function.commandQueue.empty()


def test_closeShutter_noFlag(function):
    function.data.pop("CanSetShutter", None)
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.closeShutter()
    assert function.commandQueue.empty()


def test_closeShutter_withFlag(function):
    function.data["CanSetShutter"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.closeShutter()
    assert not function.commandQueue.empty()


def test_slewCW(function):
    function.slewCW()


def test_slewCCW(function):
    function.slewCCW()


def test_abortSlew(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.abortSlew()
    assert not function.commandQueue.empty()
