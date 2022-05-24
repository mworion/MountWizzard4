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
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from indibase.indiBase import Device, Client

# local import
from logic.dome.domeIndi import DomeIndi
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        mes = pyqtSignal(object, object, object, object)

        update1s = pyqtSignal()
    global app
    app = DomeIndi(app=Test(), signals=Signals(), data={})

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
                           return_value={'PERIOD_MS': 1}):
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
                           return_value={'PERIOD_MS': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.setUpdateConfig('test')
            assert suc


def test_updateStatus_1():
    app.device = Device()
    app.client = Client()
    app.client.connected = False

    suc = app.updateStatus()
    assert not suc


def test_updateStatus_2():
    app.device = Device()
    app.client = Client()
    app.client.connected = True

    suc = app.updateStatus()
    assert suc


def test_updateNumber_1():
    app.device = None
    suc = app.updateNumber('test', 'test')
    assert not suc


def test_updateNumber_2():
    app.device = Device()
    app.deviceName = 'test'
    setattr(app.device, 'ABS_DOME_POSITION', {'state': 'Busy'})
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'TEST': 1,
                                         'DOME_ABSOLUTE_POSITION': 2}):
        suc = app.updateNumber('test', 'ABS_DOME_POSITION')
        assert suc


def test_updateNumber_3():
    app.device = Device()
    app.deviceName = 'test'
    setattr(app.device, 'DOME_SHUTTER', {'state': 'Busy'})
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'TEST': 1,
                                         'SHUTTER_OPEN': 2}):
        suc = app.updateNumber('test', 'SHUTTER_OPEN')
        assert suc


def test_updateNumber_4():
    app.device = Device()
    app.deviceName = 'test'
    setattr(app.device, 'DOME_SHUTTER', {'state': 'test'})
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'TEST': 1,
                                         'SHUTTER_OPEN': 2}):
        suc = app.updateNumber('test', 'SHUTTER_OPEN')
        assert suc


def test_slewToAltAz_1():
    suc = app.slewToAltAz()
    assert not suc


def test_slewToAltAz_2():
    app.device = Device()
    suc = app.slewToAltAz()
    assert not suc


def test_slewToAltAz_3():
    app.device = Device()
    app.deviceName = 'test'
    suc = app.slewToAltAz()
    assert not suc


def test_slewToAltAz_4():
    app.device = Device()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'DOME_ABSOLUTE_POSITION': 1}):
        suc = app.slewToAltAz()
        assert not suc


def test_slewToAltAz_5():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'DOME_ABSOLUTE_POSITION': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=False):
            suc = app.slewToAltAz()
            assert not suc


def test_slewToAltAz_6():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'DOME_ABSOLUTE_POSITION': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.slewToAltAz()
            assert suc


def test_openShutter_1():
    suc = app.openShutter()
    assert not suc


def test_openShutter_2():
    app.device = Device()
    suc = app.openShutter()
    assert not suc


def test_openShutter_3():
    app.device = Device()
    app.deviceName = 'test'
    suc = app.openShutter()
    assert not suc


def test_openShutter_4():
    app.device = Device()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'SHUTTER_OPEN': 1}):
        suc = app.openShutter()
        assert not suc


def test_openShutter_5():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'SHUTTER_OPEN': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.openShutter()
            assert not suc


def test_openShutter_6():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'SHUTTER_OPEN': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.openShutter()
            assert suc


def test_closeShutter_1():
    suc = app.closeShutter()
    assert not suc


def test_closeShutter_2():
    app.device = Device()
    suc = app.closeShutter()
    assert not suc


def test_closeShutter_3():
    app.device = Device()
    app.deviceName = 'test'
    suc = app.closeShutter()
    assert not suc


def test_closeShutter_4():
    app.device = Device()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'SHUTTER_CLOSE': 1}):
        suc = app.closeShutter()
        assert not suc


def test_closeShutter_5():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'SHUTTER_CLOSE': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.closeShutter()
            assert not suc


def test_closeShutter_6():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'SHUTTER_CLOSE': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.closeShutter()
            assert suc


def test_slewCW_1():
    suc = app.slewCW()
    assert not suc


def test_slewCW_2():
    app.device = Device()
    suc = app.slewCW()
    assert not suc


def test_slewCW_3():
    app.device = Device()
    app.deviceName = 'test'
    suc = app.slewCW()
    assert not suc


def test_slewCW_4():
    app.device = Device()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        suc = app.slewCW()
        assert not suc


def test_slewCW_5():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.slewCW()
            assert not suc


def test_slewCW_6():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.slewCW()
            assert suc


def test_slewCCW_1():
    suc = app.slewCCW()
    assert not suc


def test_slewCCW_2():
    app.device = Device()
    suc = app.slewCCW()
    assert not suc


def test_slewCCW_3():
    app.device = Device()
    app.deviceName = 'test'
    suc = app.slewCCW()
    assert not suc


def test_slewCCW_4():
    app.device = Device()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        suc = app.slewCCW()
        assert not suc


def test_slewCCW_5():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.slewCCW()
            assert not suc


def test_slewCCW_6():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'DOME_CW': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.slewCCW()
            assert suc


def test_abortSlew_1():
    suc = app.abortSlew()
    assert not suc


def test_abortSlew_2():
    app.device = Device()
    suc = app.abortSlew()
    assert not suc


def test_abortSlew_3():
    app.device = Device()
    app.deviceName = 'test'
    suc = app.abortSlew()
    assert not suc


def test_abortSlew_4():
    app.device = Device()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'ABORT': 1}):
        suc = app.abortSlew()
        assert not suc


def test_abortSlew_5():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'ABORT': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.abortSlew()
            assert not suc


def test_abortSlew_6():
    app.device = Device()
    app.client = Client()
    app.deviceName = 'test'

    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'ABORT': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.abortSlew()
            assert suc
