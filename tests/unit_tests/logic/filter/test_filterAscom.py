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
import platform

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.filter.filterAscom import FilterAscom
from base.driverDataClass import Signals
from base.ascomClass import AscomClass

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        Names = []
        Position = 1
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    func = FilterAscom(app=App(), signals=Signals(), data={})
    func.clientProps = []
    func.client = Test1()
    yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(AscomClass,
                           'workerGetInitialConfig',
                           return_value=True):
        with mock.patch.object(function,
                               'getAscomProperty',
                               return_value=None):
            suc = function.workerGetInitialConfig()
            assert not suc


def test_workerGetInitialConfig_2(function):
    with mock.patch.object(AscomClass,
                           'workerGetInitialConfig',
                           return_value=True):
        with mock.patch.object(function,
                               'getAscomProperty',
                               return_value=['test']):
            with mock.patch.object(function,
                                   'storePropertyToData'):
                suc = function.workerGetInitialConfig()
                assert suc


def test_workerPollData_1(function):
    function.client.Position = -1
    suc = function.workerPollData()
    assert not suc


def test_workerPollData_2(function):
    function.client.Position = 1
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=-1):
        suc = function.workerPollData()
        assert not suc


def test_workerPollData_3(function):
    function.client.Position = 1
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=1):
        with mock.patch.object(function,
                               'storePropertyToData'):
            suc = function.workerPollData()
            assert suc


def test_sendFilterNumber_1(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'setAscomProperty'):
        suc = function.sendFilterNumber(3)
        assert suc


def test_sendFilterNumber_2(function):
    function.deviceConnected = False
    suc = function.sendFilterNumber(3)
    assert not suc
