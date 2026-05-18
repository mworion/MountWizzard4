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
import platform
import pytest
import unittest.mock as mock

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)

from astropy.io import fits
from mw4.base.loggerMW import setupLogging
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraAscom import CameraAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


@pytest.fixture(autouse=True, scope="module")
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
        Name = "test"
        DriverVersion = "1"
        DriverInfo = "test1"
        ImageReady = True
        Gain = 100
        Offset = 0

        @staticmethod
        def StartExposure(time, light=True):
            return True

        @staticmethod
        def AbortExposure():
            return True

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
    func = CameraAscom(camera)
    func.device = Test1()
    yield func


def test_getInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.getInitialConfig()


def test_pollData_1(function):
    function.parent.exposing = False
    function.exposing = False
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        function.pollData()
    assert m.call_count == 8


def test_pollData_parentExposing(function):
    function.parent.exposing = True
    function.exposing = False
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        with mock.patch.object(function, "setExposureState") as ms:
            function.pollData()
    ms.assert_called_once()
    function.parent.exposing = False


def test_pollData_selfExposing(function):
    function.parent.exposing = False
    function.exposing = True
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        with mock.patch.object(function.parent, "exposeFinished") as mf:
            function.pollData()
    assert function.exposing is False
    mf.assert_called_once()


def test_setExposureState_stateNot2NotExposing(function):
    # state != 2, self.exposing = False -> returns early
    function.exposing = False
    with mock.patch.object(function, "getDeviceProp", return_value=0) as m:
        function.setExposureState()
    assert function.exposing is False
    assert m.call_count == 1


def test_setExposureState_state2NotExposing(function):
    # state == 2, self.exposing = False -> sets exposing=True,
    # emits message, ImageReady=False -> returns
    function.exposing = False
    with mock.patch.object(
        function, "getDeviceProp", side_effect=[2, False]
    ):
        function.setExposureState()
    assert function.exposing is True
    function.exposing = False


def test_setExposureState_state2Exposing(function):
    # state == 2, self.exposing = True -> emits message,
    # ImageReady=False -> returns
    function.exposing = True
    with mock.patch.object(
        function, "getDeviceProp", side_effect=[2, False]
    ):
        function.setExposureState()
    assert function.exposing is True
    function.exposing = False


def test_setExposureState_stateNot2Exposing(function):
    # state != 2, self.exposing = True -> emits exposed+download,
    # ImageReady=False -> returns
    function.exposing = True
    with mock.patch.object(
        function, "getDeviceProp", side_effect=[0, False]
    ):
        function.setExposureState()
    assert function.exposing is True
    function.exposing = False


def test_setExposureState_stateNot2ExposingImageReady(function):
    # state != 2, self.exposing=True, ImageReady=True -> saves and finishes
    function.exposing = True
    fakeImage = [[1, 2], [3, 4]]
    with mock.patch.object(
        function, "getDeviceProp", side_effect=[0, True, fakeImage]
    ):
        with mock.patch.object(function.parent, "writeImageFitsHeader"):
            with mock.patch.object(
                function.parent, "exposeFinished"
            ) as mf:
                with mock.patch.object(fits.PrimaryHDU, "writeto"):
                    function.setExposureState()
    assert function.exposing is False
    mf.assert_called_once()


def test_setExposureState_state2NotExposingImageReady(function):
    # state == 2, self.exposing=False -> sets exposing=True,
    # ImageReady=True -> saves and finishes
    function.exposing = False
    fakeImage = [[1, 2], [3, 4]]
    with mock.patch.object(
        function, "getDeviceProp", side_effect=[2, True, fakeImage]
    ):
        with mock.patch.object(function.parent, "writeImageFitsHeader"):
            with mock.patch.object(
                function.parent, "exposeFinished"
            ) as mf:
                with mock.patch.object(fits.PrimaryHDU, "writeto"):
                    function.setExposureState()
    assert function.exposing is False
    mf.assert_called_once()


def test_sendDownloadMode_withFastReadout(function):
    function.data["CAN_FAST"] = True
    function.parent.fastReadout = True
    with mock.patch.object(function, "setDevicePropQueued") as m:
        function.sendDownloadMode()
    m.assert_called_once_with("FastReadout", True)


def test_sendDownloadMode_noFastReadout(function):
    function.data["CAN_FAST"] = False
    with mock.patch.object(function, "setDevicePropQueued") as m:
        function.sendDownloadMode()
    m.assert_not_called()


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
        "StartExposure",
        Duration=function.parent.exposureTime,
        Light=True,
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


def test_abort_canAbort(function):
    function.data["CAN_ABORT"] = True
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        suc = function.abort()
    assert suc
    m.assert_called_once_with("AbortExposure")


def test_abort_cannotAbort(function):
    function.data["CAN_ABORT"] = False
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        suc = function.abort()
    assert suc
    m.assert_not_called()


def test_sendCoolerSwitch(function):
    with mock.patch.object(function, "setDevicePropQueued") as m:
        function.sendCoolerSwitch(coolerOn=True)
    m.assert_called_once_with("CoolerOn", True)


def test_sendCoolerTemp_withCap(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = True
    with mock.patch.object(function, "setDevicePropQueued") as m:
        function.sendCoolerTemp(temperature=-10)
    m.assert_called_once_with("SetCCDTemperature", -10)


def test_sendCoolerTemp_noCap(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = False
    with mock.patch.object(function, "setDevicePropQueued") as m:
        function.sendCoolerTemp(temperature=-10)
    m.assert_not_called()


def test_sendOffset(function):
    with mock.patch.object(function, "setDevicePropQueued") as m:
        function.sendOffset(5)
    m.assert_called_once_with("Offset", 5)


def test_sendGain(function):
    with mock.patch.object(function, "setDevicePropQueued") as m:
        function.sendGain(200)
    m.assert_called_once_with("Gain", 200)
