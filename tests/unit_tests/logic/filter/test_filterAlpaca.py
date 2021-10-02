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
# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.filter.filterAlpaca import FilterAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = FilterAlpaca(app=Test(), signals=Signals(), data={})

    yield


def test_workerGetInitialConfig_1():
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.workerGetInitialConfig()
        assert suc


def test_workerGetInitialConfig_2():
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=None):
        suc = app.workerGetInitialConfig()
        assert not suc


def test_workerGetInitialConfig_3():
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=['test', 'test1']):
        suc = app.workerGetInitialConfig()
        assert suc
        assert app.data['FILTER_NAME.FILTER_SLOT_NAME_0'] == 'test'
        assert app.data['FILTER_NAME.FILTER_SLOT_NAME_1'] == 'test1'


def test_workerGetInitialConfig_4():
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=['test', None]):
        suc = app.workerGetInitialConfig()
        assert suc
        assert app.data['FILTER_NAME.FILTER_SLOT_NAME_0'] == 'test'


def test_workerPollData_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=-1):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=-1):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=1):
        suc = app.workerPollData()
        assert suc
        assert app.data['FILTER_SLOT.FILTER_SLOT_VALUE'] == 1


def test_sendFilterNumber_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'setAlpacaProperty'):
        suc = app.sendFilterNumber()
        assert not suc


def test_sendFilterNumber_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'setAlpacaProperty'):
        suc = app.sendFilterNumber()
        assert suc
