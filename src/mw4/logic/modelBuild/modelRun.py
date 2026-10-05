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
import json
import logging
import time
from collections.abc import Iterator
from mw4.base.appProtocol import AppProtocol
from mw4.base.transform import JNowToJ2000
from mw4.logic.modelBuild.modelRunSupport import convertAngleToFloat, writeRetrofitData
from mw4.mountcontrol.progStar import ProgStar
from pathlib import Path
from PySide6.QtCore import QObject, QTimer, Signal
from skyfield.api import Angle, Star
from typing import Any


class ModelData(QObject):
    log = logging.getLogger("MW4")
    progress = Signal(dict)
    PROGRESSIVE = 2
    NORMAL = 1
    CONSERVATIVE = 0
    PAUSE_POLL_MS = 500

    statusExpose = Signal(object)
    statusSolve = Signal(object)
    statusSlew = Signal(object)
    statusRetry = Signal(int)
    startSlew = Signal()
    finished = Signal(bool)

    def __init__(self, app: AppProtocol) -> None:
        super().__init__()
        self.app = app
        self.cancelBatch: bool = False
        self.pauseBatch: bool = False
        self.endBatch: bool = False
        self.modelTiming: int = self.CONSERVATIVE
        self.modelInputData: list[tuple[float, float]] = []
        self.modelBuildData: dict[str, dict[str, Any]] = {}
        self.modelRunList: list[str] = []
        self.modelRunIterator: Iterator[str] | None = None
        self.modelRunKey: str = ""
        self.modelProgData: list[ProgStar] = []
        self.modelSaveData: list = []
        self.modelName: str = ""
        self.imageDir: Path = Path()
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
        self.slewPending: bool = False
        self.passActive: bool = False
        self.timerExposure = QTimer(self)
        self.timerExposure.setSingleShot(True)
        self.timerExposure.timeout.connect(self.checkPauseAndExpose)
        self.startSlew.connect(self.startNewSlew)

    def setupSignals(self) -> None:
        self.app.dReg["camera"].signals.exposed.connect(self.setImageExposed)
        self.app.dReg["camera"].signals.downloaded.connect(self.setImageDownloaded)
        self.app.dReg["camera"].signals.saved.connect(self.setImageSaved)
        self.app.dReg["mount"].signals.slewed.connect(self.setMountSlewed)
        self.app.dReg["dome"].signals.slewed.connect(self.setDomeSlewed)
        self.app.dReg["camera"].signals.saved.connect(self.startNewPlateSolve)
        self.app.dReg["plateSolve"].signals.result.connect(self.collectPlateSolveResult)

    def resetSignals(self) -> None:
        self.app.dReg["camera"].signals.exposed.disconnect(self.setImageExposed)
        self.app.dReg["camera"].signals.downloaded.disconnect(self.setImageDownloaded)
        self.app.dReg["camera"].signals.saved.disconnect(self.setImageSaved)
        self.app.dReg["mount"].signals.slewed.disconnect(self.setMountSlewed)
        self.app.dReg["dome"].signals.slewed.disconnect(self.setDomeSlewed)
        self.app.dReg["camera"].signals.saved.disconnect(self.startNewPlateSolve)
        self.app.dReg["plateSolve"].signals.result.disconnect(self.collectPlateSolveResult)

    def setImageExposed(self) -> None:
        if self.modelTiming == self.PROGRESSIVE:
            self.startSlew.emit()

    def setImageDownloaded(self) -> None:
        if self.modelTiming == self.NORMAL:
            self.startSlew.emit()

    def setImageSaved(self) -> None:
        if self.modelTiming == self.CONSERVATIVE:
            self.startSlew.emit()

    def startExposureAfterSlew(self) -> None:
        if self.slewPending and self.mountSlewed and self.domeSlewed:
            self.slewPending = False
            self.startNewImageExposure()

    def setMountSlewed(self) -> None:
        self.mountSlewed = True
        if not self.app.dReg["dome"].stat:
            self.domeSlewed = True
        self.startExposureAfterSlew()

    def setDomeSlewed(self) -> None:
        self.domeSlewed = True
        self.startExposureAfterSlew()

    def startNewSlew(self) -> None:
        nextKey = next(self.modelRunIterator, None)
        self.modelRunKey = nextKey or ""
        if self.cancelBatch or self.endBatch or nextKey is None:
            return
        mount = self.app.dReg["mount"]
        dome = self.app.dReg["dome"]
        point = self.modelBuildData[nextKey]
        altitude = point["altitude"]
        azimuth = point["azimuth"]
        self.mountSlewed = False
        self.domeSlewed = False
        self.slewPending = False
        self.statusSlew.emit([nextKey, altitude.degrees, azimuth.degrees])
        if not mount.obsSite.setTargetAltAz(altitude, azimuth):
            result = {
                "success": False,
                "message": "Slew not possible - limits ?",
                "imagePath": point["imagePath"],
            }
            self.app.dReg["plateSolve"].signals.result.emit(result)
            self.startSlew.emit()
            t = f"{'Slew limits ':15s}: [{nextKey}]"
            self.log.debug(t)
            return

        self.slewPending = True
        if dome.stat:
            dome.instance.slewDome(azimuth=azimuth.degrees)
        mount.obsSite.startSlewing()
        t = f"{'Start slew':15s}: [{nextKey}], "
        t += f" Alt: [{altitude.degrees:03.0f}], Az: [{azimuth.degrees:03.0f}]"
        self.log.debug(t)

    def addMountModelToBuildModel(self) -> bool:
        mount = self.app.dReg["mount"]
        if len(mount.model.starList) != len(self.modelSaveData):
            self.log.warning("Error in model data: difference in length")
            self.modelSaveData = []
            return False
        self.modelSaveData = writeRetrofitData(mount.model, self.modelSaveData)
        self.modelSaveData = convertAngleToFloat(self.modelSaveData)
        return True

    def collectBuildModelResults(self) -> None:
        self.modelSaveData.clear()
        for item in self.modelBuildData.values():
            if not item["success"]:
                continue
            saveItem = dict(item)
            saveItem["version"] = self.version
            saveItem["profile"] = self.profile
            saveItem["firmware"] = self.firmware
            saveItem["latitude"] = self.latitude
            self.modelSaveData.append(saveItem)

    def generateSaveData(self) -> bool:
        self.collectBuildModelResults()
        return self.addMountModelToBuildModel()

    def saveModelData(self, modelPath: Path) -> None:
        self.log.debug(f"{'Save model':15s}: Len: [{len(self.modelSaveData)}]")
        with open(modelPath, "w") as outfile:
            json.dump(self.modelSaveData, outfile, sort_keys=True, indent=4)

    def buildProgModel(self) -> None:
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
        item = self.modelBuildData[self.modelRunKey]
        obs = self.app.dReg["mount"].obsSite
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
        if self.cancelBatch or self.endBatch:
            return
        self.timerExposure.start(int(self.waitTimeExposure * 1000))

    def checkPauseAndExpose(self) -> None:
        if self.cancelBatch or self.endBatch:
            return
        if self.pauseBatch:
            self.timerExposure.start(self.PAUSE_POLL_MS)
            return
        self.exposeImage()

    def exposeImage(self) -> None:
        self.addMountDataToModelBuildData()
        item = self.modelBuildData[self.modelRunKey]
        cam = self.app.dReg["camera"].instance
        imagePath = item["imagePath"]
        exposureTime = item["exposureTime"] = cam.exposureTime1
        binning = item["binning"] = cam.binning1
        t = f"{'Start exposure':15s}: [{self.modelRunKey}], ExpTime: [{exposureTime:3.0f}]"
        self.log.debug(t)
        self.app.dReg["camera"].instance.expose(imagePath, exposureTime, binning)
        self.statusExpose.emit([imagePath.stem, exposureTime, binning])

    def startNewPlateSolve(self, imagePath: Path) -> None:
        self.log.debug(f"{'Start solve':15s}: [{imagePath.stem}]")
        self.app.dReg["plateSolve"].instance.solve(imagePath)

    def sendModelProgress(self) -> None:
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

    def collectPlateSolveResult(self, result: dict[str, Any]) -> None:
        key = result["imagePath"].stem
        item = self.modelBuildData[key]
        if result["success"]:
            self.app.buildPoint.setStatusBuildPSolved(item["countSequence"])
        else:
            self.app.buildPoint.setStatusBuildPFailed(item["countSequence"])
        item.update(result)
        t = f"{'Collect solve':15s}: [{key}], [{item['message']}], [{item}]"
        self.app.updatePointMarker.emit()
        item["processed"] = True
        self.sendModelProgress()
        self.log.debug(t)
        self.statusSolve.emit(item)
        if self.checkModelFinished():
            QTimer.singleShot(0, self.finishPass)

    def prepareModelBuildData(self) -> None:
        self.modelBuildData.clear()
        self.modelRunList.clear()
        self.retries = 0
        self.log.debug(f"{'Prepare model':15s}: Len: [{len(self.modelInputData)}]")
        for index, point in enumerate(self.modelInputData):
            self.app.buildPoint.setStatusBuildPUnprocessed(index)
            modelItem = {}
            imagePath = self.imageDir / f"image-{index:03d}.fits"
            modelItem["imagePath"] = imagePath
            modelItem["altitude"] = Angle(degrees=point[0])
            modelItem["azimuth"] = Angle(degrees=point[1])
            modelItem["exposureTime"] = self.app.dReg["camera"].instance.exposureTime
            modelItem["binning"] = self.app.dReg["camera"].instance.binning
            modelItem["subFrame"] = self.app.dReg["camera"].instance.subFrame
            modelItem["fastReadout"] = self.app.dReg["camera"].instance.fastReadout
            modelItem["name"] = self.modelName
            modelItem["plateSolveApp"] = self.plateSolveApp
            modelItem["focalLength"] = self.app.dReg["camera"].instance.focalLength
            modelItem["countSequence"] = index
            modelItem["message"] = ""
            modelItem["success"] = False
            modelItem["processed"] = False
            self.modelBuildData[imagePath.stem] = modelItem
            self.modelRunList.append(imagePath.stem)

    def checkRetryNeeded(self) -> bool:
        retryNeeded = not all(
            self.modelBuildData[key]["success"]
            and not self.modelBuildData[key]["message"].startswith("Slew not possible")
            for key in self.modelRunList
        )
        t = "retry needed" if retryNeeded else "no retry needed"
        self.log.debug(f"{'Check retry':15s}: Status: [{t}]")
        return retryNeeded

    def checkModelFinished(self) -> bool:
        return all(self.modelBuildData[key]["processed"] for key in self.modelRunList)

    def generateRunIterator(self) -> None:
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

    def startPass(self) -> None:
        if self.cancelBatch or self.endBatch:
            self.finishModel()
            return
        if self.retries > 0:
            self.statusRetry.emit(self.retries)
        self.generateRunIterator()
        for key in self.modelRunList:
            self.modelBuildData[key]["processed"] = False
        self.passActive = True
        if not self.modelRunList:
            QTimer.singleShot(0, self.finishPass)
            return
        self.startSlew.emit()

    def finishPass(self) -> None:
        if not self.passActive:
            return
        self.passActive = False
        stopped = self.cancelBatch or self.endBatch
        if not stopped and self.retries < self.numberRetries and self.checkRetryNeeded():
            self.retries += 1
            self.startPass()
            return
        self.finishModel()

    def finishModel(self) -> None:
        self.timerExposure.stop()
        self.resetSignals()
        if self.cancelBatch:
            self.log.info(f"{'Cancel model':15s}: by user")
            self.finished.emit(True)
            return
        self.buildProgModel()
        modelSize = len(self.modelProgData)
        if modelSize < 3:
            self.log.warning(f"Only {modelSize} points available")
            self.modelProgData = []
        self.log.debug(f"{'Finish model':15s}: len: [{modelSize}]")
        self.finished.emit(False)

    def stopRun(self) -> None:
        self.timerExposure.stop()
        if self.passActive:
            QTimer.singleShot(0, self.finishPass)

    def cancelRun(self) -> None:
        self.cancelBatch = True
        self.stopRun()

    def endRun(self) -> None:
        self.endBatch = True
        self.stopRun()

    def resetBatchFlags(self) -> None:
        self.cancelBatch = self.endBatch = self.pauseBatch = False
        self.passActive = False

    def runModel(self) -> None:
        if not self.modelInputData:
            self.finished.emit(False)
            return

        self.log.debug(f"{'Start model':15s}")
        self.runTime = time.time()
        self.setupSignals()
        self.prepareModelBuildData()
        self.startPass()
