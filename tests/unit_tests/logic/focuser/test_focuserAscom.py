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
from mw4.logic.focuser.focuserAscom import FocuserAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    try:
        app = App()
    except Exception:
        app = mock.MagicMock()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    func = FocuserAscom(parent=Parent())
    func.device = mock.MagicMock()
    func.device.Position = 1
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.pollData()


def test_move(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.move(3)
    m.assert_called_once_with("Move", Position=3)


def test_halt(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.halt()
    m.assert_called_once_with("Halt")
