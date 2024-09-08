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
# written in python3, (c) 2019-2024 by mworion
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
from base.driverDataClass import Signals
from base.fitsHeader import writeHeaderCamera, writeHeaderPointing

from logic.camera.cameraIndi import CameraIndi
from logic.camera.cameraAlpaca import CameraAlpaca
if platform.system() == 'Windows':
    from logic.camera.cameraAscom import CameraAscom
    from logic.camera.cameraSGPro import CameraSGPro
    from logic.camera.cameraNINA import CameraNINA


class Camera:
    """
    """
    __all__ = ['Camera']

    log = logging.getLogger('MW4')

    def __init__(self, app):
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data = {}
        self.exposing = False
        self.fastReadout = False
        self.imagePath = ''
        self.exposureTime = 1
        self.focalLength = 1 
        self.framework = ''
        self.defaultConfig = {'framework': '', 'frameworks': {}}
        self.obsSite = None

        self._binning = 1
        self._subFrame = 100
        self._posX = 0
        self._posY = 0
        self._width = 100
        self._height = 100
        self._posXASCOM = 0
        self._posYASCOM = 0
        self._widthASCOM = 100
        self._heightASCOM = 100
        
        self.run = {
            'indi': CameraIndi(self),
            'alpaca': CameraAlpaca(self),
        }
        if platform.system() == 'Windows':
            self.run['nina'] = CameraNINA(self)
            self.run['sgpro'] = CameraSGPro(self)
            self.run['ascom'] = CameraAscom(self)

        for fw in self.run:
            self.defaultConfig['frameworks'].update({fw: self.run[fw].defaultConfig})

        self.signals.deviceDisconnected.connect(self.abort)
        self.signals.serverDisconnected.connect(self.abort)
        self.app.mount.signals.pointDone.connect(self.setObsSite)

    @property
    def updateRate(self):
        return self.run[self.framework].updateRate

    @updateRate.setter
    def updateRate(self, value):
        value = int(value)
        for fw in self.run:
            self.run[fw].updateRate = value

    @property
    def loadConfig(self):
        return self.run[self.framework].loadConfig

    @loadConfig.setter
    def loadConfig(self, value):
        value = bool(value)
        for fw in self.run:
            self.run[fw].loadConfig = value

    @property
    def binning(self):
        return self._binning

    @binning.setter
    def binning(self, value):
        if 1 <= value <= 4 and'CCD_BINNING.HOR_BIN' in self.data:
            self._binning = int(value)
        else:
            self._binning = 1
        self.subFrame(self._subFrame) 
        
    @property
    def subFrame(self):
        return self._subFrame 

    @subFrame.setter
    def subFrame(self, value):
        maxX = self.data.get('CCD_INFO.CCD_MAX_X', 0)
        maxY = self.data.get('CCD_INFO.CCD_MAX_Y', 0) 
        if 10 <= value <= 100:
            self._width = int(maxX * value / 100)
            self._height = int(maxY * value / 100)
            self._posX = int((maxX - width) / 2)
            self._posY = int((maxY - height) / 2)
            self._widthASCOM = int(maxX * value / 100 / self._binning)
            self._heightASCOM = int(maxY * value / 100 / self._binning)
            self._posXASCOM = int((maxX - width) / 2 / self._binning)
            self._posYASCOM = int((maxY - height) / 2 / self._binning)
            self._subFrame = value
        else:
            self._width = maxX
            self._height = maxY
            self._posX = 0
            self._posY = 0 
            self._widthASCOM = int(maxX / self._binning)
            self._heightASCOM = int(maxY / self._binning)
            self._posXASCOM = 0
            self._posYASCOM = 0 
            self._subFrame = 100

    def setObsSite(self, obsSite):
        """
        """
        self.obsSite = obsSite

    def startCommunication(self) -> bool:
        """
        """
        return self.run[self.framework].startCommunication()

    def stopCommunication(self) -> bool:
        """
        """
        return self.run[self.framework].stopCommunication()

    def exposeFinished(self) -> bool:
        """
        """
        self.exposing = False
        self.signals.saved.emit(self.imagePath)
        self.signals.exposeReady.emit()
        self.signals.message.emit('')

    def expose(self,
               imagePath: Path = '',
               expTime: float = 3,
               binning: int = 1,
               subFrame: int = 100,
               fastReadout: bool = True,
               focalLength: int = 1,
               ra=None,
               dec=None) -> bool:
        """
        """
        if self.exposing:
            return False
            
        self.exposing = True
        self.imagePath = imagePath
        self.expTime = expTime
        self.binning = binning
        self.subFrame = subFrame
        self.fastReadout = fastReadout
        self.signals.message.emit('exposing')
        self.run[self.framework].expose()
        return True

    def abort(self) -> bool:
        """
        """
        self.signals.message.emit('')
        self.run[self.framework].abort()
        self.exposing = False  

    def sendDownloadMode(self) -> None:
        """
        """
        self.run[self.framework].sendDownloadMode()

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        """
        """
        self.run[self.framework].sendCoolerSwitch(coolerOn=coolerOn)

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        """
        """
        self.run[self.framework].sendCoolerTemp(temperature=temperature)

    def sendOffset(self, offset: int = 0) -> None:
        """
        """
        self.run[self.framework].sendOffset(offset=offset)

    def sendGain(self, gain: int = 0) -> None:
        """
        """
        self.run[self.framework].sendGain(gain=gain)

    def waitExposed(self, expTime: float, func: Callable) -> None: 
        """
        """
        timeLeft = expTime
        while self.exposing and func:
            text = f'expose {timeLeft:3.0f} s'
            sleepAndEvents(100)
            self.signals.message.emit(text)
            if timeLeft >= 0.1:
                timeLeft -= 0.1
            else:
                timeLeft = 0

    def waitStart(self) -> None:
        """
        """
        while self.exposing and 'integrating' not in self.data.get('Device.Message'):
            sleepAndEvents(100)

    def waitDownload(self) -> None:
        """
        """
        self.signals.message.emit('download')
        while self.exposing and 'downloading' in self.data.get('Device.Message'):
            sleepAndEvents(100)

    def waitSave(self) -> None:
        """
        """
        self.signals.message.emit('saving')
        while self.exposing and 'image is ready' in self.data.get('Device.Message'):
            sleepAndEvents(100)

    def waitFinish(self, function: Callable, param: dict) -> None:
        """
        """
        while self.exposing and not function(param):
            sleepAndEvents(100)
 
    def retrieveImage(self, function: Callable, param: dict) -> np.array:
        """
        """
        if not self.exposing:
            return np.array([], dtype=np.uint16)

        self.signals.message.emit('download')
        tmp = function(param)
        if tmp is None:
            self.exposing = False
            data = np.array([], dtype=np.uint16)
        else:
            data = np.array(tmp, dtype=np.uint16).transpose()
        return data
        
    def writeImageFitsHeader(self) -> None:
        """
        """
        with fits.open(self.imagePath, mode='update', output_verify='silentfix') as HDU:
            header = self.writeHeaderCamera(HDU[0].header, self)
            header = self.writeHeaderPointing(header, self)
 
    def updateImageFitsHeaderPointing(self) -> None:
        """
        """
        with fits.open(self.imagePath, mode='update', output_verify='silentfix') as HDU:
            header = self.writeHeaderPointing(HDU[0].header, self)

