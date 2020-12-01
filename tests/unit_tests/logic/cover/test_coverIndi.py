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
# written in python3 , (c) 2019, 2020 by mworion
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
from logic.cover.coverIndi import CoverIndi
from logic.cover.cover import CoverSignals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
    global app
    app = CoverIndi(app=Test(), signals=CoverSignals(), data={})

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
    app.UPDATE_RATE = 1
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD': 1}):
        suc = app.setUpdateConfig('test')
        assert suc


def test_setUpdateConfig_5():
    app.deviceName = 'test'
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
    app.deviceName = 'test'
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


def test_sendCoverPark_1():
    app.deviceName = 'test'
    app.device = None
    suc = app.sendCoverPark()
    assert not suc


def test_sendCoverPark_2():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = app.sendCoverPark()
        assert not suc


def test_sendCoverPark_3():
    app.deviceName = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PARK': 'On',
                                         'UNPARK': 'Off'}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.sendCoverPark()
            assert not suc


def test_sendCoverPark_4():
    app.deviceName = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PARK': 'On',
                                         '': 'Off'}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.sendCoverPark()
            assert not suc


def test_sendCoverPark_5():
    app.deviceName = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PARK': 'Off',
                                         'UNPARK': 'On'}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.sendCoverPark(park=False)
            assert suc
