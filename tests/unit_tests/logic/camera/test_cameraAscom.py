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


def test_pollData(function):
    with mock.patch.object(function, "getAndStoreAscomProperty") as m:
        function.pollData()
    assert m.call_count == 9


def test_waitFunc_imageReady(function):
    with mock.patch.object(function, "getAscomProperty", return_value=True):
        result = function.waitFunc()
    assert result is False


def test_waitFunc_imageNotReady(function):
    with mock.patch.object(function, "getAscomProperty", return_value=False):
        result = function.waitFunc()
    assert result is True


def test_expose(function):
    fakeImage = [[1, 2], [3, 4]]
    with mock.patch.object(function, "setAscomProperty"):
        with mock.patch.object(function, "callAscomMethod"):
            with mock.patch.object(function.parent, "waitExposed"):
                with mock.patch.object(
                    function, "getAscomProperty", return_value=fakeImage
                ):
                    with mock.patch.object(
                        function.parent, "writeImageFitsHeader"
                    ):
                        with mock.patch.object(
                            function.parent, "exposeFinished"
                        ) as mf:
                            with mock.patch.object(
                                fits.PrimaryHDU, "writeto"
                            ):
                                function.expose()
    mf.assert_called_once()


def test_expose_withFastReadout(function):
    function.data["CAN_FAST"] = True
    fakeImage = [[1, 2], [3, 4]]
    with mock.patch.object(function, "setAscomProperty") as ms:
        with mock.patch.object(function, "callAscomMethod"):
            with mock.patch.object(function.parent, "waitExposed"):
                with mock.patch.object(
                    function, "getAscomProperty", return_value=fakeImage
                ):
                    with mock.patch.object(
                        function.parent, "writeImageFitsHeader"
                    ):
                        with mock.patch.object(function.parent, "exposeFinished"):
                            with mock.patch.object(
                                fits.PrimaryHDU, "writeto"
                            ):
                                function.expose()
    calls = [c[0][0] for c in ms.call_args_list]
    assert "FastReadout" in calls


def test_expose_noFastReadout(function):
    function.data["CAN_FAST"] = False
    fakeImage = [[1, 2], [3, 4]]
    with mock.patch.object(function, "setAscomProperty") as ms:
        with mock.patch.object(function, "callAscomMethod"):
            with mock.patch.object(function.parent, "waitExposed"):
                with mock.patch.object(
                    function, "getAscomProperty", return_value=fakeImage
                ):
                    with mock.patch.object(
                        function.parent, "writeImageFitsHeader"
                    ):
                        with mock.patch.object(function.parent, "exposeFinished"):
                            with mock.patch.object(
                                fits.PrimaryHDU, "writeto"
                            ):
                                function.expose()
    calls = [c[0][0] for c in ms.call_args_list]
    assert "FastReadout" not in calls


def test_abort_canAbort(function):
    function.data["CAN_ABORT"] = True
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        suc = function.abort()
    assert suc
    m.assert_called_once_with("StopExposure", ())


def test_abort_cannotAbort(function):
    function.data["CAN_ABORT"] = False
    with mock.patch.object(function, "callAscomMethodQueued") as m:
        suc = function.abort()
    assert suc
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
