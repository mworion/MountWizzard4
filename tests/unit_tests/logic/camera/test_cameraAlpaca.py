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
# Licence APL2.0
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
    func = CameraAlpaca(camera)
    yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.workerGetInitialConfig()


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool, "start"):
        function.workerPollData()


def test_sendDownloadMode_1(function):
    function.data["CAN_FAST"] = True
    with mock.patch.object(function, "setDeviceProp", return_value=True):
        function.sendDownloadMode()


def test_waitFunc(function):
    with mock.patch.object(function, "getDeviceProp", return_value=False):
        suc = function.waitFunc()
        assert suc


def test_getImageArray_1(function):
    with mock.patch.object(function, "getDeviceProp", return_value="data"):
        result = function.getImageArray("")
        assert result == "data"


def test_workerExpose_1(function):
    with mock.patch.object(function.parent, "sendDownloadMode"):
        with mock.patch.object(function, "setDeviceProp"):
            with mock.patch.object(function, "callDeviceMethod"):
                with mock.patch.object(function.parent, "waitExposed"):
                    with mock.patch.object(
                        function.parent, "retrieveImage"
                    ):
                        with mock.patch.object(
                            function.parent, "writeImageFitsHeader"
                        ):
                            with mock.patch.object(fits.HDUList, "writeto"):
                                function.workerExpose()


def test_expose_1(function):
    with mock.patch.object(function.threadPool, "start"):
        function.expose()


def test_abort_1(function):
    function.data["CAN_ABORT"] = False
    suc = function.abort()
    assert suc


def test_abort_2(function):
    function.data["CAN_ABORT"] = True
    with mock.patch.object(function, "callDeviceMethod"):
        suc = function.abort()
        assert suc


def test_sendCoolerSwitch_1(function):
    with mock.patch.object(function, "setDeviceProp", return_value=True):
        function.sendCoolerSwitch()


def test_sendCoolerSwitch_2(function):
    with mock.patch.object(function, "setDeviceProp", return_value=True):
        function.sendCoolerSwitch(coolerOn=True)


def test_sendCoolerTemp_1(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = True
    with mock.patch.object(function, "setDeviceProp", return_value=True):
        function.sendCoolerTemp()


def test_sendOffset_1(function):
    with mock.patch.object(function, "setDeviceProp", return_value=True):
        function.sendOffset()


def test_sendGain_1(function):
    with mock.patch.object(function, "setDeviceProp", return_value=True):
        function.sendGain()
