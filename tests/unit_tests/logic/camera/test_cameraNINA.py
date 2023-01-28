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
from logic.camera.cameraNINA import CameraNINA
from base.driverDataClass import Signals
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    func = CameraNINA(app=App(), signals=Signals(), data={})
    yield func


def test_getCameraTemp_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc, val = function.getCameraTemp()
        assert not suc
        assert val == {}


def test_getCameraTemp_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = function.getCameraTemp()
        assert suc
        assert val == {'Success': True}


def test_setCameraTemp_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc = function.setCameraTemp(temperature=10)
        assert not suc


def test_setCameraTemp_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = function.setCameraTemp(temperature=10)
        assert suc


def test_captureImage_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc, val = function.captureImage(0)
        assert not suc
        assert val == {}


def test_captureImage_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = function.captureImage(0)
        assert suc
        assert val == {'Success': True}


def test_abortImage_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc = function.abortImage()
        assert not suc


def test_abortImage_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = function.abortImage()
        assert suc


def test_getImagePath_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc = function.getImagePath(receipt='1')
        assert not suc


def test_getImagePath_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = function.getImagePath(receipt='1')
        assert suc


def test_getCameraProps_1(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value=None):
        suc, val = function.getCameraProps()
        assert not suc
        assert val == {}


def test_getCameraProps_2(function):
    with mock.patch.object(function,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = function.getCameraProps()
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
                               'getCameraProps',
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
                               'getCameraProps',
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
                           'getCameraTemp',
                           return_value=(False, None)):
        suc = function.workerPollData()
        assert not suc


def test_workerPollData_3(function):
    function.deviceName = 'test'
    function.data['CAN_FAST'] = True
    with mock.patch.object(function,
                           'getCameraTemp',
                           return_value=(True, {'Temperature': 10})):
        suc = function.workerPollData()
        assert suc


def test_sendDownloadMode_1(function):
    suc = function.sendDownloadMode()
    assert suc


def test_workerExpose_1(function):
    with mock.patch.object(function,
                           'captureImage',
                           return_value=(False, None)):
        suc = function.workerExpose()
        assert not suc


def test_workerExpose_2(function):
    function.deviceName = 'test'
    with mock.patch.object(function,
                           'captureImage',
                           return_value=(True, {})):
        suc = function.workerExpose()
        assert not suc


def test_workerExpose_3(function):
    function.deviceName = 'test'
    function.abortExpose = False
    with mock.patch.object(function,
                           'captureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(function,
                               'waitStart'):
            with mock.patch.object(function,
                                   'waitExposedApp'):
                with mock.patch.object(function,
                                       'waitDownload'):
                    with mock.patch.object(function,
                                           'waitSave'):
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
                           'captureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(function,
                               'waitStart'):
            with mock.patch.object(function,
                                   'waitExposedApp'):
                with mock.patch.object(function,
                                       'waitDownload'):
                    with mock.patch.object(function,
                                           'waitSave'):
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
                           'abortImage'):
        suc = function.abort()
        assert not suc


def test_abort_2(function):
    function.deviceConnected = True
    function.abortExpose = False
    with mock.patch.object(function,
                           'abortImage'):
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
                           'setCameraTemp'):
        suc = function.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'setCameraTemp'):
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
