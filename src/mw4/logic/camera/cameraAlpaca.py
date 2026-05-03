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
from astropy.io import fits
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.tpool import Worker
from typing import Any


class CameraAlpaca(AlpacaClass):
    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.signals = parent.signals
        self.worker: Worker | None = None
        super().__init__(parent=parent)

    def workerGetInitialConfig(self) -> None:
        super().workerGetInitialConfig()
        self.getAndStoreDeviceProp("CameraXSize", "CCD_INFO.CCD_MAX_X")
        self.getAndStoreDeviceProp("CameraYSize", "CCD_INFO.CCD_MAX_Y")
        self.getAndStoreDeviceProp("CanFastReadout", "CAN_FAST")
        self.getAndStoreDeviceProp("CanAbortExposure", "CAN_ABORT")
        self.getAndStoreDeviceProp("CanSetCCDTemperature", "CAN_SET_CCD_TEMPERATURE")
        self.getAndStoreDeviceProp("CanGetCoolerPower", "CAN_GET_COOLER_POWER")
        self.getAndStoreDeviceProp("PixelSizeX", "CCD_INFO.CCD_PIXEL_SIZE_X")
        self.getAndStoreDeviceProp("PixelSizeY", "CCD_INFO.CCD_PIXEL_SIZE_Y")
        self.getAndStoreDeviceProp("MaxBinX", "CCD_BINNING.HOR_BIN_MAX")
        self.getAndStoreDeviceProp("MaxBinY", "CCD_BINNING.VERT_BIN_MAX")
        self.getAndStoreDeviceProp("GainMax", "CCD_GAIN.GAIN_MAX")
        self.getAndStoreDeviceProp("GainMin", "CCD_GAIN.GAIN_MIN")
        self.getAndStoreDeviceProp("Gains", "CCD_GAIN.GAIN_LIST")
        self.getAndStoreDeviceProp("OffsetMax", "CCD_OFFSET.OFFSET_MAX")
        self.getAndStoreDeviceProp("OffsetMin", "CCD_OFFSET.OFFSET_MIN")
        self.getAndStoreDeviceProp("Offsets", "CCD_OFFSET.OFFSET_LIST")
        self.getAndStoreDeviceProp("StartX", "CCD_FRAME.X")
        self.getAndStoreDeviceProp("StartY", "CCD_FRAME.Y")
        self.log.debug(f"Initial data: {self.data}")

    def workerPollData(self) -> None:
        self.getAndStoreDeviceProp("BinX", "CCD_BINNING.HOR_BIN")
        self.getAndStoreDeviceProp("BinY", "CCD_BINNING.VERT_BIN")
        self.getAndStoreDeviceProp("CameraState", "CAMERA.STATE")
        self.getAndStoreDeviceProp("Gain", "CCD_GAIN.GAIN")
        self.getAndStoreDeviceProp("Offset", "CCD_OFFSET.OFFSET")
        self.getAndStoreDeviceProp("FastReadout", "READOUT_QUALITY.QUALITY_LOW")
        self.getAndStoreDeviceProp("CCDTemperature", "CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE")
        self.getAndStoreDeviceProp("CoolerOn", "CCD_COOLER.COOLER_ON")
        self.getAndStoreDeviceProp("CoolerPower", "CCD_COOLER_POWER.CCD_COOLER_VALUE")

    def sendDownloadMode(self) -> None:
        if self.data.get("CAN_FAST", False):
            self.setDeviceProp("FastReadout", self.parent.fastReadout)

    def waitFunc(self) -> bool:
        return not self.getDeviceProp("ImageReady")

    def getImageArray(self, _: str = "") -> Any:
        return self.getDeviceProp("ImageArray")

    def workerExpose(self) -> None:
        self.sendDownloadMode()
        self.setDeviceProp("BinX", self.parent.binning)
        self.setDeviceProp("BinY", self.parent.binning)
        self.setDeviceProp("StartX", self.parent.posXASCOM)
        self.setDeviceProp("StartY", self.parent.posYASCOM)
        self.setDeviceProp("NumX", self.parent.widthASCOM)
        self.setDeviceProp("NumY", self.parent.heightASCOM)
        self.callDeviceMethod(
            "StartExposure",
            Duration=self.parent.exposureTime,
            Light=True,
        )

        self.parent.waitExposed(self.parent.exposureTime, self.waitFunc)
        self.signals.exposed.emit(self.parent.imagePath)
        data = self.parent.retrieveImage(self.getImageArray, "")
        self.signals.downloaded.emit(self.parent.imagePath)
        self.signals.message.emit("saving")
        hdu = fits.PrimaryHDU(data=data)
        hdu.writeto(self.parent.imagePath, overwrite=True)
        self.parent.writeImageFitsHeader()

    def expose(self) -> None:
        self.worker = Worker(self.workerExpose)
        self.worker.signals.finished.connect(self.parent.exposeFinished)
        self.threadPool.start(self.worker)

    def abort(self) -> bool:
        if self.data.get("CAN_ABORT", False):
            self.callDeviceMethod("StopExposure")
        return True

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        self.setDeviceProp("CoolerOn", coolerOn)

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        if self.data.get("CAN_SET_CCD_TEMPERATURE", False):
            self.setDeviceProp("SetCCDTemperature", temperature)

    def sendOffset(self, offset: int = 0) -> None:
        self.setDeviceProp("Offset", offset)

    def sendGain(self, gain: int = 0) -> None:
        self.setDeviceProp("Gain", gain)
