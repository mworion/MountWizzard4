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
import logging
import platform
from typing import Callable
from pathlib import Path

# external packages
from astropy.io import fits
import numpy as np

# local imports
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.signalsDevices import Signals
from logic.fits.fitsFunction import writeHeaderCamera, writeHeaderPointing
from logic.camera.cameraIndi import CameraIndi
from logic.camera.cameraAlpaca import CameraAlpaca

if platform.system() == "Windows":
    from logic.camera.cameraAscom import CameraAscom
    from logic.camera.cameraSGPro import CameraSGPro
    from logic.camera.cameraNINA import CameraNINA


class Camera:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, app):
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict = {}
        self.loadConfig: bool = True
        self.updateRate: int = 1000
        self.deviceType: str = ""
        self.exposing: bool = False
        self.fastReadout: bool = False
        self.imagePath: Path = Path("")
        self.exposureTime: float = 1
        self.exposureTime1: float = 1
        self.exposureTimeN: float = 1
        self.binning1: int = 1
        self.binningN: int = 1
        self.focalLength: int = 1
        self.framework: str = ""
        self.defaultConfig: dict = {"framework": "", "frameworks": {}}
        self.obsSite = None

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
            self.run["nina"] = CameraNINA(self)
            self.run["sgpro"] = CameraSGPro(self)
            self.run["ascom"] = CameraAscom(self)

        for fw in self.run:
            self.defaultConfig["frameworks"].update({fw: self.run[fw].defaultConfig})

        self.app.mount.signals.pointDone.connect(self.setObsSite)

    @property
    def binning(self):
        return self._binning

    @binning.setter
    def binning(self, value: int):
        value = int(value)
        if (1 <= value <= 4) and "CCD_BINNING.HOR_BIN" in self.data:
            self._binning = value
        else:
            self._binning = 1
        self.subFrame = self._subFrame

    @property
    def subFrame(self):
        return self._subFrame

    @subFrame.setter
    def subFrame(self, value: int):
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

    def setObsSite(self, obsSite):
        """ """
        self.obsSite = obsSite

    def startCommunication(self) -> None:
        """ """
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        """ """
        self.run[self.framework].stopCommunication()

    def exposeFinished(self) -> bool:
        """ """
        self.exposing = False
        self.signals.saved.emit(self.imagePath)
        self.signals.exposed.emit()
        self.signals.message.emit("")

    def expose(self, imagePath: Path = "", exposureTime: float = 1, binning: int = 1) -> bool:
        """ """
        if self.exposing:
            return False

        self.imagePath = imagePath
        self.exposureTime = exposureTime
        self.binning = binning
        self.exposing = True
        self.signals.message.emit("exposing")
        self.run[self.framework].expose()
        return True

    def abort(self) -> None:
        """ """
        self.signals.message.emit("")
        self.exposing = False
        self.run[self.framework].abort()

    def sendDownloadMode(self) -> None:
        """ """
        self.run[self.framework].sendDownloadMode()

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        """ """
        self.run[self.framework].sendCoolerSwitch(coolerOn=coolerOn)

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        """ """
        self.run[self.framework].sendCoolerTemp(temperature=temperature)

    def sendOffset(self, offset: int = 0) -> None:
        """ """
        self.run[self.framework].sendOffset(offset=offset)

    def sendGain(self, gain: int = 0) -> None:
        """ """
        self.run[self.framework].sendGain(gain=gain)

    def waitExposed(self, exposureTime: float, func: Callable) -> None:
        """ """
        timeLeft = exposureTime
        while self.exposing and func():
            text = f"expose {timeLeft:3.0f} s"
            sleepAndEvents(100)
            self.signals.message.emit(text)
            if timeLeft >= 0.1:
                timeLeft -= 0.1
            else:
                timeLeft = 0

    def waitStart(self) -> None:
        """ """
        while self.exposing and "integrating" not in self.data.get("Device.Message"):
            sleepAndEvents(100)

    def waitDownload(self) -> None:
        """ """
        self.signals.message.emit("download")
        while self.exposing and "downloading" in self.data.get("Device.Message"):
            sleepAndEvents(100)

    def waitSave(self) -> None:
        """ """
        self.signals.message.emit("saving")
        while self.exposing and "image is ready" in self.data.get("Device.Message"):
            sleepAndEvents(100)

    def waitFinish(self, function: Callable, param: dict) -> None:
        """ """
        while self.exposing and not function(param):
            sleepAndEvents(100)

    def retrieveImage(self, function: Callable, param: dict) -> np.array:
        """ """
        if not self.exposing:
            return np.array([], dtype=np.uint16)

        self.signals.message.emit("download")
        tmp = function(param)
        if tmp is None:
            self.exposing = False
            data = np.array([], dtype=np.uint16)
        else:
            data = np.array(tmp, dtype=np.uint16).transpose()
        return data

    def writeImageFitsHeader(self) -> None:
        """ """
        with fits.open(self.imagePath, mode="update", output_verify="silentfix") as HDU:
            header = writeHeaderCamera(HDU[0].header, self)
            header = writeHeaderPointing(header, self)
            HDU[0].header = header

    def updateImageFitsHeaderPointing(self) -> None:
        """ """
        with fits.open(self.imagePath, mode="update", output_verify="silentfix") as HDU:
            header = writeHeaderPointing(HDU[0].header, self)
            HDU[0].header = header
