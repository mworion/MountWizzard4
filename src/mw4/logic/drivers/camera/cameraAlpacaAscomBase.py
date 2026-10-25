# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
import time
from astropy.io import fits
from mw4.base.cameraKeys import (
    CAN_ABORT,
    CAN_FAST,
    CAN_GET_COOLER_POWER,
    CAN_SET_CCD_TEMPERATURE,
    CCD_BINNING_HOR_BIN,
    CCD_BINNING_HOR_BIN_MAX,
    CCD_BINNING_VERT_BIN,
    CCD_BINNING_VERT_BIN_MAX,
    CCD_COOLER_COOLER_ON,
    CCD_COOLER_POWER_CCD_COOLER_VALUE,
    CCD_FRAME_X,
    CCD_FRAME_Y,
    CCD_GAIN_GAIN,
    CCD_GAIN_GAIN_LIST,
    CCD_GAIN_GAIN_MAX,
    CCD_GAIN_GAIN_MIN,
    CCD_INFO_CCD_MAX_X,
    CCD_INFO_CCD_MAX_Y,
    CCD_INFO_CCD_PIXEL_SIZE_X,
    CCD_INFO_CCD_PIXEL_SIZE_Y,
    CCD_OFFSET_OFFSET,
    CCD_OFFSET_OFFSET_LIST,
    CCD_OFFSET_OFFSET_MAX,
    CCD_OFFSET_OFFSET_MIN,
    CCD_TEMPERATURE_CCD_TEMPERATURE_VALUE,
    READOUT_QUALITY_QUALITY_LOW,
)
from mw4.logic.drivers.frameworks.alpacaAscomCommon import AlpacaAscomCommon
from typing import Any, ClassVar


class CameraAlpacaAscomBase(AlpacaAscomCommon):
    CAMERA_STATES: ClassVar[list[str]] = [
        "CameraIdle",
        "CameraWaiting",
        "CameraExposing",
        "CameraReading",
        "CameraDownload",
        "CameraError",
    ]

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.startTimeExposure: float = 0
        self.exposing: bool = False
        self.downloading: bool = False

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        self.getAndStoreDeviceProp("CameraXSize", CCD_INFO_CCD_MAX_X)
        self.getAndStoreDeviceProp("CameraYSize", CCD_INFO_CCD_MAX_Y)
        self.getAndStoreDeviceProp("CanFastReadout", CAN_FAST)
        self.getAndStoreDeviceProp("CanAbortExposure", CAN_ABORT)
        self.getAndStoreDeviceProp("CanSetCCDTemperature", CAN_SET_CCD_TEMPERATURE)
        self.getAndStoreDeviceProp("CanGetCoolerPower", CAN_GET_COOLER_POWER)
        self.getAndStoreDeviceProp("PixelSizeX", CCD_INFO_CCD_PIXEL_SIZE_X)
        self.getAndStoreDeviceProp("PixelSizeY", CCD_INFO_CCD_PIXEL_SIZE_Y)
        self.getAndStoreDeviceProp("MaxBinX", CCD_BINNING_HOR_BIN_MAX)
        self.getAndStoreDeviceProp("MaxBinY", CCD_BINNING_VERT_BIN_MAX)
        self.getAndStoreDeviceProp("GainMax", CCD_GAIN_GAIN_MAX)
        self.getAndStoreDeviceProp("GainMin", CCD_GAIN_GAIN_MIN)
        self.getAndStoreDeviceProp("Gains", CCD_GAIN_GAIN_LIST)
        self.getAndStoreDeviceProp("OffsetMax", CCD_OFFSET_OFFSET_MAX)
        self.getAndStoreDeviceProp("OffsetMin", CCD_OFFSET_OFFSET_MIN)
        self.getAndStoreDeviceProp("Offsets", CCD_OFFSET_OFFSET_LIST)
        self.getAndStoreDeviceProp("StartX", CCD_FRAME_X)
        self.getAndStoreDeviceProp("StartY", CCD_FRAME_Y)
        self.log.debug("Initial data: %s", self.data)

    def setExposureState(self) -> None:
        if not self.parent.exposing:
            return
        state = self.getDeviceProp("CameraState")
        if state == 2:
            self.exposing = True
            timeLeft = max(self.parent.exposureTime - time.time() + self.startTimeExposure, 0)
            text = f"expose {timeLeft:3.0f} s"
            self.signals.message.emit(text)
        if not self.exposing:
            return
        if state == 4 and not self.downloading:
            self.downloading = True
            self.signals.exposed.emit(self.parent.imagePath)
            self.signals.message.emit("download")
        if not self.getDeviceProp("ImageReady"):
            return
        if not self.downloading:
            self.signals.exposed.emit(self.parent.imagePath)
        self.signals.downloaded.emit(self.parent.imagePath)
        data = self.getDeviceProp("ImageArray")
        data = np.array(data, dtype=np.uint16).transpose()
        self.signals.message.emit("save")
        hdu = fits.PrimaryHDU(data=data)
        hdu.writeto(self.parent.imagePath, overwrite=True)
        self.parent.writeImageFitsHeader()
        self.parent.exposeFinished()
        self.downloading = False
        self.exposing = False

    def pollData(self) -> None:
        self.setExposureState()
        self.getAndStoreDeviceProp("BinX", CCD_BINNING_HOR_BIN)
        self.getAndStoreDeviceProp("BinY", CCD_BINNING_VERT_BIN)
        self.getAndStoreDeviceProp("Gain", CCD_GAIN_GAIN)
        self.getAndStoreDeviceProp("Offset", CCD_OFFSET_OFFSET)
        self.getAndStoreDeviceProp("FastReadout", READOUT_QUALITY_QUALITY_LOW)
        self.getAndStoreDeviceProp("CCDTemperature", CCD_TEMPERATURE_CCD_TEMPERATURE_VALUE)
        self.getAndStoreDeviceProp("CoolerOn", CCD_COOLER_COOLER_ON)
        self.getAndStoreDeviceProp("CoolerPower", CCD_COOLER_POWER_CCD_COOLER_VALUE)

    def sendDownloadMode(self) -> None:
        if self.data.get(CAN_FAST, False):
            self.setDevicePropQueued("FastReadout", self.parent.fastReadout)

    def expose(self) -> None:
        self.sendDownloadMode()
        self.setDevicePropQueued("BinX", self.parent.binning)
        self.setDevicePropQueued("BinY", self.parent.binning)
        self.setDevicePropQueued("StartX", self.parent.posXASCOM)
        self.setDevicePropQueued("StartY", self.parent.posYASCOM)
        self.setDevicePropQueued("NumX", self.parent.widthASCOM)
        self.setDevicePropQueued("NumY", self.parent.heightASCOM)
        self.startTimeExposure = time.time()
        self.callDeviceMethodQueued(
            "StartExposure",
            Duration=self.parent.exposureTime,
            Light=True,
        )

    def abort(self) -> bool:
        if self.data.get(CAN_ABORT, False):
            self.callDeviceMethodQueued("AbortExposure")
            return True
        return False

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        self.setDevicePropQueued("CoolerOn", coolerOn)

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        if self.data.get(CAN_SET_CCD_TEMPERATURE, False):
            self.setDevicePropQueued("SetCCDTemperature", temperature)

    def sendOffset(self, offset: int = 0) -> None:
        self.setDevicePropQueued("Offset", offset)

    def sendGain(self, gain: int = 0) -> None:
        self.setDevicePropQueued("Gain", gain)
