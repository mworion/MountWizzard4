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
# written in python3, (c) 2019-2025 by mworion
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
from logic.dome.domeAscom import DomeAscom
from base.signalsDevices import Signals
from base.ascomClass import AscomClass

if not platform.system() == "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope="function")
def function():
    class Test1:
        Azimuth = 100
        Name = "test"
        DriverVersion = "1"
        DriverInfo = "test1"
        ShutterStatus = 4
        Slewing = True
        CanSetAltitude = True
        CanSetAzimuth = True
        CanSetShutter = True
        AbortSlew = False
        OpenShutter = None
        CloseShutter = None
        AbortSlew = None

        @staticmethod
        def SlewToAzimuth(azimuth):
            return True

        @staticmethod
        def SlewToAltitude(altitude):
            return True

    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        func = DomeAscom(app=App(), signals=Signals(), data={})
        func.client = Test1()
        func.clientProps = []
        yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(AscomClass, "getAndStoreAscomProperty", return_value=True):
        with mock.patch.object(function, "getAndStoreAscomProperty"):
            function.workerGetInitialConfig()


def test_processPolledData_1(function):
    function.processPolledData()


def test_workerPollData_1(function):
    with mock.patch.object(function, "getAscomProperty", return_value=0):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getAndStoreAscomProperty"):
                function.workerPollData()


def test_workerPollData_2(function):
    with mock.patch.object(function, "getAscomProperty", return_value=1):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getAndStoreAscomProperty"):
                function.workerPollData()


def test_workerPollData_3(function):
    with mock.patch.object(function, "getAscomProperty", return_value=2):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getAndStoreAscomProperty"):
                function.workerPollData()


def test_slewToAltAz_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "callMethodThreaded"):
        function.slewToAltAz(0, 0)


def test_slewToAltAz_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callMethodThreaded"):
        function.slewToAltAz(0, 0)


def test_openShutter_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "callMethodThreaded"):
        function.openShutter()


def test_openShutter_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callMethodThreaded"):
        function.openShutter()


def test_closeShutter_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "callMethodThreaded"):
        function.closeShutter()


def test_closeShutter_2(function):
    function.data["CanSetShutter"] = True
    function.deviceConnected = True
    with mock.patch.object(function, "callMethodThreaded"):
        function.closeShutter()


def test_slewCW_1(function):
    function.deviceConnected = False
    function.slewCW()


def test_slewCW_2(function):
    function.deviceConnected = True
    function.slewCW()


def test_slewCCW_1(function):
    function.deviceConnected = False
    function.slewCCW()


def test_slewCCW_2(function):
    function.deviceConnected = True
    function.slewCCW()


def test_abortSlew_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "callMethodThreaded"):
        function.abortSlew()


def test_abortSlew_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callMethodThreaded"):
        function.abortSlew()
