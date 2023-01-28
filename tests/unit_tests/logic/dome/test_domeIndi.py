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
from logic.dome.domeIndi import DomeIndi
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def function():
    func = DomeIndi(app=App(), signals=Signals(), data={})
    yield func


def test_setUpdateConfig_1(function):
    function.deviceName = ''
    function.loadConfig = True
    function.updateRate = 1000
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2(function):
    function.deviceName = 'test'
    function.device = None
    function.loadConfig = True
    function.updateRate = 1000
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3(function):
    function.deviceName = 'test'
    function.device = Device()
    function.loadConfig = True
    function.updateRate = 1000
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
                           return_value={'PERIOD_MS': 1}):
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
                           return_value={'PERIOD_MS': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.setUpdateConfig('test')
            assert suc


def test_updateStatus_1(function):
    function.device = Device()
    function.client = Client()
    function.client.connected = False

    suc = function.updateStatus()
    assert not suc


def test_updateStatus_2(function):
    function.device = Device()
    function.client = Client()
    function.client.connected = True

    suc = function.updateStatus()
    assert suc


def test_updateNumber_1(function):
    function.device = None
    suc = function.updateNumber('test', 'test')
    assert not suc


def test_updateNumber_2(function):
    function.device = Device()
    function.deviceName = 'test'
    setattr(function.device, 'ABS_DOME_POSITION', {'state': 'Busy'})
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'TEST': 1,
                                         'DOME_ABSOLUTE_POSITION': 2}):
        suc = function.updateNumber('test', 'ABS_DOME_POSITION')
        assert suc


def test_updateNumber_3(function):
    function.device = Device()
    function.deviceName = 'test'
    setattr(function.device, 'DOME_SHUTTER', {'state': 'Busy'})
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'TEST': 1,
                                         'SHUTTER_OPEN': 2}):
        suc = function.updateNumber('test', 'SHUTTER_OPEN')
        assert suc


def test_updateNumber_4(function):
    function.device = Device()
    function.deviceName = 'test'
    setattr(function.device, 'DOME_SHUTTER', {'state': 'test'})
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'TEST': 1,
                                         'SHUTTER_OPEN': 2}):
        suc = function.updateNumber('test', 'SHUTTER_OPEN')
        assert suc


def test_slewToAltAz_1(function):
    suc = function.slewToAltAz()
    assert not suc


def test_slewToAltAz_2(function):
    function.device = Device()
    suc = function.slewToAltAz()
    assert not suc


def test_slewToAltAz_3(function):
    function.device = Device()
    function.deviceName = 'test'
    suc = function.slewToAltAz()
    assert not suc


def test_slewToAltAz_4(function):
    function.device = Device()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'DOME_ABSOLUTE_POSITION': 1}):
        suc = function.slewToAltAz()
        assert not suc


def test_slewToAltAz_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'DOME_ABSOLUTE_POSITION': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=False):
            suc = function.slewToAltAz()
            assert not suc


def test_slewToAltAz_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'DOME_ABSOLUTE_POSITION': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.slewToAltAz()
            assert suc


def test_openShutter_1(function):
    suc = function.openShutter()
    assert not suc


def test_openShutter_2(function):
    function.device = Device()
    suc = function.openShutter()
    assert not suc


def test_openShutter_3(function):
    function.device = Device()
    function.deviceName = 'test'
    suc = function.openShutter()
    assert not suc


def test_openShutter_4(function):
    function.device = Device()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'SHUTTER_OPEN': 1}):
        suc = function.openShutter()
        assert not suc


def test_openShutter_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'SHUTTER_OPEN': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.openShutter()
            assert not suc


def test_openShutter_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'SHUTTER_OPEN': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.openShutter()
            assert suc


def test_closeShutter_1(function):
    suc = function.closeShutter()
    assert not suc


def test_closeShutter_2(function):
    function.device = Device()
    suc = function.closeShutter()
    assert not suc


def test_closeShutter_3(function):
    function.device = Device()
    function.deviceName = 'test'
    suc = function.closeShutter()
    assert not suc


def test_closeShutter_4(function):
    function.device = Device()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'SHUTTER_CLOSE': 1}):
        suc = function.closeShutter()
        assert not suc


def test_closeShutter_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'SHUTTER_CLOSE': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.closeShutter()
            assert not suc


def test_closeShutter_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'SHUTTER_CLOSE': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.closeShutter()
            assert suc


def test_slewCW_1(function):
    suc = function.slewCW()
    assert not suc


def test_slewCW_2(function):
    function.device = Device()
    suc = function.slewCW()
    assert not suc


def test_slewCW_3(function):
    function.device = Device()
    function.deviceName = 'test'
    suc = function.slewCW()
    assert not suc


def test_slewCW_4(function):
    function.device = Device()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        suc = function.slewCW()
        assert not suc


def test_slewCW_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.slewCW()
            assert not suc


def test_slewCW_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.slewCW()
            assert suc


def test_slewCCW_1(function):
    suc = function.slewCCW()
    assert not suc


def test_slewCCW_2(function):
    function.device = Device()
    suc = function.slewCCW()
    assert not suc


def test_slewCCW_3(function):
    function.device = Device()
    function.deviceName = 'test'
    suc = function.slewCCW()
    assert not suc


def test_slewCCW_4(function):
    function.device = Device()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        suc = function.slewCCW()
        assert not suc


def test_slewCCW_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.slewCCW()
            assert not suc


def test_slewCCW_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.slewCCW()
            assert suc


def test_abortSlew_1(function):
    suc = function.abortSlew()
    assert not suc


def test_abortSlew_2(function):
    function.device = Device()
    suc = function.abortSlew()
    assert not suc


def test_abortSlew_3(function):
    function.device = Device()
    function.deviceName = 'test'
    suc = function.abortSlew()
    assert not suc


def test_abortSlew_4(function):
    function.device = Device()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'ABORT': 1}):
        suc = function.abortSlew()
        assert not suc


def test_abortSlew_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'ABORT': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = function.abortSlew()
            assert not suc


def test_abortSlew_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = 'test'

    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'ABORT': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.abortSlew()
            assert suc
