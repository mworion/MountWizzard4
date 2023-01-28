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

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.environment.directWeather import DirectWeather


@pytest.fixture(autouse=True, scope='function')
def function():
    func = DirectWeather(app=App())
    yield func


def test_startCommunication_1(function):
    suc = function.startCommunication()
    assert suc


def test_stopCommunication_1(function):
    suc = function.stopCommunication()
    assert suc


def test_updateData_1(function):
    function.enabled = False
    function.running = False
    suc = function.updateData(1)
    assert not suc


def test_updateData_2(function):
    class Sett:
        weatherTemperature = None
        weatherPressure = 900
        weatherHumidity = 50
        weatherDewPoint = 10
        weatherAge = 10

    function.enabled = True
    function.running = True
    suc = function.updateData(Sett())
    assert suc
    assert not function.running


def test_updateData_3(function):
    class Sett:
        weatherTemperature = 10
        weatherPressure = 900
        weatherHumidity = 50
        weatherDewPoint = 10
        weatherAge = 10

    function.enabled = True
    function.running = False
    suc = function.updateData(Sett())
    assert suc
    assert function.running
