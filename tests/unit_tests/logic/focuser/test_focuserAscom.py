############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import platform

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.focuser.focuserAscom import FocuserAscom
from base.signalsDevices import Signals

if not platform.system() == "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


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

    func = FocuserAscom(app=App(), signals=Signals(), data={})
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
