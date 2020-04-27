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
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from indibase.indiBase import Device, Client

# local import
from mw4.cover.flipflatIndi import FlipFlatIndi
from mw4.cover.flipflat import FlipFlatSignals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
    global app
    app = FlipFlatIndi(app=Test(), signals=FlipFlatSignals(), data={})

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


def test_sendCoverPark_1():
    app.name = 'test'
    app.device = None
    suc = app.sendCoverPark()
    assert not suc


def test_sendCoverPark_2():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = app.sendCoverPark()
        assert not suc


def test_sendCoverPark_3():
    app.name = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PARK': True,
                                         'UNPARK': False}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.sendCoverPark()
            assert not suc


def test_sendCoverPark_4():
    app.name = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PARK': True,
                                         '': False}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=False):
            suc = app.sendCoverPark()
            assert not suc


def test_sendCoverPark_5():
    app.name = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'PARK': True,
                                         'UNPARK': False}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.sendCoverPark()
            assert suc
