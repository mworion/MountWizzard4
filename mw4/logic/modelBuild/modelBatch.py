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
import time
from pathlib import Path

# external packages
from PySide6.QtCore import Signal, QObject
from skyfield.api import Angle

# local imports
from base.transform import JNowToJ2000, J2000ToJNow
from gui.utilities.toolsQtWidget import sleepAndEvents


class ModelBatch(QObject):
    """
    """

    __all__ = ['ModelBatch']
    progres = Signal(object)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.msg = app.msg

        self.abortBatch: bool = False
        self.pauseBatch: bool = False
        self.endBatch: bool = False
        self.modelTiming: int = 0
        self.modelInputData: list = []
        self.modelBuildData: list = []
        self.modelName: str = ''
        self.imageDir: Path = Path('')
        self.exposureWaitTime: float = 0
        self.runTime: float = 0

        self.pointerSlew: int = 0
        self.pointerImage: int = 0
        self.pointerPlateSolve: int = 0
        self.pointerResult: int = 0

        self.mountSlewed: bool = False
        self.domeSlewed: bool = False

        # Signals handling exposing
        self.app.camera.signals.exposed.connect(self.setImageExposed)
        self.app.camera.signals.downloaded.connect(self.setImageDownloaded)
        self.app.camera.signals.saved.connect(self.setImageSaved)
        # Signals handling slewing
        self.app.mount.signals.slewed.connect(self.setMountSlewed)
        self.app.dome.signals.slewed.connect(self.setDomeSlewed)
        # Signals handling plate solving
        self.app.camera.signals.saved.connect(self.startNewPlateSolve)
        self.app.plateSolve.signals.result.connect(self.collectPlateSolveResult)

    def setImageExposed(self) -> None:
        """
        """
        imagePath = self.modelBuildData[self.pointerImage]['imagePath']
        self.app.showImage.emit(imagePath)
        if self.modelTiming == 2:
            self.startNewSlew()

    def setImageDownloaded(self):
        """
        """
        if self.modelTiming == 1:
            self.startNewSlew()

    def setImageSaved(self) -> None:
        """
        """
        if self.modelTiming == 0:
            self.startNewSlew()

    def setMountSlewed(self) -> None:
        """
        """
        self.mountSlewed = True
        if not self.app.deviceStat['dome']:
            self.startNewImageExposure()
            return
        if self.domeSlewed:
            self.startNewImageExposure()

    def setDomeSlewed(self) -> None:
        """
        """
        self.domeSlewed = True
        if self.mountSlewed:
            self.startNewImageExposure()

    def startNewSlew(self) -> None:
        """
        """
        self.pointerSlew += 1
        if self.pointerSlew >= len(self.modelBuildData):
            return
        if self.abortBatch or self.endBatch:
            return
        item = self.modelBuildData[self.pointerSlew]
        altitude = item['altitude']
        azimuth = item['azimuth']
        self.mountSlewed = False
        self.domeSlewed = False

        if not self.app.mount.obsSite.setTargetAltAz(altitude, azimuth):
            return
        if self.app.deviceStat['dome']:
            self.app.dome.slewDome(azimuth)
        self.app.mount.obsSite.startSlewing()

    def addMountDataToModelBuildData(self) -> None:
        """
        """
        item = self.modelBuildData[self.pointerImage]
        obs = self.app.mount.obsSite
        item['raJNowM'] = obs.raJNow
        item['decJNowM'] = obs.decJNow
        item['angularPosRA'] = obs.angularPosRA
        item['angularPosDEC'] = obs.angularPosDEC
        item['siderealTime'] = obs.timeSidereal
        item['julianDate'] = obs.timeJD
        item['pierside'] = obs.pierside
        raJ2000M, decJ2000M = JNowToJ2000(item['raJNowM'], item['decJNowM'], item['julianDate'])
        item['raJ2000M'] = raJ2000M
        item['decJ2000M'] = decJ2000M

    def startNewImageExposure(self) -> None:
        """
        """
        self.pointerImage += 1
        if self.abortBatch or self.endBatch:
            return

        waitTime = self.exposureWaitTime
        while self.pauseBatch or waitTime > 0:
            sleepAndEvents(500)
            waitTime -= 1

        item = self.modelBuildData[self.pointerImage]
        self.addMountDataToModelBuildData()

        cam = self.app.camera
        imagePath = item['imagePath']
        exposureTime = item['exposureTime'] = cam.exposureTime1
        binning = item['binning'] = cam.binning1

        self.app.camera.expose(imagePath, exposureTime, binning)

    def startNewPlateSolve(self) -> None:
        """
        """
        self.pointerPlateSolve += 1
        imagePath = self.modelBuildData[self.pointerPlateSolve]['imagePath']
        self.app.plateSolve.solve(imagePath)

    def sendModelProgress(self) -> None:
        """
        """
        fraction = (self.pointerResult + 1) / len(self.modelBuildData)
        secondsElapsed = time.time() - self.runTime
        secondsBase = secondsElapsed / fraction
        secondsEstimated = secondsBase * (1 - fraction)
        modelPercent = int(100 * fraction)

        progresData = {
            'count': len(self.modelBuildData),
            'modelPercent': modelPercent,
            'secondsElapsed': secondsElapsed,
            'secondsEstimated': secondsEstimated,
            'solved': self.pointerResult + 1,
        }
        self.progres.emit(progresData)

    def collectPlateSolveResult(self, result) -> None:
        """
        """
        self.pointerResult += 1
        item = self.modelBuildData[self.pointerResult]
        item.update(result)
        solved = result['success']

        if solved:
            raJNowS, decJNowS = J2000ToJNow(item['raJ2000S'], item['decJ2000S'], item['julianDate'])
            item['raJNowS'] = raJNowS
            item['decJNowS'] = decJNowS

        statusBuildPoint = 0 if solved else 2
        self.app.data.setStatusBuildP(self.pointerResult, statusBuildPoint)
        self.app.updatePointMarker.emit()
        self.sendModelProgress()

    def prepareModelBuildData(self) -> None:
        """
        """
        self.pointerSlew = -1
        self.pointerImage = -1
        self.pointerPlateSolve = -1
        self.pointerResult = -1
        self.modelBuildData.clear()
        for index, point in enumerate(self.modelInputData):
            modelItem = {}
            imagePath = f'{self.imageDir}/image-{index + 1:03d}.fits'
            modelItem['imagePath'] = imagePath
            modelItem['altitude'] = Angle(degrees=point[0])
            modelItem['azimuth'] = Angle(degrees=point[1])
            self.modelBuildData.append(modelItem)

    def run(self) -> None:
        """
        """
        if not self.modelInputData:
            return

        self.runTime = time.time()
        self.app.operationRunning.emit(1)
        self.prepareModelBuildData()
        self.startNewSlew()

        notFinished = self.pointerResult < len(self.modelBuildData)
        while not self.abortBatch and notFinished and not self.endBatch:
            sleepAndEvents(500)

        self.app.operationRunning.emit(0)

