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
from mw4.logic.cover.coverAscom import CoverAscom
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


@pytest.fixture(autouse=True, scope="module")
def function():
    func = CoverAscom(parent=Parent())
    func.device = mock.MagicMock()
    func.device.CoverState = 1
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getAscomProperty", return_value=1):
        with mock.patch.object(function, "storePropertyToData"):
            function.pollData()


def test_closeCover(function):
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.closeCover()
    m.assert_called_once_with("CloseCover")


def test_openCover(function):
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.openCover()
    m.assert_called_once_with("OpenCover")


def test_haltCover(function):
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        function.haltCover()
    m.assert_called_once_with("HaltCover")
