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
from base.alpacaClass import AlpacaClass
from base.tpool import Worker


class CameraAlpaca(AlpacaClass):
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
        self.getAndStoreAlpacaProperty("cameraxsize", "CCD_INFO.CCD_MAX_X")
        self.getAndStoreAlpacaProperty("cameraysize", "CCD_INFO.CCD_MAX_Y")
        self.getAndStoreAlpacaProperty("canfastreadout", "CAN_FAST")
        self.getAndStoreAlpacaProperty("canabortexposure", "CAN_ABORT")
        self.getAndStoreAlpacaProperty("cansetccdtemperature", "CAN_SET_CCD_TEMPERATURE")
        self.getAndStoreAlpacaProperty("cangetcoolerpower", "CAN_GET_COOLER_POWER")
        self.getAndStoreAlpacaProperty("pixelsizex", "CCD_INFO.CCD_PIXEL_SIZE_X")
        self.getAndStoreAlpacaProperty("pixelsizey", "CCD_INFO.CCD_PIXEL_SIZE_Y")
        self.getAndStoreAlpacaProperty("maxbinx", "CCD_BINNING.HOR_BIN_MAX")
        self.getAndStoreAlpacaProperty("maxbiny", "CCD_BINNING.VERT_BIN_MAX")
        self.getAndStoreAlpacaProperty("gainmax", "CCD_GAIN.GAIN_MAX")
        self.getAndStoreAlpacaProperty("gainmin", "CCD_GAIN.GAIN_MIN")
        self.getAndStoreAlpacaProperty("gains", "CCD_GAIN.GAIN_LIST")
        self.getAndStoreAlpacaProperty("offsetmax", "CCD_OFFSET.OFFSET_MAX")
        self.getAndStoreAlpacaProperty("offsetmin", "CCD_OFFSET.OFFSET_MIN")
        self.getAndStoreAlpacaProperty("offsets", "CCD_OFFSET.OFFSET_LIST")
        self.getAndStoreAlpacaProperty("startx", "CCD_FRAME.X")
        self.getAndStoreAlpacaProperty("starty", "CCD_FRAME.Y")
        self.log.debug(f"Initial data: {self.data}")

    def workerPollData(self) -> None:
        """ """
        self.getAndStoreAlpacaProperty("binx", "CCD_BINNING.HOR_BIN")
        self.getAndStoreAlpacaProperty("biny", "CCD_BINNING.VERT_BIN")
        self.getAndStoreAlpacaProperty("camerastate", "CAMERA.STATE")
        self.getAndStoreAlpacaProperty("gain", "CCD_GAIN.GAIN")
        self.getAndStoreAlpacaProperty("offset", "CCD_OFFSET.OFFSET")
        self.getAndStoreAlpacaProperty("fastreadout", "READOUT_QUALITY.QUALITY_LOW")
        self.getAndStoreAlpacaProperty(
            "ccdtemperature", "CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"
        )
        self.getAndStoreAlpacaProperty("cooleron", "CCD_COOLER.COOLER_ON")
        self.getAndStoreAlpacaProperty("coolerpower", "CCD_COOLER_POWER.CCD_COOLER_VALUE")

    def sendDownloadMode(self) -> None:
        """ """
        if self.data.get("CAN_FAST", False):
            self.setAlpacaProperty("fastreadout", FastReadout=self.parent.fastReadout)

    def waitFunc(self) -> bool:
        """ """
        return not self.getAlpacaProperty("imageready")

    def workerExpose(self) -> None:
        """ """
        self.sendDownloadMode()
        self.setAlpacaProperty("binx", BinX=self.parent.binning)
        self.setAlpacaProperty("biny", BinY=self.parent.binning)
        self.setAlpacaProperty("startx", StartX=self.parent.posXASCOM)
        self.setAlpacaProperty("starty", StartY=self.parent.posYASCOM)
        self.setAlpacaProperty("numx", NumX=self.parent.widthASCOM)
        self.setAlpacaProperty("numy", NumY=self.parent.heightASCOM)
        self.setAlpacaProperty("startexposure", Duration=self.parent.exposureTime, Light=True)

        self.parent.waitExposed(self.parent.exposureTime, self.waitFunc)
        self.signals.exposed.emit()
        data = self.parent.retrieveImage(self.getAlpacaProperty, "imagearray")
        self.signals.downloaded.emit()
        self.signals.message.emit("saving")
        hdu = fits.PrimaryHDU(data=data)
        hdu.writeto(self.parent.imagePath, overwrite=True)
        self.parent.writeImageFitsHeader()

    def expose(self) -> None:
        """ """
        self.worker = Worker(self.workerExpose)
        self.worker.signals.finished.connect(self.parent.exposeFinished)
        self.threadPool.start(self.worker)

    def abort(self) -> bool:
        """ """
        if self.data.get("CAN_ABORT", False):
            self.getAlpacaProperty("stopexposure")
        return True

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        """ """
        self.setAlpacaProperty("cooleron", CoolerOn=coolerOn)

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        """ """
        if self.data.get("CAN_SET_CCD_TEMPERATURE", False):
            self.setAlpacaProperty("setccdtemperature", SetCCDTemperature=temperature)

    def sendOffset(self, offset: int = 0) -> None:
        """ """
        self.setAlpacaProperty("offset", Offset=offset)

    def sendGain(self, gain: int = 0) -> None:
        """ """
        self.setAlpacaProperty("gain", Gain=gain)
