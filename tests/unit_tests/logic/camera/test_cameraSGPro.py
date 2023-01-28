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
import os

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.camera.cameraSGPro import CameraSGPro
from base.driverDataClass import Signals
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    func = CameraSGPro(app=App(), signals=Signals(), data={})
    yield func


def test_sgGetCameraTemp_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc, val = function.sgGetCameraTemp()
        assert not suc
        assert val == {}


def test_sgGetCameraTemp_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = function.sgGetCameraTemp()
        assert suc
        assert val == {'Success': True}


def test_sgSetCameraTemp_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc = function.sgSetCameraTemp(temperature=10)
        assert not suc


def test_sgSetCameraTemp_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = function.sgSetCameraTemp(temperature=10)
        assert suc


def test_sgCaptureImage_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc, val = function.sgCaptureImage(0)
        assert not suc
        assert val == {}


def test_sgCaptureImage_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = function.sgCaptureImage(0)
        assert suc
        assert val == {'Success': True}


def test_sgAbortImage_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc = function.sgAbortImage()
        assert not suc


def test_sgAbortImage_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = function.sgAbortImage()
        assert suc


def test_sgGetImagePath_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc = function.sgGetImagePath(receipt='1')
        assert not suc


def test_sgGetImagePath_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = function.sgGetImagePath(receipt='1')
        assert suc


def test_sgGetCameraProps_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc, val = function.sgGetCameraProps()
        assert not suc
        assert val == {}


def test_sgGetCameraProps_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = function.sgGetCameraProps()
        assert suc
        assert val == {'Success': True}


def test_workerGetInitialConfig_1(function):
    function.deviceName = 'controlled'
    suc = function.workerGetInitialConfig()
    assert not suc


def test_workerGetInitialConfig_2(function):
    function.deviceName = 'test'
    with mock.patch.object(function,
                           'storePropertyToData'):
        with mock.patch.object(function,
                               'sgGetCameraProps',
                               return_value=(False, {})):
            suc = function.workerGetInitialConfig()
            assert not suc


def test_workerGetInitialConfig_3(function):
    function.deviceName = 'test'
    val = {
        'Message': 'test',
        'SupportsSubframe': True,
        'NumPixelsX': 1000,
        'NumPixelsY': 500,
        'GainValues': ['1'],
        'IsoValues': ['1'],
    }
    with mock.patch.object(function,
                           'storePropertyToData'):
        with mock.patch.object(function,
                               'sgGetCameraProps',
                               return_value=(True, val)):
            suc = function.workerGetInitialConfig()
            assert suc


def test_workerPollData_1(function):
    function.deviceName = 'controlled'
    suc = function.workerPollData()
    assert not suc


def test_workerPollData_2(function):
    function.deviceName = 'test'
    function.data['CAN_FAST'] = True
    with mock.patch.object(function,
                           'sgGetCameraTemp',
                           return_value=(False, None)):
        suc = function.workerPollData()
        assert not suc


def test_workerPollData_3(function):
    function.deviceName = 'test'
    function.data['CAN_FAST'] = True
    with mock.patch.object(function,
                           'sgGetCameraTemp',
                           return_value=(True, {'Temperature': 10})):
        suc = function.workerPollData()
        assert suc


def test_sendDownloadMode_1(function):
    suc = function.sendDownloadMode()
    assert suc


def test_workerExpose_1(function):
    with mock.patch.object(function,
                           'sgCaptureImage',
                           return_value=(False, None)):
        suc = function.workerExpose()
        assert not suc


def test_workerExpose_2(function):
    with mock.patch.object(function,
                           'sgCaptureImage',
                           return_value=(True, {})):
        suc = function.workerExpose()
        assert not suc


def test_workerExpose_3(function):
    function.deviceName = 'test'
    function.abortExpose = False
    with mock.patch.object(function,
                           'sgCaptureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(function,
                               'waitStart'):
            with mock.patch.object(function,
                                   'waitExposedApp'):
                with mock.patch.object(function,
                                       'waitDownload'):
                    with mock.patch.object(function,
                                           'waitSave'):
                        with mock.patch.object(function,
                                               'waitFinish'):
                            with mock.patch.object(os.path,
                                                   'splitext',
                                                   return_value=('test', 'test')):
                                with mock.patch.object(os,
                                                       'rename'):
                                    suc = function.workerExpose()
                                    assert suc


def test_workerExpose_4(function):
    function.deviceName = 'test'
    function.data['READOUT_QUALITY.QUALITY_LOW'] = True
    function.abortExpose = True
    with mock.patch.object(function,
                           'sgCaptureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(function,
                               'waitStart'):
            with mock.patch.object(function,
                                   'waitExposedApp'):
                with mock.patch.object(function,
                                       'waitDownload'):
                    with mock.patch.object(function,
                                           'waitSave'):
                        with mock.patch.object(function,
                                               'waitFinish'):
                            suc = function.workerExpose()
                            assert suc


def test_expose_1(function):
    function.deviceConnected = False
    suc = function.expose()
    assert not suc


def test_expose_2(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.expose()
        assert suc


def test_abort_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'sgAbortImage'):
        suc = function.abort()
        assert not suc


def test_abort_2(function):
    function.deviceConnected = True
    function.abortExpose = False
    with mock.patch.object(function,
                           'sgAbortImage'):
        suc = function.abort()
        assert suc
        assert function.abortExpose


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
    with mock.patch.object(function,
                           'sgSetCameraTemp'):
        suc = function.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'sgSetCameraTemp'):
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
