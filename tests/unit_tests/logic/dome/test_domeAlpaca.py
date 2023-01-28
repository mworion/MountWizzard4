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
import PyQt5
from PyQt5.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.dome.domeAlpaca import DomeAlpaca
from base.driverDataClass import Signals
from base.alpacaClass import AlpacaClass


@pytest.fixture(autouse=True, scope='function')
def function():
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        func = DomeAlpaca(app=App(), signals=Signals(), data={})
        yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(AlpacaClass,
                           'getAndStoreAlpacaProperty',
                           return_value=True):
        with mock.patch.object(function,
                               'getAndStoreAlpacaProperty'):
            suc = function.workerGetInitialConfig()
            assert suc


def test_workerPollData_1(function):
    function.data['CAN_FAST'] = True
    with mock.patch.object(function,
                           'getAndStoreAlpacaProperty'):
        suc = function.workerPollData()
        assert suc


def test_processPolledData_1(function):
    suc = function.processPolledData()
    assert suc


def test_workerPollData_1(function):
    function.deviceConnected = False
    suc = function.workerPollData()
    assert not suc


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=0):
        with mock.patch.object(function,
                               'getAndStoreAlpacaProperty'):
            suc = function.workerPollData()
            assert suc


def test_workerPollData_3(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=1):
        with mock.patch.object(function,
                               'getAndStoreAlpacaProperty'):
            suc = function.workerPollData()
            assert suc


def test_workerPollData_4(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=3):
        with mock.patch.object(function,
                               'getAndStoreAlpacaProperty'):
            suc = function.workerPollData()
            assert suc


def test_slewToAltAz_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'setAlpacaProperty'):
        suc = function.slewToAltAz()
        assert not suc


def test_slewToAltAz_2(function):
    function.deviceConnected = True
    function.data['CanSetAzimuth'] = True
    function.data['CanSetAltitude'] = True
    with mock.patch.object(function,
                           'setAlpacaProperty'):
        suc = function.slewToAltAz()
        assert suc


def test_closeShutter_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.closeShutter()
        assert not suc


def test_closeShutter_2(function):
    function.deviceConnected = True
    function.data['CanSetShutter'] = True
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.closeShutter()
        assert suc


def test_openShutter_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.openShutter()
        assert not suc


def test_openShutter_2(function):
    function.deviceConnected = True
    function.data['CanSetShutter'] = True
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.openShutter()
        assert suc


def test_slewCW_1(function):
    function.deviceConnected = False
    suc = function.slewCW()
    assert not suc


def test_slewCW_2(function):
    function.deviceConnected = True
    suc = function.slewCW()
    assert suc


def test_slewCCW_1(function):
    function.deviceConnected = False
    suc = function.slewCCW()
    assert not suc


def test_slewCCW_2(function):
    function.deviceConnected = True
    suc = function.slewCCW()
    assert suc


def test_abortSlew_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.abortSlew()
        assert not suc


def test_abortSlew_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.abortSlew()
        assert suc
