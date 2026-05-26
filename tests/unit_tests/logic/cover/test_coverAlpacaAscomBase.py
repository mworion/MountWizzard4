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
from mw4.logic.cover.coverAlpaca import CoverAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    DEVICE_TYPE = "cover"
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    func = CoverAlpaca(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_coverstates(function):
    assert function.COVERSTATES == [
        "NotPresent",
        "Closed",
        "Moving",
        "Open",
        "Unknown",
        "Error",
    ]


def test_pollData_stateNone(function):
    with mock.patch.object(function, "getDeviceProp", return_value=None):
        function.pollData()


def test_pollData_stateClosed(function):
    with mock.patch.object(function, "getDeviceProp", return_value=1):
        with mock.patch.object(function, "storePropertyToData") as m:
            function.pollData()
            m.assert_called_once_with("Closed", "Status.Cover")


def test_pollData_stateOpen(function):
    with mock.patch.object(function, "getDeviceProp", return_value=3):
        with mock.patch.object(function, "storePropertyToData") as m:
            function.pollData()
            m.assert_called_once_with("Open", "Status.Cover")


def test_closeCover(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.closeCover()
    assert not function.commandQueue.empty()
    item = function.commandQueue.get_nowait()
    assert item.valueProp == "CloseCover"


def test_openCover(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.openCover()
    assert not function.commandQueue.empty()
    item = function.commandQueue.get_nowait()
    assert item.valueProp == "OpenCover"


def test_haltCover(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.haltCover()
    assert not function.commandQueue.empty()
    item = function.commandQueue.get_nowait()
    assert item.valueProp == "HaltCover"
