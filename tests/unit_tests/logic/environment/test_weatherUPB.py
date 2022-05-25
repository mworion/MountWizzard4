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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.environment.weatherUPB import WeatherUPB


@pytest.fixture(autouse=True, scope='function')
def function():
    func = WeatherUPB(app=App())
    yield func


def test_startCommunication_1(function):
    function.framework = ''
    suc = function.startCommunication()
    assert not suc


def test_startCommunication_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'startCommunication',
                           return_value=True):
        suc = function.startCommunication()
        assert suc


def test_stopCommunication_1(function):
    function.framework = ''
    suc = function.stopCommunication()
    assert not suc


def test_stopCommunication_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'stopCommunication',
                           return_value=True):
        suc = function.stopCommunication()
        assert suc