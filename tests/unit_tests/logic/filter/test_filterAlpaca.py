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
from logic.filter.filterAlpaca import FilterAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def function():
    func = FilterAlpaca(app=App(), signals=Signals(), data={})
    yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.workerGetInitialConfig()
        assert suc


def test_workerGetInitialConfig_2(function):
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=None):
        suc = function.workerGetInitialConfig()
        assert not suc


def test_workerGetInitialConfig_3(function):
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=['test', 'test1']):
        suc = function.workerGetInitialConfig()
        assert suc
        assert function.data['FILTER_NAME.FILTER_SLOT_NAME_0'] == 'test'
        assert function.data['FILTER_NAME.FILTER_SLOT_NAME_1'] == 'test1'


def test_workerGetInitialConfig_4(function):
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=['test', None]):
        suc = function.workerGetInitialConfig()
        assert suc
        assert function.data['FILTER_NAME.FILTER_SLOT_NAME_0'] == 'test'


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=-1):
        suc = function.workerPollData()
        assert not suc


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=-1):
        suc = function.workerPollData()
        assert not suc


def test_workerPollData_3(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=1):
        suc = function.workerPollData()
        assert suc
        assert function.data['FILTER_SLOT.FILTER_SLOT_VALUE'] == 1


def test_sendFilterNumber_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'setAlpacaProperty'):
        suc = function.sendFilterNumber()
        assert not suc


def test_sendFilterNumber_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'setAlpacaProperty'):
        suc = function.sendFilterNumber()
        assert suc
