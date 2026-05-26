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


def test_getInitialConfig_1(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp") as m,
        mock.patch.object(function, "getDeviceProp"),
    ):
        function.getInitialConfig()
        # 3 from base (Name, DriverVersion, DriverInfo) + 3 dome-specific
        assert m.call_count == 6


def test_pollData_1(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=0),
    ):
        function.pollData()
        assert function.data.get("DOME_SHUTTER.SHUTTER_OPEN") is True


def test_pollData_2(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=1),
    ):
        function.pollData()
        assert function.data.get("DOME_SHUTTER.SHUTTER_CLOSED") is True


def test_pollData_3(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=3),
    ):
        function.pollData()
        assert function.data.get("DOME_SHUTTER.SHUTTER_OPEN") is None
        assert function.data.get("DOME_SHUTTER.SHUTTER_CLOSED") is None


def test_pollData_4(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=None),
    ):
        function.pollData()
        assert function.data.get("DOME_SHUTTER.SHUTTER_OPEN") is None
        assert function.data.get("DOME_SHUTTER.SHUTTER_CLOSED") is None


def test_slewToAltAz_1(function):
    function.data.pop("CanSetAzimuth", None)
    function.data.pop("CanSetAltitude", None)
    function.slewToAltAz(0, 0)
    assert function.commandQueue.empty()


def test_slewToAltAz_2(function):
    function.data["CanSetAzimuth"] = True
    function.data["CanSetAltitude"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.slewToAltAz(10, 45)
    assert function.commandQueue.qsize() == 2


def test_closeShutter_1(function):
    function.data.pop("CanSetShutter", None)
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.closeShutter()
    assert function.commandQueue.empty()


def test_closeShutter_2(function):
    function.data["CanSetShutter"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.closeShutter()
    assert not function.commandQueue.empty()


def test_openShutter_1(function):
    function.data.pop("CanSetShutter", None)
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.openShutter()
    assert function.commandQueue.empty()


def test_openShutter_2(function):
    function.data["CanSetShutter"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.openShutter()
    assert not function.commandQueue.empty()


def test_slewCW_1(function):
    function.slewCW()


def test_slewCCW_1(function):
    function.slewCCW()


def test_abortSlew_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.abortSlew()
    assert not function.commandQueue.empty()


def test_startCommunication_1(function):
    with (
        mock.patch.object(function, "createAlpacaDevice", return_value=False),
        mock.patch.object(function.threadPool, "start") as m_start,
    ):
        function.startCommunication()
        m_start.assert_not_called()


def test_startCommunication_2(function):
    with (
        mock.patch.object(function, "createAlpacaDevice", return_value=True),
        mock.patch.object(function.threadPool, "start") as m_start,
    ):
        function.startCommunication()
        m_start.assert_called_once()
