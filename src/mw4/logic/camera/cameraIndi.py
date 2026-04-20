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
from mw4.base.tpool import Worker
from typing import Any


class CameraIndi(IndiClass):
    THRESHOLD = 0.00001
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.signals = parent.signals
        self.worker: Worker | None = None

    def setUpdateConfig(self, deviceName: str) -> None:
        self.txQueue.put((deviceName, "FITS_HEADER", {"FITS_OBJECT": "Skymodel"}))
        self.txQueue.put((deviceName, "FITS_HEADER", {"FITS_OBSERVER": "MountWizzard4"}))
        self.txQueue.put((deviceName, "ACTIVE_DEVICES", {"ACTIVE_TELESCOPE": "LX200 10micron"}))
        self.txQueue.put((deviceName, "TELESCOPE_TYPE", {"TELESCOPE_PRIMARY": "On"}))
        # toDo: Blob management detail

    def setExposureState(self, rxVector: dict) -> None:
        if not rxVector.get("CCD_EXPOSURE"):
            return
        value = rxVector["CCD_EXPOSURE"]["members"]["CCD_EXPOSURE_VALUE"]["floatvalue"]
        state = rxVector["CCD_EXPOSURE"]["state"]
        print("setExposureState", value, state)
        if state == "Busy" and value > 0:
            self.signals.message.emit(f"expose {value:2.0f} s")
        elif state == "Busy" and value == 0:
            self.signals.exposed.emit(self.parent.imagePath)
        elif state == "Ok" and value == 0:
            self.signals.downloaded.emit(self.parent.imagePath)
            self.signals.message.emit("")
        elif state in ["Alert"]:
            self.signals.exposed.emit(self.parent.imagePath)
            self.signals.downloaded.emit(self.parent.imagePath)
            self.signals.saved.emit(self.parent.imagePath)
            self.signals.message.emit("")
            self.abort()
            self.log.warning("INDI camera state alert")

    def setCanTemperature(self, rxVector: dict) -> None:
        if rxVector.get("CCD_TEMPERATURE"):
            self.data["CAN_SET_CCD_TEMPERATURE"] = True

    def addGainLimits(self, rxVector: dict) -> None:
        gain = rxVector.get("CCD_GAIN")
        if not gain:
            return
        self.data["CCD_GAIN.GAIN_MIN"] = gain["members"].get("min", 0)
        self.data["CCD_GAIN.GAIN_MAX"] = gain["members"].get("max", 0)

    def addOffsetLimits(self, rxVector: dict) -> None:
        offset = rxVector.get("CCD_OFFSET")
        if not offset:
            return
        self.data["CCD_OFFSET.OFFSET_MIN"] = offset["members"].get("min", 0)
        self.data["CCD_OFFSET.OFFSET_MAX"] = offset["members"].get("max", 0)

    def writeDeviceData(self, rxVector: dict) -> None:
        super().writeDeviceData(rxVector)
        self.addGainLimits(rxVector)
        self.addOffsetLimits(rxVector)
        self.setCanTemperature(rxVector)
        self.setExposureState(rxVector)

    def workerSaveBLOB(self, data: dict) -> None:
        self.parent.exposeFinished()

    def expose(self) -> bool:
        self.txQueue.put((self.deviceName, "READOUT_QUALITY", {"QUALITY_LOW": "On"}))
        self.txQueue.put((self.deviceName, "CCD_BINNING", {"HOR_BIN": self.parent.binning,
                                                           "VER_BIN": self.parent.binning}))
        self.txQueue.put((self.deviceName, "CCD_FRAME", {"X": self.parent.posX,
                                                         "Y": self.parent.posY,
                                                         "WIDTH": self.parent.width,
                                                         "HEIGHT": self.parent.height}))
        self.txQueue.put((self.deviceName, "CCD_EXPOSURE", {"CCD_EXPOSURE_VALUE": self.parent.exposureTime}))

    def abort(self) -> bool:
        self.txQueue.put((self.deviceName, "CCD_ABORT_EXPOSURE", {"ABORT": "On"}))

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        self.txQueue.put((self.deviceName, "CCD_COOLER", {"COOLER_ON": "On" if coolerOn else "Off"}))

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        self.txQueue.put((self.deviceName, "CCD_TEMPERATURE", {"CCD_TEMPERATURE_VALUE": temperature}))

    def sendOffset(self, offset: int = 0) -> None:
        self.txQueue.put((self.deviceName, "CCD_OFFSET", {"OFFSET": offset}))

    def sendGain(self, gain: int = 0) -> None:
        self.txQueue.put((self.deviceName, "CCD_GAIN", {"GAIN": gain}))
