############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from astropy.io import fits

# local imports
from base.tpool import Worker
from base.ascomClass import AscomClass


class CameraAscom(AscomClass):
    """ """

    def __init__(self, parent):
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.signals = parent.signals
        self.worker: Worker = None
        super().__init__(parent=parent)

    def workerGetInitialConfig(self) -> None:
        """ """
        super().workerGetInitialConfig()
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

    def workerPollData(self) -> None:
        """ """
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

    def sendDownloadMode(self) -> None:
        """ """
        if self.data.get("CAN_FAST", False):
            self.setAscomProperty("FastReadout", self.parent.fastReadout)

    def waitFunc(self) -> bool:
        """ """
        return not self.getAscomProperty("ImageReady")

    def workerExpose(self) -> None:
        """ """
        self.sendDownloadMode()
        self.setAscomProperty("BinX", self.parent.binning)
        self.setAscomProperty("BinY", self.parent.binning)
        self.setAscomProperty("StartX", self.parent.posXASCOM)
        self.setAscomProperty("StartY", self.parent.posYASCOM)
        self.setAscomProperty("NumX", self.parent.widthASCOM)
        self.setAscomProperty("NumY", self.parent.heightASCOM)
        self.client.StartExposure(self.parent.exposureTime, True)
        self.parent.waitExposed(self.parent.exposureTime, self.waitFunc)
        self.signals.exposed.emit()
        data = self.parent.retrieveImage(self.getAscomProperty, "ImageArray")
        self.signals.downloaded.emit()
        self.signals.message.emit("saving")
        hdu = fits.PrimaryHDU(data=data)
        hdu.writeto(self.parent.imagePath, overwrite=True)
        self.parent.writeImageFitsHeader()

    def expose(self) -> None:
        """ """
        self.worker = Worker(self.callerInitUnInit, self.workerExpose)
        self.worker.signals.finished.connect(self.parent.exposeFinished)
        self.threadPool.start(self.worker)

    def abort(self) -> bool:
        """ """
        if self.data.get("CAN_ABORT", False):
            self.callMethodThreaded(self.client.StopExposure)
        return True

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        """ """
        self.setAscomProperty("CoolerOn", coolerOn)

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        """ """
        if self.data.get("CAN_SET_CCD_TEMPERATURE", False):
            self.setAscomProperty("SetCCDTemperature", temperature)

    def sendOffset(self, offset: int = 0) -> None:
        """ """
        self.setAscomProperty("Offset", offset)

    def sendGain(self, gain: int = 0) -> None:
        """ """
        self.setAscomProperty("Gain", gain)
