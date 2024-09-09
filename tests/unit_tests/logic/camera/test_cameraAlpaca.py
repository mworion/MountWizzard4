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
import astropy
import unittest.mock as mock

# external packages


# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.camera.camera import Camera
from logic.camera.cameraAlpaca import CameraAlpaca
from base.driverDataClass import Signals
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def function():
    camera = Camera(App())
    camera.expTime = 1
    camera.binning = 1
    camera.focalLength = 1
    func = CameraAlpaca(camera)
    yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(function,
                           'getAndStoreAlpacaProperty'):
        function.workerGetInitialConfig()


def test_pollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool,
                           'start'):
        function.pollData()


def test_sendDownloadMode_1(function):
    function.data['CAN_FAST'] = True
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=False):
        function.sendDownloadMode()


def test_workerExpose_1(function):
    with mock.patch.object(function.parent,
                           'sendDownloadMode'):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
            with mock.patch.object(function.parent,
                                   'waitExposed'):
                with mock.patch.object(function.parent,
                                       'retrieveImage'):
                    with mock.patch.object(function.parent,
                                           'writeImageFitsHeader'):
                        suc = function.workerExpose()
                        assert suc


def test_expose_1(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        function.expose()


def test_abort_3(function):
    function.data['CAN_ABORT'] = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=True):
        suc = function.abort()
        assert suc


def test_sendCoolerSwitch_1(function):
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        function.sendCoolerSwitch()


def test_sendCoolerSwitch_2(function):
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        function.sendCoolerSwitch(coolerOn=True)


def test_sendCoolerTemp_1(function):
    function.data['CAN_SET_CCD_TEMPERATURE'] = True
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        function.sendCoolerTemp()


def test_sendOffset_1(function):
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        function.sendOffset()


def test_sendGain_1(function):
    with mock.patch.object(function,
                           'setAlpacaProperty',
                           return_value=True):
        function.sendGain()
