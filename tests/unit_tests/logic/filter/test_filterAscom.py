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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import platform

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.filter.filterAscom import FilterAscom
from logic.filter.filter import FilterSignals
from base.ascomClass import AscomClass

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        Names = []
        Position = 1
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = FilterAscom(app=Test(), signals=FilterSignals(), data={})
    app.client = Test1()

    yield


def test_getInitialConfig_0():
    app.deviceConnected = False
    with mock.patch.object(AscomClass,
                           'getInitialConfig',
                           return_value=True):
        suc = app.getInitialConfig()
        assert not suc


def test_getInitialConfig_1():
    app.deviceConnected = True
    with mock.patch.object(AscomClass,
                           'getInitialConfig',
                           return_value=True):
        suc = app.getInitialConfig()
        assert suc


def test_getInitialConfig_2():
    app.deviceConnected = True
    app.client.Names = None
    suc = app.getInitialConfig()
    assert not suc


def test_getInitialConfig_3():
    app.deviceConnected = True
    app.client.Names = ['test', 'test1']
    suc = app.getInitialConfig()
    assert suc
    assert app.data['FILTER_NAME.FILTER_SLOT_NAME_0'] == 'test'
    assert app.data['FILTER_NAME.FILTER_SLOT_NAME_1'] == 'test1'


def test_getInitialConfig_4():
    app.deviceConnected = True
    app.client.Names = ['test', None]
    suc = app.getInitialConfig()
    assert suc
    assert app.data['FILTER_NAME.FILTER_SLOT_NAME_0'] == 'test'


def test_workerPollData_0():
    app.deviceConnected = False
    app.client.Position = -1
    suc = app.workerPollData()
    assert not suc


def test_workerPollData_1():
    app.deviceConnected = True
    app.client.Position = -1
    suc = app.workerPollData()
    assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    app.client.Position = 1
    suc = app.workerPollData()
    assert suc
    assert app.data['FILTER_SLOT.FILTER_SLOT_VALUE'] == 1


def test_sendFilterNumber_1():
    app.deviceConnected = True
    suc = app.sendFilterNumber(3)
    assert suc
    assert app.client.Position == 3


def test_sendFilterNumber_2():
    app.deviceConnected = False
    suc = app.sendFilterNumber(3)
    assert not suc
