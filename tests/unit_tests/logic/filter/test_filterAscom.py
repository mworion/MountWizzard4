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
from mw4.logic.filter.filterAscom import FilterAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    signals = Signals()
    deviceType = ""
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = FilterAscom(parent=Parent())
    func.client = mock.MagicMock()
    func.client.Names = []
    func.client.Position = 1
    yield func


def test_getInitialConfig_noNames(function):
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        with mock.patch.object(function, "getAscomProperty", return_value=None):
            function.getInitialConfig()


def test_getInitialConfig_withNames(function):
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        with mock.patch.object(function, "getAscomProperty", return_value=["Red", "Green"]):
            with mock.patch.object(function, "storePropertyToData") as m:
                function.getInitialConfig()
    assert m.call_count == 2


def test_pollData_noPosition(function):
    with mock.patch.object(function, "getAscomProperty", return_value=-1):
        function.pollData()


def test_pollData_nonePosition(function):
    with mock.patch.object(function, "getAscomProperty", return_value=None):
        function.pollData()


def test_pollData_validPosition(function):
    with mock.patch.object(function, "getAscomProperty", return_value=2):
        with mock.patch.object(function, "storePropertyToData") as m:
            function.pollData()
    m.assert_called_once_with(2, "FILTER_SLOT.FILTER_SLOT_VALUE")


def test_sendFilterNumber(function):
    with mock.patch.object(function, "setAscomPropertyQueued") as m:
        function.sendFilterNumber(3)
    m.assert_called_once_with("Position", 3)
