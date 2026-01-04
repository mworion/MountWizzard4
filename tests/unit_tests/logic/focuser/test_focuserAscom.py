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

import platform
import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.focuser.focuserAscom import FocuserAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

if not platform.system() == "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    class Test1:
        @staticmethod
        def move(a):
            return True

        @staticmethod
        def halt():
            return True

        Position = 1
        Name = "test"
        DriverVersion = "1"
        DriverInfo = "test1"

    func = FocuserAscom(parent=Parent())
    func.clientProps = []
    func.client = Test1()
    yield func


def test_workerPollData_1(function):
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        function.workerPollData()


def test_move_1(function):
    function.deviceConnected = True
    function.move(3)


def test_move_2(function):
    function.deviceConnected = False
    function.move(3)


def test_halt_1(function):
    function.deviceConnected = True
    function.halt()


def test_halt_2(function):
    function.deviceConnected = False
    function.halt()
