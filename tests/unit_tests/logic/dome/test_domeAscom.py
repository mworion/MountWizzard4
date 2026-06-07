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
import platform
import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.dome.domeAscom import DomeAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    func = DomeAscom(parent=Parent())
    func.device = mock.MagicMock()
    func.device.Azimuth = 100
    func.device.Slewing = False
    yield func


def test_getInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.getInitialConfig()


def test_pollData_shutterOpen(function):
    with (
        mock.patch.object(function, "getDeviceProp", return_value=0),
        mock.patch.object(function, "storePropertyToData"),
        mock.patch.object(function, "getAndStoreDeviceProp"),
    ):
        function.pollData()


def test_pollData_shutterClosed(function):
    with (
        mock.patch.object(function, "getDeviceProp", return_value=1),
        mock.patch.object(function, "storePropertyToData"),
        mock.patch.object(function, "getAndStoreDeviceProp"),
    ):
        function.pollData()


def test_pollData_shutterOther(function):
    with (
        mock.patch.object(function, "getDeviceProp", return_value=2),
        mock.patch.object(function, "storePropertyToData"),
        mock.patch.object(function, "getAndStoreDeviceProp"),
    ):
        function.pollData()


def test_slewToAltAz(function):
    function.data["CanSetAzimuth"] = True
    function.data["CanSetAltitude"] = True
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.slewToAltAz(30.0, 180.0)
    assert m.call_count == 2
    calls = {c[0][0]: c[1] for c in m.call_args_list}
    assert "SlewToAzimuth" in calls
    assert calls["SlewToAzimuth"] == {"Azimuth": 180.0}
    assert "SlewToAltitude" in calls
    assert calls["SlewToAltitude"] == {"Altitude": 30.0}


def test_openShutter(function):
    function.data["CanSetShutter"] = True
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.openShutter()
    m.assert_called_once_with("OpenShutter")


def test_closeShutter(function):
    function.data["CanSetShutter"] = True
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.closeShutter()
    m.assert_called_once_with("CloseShutter")


def test_slewCW(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.slewCW()
    m.assert_called_once()


def test_slewCCW(function):
    function.slewCCW()


def test_abortSlew(function):
    function.abortSlew()
