############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import unittest.mock as mock

import pytest
from mw4.base.signalsDevices import Signals
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraNINA import CameraNINA

# external packages
# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000
    binning = 1
    exposureTime = 1
    imagePath = "tests/work/image/test.fit"
    width = 100
    height = 100
    subframe = 100
    posX = 0
    posY = 0
    threadPool = mock.Mock()
    exposeFinished = mock.Mock()
    waitStart = mock.Mock()
    waitExposed = mock.Mock()
    waitDownload = mock.Mock()
    waitSave = mock.Mock()
    updateImageFitsHeaderPointing = mock.Mock()


@pytest.fixture(autouse=True, scope="module")
def function():
    camera = Camera(App())
    camera.exposureTime = 1
    camera.binning = 1
    camera.focalLength = 1
    func = CameraNINA(parent=Parent())
    yield func


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function):
    def test(a):
        pass

    monkeypatch.setattr("mw4.logic.camera.cameraNINA.sleepAndEvents", test)


def test_getCameraTemp_1(function):
    with mock.patch.object(function, "requestProperty", return_value=None):
        suc, val = function.getCameraTemp()
        assert not suc
        assert val == {}


def test_getCameraTemp_2(function):
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
        suc, val = function.getCameraTemp()
        assert suc
        assert val == {"Success": True}


def test_setCameraTemp_1(function):
    with mock.patch.object(function, "requestProperty", return_value={}):
        function.setCameraTemp(temperature=10)


def test_setCameraTemp_2(function):
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
        function.setCameraTemp(temperature=10)


def test_captureImage_1(function):
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc, val = function.captureImage(0)
        assert not suc
        assert val == {}


def test_captureImage_2(function):
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
        suc, val = function.captureImage(0)
        assert suc
        assert val == {"Success": True}


def test_abortImage_1(function):
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.abortImage()
        assert not suc


def test_abortImage_2(function):
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
        suc = function.abortImage()
        assert suc


def test_getImagePath_1(function):
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.getImagePath(receipt="1")
        assert not suc


def test_getImagePath_2(function):
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
        suc = function.getImagePath(receipt="1")
        assert suc


def test_getCameraProps_1(function):
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc, val = function.getCameraProps()
        assert not suc
        assert val == {}


def test_getCameraProps_2(function):
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
        suc, val = function.getCameraProps()
        assert suc
        assert val == {"Success": True}


def test_workerGetInitialConfig_1(function):
    function.workerGetInitialConfig()
    assert function.data["CCD_BINNING.HOR_BIN"] == 1


def test_workerPollData_1(function):
    function.workerPollData()


def test_sendDownloadMode_1(function):
    function.sendDownloadMode()


def test_waitFunc(function):
    function.data["Device.Message"] = "integrating"
    suc = function.waitFunc()
    assert suc


def test_workerExpose_1(function):
    function.deviceName = "test"
    with mock.patch.object(function, "captureImage", return_value=(False, {})):
        function.workerExpose()


def test_workerExpose_2(function):
    function.deviceName = "test"
    with mock.patch.object(function, "captureImage", return_value=(True, {})):
        function.workerExpose()


def test_workerExpose_3(function, mocked_sleepAndEvents):
    function.deviceName = "test"
    function.parent.exposing = True
    with mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "123"})):
        with mock.patch.object(function.parent, "waitStart"):
            with mock.patch.object(function.parent, "waitExposed"):
                with mock.patch.object(function.parent, "waitDownload"):
                    with mock.patch.object(function.parent, "waitSave"):
                        with mock.patch.object(os, "rename"):
                            with mock.patch.object(
                                function.parent, "updateImageFitsHeaderPointing"
                            ):
                                function.workerExpose()


def test_workerExpose_4(function, mocked_sleepAndEvents):
    function.deviceName = "test"
    function.parent.exposing = False
    with mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "123"})):
        with mock.patch.object(function.parent, "waitStart"):
            with mock.patch.object(function.parent, "waitExposed"):
                with mock.patch.object(function.parent, "waitDownload"):
                    with mock.patch.object(function.parent, "waitSave"):
                        function.workerExpose()


def test_expose_1(function):
    with mock.patch.object(function.threadPool, "start"):
        function.expose()


def test_abort_1(function):
    with mock.patch.object(function, "abortImage", return_value=True):
        suc = function.abort()
        assert suc


def test_sendCoolerSwitch_1(function):
    function.sendCoolerSwitch(coolerOn=True)


def test_sendCoolerTemp_1(function):
    function.sendCoolerTemp(temperature=-10)


def test_sendOffset_2(function):
    function.sendOffset(offset=50)


def test_sendGain_2(function):
    function.sendGain(gain=50)
