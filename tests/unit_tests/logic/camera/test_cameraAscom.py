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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
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
from astropy.io import fits
import ctypes

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.camera.cameraAscom import CameraAscom
from logic.camera.camera import Camera
from base.driverDataClass import Signals
from base.ascomClass import AscomClass
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
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

    camera = Camera(App())
    camera.expTime = 1
    camera.binning = 1
    camera.focalLength = 1
    func = CameraAscom(camera)
    func.client = Test1()
    func.clientProps = []
    yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(AscomClass,
                           'getAndStoreAscomProperty',
                           return_value=True):
        with mock.patch.object(function,
                               'getAndStoreAscomProperty'):
            function.workerGetInitialConfig()


def test_workerPollData_1(function):
    function.data['CAN_FAST'] = True
    function.data['CAN_SET_CCD_TEMPERATURE'] = True
    function.data['CAN_GET_COOLER_POWER'] = True
    function.workerPollData()


def test_sendDownloadMode_1(function):
    function.data['CAN_FAST'] = True
    function.sendDownloadMode()
    
    
def test_waitFunc(function):
    with mock.patch.object(AscomClass,
                           'getAscomProperty',
                           return_value=False):
        suc = function.waitFunc()
        assert suc


def test_workerExpose_1(function):
    with mock.patch.object(function.parent,
                           'sendDownloadMode'):
        with mock.patch.object(function,
                               'setAscomProperty'):
            with mock.patch.object(function.parent,
                                   'waitExposed'):
                with mock.patch.object(function.parent,
                                       'retrieveImage'):
                    with mock.patch.object(function.parent,
                                           'writeImageFitsHeader'):
                        with mock.patch.object(fits.HDUList,
                                               'writeto'):
                            function.workerExpose()


def test_expose_1(function):
    with mock.patch.object(function,
                           'callMethodThreaded'):
        function.expose()


def test_abort_3(function):
    function.data['CAN_ABORT'] = True
    with mock.patch.object(function,
                           'callMethodThreaded'):
        suc = function.abort()
        assert suc


def test_sendCoolerSwitch_2(function):
    function.deviceConnected = True
    function.sendCoolerSwitch(coolerOn=True)


def test_sendCoolerTemp_3(function):
    function.data['CAN_SET_CCD_TEMPERATURE'] = True
    function.sendCoolerTemp(temperature=-10)


def test_sendOffset_1(function):
    function.deviceConnected = False
    function.sendOffset()
    

def test_sendGain_1(function):
    function.deviceConnected = False
    function.sendGain()
