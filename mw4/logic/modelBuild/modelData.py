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
import time
import logging
import json
from pathlib import Path

# external packages
from PySide6.QtCore import Signal, QObject
from skyfield.api import Angle, Star

# local imports
from base.transform import JNowToJ2000, J2000ToJNow
from logic.modelBuild.modelHandling import convertAngleToFloat, writeRetrofitData
from gui.utilities.toolsQtWidget import sleepAndEvents
from mountcontrol.progStar import ProgStar


class ModelData(QObject):
    """ """

    log = logging.getLogger("MW4")
    progress = Signal(object)
    PROGRESSIVE = 2
    NORMAL = 1
    CONSERVATIVE = 0

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.cancelBatch: bool = False
        self.pauseBatch: bool = False
        self.endBatch: bool = False
        self.modelTiming: int = self.CONSERVATIVE
        self.modelInputData: list = []
        self.modelBuildData: list = []
        self.modelProgData: list = []
        self.modelSaveData: list = []
        self.modelName: str = ""
        self.imageDir: Path = Path("")
        self.latitude: float = 0
        self.version: str = ""
        self.firmware: str = ""
        self.profile: str = ""
        self.plateSolveApp: str = ""
        self.exposureWaitTime: float = 0
        self.runTime: float = 0
        self.numberRetries: int = 0

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
        """ """
        imagePath = self.modelBuildData[self.pointerImage]["imagePath"]
        self.app.showImage.emit(imagePath)
        if self.modelTiming == self.PROGRESSIVE:
            self.startNewSlew()

    def setImageDownloaded(self):
        """ """
        if self.modelTiming == self.NORMAL:
            self.startNewSlew()

    def setImageSaved(self) -> None:
        """ """
        if self.modelTiming == self.CONSERVATIVE:
            self.startNewSlew()

    def setMountSlewed(self) -> None:
        """ """
        self.mountSlewed = True
        if not self.app.deviceStat["dome"]:
            self.startNewImageExposure()
            return
        if self.domeSlewed:
            self.startNewImageExposure()

    def setDomeSlewed(self) -> None:
        """ """
        self.domeSlewed = True
        if self.mountSlewed:
            self.startNewImageExposure()

    def startNewSlew(self) -> None:
        """ """
        self.pointerSlew += 1
        if self.pointerSlew >= len(self.modelBuildData):
            return
        if self.cancelBatch or self.endBatch:
            return
        item = self.modelBuildData[self.pointerSlew]
        altitude = item["altitude"]
        azimuth = item["azimuth"]
        self.mountSlewed = False
        self.domeSlewed = False

        if not self.app.mount.obsSite.setTargetAltAz(altitude, azimuth):
            return
        if self.app.deviceStat["dome"]:
            self.app.dome.slewDome(azimuth)
        self.app.mount.obsSite.startSlewing()

    def addMountModelToBuildModel(self) -> None:
        """ """
        if len(self.app.mount.model.starList) == len(self.modelSaveData):
            self.modelSaveData = writeRetrofitData(self.app.mount.model, self.modelSaveData)
            self.modelSaveData = convertAngleToFloat(self.modelSaveData)
        else:
            self.log.warning("Error in model data: difference in length")
            self.modelSaveData = []

    def collectBuildModelResults(self) -> None:
        """ """
        self.modelSaveData.clear()
        for modelBuildPoint in self.modelBuildData:
            if not modelBuildPoint["success"]:
                continue

            modelSavePoint = dict()
            modelSavePoint.update(modelBuildPoint)
            modelSavePoint["julianDate"] = modelSavePoint["julianDate"]
            modelSavePoint["version"] = self.version
            modelSavePoint["profile"] = self.profile
            modelSavePoint["firmware"] = self.firmware
            modelSavePoint["latitude"] = self.latitude
            self.modelSaveData.append(modelSavePoint)

    def generateSaveData(self) -> None:
        """ """
        self.collectBuildModelResults()
        self.addMountModelToBuildModel()

    def saveModelData(self, modelPath: Path) -> None:
        """ """
        with open(modelPath, "w") as outfile:
            json.dump(self.modelSaveData, outfile, sort_keys=True, indent=4)

    def buildProgModel(self) -> None:
        """ """
        self.modelProgData = list()
        for mPoint in self.modelBuildData:
            mCoord = Star(mPoint["raJNowM"], mPoint["decJNowM"])
            sCoord = Star(mPoint["raJNowS"], mPoint["decJNowS"])
            sidereal = mPoint["siderealTime"]
            pierside = mPoint["pierside"]
            programmingPoint = ProgStar(mCoord, sCoord, sidereal, pierside)
            self.modelProgData.append(programmingPoint)

    def addMountDataToModelBuildData(self) -> None:
        """ """
        item = self.modelBuildData[self.pointerImage]
        obs = self.app.mount.obsSite
        item["raJNowM"] = obs.raJNow
        item["decJNowM"] = obs.decJNow
        item["angularPosRA"] = obs.angularPosRA
        item["angularPosDEC"] = obs.angularPosDEC
        item["siderealTime"] = obs.timeSidereal
        item["julianDate"] = obs.timeJD
        item["pierside"] = obs.pierside
        raJ2000M, decJ2000M = JNowToJ2000(
            item["raJNowM"], item["decJNowM"], item["julianDate"]
        )
        item["raJ2000M"] = raJ2000M
        item["decJ2000M"] = decJ2000M

    def startNewImageExposure(self) -> None:
        """ """
        self.pointerImage += 1
        if self.cancelBatch or self.endBatch:
            return

        waitTime = self.exposureWaitTime
        while self.pauseBatch or waitTime > 0:
            sleepAndEvents(500)
            waitTime -= 1

        item = self.modelBuildData[self.pointerImage]
        self.addMountDataToModelBuildData()
        cam = self.app.camera
        imagePath = item["imagePath"]
        exposureTime = item["exposureTime"] = cam.exposureTime1
        binning = item["binning"] = cam.binning1
        self.app.camera.expose(imagePath, exposureTime, binning)

    def startNewPlateSolve(self) -> None:
        """ """
        self.pointerPlateSolve += 1
        imagePath = self.modelBuildData[self.pointerPlateSolve]["imagePath"]
        self.app.plateSolve.solve(imagePath)

    def sendModelProgress(self) -> None:
        """ """
        fraction = (self.pointerResult + 1) / len(self.modelBuildData)
        secondsElapsed = time.time() - self.runTime
        secondsBase = secondsElapsed / fraction
        secondsEstimated = secondsBase * (1 - fraction)
        modelPercent = int(100 * fraction)

        progressData = {
            "count": len(self.modelBuildData),
            "modelPercent": modelPercent,
            "secondsElapsed": secondsElapsed,
            "secondsEstimated": secondsEstimated,
            "solved": self.pointerResult + 1,
        }
        self.progress.emit(progressData)

    def collectPlateSolveResult(self, result) -> None:
        """ """
        self.pointerResult += 1
        item = self.modelBuildData[self.pointerResult]
        item.update(result)
        solved = result["success"]

        if solved:
            raJNowS, decJNowS = J2000ToJNow(
                item["raJ2000S"], item["decJ2000S"], item["julianDate"]
            )
            item["raJNowS"] = raJNowS
            item["decJNowS"] = decJNowS

        statusBuildPoint = 0 if solved else 2
        self.app.data.setStatusBuildP(self.pointerResult, statusBuildPoint)
        self.app.updatePointMarker.emit()
        self.sendModelProgress()

    def prepareModelBuildData(self) -> None:
        """ """
        self.pointerSlew = -1
        self.pointerImage = -1
        self.pointerPlateSolve = -1
        self.pointerResult = -1
        self.modelBuildData.clear()
        for index, point in enumerate(self.modelInputData):
            modelItem = {}
            imagePath = self.imageDir / f"image-{index + 1:03d}.fits"
            modelItem["imagePath"] = imagePath
            modelItem["altitude"] = Angle(degrees=point[0])
            modelItem["azimuth"] = Angle(degrees=point[1])
            modelItem["exposureTime"] = self.app.camera.exposureTime
            modelItem["binning"] = self.app.camera.binning
            modelItem["subFrame"] = self.app.camera.subFrame
            modelItem["fastReadout"] = self.app.camera.fastReadout
            modelItem["name"] = self.modelName
            modelItem["plateSolveApp"] = self.plateSolveApp
            modelItem["focalLength"] = self.app.camera.focalLength
            modelItem["waitTime"] = self.exposureWaitTime
            self.modelBuildData.append(modelItem)

    def runModel(self) -> None:
        """
        todo: implement retries
        """
        if not self.modelInputData:
            return

        self.runTime = time.time()
        self.prepareModelBuildData()
        self.startNewSlew()

        notFinished = self.pointerResult < len(self.modelBuildData)
        while not self.cancelBatch and notFinished and not self.endBatch:
            sleepAndEvents(500)

        self.buildProgModel()
        modelSize = len(self.modelProgData)
        if modelSize < 3:
            self.log.warning(f"Only {modelSize} points available")
            self.modelProgData = []
