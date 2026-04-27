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
from mw4.base.indiClass import IndiClass
from pathlib import Path
from typing import Any


class CameraIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.signals = parent.signals

    def setUpdateConfig(self, deviceName: str) -> None:
        self.txQ.put((deviceName, "FITS_HEADER", {"FITS_OBJECT": "Skymodel"}))
        self.txQ.put((deviceName, "FITS_HEADER", {"FITS_OBSERVER": "MountWizzard4"}))
        self.txQ.put((deviceName, "ACTIVE_DEVICES", {"ACTIVE_TELESCOPE": "LX200 10micron"}))
        self.txQ.put((deviceName, "TELESCOPE_TYPE", {"TELESCOPE_PRIMARY": "On"}))

    def setExposureState(self, vectors: dict) -> None:
        if not vectors.get("CCD_EXPOSURE"):
            return
        value = vectors["CCD_EXPOSURE"]["members"]["CCD_EXPOSURE_VALUE"]["floatvalue"]
        state = vectors["CCD_EXPOSURE"]["state"]
        if state == "Busy" and value > 0:
            self.signals.message.emit(f"expose {value:2.0f} s")
        elif state == "Busy" and value == 0:
            self.signals.exposed.emit(self.parent.imagePath)
        elif state == "Ok" and value == 0:
            self.signals.downloaded.emit(self.parent.imagePath)
            self.signals.message.emit("")
        elif state in ["Alert"]:
            self.signals.exposed.emit(Path())
            self.signals.downloaded.emit(Path())
            self.parent.exposeFinished()
            self.abort()
            self.log.warning("INDI camera state alert")

    def setCanTemperature(self, vectors: dict) -> None:
        if vectors.get("CCD_TEMPERATURE"):
            self.data["CAN_SET_CCD_TEMPERATURE"] = True

    def addGainLimits(self, vectors: dict) -> None:
        gain = vectors.get("CCD_GAIN", {})
        if not gain:
            return
        self.data["CCD_GAIN.GAIN_MIN"] = gain["members"].get("min", 0)
        self.data["CCD_GAIN.GAIN_MAX"] = gain["members"].get("max", 1)

    def addOffsetLimits(self, vectors: dict) -> None:
        offset = vectors.get("CCD_OFFSET", {})
        if not offset:
            return
        self.data["CCD_OFFSET.OFFSET_MIN"] = offset["members"].get("min", 0)
        self.data["CCD_OFFSET.OFFSET_MAX"] = offset["members"].get("max", 1)

    def saveBLOB(self, vectors:dict) -> None:
        # todo: check if abort still send a blob
        blob = vectors.get("CCD1", {})
        if not blob:
            return 
        # todo: move file to target directory
        self.parent.writeImageFitsHeader()
        # todo: check if XISF will work
        self.parent.exposeFinished()

    def writeVectorsToData(self, vectors: dict) -> None:
        super().writeVectorsToData(vectors)
        self.addGainLimits(vectors)
        self.addOffsetLimits(vectors)
        self.setCanTemperature(vectors)
        self.setExposureState(vectors)
        self.saveBLOB(vectors)

    def sendDownloadMode(self) -> None:
        self.txQ.put((self.deviceName, "READOUT_QUALITY", {"QUALITY_LOW": "On"}))

    def expose(self) -> None:
        self.sendDownloadMode()
        self.txQ.put((self.deviceName, "READOUT_QUALITY", {"QUALITY_LOW": "On"}))
        self.txQ.put((self.deviceName, "CCD_BINNING", {"HOR_BIN": self.parent.binning,
                                                           "VER_BIN": self.parent.binning}))
        self.txQ.put((self.deviceName, "CCD_FRAME", {"X": self.parent.posX,
                                                       "Y": self.parent.posY,
                                                       "WIDTH": self.parent.width,
                                                       "HEIGHT": self.parent.height}))
        self.txQ.put((self.deviceName, "CCD_EXPOSURE", {"CCD_EXPOSURE_VALUE": self.parent.exposureTime}))

    def abort(self) -> None:
        self.txQ.put((self.deviceName, "CCD_ABORT_EXPOSURE", {"ABORT": "On"}))

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        self.txQ.put((self.deviceName, "CCD_COOLER", {"COOLER_ON": "On" if coolerOn else "Off"}))

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        self.txQ.put((self.deviceName, "CCD_TEMPERATURE", {"CCD_TEMPERATURE_VALUE": temperature}))

    def sendOffset(self, offset: int = 0) -> None:
        self.txQ.put((self.deviceName, "CCD_OFFSET", {"OFFSET": offset}))

    def sendGain(self, gain: int = 1) -> None:
        self.txQ.put((self.deviceName, "CCD_GAIN", {"GAIN": gain}))
