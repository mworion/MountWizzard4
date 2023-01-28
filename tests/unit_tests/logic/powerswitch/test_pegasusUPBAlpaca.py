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

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.powerswitch.pegasusUPBAlpaca import PegasusUPBAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def function():
    func = PegasusUPBAlpaca(app=App(), signals=Signals(), data={})
    yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.workerPollData()
        assert not suc


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=15):
        with mock.patch.object(function,
                               'storePropertyToData'):
            suc = function.workerPollData()
            assert suc


def test_workerPollData_3(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=21):
        with mock.patch.object(function,
                               'storePropertyToData'):
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
                           'setAlpacaProperty'):
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
                           'getAlpacaProperty',
                           return_value=21):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
            suc = function.togglePortUSB('1')
            assert suc


def test_toggleAutoDew_1(function):
    function.deviceConnected = False
    suc = function.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=21):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
            suc = function.toggleAutoDew()
            assert suc


def test_toggleAutoDew_3(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=15):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
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
                           'getAlpacaProperty',
                           return_value=21):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
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