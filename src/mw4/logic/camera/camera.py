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
import logging
import platform
from astropy.io import fits
from mw4.base.signalsDevices import Signals
from mw4.logic.camera.cameraAlpaca import CameraAlpaca
from mw4.logic.camera.cameraIndi import CameraIndi
from mw4.logic.fits.fitsFunction import writeHeaderCamera, writeHeaderPointing
from pathlib import Path
from typing import Any

if platform.system() == "Windows":
    from mw4.logic.camera.cameraAscom import CameraAscom


class Camera:
    log = logging.getLogger("MW4")
    DEVICE_TYPE: str = "camera"

    def __init__(self, app: Any) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        self.exposing: bool = False
        self.fastReadout: bool = False
        self.imagePath: Path = Path()
        self.exposureTime: float = 1
        self.exposureTime1: float = 1
        self.exposureTimeN: float = 1
        self.binning1: int = 1
        self.binningN: int = 1
        self.focalLength: int = 1
        self.framework: str = ""
        self._binning: int = 1
        self._subFrame: int = 100
        self.posX: int = 0
        self.posY: int = 0
        self.width: int = 100
        self.height: int = 100
        self.posXASCOM: int = 0
        self.posYASCOM: int = 0
        self.widthASCOM: int = 100
        self.heightASCOM: int = 100

        self.run = {
            "indi": CameraIndi(self),
            "alpaca": CameraAlpaca(self),
        }
        if platform.system() == "Windows":
            self.run["ascom"] = CameraAscom(self)

    @property
    def binning(self) -> int:
        return self._binning

    @binning.setter
    def binning(self, value: int) -> None:
        value = int(value)
        if (1 <= value <= 4) and "CCD_BINNING.HOR_BIN" in self.data:
            self._binning = value
        else:
            self._binning = 1
        self.subFrame = self._subFrame

    @property
    def subFrame(self) -> int:
        return self._subFrame

    @subFrame.setter
    def subFrame(self, value: int) -> None:
        maxX = int(self.data.get("CCD_INFO.CCD_MAX_X", 0))
        maxY = int(self.data.get("CCD_INFO.CCD_MAX_Y", 0))
        if 10 <= value < 100:
            self._subFrame = value
            self.width = int(maxX * self._subFrame / 100)
            self.height = int(maxY * self._subFrame / 100)
            self.posX = int((maxX - self.width) / 2)
            self.posY = int((maxY - self.height) / 2)
            self.widthASCOM = int(maxX * self._subFrame / 100 / self._binning)
            self.heightASCOM = int(maxY * self._subFrame / 100 / self._binning)
            self.posXASCOM = int((maxX - self.width) / 2 / self._binning)
            self.posYASCOM = int((maxY - self.height) / 2 / self._binning)
        else:
            self._subFrame = 100
            self.width = maxX
            self.height = maxY
            self.posX = 0
            self.posY = 0
            self.widthASCOM = int(maxX / self._binning)
            self.heightASCOM = int(maxY / self._binning)
            self.posXASCOM = 0
            self.posYASCOM = 0

    def startCommunication(self) -> None:
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()

    def exposeFinished(self) -> None:
        self.exposing = False
        self.signals.message.emit("")
        self.signals.saved.emit(self.imagePath)
        self.app.showImage.emit(self.imagePath)

    def expose(self, imagePath: Path, exposureTime: float = 1, binning: int = 1) -> bool:
        if self.exposing:
            return False

        self.exposing = True
        self.imagePath = imagePath
        self.exposureTime = exposureTime
        self.binning = binning
        self.signals.message.emit(f"expose {self.exposureTime:3.0f} s")
        self.run[self.framework].expose()
        return True

    def abort(self) -> bool:
        if self.run[self.framework].abort():
            self.signals.message.emit("")
            self.exposing = False
            return True
        else:
            return False

    def sendDownloadMode(self) -> None:
        self.run[self.framework].sendDownloadMode()

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        self.run[self.framework].sendCoolerSwitch(coolerOn=coolerOn)

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        self.run[self.framework].sendCoolerTemp(temperature=temperature)

    def sendOffset(self, offset: int = 0) -> None:
        self.run[self.framework].sendOffset(offset=offset)

    def sendGain(self, gain: int = 0) -> None:
        self.run[self.framework].sendGain(gain=gain)

    def writeImageFitsHeader(self) -> None:
        with fits.open(self.imagePath, mode="update", output_verify="silentfix") as HDU:
            header = writeHeaderCamera(HDU[0].header, self)
            header = writeHeaderPointing(header, self)
            HDU[0].header = header

    def updateImageFitsHeaderPointing(self) -> None:
        with fits.open(self.imagePath, mode="update", output_verify="silentfix") as HDU:
            header = writeHeaderPointing(HDU[0].header, self)
            HDU[0].header = header
