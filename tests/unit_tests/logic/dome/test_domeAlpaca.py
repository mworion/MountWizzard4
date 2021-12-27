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
import PyQt5
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.dome.domeAlpaca import DomeAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = DomeAlpaca(app=Test(), signals=Signals(), data={})
        yield


def test_workerPollData_1():
    app.data['CAN_FAST'] = True
    with mock.patch.object(app,
                           'getAndStoreAlpacaProperty'):
        suc = app.workerPollData()
        assert suc


def test_processPolledData_1():
    suc = app.processPolledData()
    assert suc


def test_workerPollData_1():
    app.deviceConnected = False
    suc = app.workerPollData()
    assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=0):
        with mock.patch.object(app,
                               'getAndStoreAlpacaProperty'):
            suc = app.workerPollData()
            assert suc


def test_workerPollData_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=1):
        with mock.patch.object(app,
                               'getAndStoreAlpacaProperty'):
            suc = app.workerPollData()
            assert suc


def test_workerPollData_4():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=3):
        with mock.patch.object(app,
                               'getAndStoreAlpacaProperty'):
            suc = app.workerPollData()
            assert suc


def test_slewToAltAz_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'setAlpacaProperty'):
        suc = app.slewToAltAz()
        assert not suc


def test_slewToAltAz_2():
    app.deviceConnected = True
    app.data['CanSetAzimuth'] = True
    app.data['CanSetAltitude'] = True
    with mock.patch.object(app,
                           'setAlpacaProperty'):
        suc = app.slewToAltAz()
        assert suc


def test_closeShutter_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.closeShutter()
        assert not suc


def test_closeShutter_2():
    app.deviceConnected = True
    app.data['CanSetShutter'] = True
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.closeShutter()
        assert suc


def test_openShutter_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.openShutter()
        assert not suc


def test_openShutter_2():
    app.deviceConnected = True
    app.data['CanSetShutter'] = True
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.openShutter()
        assert suc


def test_abortSlew_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.abortSlew()
        assert not suc


def test_abortSlew_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.abortSlew()
        assert suc
