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
