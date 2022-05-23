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
import platform

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.filter.filterAscom import FilterAscom
from base.driverDataClass import Signals
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
        messageN = pyqtSignal(object, object, object, object)

    global app
    app = FilterAscom(app=Test(), signals=Signals(), data={})
    app.clientProps = []
    app.client = Test1()
    yield


def test_workerGetInitialConfig_1():
    with mock.patch.object(AscomClass,
                           'workerGetInitialConfig',
                           return_value=True):
        with mock.patch.object(app,
                               'getAscomProperty',
                               return_value=None):
            suc = app.workerGetInitialConfig()
            assert not suc


def test_workerGetInitialConfig_2():
    with mock.patch.object(AscomClass,
                           'workerGetInitialConfig',
                           return_value=True):
        with mock.patch.object(app,
                               'getAscomProperty',
                               return_value=['test']):
            with mock.patch.object(app,
                                   'storePropertyToData'):
                suc = app.workerGetInitialConfig()
                assert suc


def test_workerPollData_1():
    app.client.Position = -1
    suc = app.workerPollData()
    assert not suc


def test_workerPollData_2():
    app.client.Position = 1
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=-1):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_3():
    app.client.Position = 1
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=1):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollData()
            assert suc


def test_sendFilterNumber_1():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'setAscomProperty'):
        suc = app.sendFilterNumber(3)
        assert suc


def test_sendFilterNumber_2():
    app.deviceConnected = False
    suc = app.sendFilterNumber(3)
    assert not suc
