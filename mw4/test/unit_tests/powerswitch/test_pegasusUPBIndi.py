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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
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
from mw4.powerswitch.pegasusUPB import PegasusUPBIndi
from mw4.powerswitch.pegasusUPB import PegasusUPBSignals
from mw4.base.indiClass import IndiClass


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
    global app
    app = PegasusUPBIndi(app=Test(), signals=PegasusUPBSignals(), data={})

    yield


def test_setUpdateConfig_1():
    app.name = ''
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2():
    app.name = 'test'
    app.device = None
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = app.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_4():
    app.name = 'test'
    app.device = Device()
    app.UPDATE_RATE = 1
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        suc = app.setUpdateConfig('test')
        assert suc


def test_setUpdateConfig_5():
    app.name = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=False):
            suc = app.setUpdateConfig('test')
            assert not suc


def test_setUpdateConfig_6():
    app.name = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.setUpdateConfig('test')
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
                           return_value={'POWER_CONTROL_0': True}):
        suc = app.togglePowerPort(port=1)
        assert not suc


def test_togglePowerPort_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'POWER_CONTROL_1': True}):
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
                           return_value={'POWER_PORT_0': True}):
        suc = app.togglePowerPortBoot(port=1)
        assert not suc


def test_togglePowerPortBoot_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'POWER_PORT_1': True}):
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
                           return_value={'test': True,
                                         'test': True}):
        suc = app.toggleHubUSB()
        assert not suc


def test_toggleHubUSB_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'ENABLED': True,
                                         'DISABLED': True}):
        suc = app.toggleHubUSB()
        assert not suc


def test_togglePortUSB_1():
    suc = app.togglePortUSB()
    assert not suc


def test_togglePortUSB_2():
    suc = app.togglePortUSB(port=1)
    assert not suc


def test_togglePortUSB_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PORT_1': True}):
        suc = app.togglePortUSB(port=1)
        assert not suc


def test_togglePortUSB_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PORT_1': True}):
        suc = app.togglePortUSB(port=0)
        assert not suc


def test_toggleAutoDew_1():
    suc = app.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2():
    suc = app.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'AUTO_DEW_ENABLED': True,
                                         'AUTO_DEW_DISABLED': True}):
        suc = app.toggleAutoDew()
        assert not suc


def test_toggleAutoDew_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'AUTO_DEW_ENABLED': True,
                                         'AUTO_DEW_DISABLED': True}):
        suc = app.toggleAutoDew()
        assert not suc


def test_toggleAutoDewPort_1():
    suc = app.toggleAutoDewPort()
    assert not suc


def test_toggleAutoDewPort_2():
    suc = app.toggleAutoDewPort(port=1)
    assert not suc


def test_toggleAutoDewPort_3():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'DEW_1': True}):
        suc = app.toggleAutoDewPort(port=0)
        assert not suc


def test_toggleAutoDewPort_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'DEW_1': True}):
        suc = app.toggleAutoDewPort(port=1)
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
                           'getSwitch',
                           return_value={'DEW_1': True}):
        suc = app.sendDew(port=1)
        assert not suc


def test_sendDew_4():
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'DEW_1': True}):
        suc = app.sendDew(port=1)
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
        assert not suc
