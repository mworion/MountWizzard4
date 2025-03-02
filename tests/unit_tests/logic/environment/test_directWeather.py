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

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.environment.directWeather import DirectWeather


@pytest.fixture(autouse=True, scope="function")
def function():
    func = DirectWeather(app=App())
    yield func


def test_startCommunication_1(function):
    function.startCommunication()


def test_stopCommunication_1(function):
    function.stopCommunication()


def test_updateData_1(function):
    function.enabled = False
    function.running = False
    function.updateData(1)


def test_updateData_2(function):
    class Sett:
        weatherTemperature = None
        weatherPressure = 900
        weatherHumidity = 50
        weatherDewPoint = 10
        weatherAge = 10

    function.enabled = True
    function.running = True
    function.updateData(Sett())
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
    function.updateData(Sett())
    assert function.running
