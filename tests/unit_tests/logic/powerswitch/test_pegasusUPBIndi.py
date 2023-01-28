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
from logic.powerswitch.pegasusUPBIndi import PegasusUPBIndi
from base.driverDataClass import Signals
from base.indiClass import IndiClass


@pytest.fixture(autouse=True, scope='function')
def function():
    func = PegasusUPBIndi(app=App(), signals=Signals(), data={})
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


def test_updateText_1(function):
    suc = function.updateText('test', 'test')
    assert not suc


def test_updateText_2(function):
    function.data = {'AUTO_DEW.DEW_C': 1,
                     'VERSION.UPB': 1}
    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = function.updateText('test', 'test')
        assert not suc


def test_updateText_3(function):
    function.data = {'DRIVER_INFO.DEVICE_MODEL': 'UPB',
                     'FIRMWARE_INFO.VERSION': '1.4'}

    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = function.updateText('test', 'DRIVER_INFO')
        assert suc


def test_updateText_4(function):
    function.data = {'DRIVER_INFO.DEVICE_MODEL': 'UPBv2',
                     'FIRMWARE_INFO.VERSION': '1.5'}

    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = function.updateText('test', 'DRIVER_INFO')
        assert suc


def test_updateText_5(function):
    function.data = {'DRIVER_INFO.DEVICE_MODEL': 'UPBv2',
                     'FIRMWARE_INFO.VERSION': '1.4'}
    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = function.updateText('test', 'DRIVER_INFO')
        assert suc


def test_updateText_6(function):
    function.data = {'DRIVER_INFO.DEVICE_MODEL': 'UPB',
                     'FIRMWARE_INFO.VERSION': '1.5'}
    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = function.updateText('test', 'DRIVER_INFO')
        assert suc


def test_updateNumber_1(function):
    suc = function.updateNumber('test', 'test')
    assert not suc


def test_updateNumber_2(function):
    function.data = {'AUTO_DEW.DEW_C': 1,
                     'VERSION.UPB': 1}
    with mock.patch.object(IndiClass,
                           'updateNumber',
                           return_value=True):
        suc = function.updateNumber('test', 'test')
        assert suc


def test_updateSwitch_1(function):
    suc = function.updateSwitch('test', 'test')
    assert not suc


def test_updateSwitch_2(function):
    function.data = {'AUTO_DEW.AUTO_DEW_ENABLED': 1,
                     'VERSION.UPB': 2}
    with mock.patch.object(IndiClass,
                           'updateSwitch',
                           return_value=True):
        suc = function.updateSwitch('test', 'test')
        assert suc


def test_togglePowerPort_1(function):
    suc = function.togglePowerPort()
    assert not suc


def test_togglePowerPort_2(function):
    suc = function.togglePowerPort(port=1)
    assert not suc


def test_togglePowerPort_3(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'POWER_CONTROL_0': 'On'}):
        suc = function.togglePowerPort(port=1)
        assert not suc


def test_togglePowerPort_4(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'POWER_CONTROL_1': 'On'}):
        suc = function.togglePowerPort(port=1)
        assert not suc


def test_togglePowerPort_5(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'OUTLET_1': 'On'}):
        suc = function.togglePowerPort(port=1)
        assert not suc


def test_togglePowerPort_6(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'OUTLET_1': 'Off'}):
        suc = function.togglePowerPort(port=1)
        assert not suc


def test_togglePowerPortBoot_1(function):
    suc = function.togglePowerPortBoot()
    assert not suc


def test_togglePowerPortBoot_2(function):
    suc = function.togglePowerPortBoot(port=1)
    assert not suc


def test_togglePowerPortBoot_3(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'POWER_PORT_0': 'On'}):
        suc = function.togglePowerPortBoot(port=1)
        assert not suc


def test_togglePowerPortBoot_4(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'POWER_PORT_1': 'On'}):
        suc = function.togglePowerPortBoot(port=1)
        assert not suc


def test_togglePowerPortBoot_5(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'POWER_PORT_1': 'On'}):
        suc = function.togglePowerPortBoot(port=1)
        assert not suc


def test_togglePowerPortBoot_6(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'POWER_PORT_1': 'Off'}):
        suc = function.togglePowerPortBoot(port=1)
        assert not suc


def test_togglePowerPortBoot_7(function):
    function.device = Device()
    function.isINDIGO = False
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'POWER_PORT_1': 'Off'}):
        suc = function.togglePowerPortBoot(port=1)
        assert not suc


def test_toggleHubUSB_1(function):
    suc = function.toggleHubUSB()
    assert not suc


def test_toggleHubUSB_2(function):
    suc = function.toggleHubUSB()
    assert not suc


def test_toggleHubUSB_3(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'test': 'On'}):
        suc = function.toggleHubUSB()
        assert not suc


def test_toggleHubUSB_4(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'Off'}):
        suc = function.toggleHubUSB()
        assert not suc


def test_toggleHubUSB_5(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'Off'}):
        suc = function.toggleHubUSB()
        assert not suc


def test_toggleHubUSB_6(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'Off',
                                         'INDI_DISABLED': 'On'}):
        suc = function.toggleHubUSB()
        assert not suc


def test_togglePortUSB_1(function):
    suc = function.togglePortUSB()
    assert not suc


def test_togglePortUSB_2(function):
    suc = function.togglePortUSB(port='1')
    assert not suc


def test_togglePortUSB_3(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PORT_1': 'On'}):
        suc = function.togglePortUSB(port='1')
        assert not suc


def test_togglePortUSB_4(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PORT_1': 'On'}):
        suc = function.togglePortUSB(port='0')
        assert not suc


def test_togglePortUSB_5(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PORT_1': 'On'}):
        suc = function.togglePortUSB(port='0')
        assert not suc


def test_togglePortUSB_6(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'PORT_0': 'Off'}):
        suc = function.togglePortUSB(port='0')
        assert not suc


def test_toggleAutoDew_1(function):
    suc = function.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2(function):
    function.device = Device()
    function.modelVersion = 1
    suc = function.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2b(function):
    function.device = Device()
    function.modelVersion = 0
    suc = function.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_3(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'On',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = function.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_4(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'On',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = function.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_5(function):
    function.device = Device()
    function.modelVersion = 1
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'Off',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = function.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_6(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'MANUAL': 'On',
                                         'AUTOMATIC': 'Off',
                                         'DEW_A': 'On',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = function.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_7(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'MANUAL': 'Off',
                                         'AUTOMATIC': 'Off',
                                         'DEW_A': 'Off',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = function.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_8(function):
    function.device = Device()
    function.modelVersion = 1
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'Off',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'On',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = function.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_9(function):
    function.device = Device()
    function.modelVersion = 2
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'Off',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = function.toggleAutoDew()
        assert not suc


def test_sendDew_1(function):
    suc = function.sendDew()
    assert not suc


def test_sendDew_2(function):
    suc = function.sendDew(port=1)
    assert not suc


def test_sendDew_3(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'DEW_1': 50}):
        suc = function.sendDew(port=1)
        assert not suc


def test_sendDew_4(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'DEW_1': 50}):
        suc = function.sendDew(port='A')
        assert not suc


def test_sendDew_5(function):
    function.device = Device()
    function.isINDIGO = 'On'
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'OUTLET_1': 50}):
        suc = function.sendDew(port='A')
        assert not suc


def test_sendAdjustableOutput_1(function):
    suc = function.sendAdjustableOutput()
    assert not suc


def test_sendAdjustableOutput_2(function):
    suc = function.sendAdjustableOutput()
    assert not suc


def test_sendAdjustableOutput_3(function):
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'ADJUSTABLE_VOLTAGE': 12}):
        suc = function.sendAdjustableOutput()
        assert not suc


def test_sendAdjustableOutput_4(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'ADJUSTABLE_VOLTAGE': 12}):
        suc = function.sendAdjustableOutput()
        assert not suc


def test_reboot_1(function):
    suc = function.reboot()
    assert not suc


def test_reboot_2(function):
    function.device = Device()
    suc = function.reboot()
    assert not suc


def test_reboot_3(function):
    function.device = Device()
    function.isINDIGO = True
    suc = function.reboot()
    assert not suc


def test_reboot_4(function):
    function.device = Device()
    function.isINDIGO = True
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'REBOOT': 'On'}):
        suc = function.reboot()
        assert not suc
