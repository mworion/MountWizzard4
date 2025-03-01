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
import PySide6

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.cover.coverAscom import CoverAscom
from base.signalsDevices import Signals

if not platform.system() == "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope="function")
def function():
    class Test1:
        Name = "test"
        DriverVersion = "1"
        DriverInfo = "test1"
        CoverState = 1

        @staticmethod
        def CloseCover():
            return True

        @staticmethod
        def OpenCover():
            return True

        @staticmethod
        def HaltCover():
            return True

        @staticmethod
        def CalibratorOn():
            return True

        @staticmethod
        def CalibratorOff():
            return True

        @staticmethod
        def Brightness(a):
            return True

    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        func = CoverAscom(app=App(), signals=Signals(), data={})
        func.client = Test1()
        func.clientProps = []
        yield func


def test_workerPollData_1(function):
    with mock.patch.object(function, "getAscomProperty", return_value=1):
        with mock.patch.object(function, "storePropertyToData"):
            function.workerPollData()


def test_closeCover_1(function):
    function.deviceConnected = False
    function.closeCover()


def test_closeCover_2(function):
    function.deviceConnected = True
    function.closeCover()


def test_closeCover_3(function):
    function.deviceConnected = True
    function.closeCover()


def test_openCover_1(function):
    function.deviceConnected = False
    function.openCover()


def test_openCover_2(function):
    function.deviceConnected = True
    function.openCover()


def test_openCover_3(function):
    function.deviceConnected = True
    function.openCover()


def test_haltCover_1(function):
    function.deviceConnected = False
    function.haltCover()


def test_haltCover_2(function):
    function.deviceConnected = True
    function.haltCover()


def test_haltCover_3(function):
    function.deviceConnected = True
    function.haltCover()


def test_lightOn_1(function):
    function.deviceConnected = False
    function.lightOn()


def test_lightOn_2(function):
    function.deviceConnected = True
    function.lightOn()


def test_lightOn_3(function):
    function.deviceConnected = True
    function.lightOn()


def test_lightOff_1(function):
    function.deviceConnected = False
    function.lightOff()


def test_lightOff_2(function):
    function.deviceConnected = True
    function.lightOff()


def test_lightOff_3(function):
    function.deviceConnected = True
    function.lightOff()


def test_lightIntensity_1(function):
    function.deviceConnected = False
    function.lightIntensity(0)


def test_lightIntensity_2(function):
    function.deviceConnected = True
    function.lightIntensity(0)


def test_lightIntensity_3(function):
    function.deviceConnected = True
    function.lightIntensity(0)
