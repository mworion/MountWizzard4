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
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from mw4.logic.dome.domeAscom import DomeAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = DomeAscom(parent=Parent())
    func.device = mock.MagicMock()
    func.device.Azimuth = 100
    func.device.Slewing = False
    yield func


def test_getInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        function.getInitialConfig()


def test_pollData_shutterOpen(function):
    with mock.patch.object(function, "getAscomProperty", return_value=0):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getAndStoreAscomProperty"):
                function.pollData()


def test_pollData_shutterClosed(function):
    with mock.patch.object(function, "getAscomProperty", return_value=1):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getAndStoreAscomProperty"):
                function.pollData()


def test_pollData_shutterOther(function):
    with mock.patch.object(function, "getAscomProperty", return_value=2):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getAndStoreAscomProperty"):
                function.pollData()


def test_slewToAltAz(function):
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.slewToAltAz(30.0, 180.0)
    assert m.call_count == 2
    calls = {c[0][0]: c[1] for c in m.call_args_list}
    assert "SlewToAzimuth" in calls
    assert calls["SlewToAzimuth"] == {"Azimuth": 180.0}
    assert "SlewToAltitude" in calls
    assert calls["SlewToAltitude"] == {"Altitude": 30.0}


def test_openShutter(function):
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.openShutter()
    m.assert_called_once_with("OpenShutter")


def test_closeShutter(function):
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.closeShutter()
    m.assert_called_once_with("CloseShutter")


def test_slewCW(function):
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.slewCW()
    m.assert_called_once()


def test_slewCCW(function):
    function.slewCCW()


def test_abortSlew(function):
    function.abortSlew()
