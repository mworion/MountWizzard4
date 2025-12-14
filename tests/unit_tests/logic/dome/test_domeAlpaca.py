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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import PySide6
import pytest
import unittest.mock as mock
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.signalsDevices import Signals
from mw4.logic.dome.domeAlpaca import DomeAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        func = DomeAlpaca(parent=Parent())
        yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(AlpacaClass, "getAndStoreAlpacaProperty", return_value=True):
        with mock.patch.object(function, "getAndStoreAlpacaProperty"):
            function.workerGetInitialConfig()


def test_workerPollData_1(function):
    function.data["CAN_FAST"] = True
    with mock.patch.object(function, "getAndStoreAlpacaProperty"):
        function.workerPollData()


def test_processPolledData_1(function):
    function.processPolledData()


def test_workerPollData_1(function):
    function.deviceConnected = False
    function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=0):
        with mock.patch.object(function, "getAndStoreAlpacaProperty"):
            function.workerPollData()


def test_workerPollData_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=1):
        with mock.patch.object(function, "getAndStoreAlpacaProperty"):
            function.workerPollData()


def test_workerPollData_4(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=3):
        with mock.patch.object(function, "getAndStoreAlpacaProperty"):
            function.workerPollData()


def test_slewToAltAz_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "setAlpacaProperty"):
        function.slewToAltAz(0, 0)


def test_slewToAltAz_2(function):
    function.deviceConnected = True
    function.data["CanSetAzimuth"] = True
    function.data["CanSetAltitude"] = True
    with mock.patch.object(function, "setAlpacaProperty"):
        function.slewToAltAz(0, 0)


def test_closeShutter_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getAlpacaProperty"):
        function.closeShutter()


def test_closeShutter_2(function):
    function.deviceConnected = True
    function.data["CanSetShutter"] = True
    with mock.patch.object(function, "getAlpacaProperty"):
        function.closeShutter()


def test_openShutter_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getAlpacaProperty"):
        function.openShutter()


def test_openShutter_2(function):
    function.deviceConnected = True
    function.data["CanSetShutter"] = True
    with mock.patch.object(function, "getAlpacaProperty"):
        function.openShutter()


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
    with mock.patch.object(function, "getAlpacaProperty"):
        function.abortSlew()


def test_abortSlew_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty"):
        function.abortSlew()
