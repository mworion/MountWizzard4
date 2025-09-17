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
import zlib

# external packages
from astropy.io import fits

# local imports
from base.tpool import Worker
from base.indiClass import IndiClass


class CameraIndi(IndiClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.signals = parent.signals
        self.worker: Worker = None
        self.isDownloading: bool = False
        self.loadConfig: bool = True

    def setUpdateConfig(self, deviceName: str) -> None:
        """ """
        suc = self.client.setBlobMode(blobHandling="Also", deviceName=deviceName)
        self.log.info(f"Blob mode [{deviceName}] success: [{suc}]")

        objectName = self.device.getText("FITS_HEADER")
        objectName["FITS_OBJECT"] = "Skymodel"
        objectName["FITS_OBSERVER"] = "MountWizzard4"
        suc = self.client.sendNewText(
            deviceName=deviceName, propertyName="FITS_HEADER", elements=objectName
        )
        self.log.info(f"Fits Header [{deviceName}] success: [{suc}]")

        telescope = self.device.getText("ACTIVE_DEVICES")
        telescope["ACTIVE_TELESCOPE"] = "LX200 10micron"
        suc = self.client.sendNewText(
            deviceName=deviceName, propertyName="ACTIVE_DEVICES", elements=telescope
        )
        self.log.info(f"Active telescope [{deviceName}] success: [{suc}]")

        telescope = self.device.getSwitch("TELESCOPE_TYPE")
        telescope["TELESCOPE_PRIMARY"] = "On"
        suc = self.client.sendNewSwitch(
            deviceName=deviceName, propertyName="TELESCOPE_TYPE", elements=telescope
        )
        self.log.info(f"Primary telescope [{deviceName}] success: [{suc}]")

    def setExposureState(self) -> bool:
        """
        setExposureState rebuilds the state information integrated and download
        as it is not explicit defined in the INDI spec. So downloaded is reached
        when that INDI state for CCD_EXPOSURE goes to IDLE or OK -> Jasem Mutlaq.
        Another definition is done by myself, when INDI state for CCD_EXPOSURE is
        BUSY and the CCD_EXPOSURE_VALUE is not 0, then we should be on integration
        side, else the download should be started. The whole stuff is made,
        because on ALPACA and ASCOM side it's a step by step sequence, which has
        very defined states for each step. I would like ta have a common
        approach for all frameworks.
        """
        THRESHOLD = 0.00001
        value = self.data.get("CCD_EXPOSURE.CCD_EXPOSURE_VALUE")
        if self.device.CCD_EXPOSURE["state"] == "Busy":
            if value is None:
                return False
            elif value <= THRESHOLD:
                if not self.isDownloading:
                    self.signals.exposed.emit()
                self.isDownloading = True
                self.signals.message.emit("download")
            else:
                self.signals.message.emit(f"expose {value:2.0f} s")
        elif self.device.CCD_EXPOSURE["state"] in ["Idle", "Ok"]:
            self.signals.downloaded.emit()
            self.signals.message.emit("")
            self.isDownloading = False
        elif self.device.CCD_EXPOSURE["state"] in ["Alert"]:
            self.isDownloading = False
            self.signals.exposed.emit()
            self.signals.downloaded.emit()
            self.signals.saved.emit("")
            self.abort()
            self.log.warning("INDI camera state alert")
        else:
            t = f"[{self.deviceName}] state: [{self.device.CCD_EXPOSURE['state']}]"
            self.log.warning(t)

        return True

    def updateNumber(self, deviceName: str, propertyName: str) -> bool:
        """ """
        if propertyName == "CCD_GAIN":
            elements = self.device.CCD_GAIN["elementList"]["GAIN"]
            if "min" in elements and "max" in elements:
                self.data["CCD_GAIN.GAIN_MIN"] = elements.get("min", 0)
                self.data["CCD_GAIN.GAIN_MAX"] = elements.get("max", 0)

        if propertyName == "CCD_OFFSET":
            elements = self.device.CCD_OFFSET["elementList"]["OFFSET"]
            if "min" in elements and "max" in elements:
                self.data["CCD_OFFSET.OFFSET_MIN"] = elements.get("min", 0)
                self.data["CCD_OFFSET.OFFSET_MAX"] = elements.get("max", 0)

        if not super().updateNumber(deviceName, propertyName):
            return False

        if propertyName == "CCD_EXPOSURE":
            self.setExposureState()

        if propertyName == "CCD_TEMPERATURE":
            self.data["CAN_SET_CCD_TEMPERATURE"] = True
        return True

    def workerSaveBLOB(self, data: dict) -> None:
        """ """
        self.signals.message.emit("saving")

        if data["format"] == ".fits.fz":
            HDU = fits.HDUList.fromstring(data["value"])
            self.log.info("Image BLOB is in FPacked format")

        elif data["format"] == ".fits.z":
            HDU = fits.HDUList.fromstring(zlib.decompress(data["value"]))
            self.log.info("Image BLOB is compressed fits format")

        elif data["format"] == ".fits":
            HDU = fits.HDUList.fromstring(data["value"])
            self.log.info("Image BLOB is uncompressed fits format")

        else:
            self.log.info("Image BLOB is not supported")
            return

        fits.writeto(self.parent.imagePath, HDU[0].data, HDU[0].header, overwrite=True)
        self.parent.writeImageFitsHeader()

    def updateBLOB(self, deviceName: str, propertyName: str) -> bool:
        """ """
        if not super().updateBLOB(deviceName, propertyName):
            return False

        data = self.device.getBlob(propertyName)
        if "value" not in data:
            return False
        if "name" not in data:
            return False
        if "format" not in data:
            return False
        if data.get("name", "") != "CCD1":
            return False

        self.worker = Worker(self.workerSaveBLOB, data)
        self.worker.signals.finished.connect(self.parent.exposeFinished)
        self.threadPool.start(self.worker)
        return True

    def sendDownloadMode(self) -> None:
        """ """
        quality = self.device.getSwitch("READOUT_QUALITY")
        quality["QUALITY_LOW"] = "On"
        quality["QUALITY_HIGH"] = "Off"
        self.client.sendNewSwitch(
            deviceName=self.deviceName, propertyName="READOUT_QUALITY", elements=quality
        )

    def expose(self) -> bool:
        """ """
        self.sendDownloadMode()
        indiCmd = self.device.getNumber("CCD_BINNING")
        indiCmd["HOR_BIN"] = self.parent.binning
        indiCmd["VER_BIN"] = self.parent.binning
        self.client.sendNewNumber(
            deviceName=self.deviceName, propertyName="CCD_BINNING", elements=indiCmd
        )

        indiCmd = self.device.getNumber("CCD_FRAME")
        indiCmd["X"] = self.parent.posX
        indiCmd["Y"] = self.parent.posY
        indiCmd["WIDTH"] = self.parent.width
        indiCmd["HEIGHT"] = self.parent.height
        self.client.sendNewNumber(
            deviceName=self.deviceName, propertyName="CCD_FRAME", elements=indiCmd
        )

        indiCmd = self.device.getNumber("CCD_EXPOSURE")
        indiCmd["CCD_EXPOSURE_VALUE"] = self.parent.exposureTime
        return self.client.sendNewNumber(
            deviceName=self.deviceName, propertyName="CCD_EXPOSURE", elements=indiCmd
        )

    def abort(self) -> bool:
        """ """
        indiCmd = self.device.getSwitch("CCD_ABORT_EXPOSURE")
        if "ABORT" not in indiCmd:
            return False

        indiCmd["ABORT"] = "On"
        return self.client.sendNewSwitch(
            deviceName=self.deviceName,
            propertyName="CCD_ABORT_EXPOSURE",
            elements=indiCmd,
        )

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        """ """
        cooler = self.device.getSwitch("CCD_COOLER")
        cooler["COOLER_ON"] = "On" if coolerOn else "Off"
        cooler["COOLER_OFF"] = "Off" if coolerOn else "On"
        self.client.sendNewSwitch(
            deviceName=self.deviceName, propertyName="CCD_COOLER", elements=cooler
        )

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        """ """
        element = self.device.getNumber("CCD_TEMPERATURE")
        if "CCD_TEMPERATURE_VALUE" not in element:
            return

        element["CCD_TEMPERATURE_VALUE"] = temperature
        self.client.sendNewNumber(
            deviceName=self.deviceName, propertyName="CCD_TEMPERATURE", elements=element
        )

    def sendOffset(self, offset: int = 0) -> None:
        """ """
        element = self.device.getNumber("CCD_OFFSET")
        if "OFFSET" not in element:
            return

        element["OFFSET"] = offset
        self.client.sendNewNumber(
            deviceName=self.deviceName, propertyName="CCD_OFFSET", elements=element
        )

    def sendGain(self, gain: int = 0) -> None:
        """ """
        element = self.device.getNumber("CCD_GAIN")
        if "GAIN" not in element:
            return

        element["GAIN"] = gain
        self.client.sendNewNumber(
            deviceName=self.deviceName, propertyName="CCD_GAIN", elements=element
        )
