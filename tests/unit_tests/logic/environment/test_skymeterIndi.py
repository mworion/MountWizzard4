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
from indibase.indiBase import Device, Client

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.environment.skymeterIndi import SkymeterIndi
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = SkymeterIndi(app=App(), signals=Signals(), data={})
    yield


def test_setUpdateConfig_1():
    app.deviceName = ''
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2():
    app.deviceName = 'test'
    app.device = None
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = app.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_4():
    app.deviceName = 'test'
    app.device = Device()
    app.client = Client()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=False):
            suc = app.setUpdateConfig('test')
            assert not suc


def test_setUpdateConfig_5():
    app.deviceName = 'test'
    app.device = Device()
    app.client = Client()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.setUpdateConfig('test')
            assert suc
