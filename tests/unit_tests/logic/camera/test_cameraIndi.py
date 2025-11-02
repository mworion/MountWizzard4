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
import unittest.mock as mock
import zlib

import pytest

# external packages
from astropy.io import fits
from PySide6.QtCore import QObject, Signal

from mw4.base.indiClass import IndiClass
from mw4.base.signalsDevices import Signals
from mw4.indibase.indiClient import Client
from mw4.indibase.indiDevice import Device
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraIndi import CameraIndi

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent(QObject):
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000
    binning = 1
    posX = 0
    posY = 0
    width = 1000
    height = 1000
    exposureTime = 1
    exposeFinished = Signal()
    imagePath = "tests/work/image/test.fit"

    def writeImageFitsHeader(self, hdu, data):
        """Mock method to simulate writing FITS header."""
        pass

    def writePointingFitsHeader(self, hdu, data):
        """Mock method to simulate writing pointing FITS header."""
        pass


@pytest.fixture(autouse=True, scope="module")
def function():
    camera = Camera(App())
    camera.exposureTime = 1
    camera.binning = 1
    camera.focalLength = 1
    func = CameraIndi(parent=Parent())
    yield func
    func.app.threadPool.waitForDone(5000)


def test_setUpdateConfig_3(function):
    function.deviceName = "test"
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"Test": 1}):
        function.setUpdateConfig("test")


def test_setUpdateConfig_4(function):
    function.deviceName = "test"
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD_MS": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=False):
            function.setUpdateConfig("test")


def test_setUpdateConfig_5(function):
    function.deviceName = "test"
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD_MS": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.setUpdateConfig("test")


def test_setExposureState_1(function):
    function.device = Device()
    setattr(function.device, "CCD_EXPOSURE", {"state": "Busy"})
    function.data = {"CCD_EXPOSURE.CCD_EXPOSURE_VALUE": 0.0000001}
    function.isDownloading = False
    function.setExposureState()
    assert function.isDownloading


def test_setExposureState_2(function):
    function.device = Device()
    setattr(function.device, "CCD_EXPOSURE", {"state": "Busy"})
    function.data = {"CCD_EXPOSURE.CCD_EXPOSURE_VALUE": 0.0000001}
    function.isDownloading = True
    function.setExposureState()
    assert function.isDownloading


def test_setExposureState_3(function):
    function.device = Device()
    setattr(function.device, "CCD_EXPOSURE", {"state": "Busy"})
    function.data = {"CCD_EXPOSURE.CCD_EXPOSURE_VALUE": 1}
    function.isDownloading = True
    function.setExposureState()
    assert function.isDownloading


def test_setExposureState_4(function):
    function.device = Device()
    setattr(function.device, "CCD_EXPOSURE", {"state": "Busy"})
    function.data = {"CCD_EXPOSURE.CCD_EXPOSURE_VALUE": None}
    function.isDownloading = True
    function.setExposureState()
    assert function.isDownloading


def test_setExposureState_5(function):
    function.device = Device()
    setattr(function.device, "CCD_EXPOSURE", {"state": "Ok"})
    function.data = {"CCD_EXPOSURE.CCD_EXPOSURE_VALUE": None}
    function.isDownloading = True
    function.setExposureState()
    assert not function.isDownloading


def test_setExposureState_6(function):
    function.device = Device()
    setattr(function.device, "CCD_EXPOSURE", {"state": "test"})
    function.data = {"CCD_EXPOSURE.CCD_EXPOSURE_VALUE": None}
    function.isDownloading = True
    function.setExposureState()
    assert function.isDownloading


def test_setExposureState_7(function):
    function.device = Device()
    setattr(function.device, "CCD_EXPOSURE", {"state": "Alert"})
    function.data = {"CCD_EXPOSURE.CCD_EXPOSURE_VALUE": None}
    function.isDownloading = True
    function.setExposureState()
    assert not function.isDownloading


def test_sendDownloadMode_1(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"Test": 1}):
        function.sendDownloadMode()


def test_updateNumber_2(function):
    function.device = Device()
    setattr(function.device, "CCD_EXPOSURE", {"state": "Busy"})

    function.data = {"AUTO_DEW.DEW_C": 1, "VERSION.UPB": 1}
    with mock.patch.object(IndiClass, "updateNumber", return_value=True):
        function.updateNumber("test", "CCD_EXPOSURE")


def test_updateNumber_3(function):
    function.data = {"AUTO_DEW.DEW_C": 1, "VERSION.UPB": 1}
    with mock.patch.object(IndiClass, "updateNumber", return_value=True):
        function.updateNumber("test", "CCD_TEMPERATURE")


def test_updateNumber_4(function):
    function.device = Device()
    data = {"elementList": {"GAIN": {"min": 1, "max": 1}}}
    setattr(function.device, "CCD_GAIN", data)
    with mock.patch.object(IndiClass, "updateNumber", return_value=True):
        with mock.patch.object(function, "setExposureState"):
            function.updateNumber("test", "CCD_GAIN")


def test_updateNumber_5(function):
    function.device = Device()
    data = {"elementList": {"OFFSET": {"min": 1, "max": 1}}}
    setattr(function.device, "CCD_OFFSET", data)
    with mock.patch.object(IndiClass, "updateNumber", return_value=True):
        with mock.patch.object(function, "setExposureState"):
            function.updateNumber("test", "CCD_OFFSET")


def test_updateNumber_6(function):
    function.device = Device()
    data = {"elementList": {"OFFSET": {"min": 1, "max": 1}}}
    setattr(function.device, "CCD_OFFSET", data)
    with mock.patch.object(IndiClass, "updateNumber", return_value=False):
        with mock.patch.object(function, "setExposureState"):
            function.updateNumber("test", "CCD_OFFSET")


def test_workerSaveBLOB_1(function):
    function.imagePath = "tests/work/image/test.fit"
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {"value": "1", "name": "CCD1", "format": ".fits.fz"}
    with mock.patch.object(fits.HDUList, "fromstring", return_value=hdu):
        with mock.patch.object(fits.HDUList, "writeto"):
            with mock.patch.object(function.parent, "writeImageFitsHeader"):
                function.workerSaveBLOB(data)


def test_workerSaveBLOB_2(function):
    function.imagePath = "tests/work/image/test.fit"
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {"value": zlib.compress(b"1"), "name": "CCD1", "format": ".fits.z"}
    with mock.patch.object(fits.HDUList, "fromstring", return_value=hdu):
        with mock.patch.object(fits.HDUList, "writeto"):
            with mock.patch.object(function.parent, "writeImageFitsHeader"):
                function.workerSaveBLOB(data)


def test_workerSaveBLOB_3(function):
    function.imagePath = "tests/work/image/test.fit"
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {"value": "1", "name": "CCD1", "format": ".fits"}
    with mock.patch.object(fits.HDUList, "fromstring", return_value=hdu):
        with mock.patch.object(fits.HDUList, "writeto"):
            with mock.patch.object(function.parent, "writeImageFitsHeader"):
                function.workerSaveBLOB(data)


def test_workerSaveBLOB_4(function):
    function.imagePath = "tests/work/image/test.fit"
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {"value": "1", "name": "CCD1", "format": ".test"}
    with mock.patch.object(fits.HDUList, "fromstring", return_value=hdu):
        with mock.patch.object(fits.HDUList, "writeto"):
            with mock.patch.object(function.parent, "writeImageFitsHeader"):
                function.workerSaveBLOB(data)


def test_updateBLOB_1(function):
    function.device = Device()
    with mock.patch.object(IndiClass, "updateBLOB", return_value=False):
        with mock.patch.object(function.device, "getBlob", return_value={}):
            function.updateBLOB("test", "test")


def test_updateBLOB_2(function):
    function.device = Device()
    with mock.patch.object(IndiClass, "updateBLOB", return_value=True):
        with mock.patch.object(function.device, "getBlob", return_value={}):
            function.updateBLOB("test", "test")


def test_updateBLOB_3(function):
    function.device = Device()
    with mock.patch.object(IndiClass, "updateBLOB", return_value=True):
        with mock.patch.object(function.device, "getBlob", return_value={"value": 1}):
            function.updateBLOB("test", "test")


def test_updateBLOB_4(function):
    function.device = Device()
    with mock.patch.object(IndiClass, "updateBLOB", return_value=True):
        with mock.patch.object(
            function.device, "getBlob", return_value={"value": 1, "name": "test"}
        ):
            function.updateBLOB("test", "test")


def test_updateBLOB_5(function):
    function.device = Device()
    with mock.patch.object(IndiClass, "updateBLOB", return_value=True):
        with mock.patch.object(
            function.device,
            "getBlob",
            return_value={"value": 1, "name": "CCD2", "format": "test"},
        ):
            function.updateBLOB("test", "test")


def test_updateBLOB_6(function):
    function.device = Device()
    with mock.patch.object(IndiClass, "updateBLOB", return_value=True):
        with mock.patch.object(
            function.device,
            "getBlob",
            return_value={"value": 1, "name": "CCD1", "format": "test"},
        ):
            with mock.patch.object(function.threadPool, "start"):
                function.updateBLOB("test", "test")


def test_expose_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function, "sendDownloadMode", return_value=False):
        suc = function.expose()
        assert not suc


def test_expose_3(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=False):
            suc = function.expose()
            assert not suc


def test_expose_4(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            suc = function.expose()
            assert suc


def test_abort_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"Test": 1}):
        suc = function.abort()
        assert not suc


def test_abort_3(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"ABORT": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            suc = function.abort()
            assert suc


def test_sendCoolerSwitch_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"Test": 1}):
        function.sendCoolerSwitch()


def test_sendCoolerSwitch_3(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"COOLER_ON": True}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.sendCoolerSwitch(True)


def test_sendCoolerTemp_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"Test": 1}):
        function.sendCoolerTemp()


def test_sendCoolerTemp_3(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(
        function.device, "getNumber", return_value={"CCD_TEMPERATURE_VALUE": 1}
    ):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.sendCoolerTemp()


def test_sendOffset_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"Test": 1}):
        function.sendOffset()


def test_sendOffset_3(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"OFFSET": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.sendOffset()


def test_sendGain_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"Test": 1}):
        function.sendGain()


def test_sendGain_3(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"GAIN": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.sendGain()
