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
import platform
import unittest.mock as mock

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.powerswitch.pegasusUPBAscom import PegasusUPBAscom
from base.driverDataClass import Signals

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

        @staticmethod
        def getswitch(a):
            return False

        @staticmethod
        def getswitchvalue(a):
            return 0

    func = PegasusUPBAscom(app=App(), signals=Signals(), data={})
    func.clientProps = []
    func.client = Test1()
    yield func


def test_workerPollData_1(function):
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=15):
        suc = function.workerPollData()
        assert suc


def test_workerPollData_2(function):
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=21):
        suc = function.workerPollData()
        assert suc


def test_togglePowerPort_1(function):
    function.deviceConnected = False
    suc = function.togglePowerPort()
    assert not suc


def test_togglePowerPort_2(function):
    function.deviceConnected = True
    suc = function.togglePowerPort()
    assert not suc


def test_togglePowerPort_3(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'callAscomMethod'):
        suc = function.togglePowerPort('1')
        assert suc


def test_togglePowerPortBoot_1(function):
    function.deviceConnected = False
    suc = function.togglePowerPortBoot()
    assert not suc


def test_togglePowerPortBoot_2(function):
    function.deviceConnected = True
    suc = function.togglePowerPortBoot()
    assert suc


def test_toggleHubUSB_1(function):
    function.deviceConnected = False
    suc = function.toggleHubUSB()
    assert not suc


def test_toggleHubUSB_2(function):
    function.deviceConnected = True
    suc = function.toggleHubUSB()
    assert suc


def test_togglePortUSB_1(function):
    function.deviceConnected = False
    suc = function.togglePortUSB()
    assert not suc


def test_togglePortUSB_2(function):
    function.deviceConnected = True
    suc = function.togglePortUSB()
    assert not suc


def test_togglePortUSB_3(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=21):
        with mock.patch.object(function,
                               'callAscomMethod'):
            suc = function.togglePortUSB('1')
            assert suc


def test_toggleAutoDew_1(function):
    function.deviceConnected = False
    suc = function.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=21):
        with mock.patch.object(function,
                               'callAscomMethod'):
            suc = function.toggleAutoDew()
            assert suc


def test_toggleAutoDew_3(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=15):
        with mock.patch.object(function,
                               'callAscomMethod'):
            suc = function.toggleAutoDew()
            assert suc


def test_sendDew_1(function):
    function.deviceConnected = False
    suc = function.sendDew()
    assert not suc


def test_sendDew_2(function):
    function.deviceConnected = True
    suc = function.sendDew()
    assert not suc


def test_sendDew_3(function):
    function.deviceConnected = True
    suc = function.sendDew('1')
    assert not suc


def test_sendDew_4(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=21):
        with mock.patch.object(function,
                               'callAscomMethod'):
            suc = function.sendDew('1', 10)
            assert suc


def test_sendAdjustableOutput_1(function):
    function.deviceConnected = False
    suc = function.sendAdjustableOutput()
    assert not suc


def test_sendAdjustableOutput_2(function):
    function.deviceConnected = True
    suc = function.sendAdjustableOutput(4)
    assert suc


def test_reboot_1(function):
    function.deviceConnected = False
    suc = function.reboot()
    assert not suc


def test_reboot_2(function):
    function.deviceConnected = True
    suc = function.reboot()
    assert suc
