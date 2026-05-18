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
import pytest
import unittest.mock as mock
from astropy.io import fits
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraAlpaca import CameraAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    camera = Camera(App())
    camera.exposureTime = 1
    camera.binning = 1
    camera.focalLength = 1
    camera.posXASCOM = 0
    camera.posYASCOM = 0
    camera.widthASCOM = 100
    camera.heightASCOM = 100
    camera.fastReadout = False
    camera.imagePath = "/tmp/test.fits"
    func = CameraAlpaca(camera)
    func.device = mock.MagicMock()
    yield func


def test_getInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        with mock.patch.object(function, "getDeviceProp"):
            function.getInitialConfig()


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        function.pollData()
    assert m.call_count == 9


def test_sendDownloadMode_1(function):
    function.data["CAN_FAST"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendDownloadMode()
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "FastReadout"


def test_sendDownloadMode_2(function):
    function.data["CAN_FAST"] = False
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendDownloadMode()
    assert function.commandQueue.empty()


def test_saveImage_notExposing(function):
    function.parent.exposing = False
    function.saveImage()


def test_saveImage_imageNotReady(function):
    function.parent.exposing = True
    function.data["CAMERA.STATE"] = 0
    with mock.patch.object(function, "getDeviceProp", return_value=False):
        function.saveImage()
    function.parent.exposing = False


def test_saveImage_imageReady(function):
    function.parent.exposing = True
    function.data["CAMERA.STATE"] = 0
    fakeImage = [[1, 2], [3, 4]]
    with mock.patch.object(
        function, "getDeviceProp", side_effect=[True, fakeImage]
    ):
        with mock.patch.object(function.parent, "writeImageFitsHeader"):
            with mock.patch.object(
                function.parent, "exposeFinished"
            ) as mf:
                with mock.patch.object(fits.PrimaryHDU, "writeto"):
                    function.saveImage()
    mf.assert_called_once()
    function.parent.exposing = False


def test_expose_basic(function):
    function.data.pop("CAN_FAST", None)
    with mock.patch.object(function, "setDevicePropQueued") as ms:
        with mock.patch.object(function, "callDeviceMethodQueued") as mc:
            function.expose()
    props_set = [c.args[0] for c in ms.call_args_list]
    assert "BinX" in props_set
    assert "BinY" in props_set
    assert "FastReadout" not in props_set
    mc.assert_called_once_with(
        "StartExposure", Duration=1, Light=True
    )


def test_expose_withFastReadout(function):
    function.data["CAN_FAST"] = True
    function.parent.fastReadout = True
    with mock.patch.object(function, "setDevicePropQueued") as ms:
        with mock.patch.object(function, "callDeviceMethodQueued"):
            function.expose()
    props_set = [c.args[0] for c in ms.call_args_list]
    assert "FastReadout" in props_set


def test_expose_noFastReadout(function):
    function.data["CAN_FAST"] = False
    with mock.patch.object(function, "setDevicePropQueued") as ms:
        with mock.patch.object(function, "callDeviceMethodQueued"):
            function.expose()
    props_set = [c.args[0] for c in ms.call_args_list]
    assert "FastReadout" not in props_set


def test_abort_1(function):
    function.data["CAN_ABORT"] = False
    suc = function.abort()
    assert suc


def test_abort_2(function):
    function.data["CAN_ABORT"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    suc = function.abort()
    assert suc
    assert not function.commandQueue.empty()


def test_sendCoolerSwitch_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerSwitch()
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "CoolerOn"
    assert item.value is False


def test_sendCoolerSwitch_2(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerSwitch(coolerOn=True)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "CoolerOn"
    assert item.value is True


def test_sendCoolerTemp_1(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerTemp(temperature=-10.0)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "SetCCDTemperature"
    assert item.value == -10.0


def test_sendCoolerTemp_2(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = False
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerTemp(temperature=-10.0)
    assert function.commandQueue.empty()


def test_sendOffset_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendOffset(offset=50)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "Offset"
    assert item.value == 50


def test_sendGain_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendGain(gain=100)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "Gain"
    assert item.value == 100
