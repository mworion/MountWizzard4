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
    func.device = mock.MagicMock()
    yield func


def test_getInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        with mock.patch.object(function, "getDeviceProp"):
            function.getInitialConfig()


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        function.pollData()
        assert m.call_count >= 1


def test_sendDownloadMode_1(function):
    function.data["CAN_FAST"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendDownloadMode()
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.name == "FastReadout"


def test_sendDownloadMode_2(function):
    function.data["CAN_FAST"] = False
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendDownloadMode()
    assert function.commandQueue.empty()


def test_waitFunc(function):
    with mock.patch.object(function, "getDeviceProp", return_value=False):
        suc = function.waitFunc()
        assert suc


def test_workerExpose_1(function):
    with mock.patch.object(function, "sendDownloadMode"):
        with mock.patch.object(function, "setDeviceProp"):
            with mock.patch.object(function, "callDeviceMethod"):
                with mock.patch.object(
                    function, "getDeviceProp", return_value=[[1, 2], [3, 4]]
                ):
                    with mock.patch.object(function.parent, "waitExposed"):
                        with mock.patch.object(function.parent, "writeImageFitsHeader"):
                            with mock.patch.object(fits.PrimaryHDU, "writeto"):
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
    assert item.name == "CoolerOn"
    assert item.value is False


def test_sendCoolerSwitch_2(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerSwitch(coolerOn=True)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.name == "CoolerOn"
    assert item.value is True


def test_sendCoolerTemp_1(function):
    function.data["CAN_SET_CCD_TEMPERATURE"] = True
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendCoolerTemp(temperature=-10.0)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.name == "SetCCDTemperature"
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
    assert item.name == "Offset"
    assert item.value == 50


def test_sendGain_1(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.sendGain(gain=100)
    item = function.commandQueue.get_nowait()
    assert item.cmdType == "set"
    assert item.name == "Gain"
    assert item.value == 100
