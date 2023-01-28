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
import platform

# external packages
import PyQt5
from PyQt5.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.dome.domeAscom import DomeAscom
from base.driverDataClass import Signals
from base.ascomClass import AscomClass

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        Azimuth = 100
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'
        ShutterStatus = 4
        Slewing = True
        CanSetAltitude = True
        CanSetAzimuth = True
        CanSetShutter = True
        AbortSlew = False
        OpenShutter = None
        CloseShutter = None
        AbortSlew = None

        @staticmethod
        def SlewToAzimuth(azimuth):
            return True

        @staticmethod
        def SlewToAltitude(altitude):
            return True
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        func = DomeAscom(app=App(), signals=Signals(), data={})
        func.client = Test1()
        func.clientProps = []
        yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(AscomClass,
                           'getAndStoreAscomProperty',
                           return_value=True):
        with mock.patch.object(function,
                               'getAndStoreAscomProperty'):
            suc = function.workerGetInitialConfig()
            assert suc


def test_processPolledData_1(function):
    suc = function.processPolledData()
    assert suc


def test_workerPollData_1(function):
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=0):
        with mock.patch.object(function,
                               'storePropertyToData'):
            with mock.patch.object(function,
                                   'getAndStoreAscomProperty'):
                suc = function.workerPollData()
                assert suc


def test_workerPollData_2(function):
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=1):
        with mock.patch.object(function,
                               'storePropertyToData'):
            with mock.patch.object(function,
                                   'getAndStoreAscomProperty'):
                suc = function.workerPollData()
                assert suc


def test_workerPollData_3(function):
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=2):
        with mock.patch.object(function,
                               'storePropertyToData'):
            with mock.patch.object(function,
                                   'getAndStoreAscomProperty'):
                suc = function.workerPollData()
                assert suc


def test_slewToAltAz_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.slewToAltAz()
        assert not suc


def test_slewToAltAz_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.slewToAltAz()
        assert suc


def test_openShutter_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.openShutter()
        assert not suc


def test_openShutter_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.openShutter()
        assert suc


def test_closeShutter_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.closeShutter()
        assert not suc


def test_closeShutter_2(function):
    function.data['CanSetShutter'] = True
    function.deviceConnected = True
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.closeShutter()
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
                           'callMethodThreaded'):
        suc = function.abortSlew()
        assert not suc


def test_abortSlew_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.abortSlew()
        assert suc
