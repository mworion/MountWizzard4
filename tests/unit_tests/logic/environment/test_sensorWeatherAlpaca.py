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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.environment.sensorWeatherAlpaca import SensorWeatherAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def function():
    func = SensorWeatherAlpaca(app=App(), signals=Signals(), data={})
    yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAndStoreAlpacaProperty'):
        suc = function.workerPollData()
        assert not suc


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAndStoreAlpacaProperty'):
        suc = function.workerPollData()
        assert suc
