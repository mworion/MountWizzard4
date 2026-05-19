############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import logging
import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.camera.cameraSgproNinaBase import CameraSgproNinaBase
from pathlib import Path


class ConcreteCameraBase(CameraSgproNinaBase):
    log = logging.getLogger("MW4")

    def __init__(self) -> None:
        pass

    def requestProperty(self, valueProp: str, params: dict | None = None) -> dict:
        return {}


class Parent:
    signals = Signals()
    binning = 1
    exposureTime = 1
    imagePath = Path("tests/work/image/test.fit")
    exposing = True
    exposeFinished = mock.Mock()
    waitStart = mock.Mock()
    waitExposed = mock.Mock()
    waitDownload = mock.Mock()
    waitSave = mock.Mock()
    waitFinish = mock.Mock()
    updateImageFitsHeaderPointing = mock.Mock()


@pytest.fixture(autouse=True, scope="module")
def function():
    func = ConcreteCameraBase()
    func.data = {}
    func.signals = Parent.signals
    func.parent = Parent()
    func.threadPool = mock.Mock()
    func.worker = None
    yield func


def test_workerGetInitialConfig(function):
    function.storePropertyToData = mock.Mock()
    function.workerGetInitialConfig()
    function.storePropertyToData.assert_called_once_with(1, "CCD_BINNING.HOR_BIN")


def test_sendDownloadMode(function):
    result = function.sendDownloadMode()
    assert result is None


def test_waitFunc_true(function):
    function.data["Device.Message"] = "integrating the signal"
    suc = function.waitFunc()
    assert suc


def test_waitFunc_false(function):
    function.data["Device.Message"] = "idle"
    suc = function.waitFunc()
    assert not suc


def test_workerExpose_1(function):
    with mock.patch.object(function, "captureImage", return_value=(False, {})):
        function.workerExpose()


def test_workerExpose_2(function):
    with mock.patch.object(function, "captureImage", return_value=(True, {})):
        function.workerExpose()


def test_workerExpose_3(function):
    function.parent.exposing = True
    with mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "123"})):
        with mock.patch.object(function.parent, "waitStart"):
            with mock.patch.object(function.parent, "waitExposed"):
                with mock.patch.object(function.parent, "waitDownload"):
                    with mock.patch.object(function.parent, "waitSave"):
                        with mock.patch.object(function.parent, "waitFinish"):
                            with mock.patch.object(
                                function.parent,
                                "updateImageFitsHeaderPointing",
                            ):
                                function.workerExpose()


def test_workerExpose_4(function):
    function.parent.exposing = False
    function.parent.imagePath = Path("tests/work/image/test.fit")
    with mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "123"})):
        with mock.patch.object(function.parent, "waitStart"):
            with mock.patch.object(function.parent, "waitExposed"):
                with mock.patch.object(function.parent, "waitDownload"):
                    with mock.patch.object(function.parent, "waitSave"):
                        with mock.patch.object(function.parent, "waitFinish"):
                            function.workerExpose()
    assert function.parent.imagePath == Path()


def test_expose_1(function):
    with mock.patch.object(function.threadPool, "start"):
        function.expose()
    assert function.worker is not None


def test_abort_1(function):
    with mock.patch.object(function, "abortImage", return_value=True) as m:
        suc = function.abort()
        assert suc
        m.assert_called_once()


def test_sendCoolerSwitch_1(function):
    result = function.sendCoolerSwitch(coolerOn=True)
    assert result is None


def test_sendCoolerTemp_1(function):
    result = function.sendCoolerTemp(temperature=-10)
    assert result is None


def test_sendOffset_1(function):
    result = function.sendOffset(offset=50)
    assert result is None


def test_sendGain_1(function):
    result = function.sendGain(gain=50)
    assert result is None


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
