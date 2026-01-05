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
from mw4.base.transform import J2000ToJNow, JNowToJ2000
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
        self.waitTimeExposure: float = 0
        self.runTime: float = 0
        self.numberRetries: int = 0
        self.pointerModel: int = 0
        self.mountSlewed: bool = False
        self.domeSlewed: bool = False

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

    def setImageExposed(self, imagePath) -> None:
        """ """
        self.app.showImage.emit(imagePath)
        if self.modelTiming == self.PROGRESSIVE:
            self.startNewSlew()

    def setImageDownloaded(self) -> None:
        """ """
        if self.modelTiming == self.NORMAL:
            self.startNewSlew()

    def setImageSaved(self) -> None:
        """ """
        if self.modelTiming == self.CONSERVATIVE:
            self.startNewSlew()

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
        isPossibleTarget = False
        while not isPossibleTarget:
            self.pointerModel += 1
            if self.pointerModel >= len(self.modelBuildData):
                self.log.info(f"{'Start slew':15s}: Last point done")
                return
            if self.cancelBatch or self.endBatch:
                return
            item = self.modelBuildData[self.pointerModel]
            altitude = item["altitude"]
            azimuth = item["azimuth"]
            self.mountSlewed = False
            self.domeSlewed = False
            t = f"{'Start slew':15s}: [{self.pointerModel:02d}], "
            t += f" Alt: [{altitude.degrees:03.0f}], Az: [{azimuth.degrees:03.0f}]"
            self.log.debug(t)
            isPossibleTarget = self.app.mount.obsSite.setTargetAltAz(altitude, azimuth)
            data = [self.modelBuildData[self.pointerModel]["imagePath"].stem]
            data += [altitude.degrees, azimuth.degrees]
            status = [""] if isPossibleTarget else ["Point skipped - slew not possible"]
            data += status
            self.statusSlew.emit(data)
            if not isPossibleTarget:
                item["success"] = False
                self.log.debug(f"{'Skip point':15s}: No target setting possible")
                continue
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
            self.modelSaveData.append(modelBuildPoint)
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
        for mPoint in self.modelBuildData:
            if not mPoint["success"]:
                continue
            mCoord = Star(mPoint["raJNowM"], mPoint["decJNowM"])
            sCoord = Star(mPoint["raJNowS"], mPoint["decJNowS"])
            sidereal = mPoint["siderealTime"]
            pierside = mPoint["pierside"]
            programmingPoint = ProgStar(mCoord, sCoord, sidereal, pierside)
            self.modelProgData.append(programmingPoint)

    def addMountDataToModelBuildData(self, pointerModel: int) -> None:
        """ """
        item = self.modelBuildData[pointerModel]
        obs = self.app.mount.obsSite
        t = f"{'Add mount data':15s}: [{pointerModel:02d}], Ra: [{obs.raJNow}], "
        t += f"Dec: [{obs.decJNow}], Jd: [{obs.timeJD}]"
        self.log.debug(t)
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
        if self.cancelBatch or self.endBatch:
            return

        waitTime = self.waitTimeExposure
        while self.pauseBatch or waitTime > 0:
            sleepAndEvents(500)
            waitTime -= 1

        item = self.modelBuildData[self.pointerModel]
        self.addMountDataToModelBuildData(self.pointerModel)
        cam = self.app.camera
        imagePath = item["imagePath"]
        exposureTime = item["exposureTime"] = cam.exposureTime1
        binning = item["binning"] = cam.binning1
        t = f"{'Start exposure':15s}: [{self.pointerModel:02d}], "
        t += f"File: [{imagePath.stem}], ExpTime: [{exposureTime:3.0f}]"
        self.log.debug(t)
        self.app.camera.expose(imagePath, exposureTime, binning)
        self.statusExpose.emit([imagePath.stem, exposureTime, binning])

    def startNewPlateSolve(self, imagePath: Path) -> None:
        """ """
        pointerPlateSolve = int(imagePath.stem.split("-")[-1])
        self.log.debug(f"{'Start solve':15s}: [{pointerPlateSolve:02d}]")
        imagePath = self.modelBuildData[pointerPlateSolve]["imagePath"]
        self.app.plateSolve.solve(imagePath)

    def sendModelProgress(self, pointerResult: int) -> None:
        """ """
        fraction = (pointerResult + 1) / len(self.modelBuildData)
        secondsElapsed = time.time() - self.runTime
        secondsBase = secondsElapsed / fraction
        secondsEstimated = secondsBase * (1 - fraction)
        modelPercent = int(100 * fraction)

        progressData = {
            "count": pointerResult + 1,
            "number": len(self.modelBuildData),
            "modelPercent": modelPercent,
            "secondsElapsed": secondsElapsed,
            "secondsEstimated": secondsEstimated,
            "solved": pointerResult + 1,
        }
        self.progress.emit(progressData)

    def collectPlateSolveResult(self, result) -> None:
        """ """
        pointerResult = int(result["imagePath"].stem.split("-")[-1])
        item = self.modelBuildData[pointerResult]
        item.update(result)
        item["success"] = result["success"]

        if item["success"]:
            raJNowS, decJNowS = J2000ToJNow(
                item["raJ2000S"], item["decJ2000S"], item["julianDate"]
            )
            item["raJNowS"] = raJNowS
            item["decJNowS"] = decJNowS
            self.app.data.setStatusBuildPSolved(pointerResult)
        else:
            self.app.data.setStatusBuildPFailed(pointerResult)
        textResult = "Solved" if item["success"] else "Failed"
        t = f"{'Collect solve':15s}: [{pointerResult:02d}], [{textResult}], [{item}]"
        self.log.debug(t)
        self.statusSolve.emit(item)
        self.app.updatePointMarker.emit()
        self.sendModelProgress(pointerResult)
        self.endBatch = pointerResult == len(self.modelBuildData) - 1

    def prepareModelBuildData(self) -> None:
        """ """
        self.modelBuildData.clear()
        self.log.debug(f"{'Prepare model':15s}: Len: [{len(self.modelInputData)}]")
        for index, point in enumerate(self.modelInputData):
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
            modelItem["success"] = False
            self.modelBuildData.append(modelItem)

    def checkRetryNeeded(self) -> None:
        """ """
        retryNeeded = not all(p["success"] for p in self.modelBuildData)
        t = "retry needed" if retryNeeded else "no retry needed"
        self.log.debug(f"{'Check retry':15s}: Status: [{t}]")
        return retryNeeded

    def runThroughModelBuildData(self) -> None:
        """ """
        self.pointerModel = -1
        self.endBatch = False
        self.startNewSlew()
        while not self.cancelBatch and not self.endBatch:
            sleepAndEvents(500)
    """
    def runThroughModelBuildDataRetries(self) -> None:
        """ """
        while self.numberRetries >= 0:
            self.log.debug(f"{'Run retries':15s}: Count: [{self.numberRetries:1.0f}]")
            self.runThroughModelBuildData()
            if not self.checkRetryNeeded():
                break
            self.numberRetries -= 1
    """

    def runModel(self) -> None:
        """ """
        if not self.modelInputData:
            return

        self.log.debug(f"{'Start model':15s}")
        self.runTime = time.time()
        self.setupSignals()
        self.prepareModelBuildData()
        self.runThroughModelBuildData()
        self.buildProgModel()
        modelSize = len(self.modelProgData)
        if modelSize < 3:
            self.log.warning(f"Only {modelSize} points available")
            self.modelProgData = []
        self.log.debug(f"{'Finish model':15s}: [{modelSize}]")
        self.resetSignals()
