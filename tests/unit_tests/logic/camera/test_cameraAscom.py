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
if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)

# external packages
import ctypes

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.camera.cameraAscom import CameraAscom
from base.driverDataClass import Signals
from base.ascomClass import AscomClass
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        CameraXSize = 1000
        CameraYSize = 500
        CanAbortExposure = True
        CanFastReadout = True
        CanGetCoolerPower = True
        CanSetCCDTemperature = True
        FastReadout = True
        PixelSizeX = 4
        PixelSizeY = 4
        MaxBinX = 3
        MaxBinY = 3
        BinX = 1
        BinY = 1
        StartX = 0
        StartY = 0
        CameraState = 0
        CCDTemperature = 10
        CoolerOn = True
        CoolerPower = 100
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'
        ImageReady = True
        image = [1, 1, 1]
        ImageArray = (ctypes.c_int * len(image))(*image)

        @staticmethod
        def StartExposure(time, light=True):
            return True

        @staticmethod
        def StopExposure(function):
            return True

    func = CameraAscom(app=App(), signals=Signals(), data={})
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


def test_workerPollData_1(function):
    function.data['CAN_FAST'] = True
    function.data['CAN_SET_CCD_TEMPERATURE'] = True
    function.data['CAN_GET_COOLER_POWER'] = True
    suc = function.workerPollData()
    assert suc


def test_sendDownloadMode_1(function):
    function.data['CAN_FAST'] = True
    suc = function.sendDownloadMode()
    assert suc


def test_sendDownloadMode_2(function):
    function.data['CAN_FAST'] = True
    suc = function.sendDownloadMode(fastReadout=True)
    assert suc


def test_sendDownloadMode_3(function):
    function.data['CAN_FAST'] = False
    suc = function.sendDownloadMode()
    assert not suc


def test_workerExpose_1(function):
    with mock.patch.object(function,
                           'sendDownloadMode'):
        with mock.patch.object(function,
                               'setAscomProperty'):
            with mock.patch.object(function,
                                   'waitExposedAscom'):
                with mock.patch.object(function,
                                       'retrieveFits'):
                    with mock.patch.object(function,
                                           'saveFits'):
                        suc = function.workerExpose()
                        assert suc


def test_expose_1(function):
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.expose()
        assert suc


def test_abort_1(function):
    function.deviceConnected = False
    suc = function.abort()
    assert not suc


def test_abort_2(function):
    function.deviceConnected = True
    function.data['CAN_ABORT'] = False
    suc = function.abort()
    assert not suc


def test_abort_3(function):
    function.deviceConnected = True
    function.data['CAN_ABORT'] = True
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.abort()
        assert suc


def test_sendCoolerSwitch_1(function):
    function.deviceConnected = False
    suc = function.sendCoolerSwitch()
    assert not suc


def test_sendCoolerSwitch_2(function):
    function.deviceConnected = True
    suc = function.sendCoolerSwitch(coolerOn=True)
    assert suc


def test_sendCoolerTemp_1(function):
    function.deviceConnected = False
    suc = function.sendCoolerTemp()
    assert not suc


def test_sendCoolerTemp_2(function):
    function.deviceConnected = True
    function.data['CAN_SET_CCD_TEMPERATURE'] = False
    suc = function.sendCoolerTemp(temperature=-10)
    assert not suc


def test_sendCoolerTemp_3(function):
    function.deviceConnected = True
    function.data['CAN_SET_CCD_TEMPERATURE'] = True
    suc = function.sendCoolerTemp(temperature=-10)
    assert suc


def test_sendOffset_1(function):
    function.deviceConnected = False
    suc = function.sendOffset()
    assert not suc


def test_sendOffset_2(function):
    function.deviceConnected = True
    suc = function.sendOffset(offset=50)
    assert suc


def test_sendGain_1(function):
    function.deviceConnected = False
    suc = function.sendGain()
    assert not suc


def test_sendGain_2(function):
    function.deviceConnected = True
    suc = function.sendGain(gain=50)
    assert suc
