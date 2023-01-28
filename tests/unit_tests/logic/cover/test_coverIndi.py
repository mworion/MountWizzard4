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
from logic.cover.coverIndi import CoverIndi
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def function():
    func = CoverIndi(app=App(), signals=Signals(), data={})
    yield func


def test_setUpdateConfig_1(function):
    function.deviceName = ''
    function.loadConfig = True
    function.updateRate = 1000
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2(function):
    function.deviceName = 'test'
    function.loadConfig = True
    function.updateRate = 1000
    function.device = None
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3(function):
    function.deviceName = 'test'
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_4(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=False):
            suc = function.setUpdateConfig('test')
            assert not suc


def test_setUpdateConfig_5(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.setUpdateConfig('test')
            assert suc


def test_updateText_1(function):
    function.device = None
    suc = function.updateText('test', 'test')
    assert not suc


def test_updateText_2(function):
    function.device = Device()
    function.deviceName = 'test'
    with mock.patch.object(function.device,
                           'getText',
                           return_value={'Cover': 'OPEN'}):
        suc = function.updateText('test', 'CAP_PARK')
        assert suc


def test_updateText_3(function):
    function.device = Device()
    function.deviceName = 'test'
    with mock.patch.object(function.device,
                           'getText',
                           return_value={'Cover': 'CLOSED'}):
        suc = function.updateText('test', 'CAP_PARK')
        assert suc


def test_updateText_4(function):
    function.device = Device()
    function.deviceName = 'test'
    with mock.patch.object(function.device,
                           'getText',
                           return_value={'Cover': 'test'}):
        suc = function.updateText('test', 'CAP_PARK')
        assert suc


def test_closeCover_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.closeCover()
    assert not suc


def test_closeCover_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = function.closeCover()
        assert not suc


def test_closeCover_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PARK': 'On',
                                         'UNPARK': 'Off'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.closeCover()
            assert not suc


def test_closeCover_4(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PARK': 'On',
                                         '': 'Off'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.closeCover()
            assert not suc


def test_closeCover_5(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PARK': 'Off',
                                         'UNPARK': 'On'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.closeCover()
            assert suc


def test_openCover_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.openCover()
    assert not suc


def test_openCover_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = function.openCover()
        assert not suc


def test_openCover_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PARK': 'On',
                                         'UNPARK': 'Off'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.openCover()
            assert not suc


def test_openCover_4(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PARK': 'On',
                                         '': 'Off'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.openCover()
            assert not suc


def test_openCover_5(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PARK': 'Off',
                                         'UNPARK': 'On'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.openCover()
            assert suc


def test_haltCover_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.haltCover()
    assert not suc


def test_lightOn_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.lightOn()
    assert not suc


def test_lightOn_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = function.lightOn()
        assert not suc


def test_lightOn_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'FLAT_LIGHT_ON': 'On',
                                         'FLAT_LIGHT_OFF': 'Off'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.lightOn()
            assert not suc


def test_lightOn_4(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'FLAT_LIGHT_ON': 'On',
                                         '': 'Off'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.lightOn()
            assert not suc


def test_lightOn_5(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'FLAT_LIGHT_ON': 'Off',
                                         'FLAT_LIGHT_OFF': 'On'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.lightOn()
            assert suc


def test_lightOff_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.lightOff()
    assert not suc


def test_lightOff_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = function.lightOff()
        assert not suc


def test_lightOff_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'FLAT_LIGHT_ON': 'Off',
                                         'FLAT_LIGHT_OFF': 'On'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.lightOff()
            assert not suc


def test_lightOff_4(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'FLAT_LIGHT_OFF': 'On',
                                         '': 'Off'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.lightOff()
            assert not suc


def test_lightOff_5(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'FLAT_LIGHT_ON': 'On',
                                         'FLAT_LIGHT_OFF': 'Off'}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.lightOff()
            assert suc


def test_lightIntensity_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.lightIntensity(1)
    assert not suc


def test_lightIntensity_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.lightIntensity(1)
        assert not suc


def test_lightIntensity_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'FLAT_LIGHT_INTENSITY_VALUE': 128}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=False):
            suc = function.lightIntensity(1)
            assert not suc


def test_lightIntensity_4(function):
    function.deviceName = 'test'
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'FLAT_LIGHT_INTENSITY_VALUE': 128}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.lightIntensity(1)
            assert suc
