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
from logic.camera.cameraAlpaca import CameraAlpaca
from base.driverDataClass import Signals
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    func = CameraAlpaca(app=App(), signals=Signals(), data={})
    yield func


def test_workerGetInitialConfig_1(function):
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


def test_pollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.pollData()
        assert not suc


def test_pollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.pollData()
        assert suc


def test_sendDownloadMode_1(function):
    function.data['CAN_FAST'] = True
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=False):
        suc = function.sendDownloadMode()
        assert suc


def test_sendDownloadMode_2(function):
    function.data['CAN_FAST'] = True
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendDownloadMode(fastReadout=True)
        assert suc


def test_sendDownloadMode_3(function):
    function.data['CAN_FAST'] = False
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendDownloadMode()
        assert not suc


def test_workerExpose_1(function):
    with mock.patch.object(function,
                           'sendDownloadMode'):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
            with mock.patch.object(function,
                                   'waitExposedAlpaca'):
                with mock.patch.object(function,
                                       'retrieveFits'):
                    with mock.patch.object(function,
                                           'saveFits'):
                        suc = function.workerExpose()
                        assert suc


def test_expose_1(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.expose()
        assert suc


def test_expose_2(function):
    function.deviceConnected = True
    function.data['CCD_BINNING.HOR_BIN_MAX'] = 3
    function.data['CCD_BINNING.VERT_BIN_MAX'] = 3

    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.expose()
        assert suc


def test_expose_3(function):
    function.deviceConnected = True
    function.data['CCD_BINNING.HOR_BIN_MAX'] = 3
    function.data['CCD_BINNING.VERT_BIN_MAX'] = 3

    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.expose(expTime=1,
                         binning=4)
        assert suc


def test_abort_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=True):
        suc = function.abort()
        assert not suc


def test_abort_2(function):
    function.deviceConnected = True
    function.data['CAN_ABORT'] = False
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=True):
        suc = function.abort()
        assert not suc


def test_abort_3(function):
    function.deviceConnected = True
    function.data['CAN_ABORT'] = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=True):
        suc = function.abort()
        assert suc


def test_sendCoolerSwitch_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendCoolerSwitch()
        assert not suc


def test_sendCoolerSwitch_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendCoolerSwitch(coolerOn=True)
        assert suc


def test_sendCoolerTemp_1(function):
    function.deviceConnected = False
    function.data['CAN_SET_CCD_TEMPERATURE'] = True
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_2(function):
    function.deviceConnected = True
    function.data['CAN_SET_CCD_TEMPERATURE'] = False
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendCoolerTemp(temperature=-10)
        assert not suc


def test_sendCoolerTemp_3(function):
    function.deviceConnected = True
    function.data['CAN_SET_CCD_TEMPERATURE'] = True
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendCoolerTemp(temperature=-10)
        assert suc


def test_sendOffset_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendOffset()
        assert not suc


def test_sendOffset_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendOffset(offset=50)
        assert suc


def test_sendGain_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendGain()
        assert not suc


def test_sendGain_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        suc = function.sendGain(gain=50)
        assert suc
