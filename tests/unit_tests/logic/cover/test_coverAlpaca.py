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

import PySide6
import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.cover.coverAlpaca import CoverAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        func = CoverAlpaca(parent=Parent())
        yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=None):
        function.workerPollData()


def test_workerPollData_3(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getDeviceProp", return_value=1):
        with mock.patch.object(function, "storePropertyToData") as m:
            function.workerPollData()
            m.assert_called_once_with("Closed", "Status.Cover")


def test_closeCover_1(function):
    function.deviceConnected = False
    function.closeCover()


def test_closeCover_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.closeCover()
        m.assert_called_once_with("CloseCover")


def test_openCover_1(function):
    function.deviceConnected = False
    function.openCover()


def test_openCover_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.openCover()
        m.assert_called_once_with("OpenCover")


def test_haltCover_1(function):
    function.deviceConnected = False
    function.haltCover()


def test_haltCover_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "callDeviceMethod") as m:
        function.haltCover()
        m.assert_called_once_with("HaltCover")
