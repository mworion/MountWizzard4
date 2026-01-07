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
import json
import logging
import time
from mw4.base.transform import JNowToJ2000
from mw4.gui.utilities.toolsQtWidget import sleepAndEvents
from mw4.logic.modelBuild.modelRunSupport import convertAngleToFloat, writeRetrofitData
from mw4.mountcontrol.progStar import ProgStar
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from skyfield.api import Angle, Star


class ModelData(QObject):
    """ """

    log = logging.getLogger("MW4")
    progress = Signal(object)
    PROGRESSIVE = 2
    NORMAL = 1
    CONSERVATIVE = 0

    statusExpose = Signal(object)
    statusSolve = Signal(object)
    statusSlew = Signal(object)
    statusRetry = Signal(object)
    startSlew = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.cancelBatch: bool = False
        self.pauseBatch: bool = False
        self.endBatch: bool = False
        self.modelTiming: int = self.CONSERVATIVE
        self.modelInputData: list = []
        self.modelBuildData: dict = {}
        self.modelRunList: list = []
        self.modelRunIterator = None
        self.modelRunKey: str = ""
        self.modelProgData: list = []
        self.modelSaveData: list = []
        self.modelName: str = ""
        self.imageDir: Path = Path("")
        self.latitude: float = 0
        self.version: str = ""
        self.firmware: str = ""
        self.profile: str = ""
        self.plateSolveApp: str = ""
        self.waitTimeExposure: float = 0
        self.runTime: float = 0
        self.numberRetries: int = 0
        self.retries: int = 0
        self.retriesReverse: bool = False
        self.mountSlewed: bool = False
        self.domeSlewed: bool = False
        self.startSlew.connect(self.startNewSlew)

    def setupSignals(self) -> None:
        """ """
        self.app.camera.signals.exposed.connect(self.setImageExposed)
        self.app.camera.signals.downloaded.connect(self.setImageDownloaded)
        self.app.camera.signals.saved.connect(self.setImageSaved)
        self.app.mount.signals.slewed.connect(self.setMountSlewed)
        self.app.dome.signals.slewed.connect(self.setDomeSlewed)
        self.app.camera.signals.saved.connect(self.startNewPlateSolve)
        self.app.plateSolve.signals.result.connect(self.collectPlateSolveResult)

    def resetSignals(self) -> None:
        """ """
        self.app.camera.signals.exposed.disconnect(self.setImageExposed)
        self.app.camera.signals.downloaded.disconnect(self.setImageDownloaded)
        self.app.camera.signals.saved.disconnect(self.setImageSaved)
        self.app.mount.signals.slewed.disconnect(self.setMountSlewed)
        self.app.dome.signals.slewed.disconnect(self.setDomeSlewed)
        self.app.camera.signals.saved.disconnect(self.startNewPlateSolve)
        self.app.plateSolve.signals.result.disconnect(self.collectPlateSolveResult)

    def setImageExposed(self) -> None:
        """ """
        if self.modelTiming == self.PROGRESSIVE:
            self.startSlew.emit()

    def setImageDownloaded(self) -> None:
        """ """
        if self.modelTiming == self.NORMAL:
            self.startSlew.emit()

    def setImageSaved(self) -> None:
        """ """
        if self.modelTiming == self.CONSERVATIVE:
            self.startSlew.emit()

    def startExposureAfterSlew(self) -> None:
        """ """
        if self.mountSlewed and self.domeSlewed:
            self.startNewImageExposure()

    def setMountSlewed(self) -> None:
        """ """
        self.mountSlewed = True
        if not self.app.deviceStat["dome"]:
            self.domeSlewed = True
        self.startExposureAfterSlew()

    def setDomeSlewed(self) -> None:
        """ """
        self.domeSlewed = True
        self.startExposureAfterSlew()

    def startNewSlew(self) -> None:
        """ """
        self.modelRunKey = next(self.modelRunIterator, False)
        if self.cancelBatch or self.endBatch or not self.modelRunKey:
            return
        altitude = self.modelBuildData[self.modelRunKey]["altitude"]
        azimuth = self.modelBuildData[self.modelRunKey]["azimuth"]
        self.mountSlewed = False
        self.domeSlewed = False
        self.statusSlew.emit([self.modelRunKey, altitude.degrees, azimuth.degrees])
        if not self.app.mount.obsSite.setTargetAltAz(altitude, azimuth):
            result = {
                "success": False,
                "message": "Slew not possible - limits ?",
                "imagePath": self.modelBuildData[self.modelRunKey]["imagePath"],
            }
            self.app.plateSolve.signals.result.emit(result)
            self.startSlew.emit()
            t = f"{'Slew limits ':15s}: [{self.modelRunKey}]"
            self.log.debug(t)
        else:
            if self.app.deviceStat["dome"]:
                self.app.dome.slewDome(azimuth)
            self.app.mount.obsSite.startSlewing()
            t = f"{'Start slew':15s}: [{self.modelRunKey}], "
            t += f" Alt: [{altitude.degrees:03.0f}], Az: [{azimuth.degrees:03.0f}]"
            self.log.debug(t)

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
        for key in self.modelBuildData:
            if not self.modelBuildData[key]["success"]:
                continue
            self.modelSaveData.append(self.modelBuildData[key])
            self.modelSaveData[-1]["version"] = self.version
            self.modelSaveData[-1]["profile"] = self.profile
            self.modelSaveData[-1]["firmware"] = self.firmware
            self.modelSaveData[-1]["latitude"] = self.latitude

    def generateSaveData(self) -> None:
        """ """
        self.collectBuildModelResults()
        self.addMountModelToBuildModel()

    def saveModelData(self, modelPath: Path) -> None:
        """ """
        self.log.debug(f"{'Save model':15s}: Len: [{len(self.modelSaveData)}]")
        with open(modelPath, "w") as outfile:
            json.dump(self.modelSaveData, outfile, sort_keys=True, indent=4)

    def buildProgModel(self) -> None:
        """ """
        self.log.debug(f"{'Build progmodel':15s}: Len: [{len(self.modelBuildData)}]")
        self.modelProgData = []
        for key in self.modelBuildData:
            mPoint = self.modelBuildData[key]
            if not mPoint["success"]:
                continue
            mCoord = Star(mPoint["raJNowM"], mPoint["decJNowM"])
            sCoord = Star(mPoint["raJNowS"], mPoint["decJNowS"])
            sidereal = mPoint["siderealTime"]
            pierside = mPoint["pierside"]
            programmingPoint = ProgStar(mCoord, sCoord, sidereal, pierside)
            self.modelProgData.append(programmingPoint)

    def addMountDataToModelBuildData(self) -> None:
        """ """
        item = self.modelBuildData[self.modelRunKey]
        obs = self.app.mount.obsSite
        t = f"{'Add mount data':15s}: [{self.modelRunKey}], Ra: [{obs.raJNow}], "
        t += f"Dec: [{obs.decJNow}], Jd: [{obs.timeJD}]"
        self.log.debug(t)
        item["raJNowM"] = obs.raJNow
        item["decJNowM"] = obs.decJNow
        item["angularPosRA"] = obs.angularPosRA
        item["angularPosDEC"] = obs.angularPosDEC
        item["siderealTime"] = obs.timeSidereal
        item["julianDate"] = obs.timeJD
        item["pierside"] = obs.pierside
        ra, dec = JNowToJ2000(item["raJNowM"], item["decJNowM"], obs.timeJD)
        item["raJ2000M"] = ra
        item["decJ2000M"] = dec

    def startNewImageExposure(self) -> None:
        """ """
        if self.cancelBatch or self.endBatch:
            return

        waitTime = self.waitTimeExposure
        while self.pauseBatch or waitTime > 0:
            sleepAndEvents(500)
            waitTime -= 1

        self.addMountDataToModelBuildData()
        item = self.modelBuildData[self.modelRunKey]
        cam = self.app.camera
        imagePath = item["imagePath"]
        exposureTime = item["exposureTime"] = cam.exposureTime1
        binning = item["binning"] = cam.binning1
        t = f"{'Start exposure':15s}: [{self.modelRunKey}], ExpTime: [{exposureTime:3.0f}]"
        self.log.debug(t)
        self.app.camera.expose(imagePath, exposureTime, binning)
        self.statusExpose.emit([imagePath.stem, exposureTime, binning])

    def startNewPlateSolve(self, imagePath: Path) -> None:
        """ """
        self.log.debug(f"{'Start solve':15s}: [{imagePath.stem}]")
        self.app.plateSolve.solve(imagePath)

    def sendModelProgress(self) -> None:
        """ """
        donePoints = sum(
            1 for key in self.modelBuildData if self.modelBuildData[key]["processed"]
        )
        fraction = donePoints / len(self.modelBuildData)
        secondsElapsed = time.time() - self.runTime
        secondsBase = secondsElapsed / fraction
        secondsEstimated = secondsBase * (1 - fraction)
        modelPercent = int(100 * fraction)
        progressData = {
            "count": donePoints,
            "number": len(self.modelBuildData),
            "modelPercent": modelPercent,
            "secondsElapsed": secondsElapsed,
            "secondsEstimated": secondsEstimated,
        }
        self.progress.emit(progressData)

    def collectPlateSolveResult(self, result) -> None:
        """ """
        key = result["imagePath"].stem
        item = self.modelBuildData[key]
        if result["success"]:
            self.app.data.setStatusBuildPSolved(item["countSequence"])
        else:
            self.app.data.setStatusBuildPFailed(item["countSequence"])
        item.update(result)
        t = f"{'Collect solve':15s}: [{key}], [{item['message']}], [{item}]"
        self.app.updatePointMarker.emit()
        item["processed"] = True
        self.sendModelProgress()
        self.log.debug(t)
        self.statusSolve.emit(item)

    def prepareModelBuildData(self) -> None:
        """ """
        self.modelBuildData.clear()
        self.modelRunList.clear()
        self.retries = 0
        self.log.debug(f"{'Prepare model':15s}: Len: [{len(self.modelInputData)}]")
        for index, point in enumerate(self.modelInputData):
            self.app.data.setStatusBuildPUnprocessed(index)
            modelItem = {}
            imagePath = self.imageDir / f"image-{index:03d}.fits"
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
            modelItem["countSequence"] = index
            modelItem["message"] = ""
            modelItem["success"] = False
            modelItem["processed"] = False
            self.modelBuildData[imagePath.stem] = modelItem
            self.modelRunList.append(imagePath.stem)

    def checkRetryNeeded(self) -> bool:
        """ """
        retryNeeded = not all(
            self.modelBuildData[key]["success"]
            and not self.modelBuildData[key]["message"].startswith("Slew not possible")
            for key in self.modelRunList
        )
        t = "retry needed" if retryNeeded else "no retry needed"
        self.log.debug(f"{'Check retry':15s}: Status: [{t}]")
        return retryNeeded

    def checkModelFinished(self) -> bool:
        """ """
        return all(self.modelBuildData[key]["processed"] for key in self.modelRunList)

    def runThroughModelBuildData(self) -> None:
        """ """
        self.endBatch = self.cancelBatch = False
        for key in self.modelRunList:
            self.modelBuildData[key]["processed"] = False
        self.startSlew.emit()
        while not self.cancelBatch and not self.endBatch and not self.checkModelFinished():
            sleepAndEvents(500)

    def generateRunIterator(self):
        """ """
        nextList = []
        self.log.debug(f"{'Run retries':15s}: Count: [{self.numberRetries:1.0f}]")
        for key in self.modelRunList:
            if self.modelBuildData[key]["success"]:
                continue
            if not self.modelBuildData[key]["message"].startswith("Slew not possible"):
                nextList.append(key)
        if self.retriesReverse and self.retries % 2 == 1:
            self.modelRunList = list(reversed(nextList))
        else:
            self.modelRunList = nextList
        self.modelRunIterator = iter(self.modelRunList)

    def runThroughModelBuildDataRetries(self) -> None:
        """ """
        while self.retries <= self.numberRetries:
            if self.retries > 0:
                self.statusRetry.emit(self.retries)
            if self.cancelBatch or self.endBatch:
                break
            self.generateRunIterator()
            self.runThroughModelBuildData()
            if not self.checkRetryNeeded():
                break
            self.retries += 1

    def runModel(self) -> None:
        """ """
        if not self.modelInputData:
            return

        self.log.debug(f"{'Start model':15s}")
        self.runTime = time.time()
        self.setupSignals()
        self.prepareModelBuildData()
        self.runThroughModelBuildDataRetries()
        if self.cancelBatch:
            self.log.info(f"{'Cancel model':15s}: by user")
            self.resetSignals()
            return
        self.buildProgModel()
        modelSize = len(self.modelProgData)
        if modelSize < 3:
            self.log.warning(f"Only {modelSize} points available")
            self.modelProgData = []
        self.log.debug(f"{'Finish model':15s}: [{modelSize}]")
        self.resetSignals()
