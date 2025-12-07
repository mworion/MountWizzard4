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

import unittest.mock as mock


import PySide6
import pytest

from mw4.base.signalsDevices import Signals
from mw4.logic.cover.coverAlpaca import CoverAlpaca


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
        func = CoverAlpaca(parent=Parent())
        yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getAlpacaProperty", return_value=1):
        function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=1):
        with mock.patch.object(function, "storePropertyToData"):
            function.workerPollData()


def test_closeCover_1(function):
    with mock.patch.object(function, "getAlpacaProperty"):
        function.closeCover()


def test_closeCover_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty"):
        function.closeCover()


def test_openCover_1(function):
    with mock.patch.object(function, "getAlpacaProperty"):
        function.openCover()


def test_openCover_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty"):
        function.openCover()


def test_haltCover_1(function):
    with mock.patch.object(function, "getAlpacaProperty"):
        function.haltCover()


def test_haltCover_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty"):
        function.haltCover()


def test_lightOn_1(function):
    with mock.patch.object(function, "getAlpacaProperty", return_value=0):
        with mock.patch.object(function, "setAlpacaProperty"):
            function.lightOn()


def test_lightOn_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty", return_value=0):
        with mock.patch.object(function, "setAlpacaProperty"):
            function.lightOn()


def test_lightOff_1(function):
    with mock.patch.object(function, "getAlpacaProperty"):
        function.lightOff()


def test_lightOff_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAlpacaProperty"):
        function.lightOff()


def test_lightIntensity_1(function):
    with mock.patch.object(function, "setAlpacaProperty"):
        function.lightIntensity(0)


def test_lightIntensity_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "setAlpacaProperty"):
        function.lightIntensity(0)
