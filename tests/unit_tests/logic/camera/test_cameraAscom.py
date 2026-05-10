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
import ctypes
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
        image = [1, 1, 1]
        ImageArray = (ctypes.c_int * len(image))(*image)

        @staticmethod
        def StartExposure(time, light=True):
            return True

        @staticmethod
        def StopExposure():
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
    func.client = Test1()
    yield func


def test_getInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        function.getInitialConfig()


def test_pollData_regular(function):
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        function.exposurePending = False
        function.exposing = False
        function.pollData()


def test_pollData_exposureStart(function):
    function.exposurePending = True
    function.exposing = False
    function.data["CAN_FAST"] = False
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        with mock.patch.object(function, "setAscomProperty"):
            with mock.patch.object(function, "callAscomMethod") as mc:
                with mock.patch.object(function, "getAscomProperty", return_value=False):
                    function.pollData()
    assert function.exposing
    mc.assert_called_once_with("StartExposure", (function.parent.exposureTime, True))


def test_pollData_exposureStart_fastReadout(function):
    function.exposurePending = True
    function.exposing = False
    function.data["CAN_FAST"] = True
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        with mock.patch.object(function, "setAscomProperty") as ms:
            with mock.patch.object(function, "callAscomMethod"):
                with mock.patch.object(function, "getAscomProperty", return_value=False):
                    function.pollData()
    calls = [c[0][0] for c in ms.call_args_list]
    assert "FastReadout" in calls


def test_pollData_imageReady(function):
    function.exposurePending = False
    function.exposing = True
    fakeImage = [[1, 2], [3, 4]]

    def fake_getprop(prop: str):
        if prop == "ImageArray":
            return fakeImage
        return True

    with mock.patch.object(function, "getAndStoreAscomProperty"):
        with mock.patch.object(
            function, "getAscomProperty", side_effect=fake_getprop
        ):
            with mock.patch.object(function.parent, "writeImageFitsHeader"):
                with mock.patch.object(
                    function.parent, "exposeFinished"
                ) as mf:
                    with mock.patch.object(fits.HDUList, "writeto"):
                        function.pollData()
    assert not function.exposing
    mf.assert_called_once()


def test_pollData_imageNotReady(function):
    function.exposurePending = False
    function.exposing = True
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        with mock.patch.object(function, "getAscomProperty", return_value=False):
            with mock.patch.object(function.parent, "exposeFinished") as mf:
                function.pollData()
    assert function.exposing
    mf.assert_not_called()


def test_expose(function):
    function.exposurePending = False
    function.expose()
    assert function.exposurePending


def test_abort_canAbort(function):
    function.data["CAN_ABORT"] = True
    function.exposurePending = True
    function.exposing = True
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        suc = function.abort()
    assert suc
    assert not function.exposurePending
    assert not function.exposing
    m.assert_called_once_with("StopExposure", ())


def test_abort_cannotAbort(function):
    function.data["CAN_ABORT"] = False
    function.exposurePending = True
    function.exposing = True
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        suc = function.abort()
    assert suc
    assert not function.exposurePending
    assert not function.exposing
    m.assert_not_called()


def test_sendCoolerSwitch(function):
    with mock.patch.object(function, "setAscomPropertyQueued") as m:
        function.sendCoolerSwitch(coolerOn=True)
    m.assert_called_once_with("CoolerOn", True)


def test_sendCoolerTemp_withCap(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = True
    with mock.patch.object(function, "setAscomPropertyQueued") as m:
        function.sendCoolerTemp(temperature=-10)
    m.assert_called_once_with("SetCCDTemperature", -10)


def test_sendCoolerTemp_noCap(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = False
    with mock.patch.object(function, "setAscomPropertyQueued") as m:
        function.sendCoolerTemp(temperature=-10)
    m.assert_not_called()


def test_sendOffset(function):
    with mock.patch.object(function, "setAscomPropertyQueued") as m:
        function.sendOffset(5)
    m.assert_called_once_with("Offset", 5)


def test_sendGain(function):
    with mock.patch.object(function, "setAscomPropertyQueued") as m:
        function.sendGain(200)
    m.assert_called_once_with("Gain", 200)
