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
import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.environment.sensorWeatherAlpaca import SensorWeatherAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="module")
def function():
    func = SensorWeatherAlpaca(parent=Parent())
    yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getAndStoreAlpacaProperty"):
        function.workerPollData()


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAndStoreAlpacaProperty"):
        function.workerPollData()
