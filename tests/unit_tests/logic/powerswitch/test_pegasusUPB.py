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
from unittest import mock

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.powerswitch.pegasusUPB import PegasusUPB


@pytest.fixture(autouse=True, scope='function')
def function():
    func = PegasusUPB(app=App())
    yield func


def test_properties(function):
    function.framework = 'indi'
    function.host = ('localhost', 7624)
    assert function.host == ('localhost', 7624)

    function.deviceName = 'test'
    assert function.deviceName == 'test'


def test_properties_2(function):
    function.updateRate = 1000
    function.loadConfig = True
    function.framework = 'indi'
    assert function.updateRate == 1000
    assert function.loadConfig


def test_startCommunication_1(function):
    function.framework = ''
    suc = function.startCommunication()
    assert not suc


def test_startCommunication_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'startCommunication',
                           return_value=True):
        suc = function.startCommunication()
        assert suc


def test_stopCommunication_1(function):
    function.framework = ''
    suc = function.stopCommunication()
    assert not suc


def test_stopCommunication_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'stopCommunication',
                           return_value=True):
        suc = function.stopCommunication()
        assert suc


def test_togglePowerPort_1(function):
    function.framework = ''
    suc = function.togglePowerPort()
    assert not suc


def test_togglePowerPort_2(function):
    function.framework = 'indi'
    suc = function.togglePowerPort()
    assert not suc


def test_togglePowerPortBoot_1(function):
    function.framework = ''
    suc = function.togglePowerPortBoot()
    assert not suc


def test_togglePowerPortBoot_2(function):
    function.framework = 'indi'
    suc = function.togglePowerPortBoot()
    assert not suc


def test_toggleHubUSB_1(function):
    function.framework = ''
    suc = function.toggleHubUSB()
    assert not suc


def test_toggleHubUSB_2(function):
    function.framework = 'indi'
    suc = function.toggleHubUSB()
    assert not suc


def test_togglePortUSB_1(function):
    function.framework = ''
    suc = function.togglePortUSB()
    assert not suc


def test_togglePortUSB_2(function):
    function.framework = 'indi'
    suc = function.togglePortUSB()
    assert not suc


def test_toggleAutoDew_1(function):
    function.framework = ''
    suc = function.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2(function):
    function.framework = 'indi'
    suc = function.toggleAutoDew()
    assert not suc


def test_sendDew_1(function):
    function.framework = ''
    suc = function.sendDew()
    assert not suc


def test_sendDew_2(function):
    function.framework = 'indi'
    suc = function.sendDew()
    assert not suc


def test_sendAdjustableOutput_1(function):
    function.framework = ''
    suc = function.sendAdjustableOutput()
    assert not suc


def test_sendAdjustableOutput_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendAdjustableOutput',
                           return_value=False):
        suc = function.sendAdjustableOutput()
        assert not suc


def test_sendAdjustableOutput_3(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendAdjustableOutput',
                           return_value=True):
        suc = function.sendAdjustableOutput()
        assert suc


def test_reboot_1(function):
    function.framework = ''
    suc = function.reboot()
    assert not suc


def test_reboot_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'reboot',
                           return_value=False):
        suc = function.reboot()
        assert not suc


def test_reboot_3(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'reboot',
                           return_value=True):
        suc = function.reboot()
        assert suc
