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
import os

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.camera.camera import Camera
from logic.camera.cameraSGPro import CameraSGPro
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    camera = Camera(App())
    camera.expTime = 1
    camera.binning = 1
    camera.focalLength = 1
    func = CameraSGPro(camera)
    yield func


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function):
    def test(a):
        pass

    monkeypatch.setattr('logic.camera.cameraSGPro.sleepAndEvents', test)


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
    function.workerGetInitialConfig()
    assert function.data['CCD_BINNING.HOR_BIN'] == 1


def test_workerPollData_1(function):
    function.workerPollData()


def test_sendDownloadMode_1(function):
    function.sendDownloadMode()
    
    
def test_waitFunc(function):
    function.data['Device.Message'] = 'integrating'
    suc = function.waitFunc() 
    assert suc


def test_workerExpose_1(function):
    with mock.patch.object(function,
                           'sgCaptureImage',
                           return_value=(False, None)):
        function.workerExpose()


def test_workerExpose_2(function):
    with mock.patch.object(function,
                           'sgCaptureImage',
                           return_value=(True, {})):
        function.workerExpose()


def test_workerExpose_3(function, mocked_sleepAndEvents):
    function.deviceName = 'test'
    function.parent.exposing = True
    with mock.patch.object(function,
                           'sgCaptureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(function.parent,
                               'waitStart'):
            with mock.patch.object(function.parent,
                                   'waitExposed'):
                with mock.patch.object(function.parent,
                                       'waitDownload'):
                    with mock.patch.object(function.parent,
                                           'waitSave'):
                        with mock.patch.object(function.parent,
                                               'waitFinish'):
                            with mock.patch.object(os,
                                                   'rename'):
                                with mock.patch.object(function.parent,
                                                       'updateImageFitsHeaderPointing'):
                                    function.workerExpose()


def test_workerExpose_4(function, mocked_sleepAndEvents):
    function.deviceName = 'test'
    function.parent.exposing = False
    with mock.patch.object(function,
                           'sgCaptureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(function.parent,
                               'waitStart'):
            with mock.patch.object(function.parent,
                                   'waitExposed'):
                with mock.patch.object(function.parent,
                                       'waitDownload'):
                    with mock.patch.object(function.parent,
                                           'waitSave'):
                        with mock.patch.object(function.parent,
                                               'waitFinish'):
                            function.workerExpose()


def test_expose_1(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool,
                           'start'):
        function.expose()


def test_abort_1(function):
    with mock.patch.object(function,
                           'sgAbortImage'):
        function.abort()


def test_sendCoolerSwitch_1(function):
    function.sendCoolerSwitch(coolerOn=True)


def test_sendCoolerTemp_1(function):
    function.sendCoolerTemp(temperature=-10)


def test_sendOffset_1(function):
    function.sendOffset()


def test_sendGain_2(function):
    function.sendGain(gain=50)
