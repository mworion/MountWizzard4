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
import numpy as np
from astropy.io import fits
from mw4.base.ascomClass import AscomClass
from typing import Any
import platform
if platform.system() == "Windows":
    from pythoncom import CoInitialize, CoUninitialize

class CameraAscom(AscomClass):
    CAMERA_STATES: list[str] = ["CameraIdle", "CameraWaiting", "CameraExposing", "CameraReading",
                                "CameraDownload", "CameraError"]
    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.signals = parent.signals
        super().__init__(parent=parent)

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        self.getAndStoreAscomProperty("CameraXSize", "CCD_INFO.CCD_MAX_X")
        self.getAndStoreAscomProperty("CameraYSize", "CCD_INFO.CCD_MAX_Y")
        self.getAndStoreAscomProperty("CanFastReadout", "CAN_FAST")
        self.getAndStoreAscomProperty("CanAbortExposure", "CAN_ABORT")
        self.getAndStoreAscomProperty("CanSetCCDTemperature", "CAN_SET_CCD_TEMPERATURE")
        self.getAndStoreAscomProperty("CanGetCoolerPower", "CAN_GET_COOLER_POWER")
        self.getAndStoreAscomProperty("PixelSizeX", "CCD_INFO.CCD_PIXEL_SIZE_X")
        self.getAndStoreAscomProperty("PixelSizeY", "CCD_INFO.CCD_PIXEL_SIZE_Y")
        self.getAndStoreAscomProperty("MaxBinX", "CCD_BINNING.HOR_BIN_MAX")
        self.getAndStoreAscomProperty("MaxBinY", "CCD_BINNING.VERT_BIN_MAX")
        self.getAndStoreAscomProperty("GainMax", "CCD_GAIN.GAIN_MAX")
        self.getAndStoreAscomProperty("GainMin", "CCD_GAIN.GAIN_MIN")
        self.getAndStoreAscomProperty("Gains", "CCD_GAIN.GAIN_LIST")
        self.getAndStoreAscomProperty("OffsetMax", "CCD_OFFSET.OFFSET_MAX")
        self.getAndStoreAscomProperty("OffsetMin", "CCD_OFFSET.OFFSET_MIN")
        self.getAndStoreAscomProperty("Offsets", "CCD_OFFSET.OFFSET_LIST")
        self.getAndStoreAscomProperty("StartX", "CCD_FRAME.X")
        self.getAndStoreAscomProperty("StartY", "CCD_FRAME.Y")
        self.log.debug(f"Initial data: {self.data}")

    def saveImage(self):
        if not self.getAscomProperty("ImageReady"):
            timeLeft = 1
            text = f"expose {timeLeft:3.0f} s"
            self.signals.message.emit(text)
            return

        self.signals.exposed.emit(self.parent.imagePath)
        self.signals.message.emit("download")
        data = self.getAscomProperty("ImageArray")
        data = np.array(data, dtype=np.uint16).transpose()
        self.signals.downloaded.emit(self.parent.imagePath)
        self.signals.message.emit("saving")
        hdu = fits.PrimaryHDU(data=data)
        hdu.writeto(self.parent.imagePath, overwrite=True)
        self.parent.writeImageFitsHeader()
        self.parent.exposeFinished()

    def pollData(self) -> None:
        super().pollData()
        self.getAndStoreAscomProperty("BinX", "CCD_BINNING.HOR_BIN")
        self.getAndStoreAscomProperty("BinY", "CCD_BINNING.VERT_BIN")
        self.getAndStoreAscomProperty("CameraState", "CAMERA.STATE")
        self.getAndStoreAscomProperty("Gain", "CCD_GAIN.GAIN")
        self.getAndStoreAscomProperty("Offset", "CCD_OFFSET.OFFSET")
        self.getAndStoreAscomProperty("FastReadout", "READOUT_QUALITY.QUALITY_LOW")
        self.getAndStoreAscomProperty(
            "CCDTemperature", "CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"
        )
        self.getAndStoreAscomProperty("CoolerOn", "CCD_COOLER.COOLER_ON")
        self.getAndStoreAscomProperty("CoolerPower", "CCD_COOLER_POWER.CCD_COOLER_VALUE")
        print(self.data["CAMERA.STATE"])
        # self.saveImage()

    def expose(self) -> None:
        self.setAscomPropertyQueued("BinX", self.parent.binning)
        self.setAscomPropertyQueued("BinY", self.parent.binning)
        self.setAscomPropertyQueued("StartX", self.parent.posXASCOM)
        self.setAscomPropertyQueued("StartY", self.parent.posYASCOM)
        self.setAscomPropertyQueued("NumX", self.parent.widthASCOM)
        self.setAscomPropertyQueued("NumY", self.parent.heightASCOM)
        if self.data.get("CAN_FAST", False):
            self.setAscomPropertyQueued("FastReadout", self.parent.fastReadout)
        self.callAscomMethodQueued("StartExposure", Duration=self.parent.exposureTime, Light=True)

    def abort(self) -> bool:
        if self.data.get("CAN_ABORT", False):
            self.callAscomMethodQueued("StopExposure")
        return True

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        self.setAscomPropertyQueued("CoolerOn", coolerOn)

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        if self.data.get("CAN_SET_CCD_TEMPERATURE", False):
            self.setAscomPropertyQueued("SetCCDTemperature", temperature)

    def sendOffset(self, offset: int = 0) -> None:
        self.setAscomPropertyQueued("Offset", offset)

    def sendGain(self, gain: int = 0) -> None:
        self.setAscomPropertyQueued("Gain", gain)
