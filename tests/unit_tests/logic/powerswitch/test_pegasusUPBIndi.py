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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from indibase.indiBase import Device, Client

# local import
from logic.powerswitch.pegasusUPBIndi import PegasusUPBIndi
from base.driverDataClass import Signals
from base.indiClass import IndiClass


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        mes = pyqtSignal(object, object, object, object)

    global app
    app = PegasusUPBIndi(app=Test(), signals=Signals(), data={})

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


def test_updateText_1():
    suc = app.updateText('test', 'test')
    assert not suc


def test_updateText_2():
    app.data = {'AUTO_DEW.DEW_C': 1,
                'VERSION.UPB': 1}
    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = app.updateText('test', 'test')
        assert not suc


def test_updateText_3():
    app.data = {'DRIVER_INFO.DEVICE_MODEL': 'UPB',
                'FIRMWARE_INFO.VERSION': '1.4'}

    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = app.updateText('test', 'DRIVER_INFO')
        assert suc


def test_updateText_4():
    app.data = {'DRIVER_INFO.DEVICE_MODEL': 'UPBv2',
                'FIRMWARE_INFO.VERSION': '1.5'}

    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = app.updateText('test', 'DRIVER_INFO')
        assert suc


def test_updateText_5():
    app.data = {'DRIVER_INFO.DEVICE_MODEL': 'UPBv2',
                'FIRMWARE_INFO.VERSION': '1.4'}
    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = app.updateText('test', 'DRIVER_INFO')
        assert suc


def test_updateText_6():
    app.data = {'DRIVER_INFO.DEVICE_MODEL': 'UPB',
                'FIRMWARE_INFO.VERSION': '1.5'}
    with mock.patch.object(IndiClass,
                           'updateText',
                           return_value=True):
        suc = app.updateText('test', 'DRIVER_INFO')
        assert suc


def test_updateNumber_1():
    suc = app.updateNumber('test', 'test')
    assert not suc


def test_updateNumber_2():
    app.data = {'AUTO_DEW.DEW_C': 1,
                'VERSION.UPB': 1}
    with mock.patch.object(IndiClass,
                           'updateNumber',
                           return_value=True):
        suc = app.updateNumber('test', 'test')
        assert suc


def test_updateSwitch_1():
    suc = app.updateSwitch('test', 'test')
    assert not suc


def test_updateSwitch_2():
    app.data = {'AUTO_DEW.AUTO_DEW_ENABLED': 1,
                'VERSION.UPB': 2}
    with mock.patch.object(IndiClass,
                           'updateSwitch',
                           return_value=True):
        suc = app.updateSwitch('test', 'test')
        assert suc


def test_togglePowerPort_1():
    suc = app.togglePowerPort()
    assert not suc


def test_togglePowerPort_2():
    suc = app.togglePowerPort(port=1)
    assert not suc


def test_togglePowerPort_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'POWER_CONTROL_0': 'On'}):
        suc = app.togglePowerPort(port=1)
        assert not suc


def test_togglePowerPort_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'POWER_CONTROL_1': 'On'}):
        suc = app.togglePowerPort(port=1)
        assert not suc


def test_togglePowerPort_5():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'OUTLET_1': 'On'}):
        suc = app.togglePowerPort(port=1)
        assert not suc


def test_togglePowerPort_6():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'OUTLET_1': 'Off'}):
        suc = app.togglePowerPort(port=1)
        assert not suc


def test_togglePowerPortBoot_1():
    suc = app.togglePowerPortBoot()
    assert not suc


def test_togglePowerPortBoot_2():
    suc = app.togglePowerPortBoot(port=1)
    assert not suc


def test_togglePowerPortBoot_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'POWER_PORT_0': 'On'}):
        suc = app.togglePowerPortBoot(port=1)
        assert not suc


def test_togglePowerPortBoot_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'POWER_PORT_1': 'On'}):
        suc = app.togglePowerPortBoot(port=1)
        assert not suc


def test_togglePowerPortBoot_5():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'POWER_PORT_1': 'On'}):
        suc = app.togglePowerPortBoot(port=1)
        assert not suc


def test_togglePowerPortBoot_6():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'POWER_PORT_1': 'Off'}):
        suc = app.togglePowerPortBoot(port=1)
        assert not suc


def test_togglePowerPortBoot_7():
    app.device = Device()
    app.isINDIGO = False
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'POWER_PORT_1': 'Off'}):
        suc = app.togglePowerPortBoot(port=1)
        assert not suc


def test_toggleHubUSB_1():
    suc = app.toggleHubUSB()
    assert not suc


def test_toggleHubUSB_2():
    suc = app.toggleHubUSB()
    assert not suc


def test_toggleHubUSB_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'test': 'On'}):
        suc = app.toggleHubUSB()
        assert not suc


def test_toggleHubUSB_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'Off'}):
        suc = app.toggleHubUSB()
        assert not suc


def test_toggleHubUSB_5():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'Off'}):
        suc = app.toggleHubUSB()
        assert not suc


def test_toggleHubUSB_6():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'Off',
                                         'INDI_DISABLED': 'On'}):
        suc = app.toggleHubUSB()
        assert not suc


def test_togglePortUSB_1():
    suc = app.togglePortUSB()
    assert not suc


def test_togglePortUSB_2():
    suc = app.togglePortUSB(port='1')
    assert not suc


def test_togglePortUSB_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PORT_1': 'On'}):
        suc = app.togglePortUSB(port='1')
        assert not suc


def test_togglePortUSB_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PORT_1': 'On'}):
        suc = app.togglePortUSB(port='0')
        assert not suc


def test_togglePortUSB_5():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PORT_1': 'On'}):
        suc = app.togglePortUSB(port='0')
        assert not suc


def test_togglePortUSB_6():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PORT_0': 'Off'}):
        suc = app.togglePortUSB(port='0')
        assert not suc


def test_toggleAutoDew_1():
    suc = app.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2():
    app.device = Device()
    app.modelVersion = 1
    suc = app.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2b():
    app.device = Device()
    app.modelVersion = 0
    suc = app.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'On',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = app.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'On',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = app.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_5():
    app.device = Device()
    app.modelVersion = 1
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'Off',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = app.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_6():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'MANUAL': 'On',
                                         'AUTOMATIC': 'Off',
                                         'DEW_A': 'On',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = app.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_7():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'MANUAL': 'Off',
                                         'AUTOMATIC': 'Off',
                                         'DEW_A': 'Off',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = app.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_8():
    app.device = Device()
    app.modelVersion = 1
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'Off',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'On',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = app.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_9():
    app.device = Device()
    app.modelVersion = 2
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'INDI_ENABLED': 'On',
                                         'INDI_DISABLED': 'On',
                                         'DEW_A': 'Off',
                                         'DEW_B': 'On',
                                         'DEW_C': 'On',
                                         }):
        suc = app.toggleAutoDew()
        assert not suc


def test_sendDew_1():
    suc = app.sendDew()
    assert not suc


def test_sendDew_2():
    suc = app.sendDew(port=1)
    assert not suc


def test_sendDew_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'DEW_1': 50}):
        suc = app.sendDew(port=1)
        assert not suc


def test_sendDew_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'DEW_1': 50}):
        suc = app.sendDew(port='A')
        assert not suc


def test_sendDew_5():
    app.device = Device()
    app.isINDIGO = 'On'
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'OUTLET_1': 50}):
        suc = app.sendDew(port='A')
        assert not suc


def test_sendAdjustableOutput_1():
    suc = app.sendAdjustableOutput()
    assert not suc


def test_sendAdjustableOutput_2():
    suc = app.sendAdjustableOutput()
    assert not suc


def test_sendAdjustableOutput_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'ADJUSTABLE_VOLTAGE': 12}):
        suc = app.sendAdjustableOutput()


def test_sendAdjustableOutput_4():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'ADJUSTABLE_VOLTAGE': 12}):
        suc = app.sendAdjustableOutput()
        assert not suc


def test_reboot_1():
    suc = app.reboot()
    assert not suc


def test_reboot_2():
    app.device = Device()
    suc = app.reboot()
    assert not suc


def test_reboot_3():
    app.device = Device()
    app.isINDIGO = True
    suc = app.reboot()
    assert not suc


def test_reboot_4():
    app.device = Device()
    app.isINDIGO = True
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'REBOOT': 'On'}):
        suc = app.reboot()
        assert not suc
