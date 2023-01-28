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
from indibase.indiBase import Device, Client

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.focuser.focuserIndi import FocuserIndi
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def function():
    func = FocuserIndi(app=App(), signals=Signals(), data={})
    yield func


def test_setUpdateConfig_1(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = ''
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = 'test'
    function.device = None
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_4(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=False):
            suc = function.setUpdateConfig('test')
            assert not suc


def test_setUpdateConfig_5(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.setUpdateConfig('test')
            assert suc


def test_move_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.move()
    assert not suc


def test_move_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.move()
        assert not suc


def test_move_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'ABS_FOCUS_POSITION': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.move()
            assert suc


def test_halt_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.halt()
    assert not suc


def test_halt_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.halt()
        assert not suc


def test_halt_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'ABS_FOCUS_POSITION': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.halt()
            assert suc
