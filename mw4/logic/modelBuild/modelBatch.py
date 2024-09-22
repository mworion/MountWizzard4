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
    statusModel = Signal(object)

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.abortBatch: bool = False
        self.pauseBatch: bool = False
        self.progressiveTiming: bool = False
        self.normalTiming: bool = False
        self.modelInputData: list = []
        self.modelBuildData: list = []
        self.modelName: str = ''
        self.imageDir: Path = Path('')
        self.exposureWaitTime: float = 0

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
        self.app.plateSolve.signals.saved.connect(self.startNewPlateSolve)

    def setImageExposed(self) -> None:
        """
        """
        imagePath = self.modelInputData[self.pointerImage]['imagePath']
        self.app.showImage.emit(imagePath)
        if self.progressiveTiming:
            self.startNewSlew()

    def setImageDownloaded(self):
        """
        """
        if self.normalTiming:
            self.startNewSlew()

    def setImageSaved(self) -> None:
        """
        """
        if not self.progressiveTiming and not self.normalTiming:
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
        altitude = self.modelInputData[self.pointerSlew]['altitude']
        azimuth = self.modelInputData[self.pointerSlew]['azimuth']
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
        item['raJ2000M'], item['decJ2000M'] = JNowToJ2000(item['raJNowM'],
                                                          item['decJNowM'],
                                                          item['julianDate'])

    def startNewImageExposure(self) -> None:
        """
        """
        self.pointerImage += 1

        waitTime = self.exposureWaitTime
        while self.pauseBatch or waitTime > 0:
            sleepAndEvents(500)
            waitTime -= 1

        imagePath = self.modelInputData[self.pointerImage]['imagePath']
        exposureTime = self.modelInputData[self.pointerImage]['exposureTime']
        binning = self.modelInputData[self.pointerImage]['binning']
        self.addMountDataToModelBuildData()
        self.app.camera.expose(imagePath, exposureTime, binning)

    def startNewPlateSolve(self) -> None:
        """
        """
        self.pointerPlateSolve += 1
        imagePath = self.modelInputData[self.pointerPlateSolve]['imagePath']
        self.app.plateSolve.solve(imagePath)

    def collectPlateSolveResult(self, result) -> None:
        """
        """
        self.pointerResult += 1
        item = self.modelBuildData[self.pointerResult]
        item.update(result)
        raJNowS, decJNowS = J2000ToJNow(item['raJ2000S'], item['decJ2000S'], item['julianDate'])
        item['raJNowS'] = raJNowS
        item['decJNowS'] = decJNowS

        statusBuildPoint = 2 if result['success'] else 0
        self.app.data.setStatusBuildP(self.pointerResult, statusBuildPoint)
        self.app.updatePointMarker.emit()

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
            modelItem['exposureTime'] = imagePath
            modelItem['binning'] = imagePath
            modelItem['altitude'] = Angle(degrees=point[0])
            modelItem['azimuth'] = Angle(degrees=point[1])

    def runBatch(self):
        """
        """
        if not self.modelInputData:
            return False

        self.prepareModelBuildData()
        self.startNewSlew()


