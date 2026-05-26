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
from mw4.logic.camera.cameraAlpacaAscomBase import CameraAlpacaAscomBase
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


def test_cameraAlpacaAscomBase_cameraStates(function):
    assert CameraAlpacaAscomBase.CAMERA_STATES == [
        "CameraIdle",
        "CameraWaiting",
        "CameraExposing",
        "CameraReading",
        "CameraDownload",
        "CameraError",
    ]


def test_cameraAlpacaAscomBase_initAttributes(function):
    assert hasattr(function, "parent")
    assert hasattr(function, "startTimeExposure")
    assert hasattr(function, "exposing")
    assert function.startTimeExposure == 0
    assert function.exposing is False


def test_getInitialConfig(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp") as m,
        mock.patch.object(function, "getDeviceProp"),
    ):
        function.getInitialConfig()
    assert m.call_count >= 18


def test_pollData_notExposingNotSelfExposing(function):
    function.parent.exposing = False
    function.exposing = False
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        function.pollData()
    assert m.call_count == 8


def test_pollData_parentExposing(function):
    function.parent.exposing = True
    function.exposing = False
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "setExposureState") as ms,
    ):
        function.pollData()
    ms.assert_called_once()
    function.parent.exposing = False


def test_pollData_selfExposing(function):
    function.parent.exposing = False
    function.exposing = True
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function.parent, "exposeFinished") as mf,
    ):
        function.pollData()
    assert function.exposing is False
    mf.assert_called_once()


def test_sendDownloadMode_canFast(function):
    function.data["CAN_FAST"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendDownloadMode()
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "FastReadout"


def test_sendDownloadMode_noFast(function):
    function.data["CAN_FAST"] = False
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendDownloadMode()
    assert function.commandQueue.empty()


def test_setExposureState_stateNot2NotExposing(function):
    # state != 2, self.exposing = False -> returns early
    function.exposing = False
    with mock.patch.object(function, "getDeviceProp", return_value=0) as m:
        function.setExposureState()
    assert function.exposing is False
    assert m.call_count == 1


def test_setExposureState_stateNot0Not2NotExposing(function):
    # state != 0 and != 2, not self.exposing -> reaches the
    # "state != 2 and not self.exposing" guard and returns
    function.exposing = False
    with mock.patch.object(function, "getDeviceProp", return_value=4) as m:
        function.setExposureState()
    assert function.exposing is False
    assert m.call_count == 1


def test_setExposureState_state2NotExposing(function):
    # state == 2, self.exposing = False -> sets exposing=True,
    # emits message, ImageReady=False -> returns
    function.exposing = False
    with mock.patch.object(function, "getDeviceProp", side_effect=[2, False]):
        function.setExposureState()
    assert function.exposing is True
    function.exposing = False


def test_setExposureState_state2Exposing(function):
    # state == 2, self.exposing = True -> emits message,
    # ImageReady=False -> returns
    function.exposing = True
    with mock.patch.object(function, "getDeviceProp", side_effect=[2, False]):
        function.setExposureState()
    assert function.exposing is True
    function.exposing = False


def test_setExposureState_stateNot2Exposing(function):
    # state != 2, self.exposing = True -> emits exposed+download,
    # ImageReady=False -> returns
    function.exposing = True
    with mock.patch.object(function, "getDeviceProp", side_effect=[0, False]):
        function.setExposureState()
    assert function.exposing is True
    function.exposing = False


def test_setExposureState_stateNot2ExposingImageReady(function):
    # state != 2, self.exposing=True, ImageReady=True
    # -> saves and finishes
    function.exposing = True
    fakeImage = [[1, 2], [3, 4]]
    with (
        mock.patch.object(function, "getDeviceProp", side_effect=[0, True, True, fakeImage]),
        mock.patch.object(function.parent, "writeImageFitsHeader"),
        mock.patch.object(function.parent, "exposeFinished") as mf,
        mock.patch.object(fits.PrimaryHDU, "writeto"),
    ):
        function.setExposureState()
    assert function.exposing is False
    mf.assert_called_once()


def test_setExposureState_state2NotExposingImageReady(function):
    # state == 2, self.exposing=False -> sets exposing=True,
    # ImageReady=True -> saves and finishes
    function.exposing = False
    fakeImage = [[1, 2], [3, 4]]
    with (
        mock.patch.object(function, "getDeviceProp", side_effect=[2, True, True, fakeImage]),
        mock.patch.object(function.parent, "writeImageFitsHeader"),
        mock.patch.object(function.parent, "exposeFinished") as mf,
        mock.patch.object(fits.PrimaryHDU, "writeto"),
    ):
        function.setExposureState()
    assert function.exposing is False
    mf.assert_called_once()


def test_expose_basic(function):
    function.data.pop("CAN_FAST", None)
    with (
        mock.patch.object(function, "setDevicePropQueued") as ms,
        mock.patch.object(function, "callDeviceMethodQueued") as mc,
    ):
        function.expose()
    props_set = [c.args[0] for c in ms.call_args_list]
    assert "BinX" in props_set
    assert "BinY" in props_set
    assert "FastReadout" not in props_set
    mc.assert_called_once_with("StartExposure", Duration=1, Light=True)


def test_expose_withFastReadout(function):
    function.data["CAN_FAST"] = True
    function.parent.fastReadout = True
    with (
        mock.patch.object(function, "setDevicePropQueued") as ms,
        mock.patch.object(function, "callDeviceMethodQueued"),
    ):
        function.expose()
    props_set = [c.args[0] for c in ms.call_args_list]
    assert "FastReadout" in props_set


def test_expose_noFastReadout(function):
    function.data["CAN_FAST"] = False
    with (
        mock.patch.object(function, "setDevicePropQueued") as ms,
        mock.patch.object(function, "callDeviceMethodQueued"),
    ):
        function.expose()
    props_set = [c.args[0] for c in ms.call_args_list]
    assert "FastReadout" not in props_set


def test_abort_cannotAbort(function):
    function.data["CAN_ABORT"] = False
    suc = function.abort()
    assert not suc


def test_abort_canAbort(function):
    function.data["CAN_ABORT"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    suc = function.abort()
    assert suc
    assert not function.commandQueue.empty()


def test_sendCoolerSwitch_default(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerSwitch()
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "CoolerOn"
    assert item.value is False


def test_sendCoolerSwitch_on(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerSwitch(coolerOn=True)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "CoolerOn"
    assert item.value is True


def test_sendCoolerTemp_withCap(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerTemp(temperature=-10.0)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "SetCCDTemperature"
    assert item.value == -10.0


def test_sendCoolerTemp_noCap(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = False
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerTemp(temperature=-10.0)
    assert function.commandQueue.empty()


def test_sendOffset(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendOffset(offset=50)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "Offset"
    assert item.value == 50


def test_sendGain(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendGain(gain=100)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.valueProp == "Gain"
    assert item.value == 100
