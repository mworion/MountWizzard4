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
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import partial
from mw4.base.operationStatus import OperationStatus
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.nativeQt.qtMessageDialog import MWMessageDialog
from mw4.gui.utilities.qtHelpers import changeStyleDynamic
from mw4.logic.modelBuild.modelRun import ModelData
from mw4.logic.modelBuild.modelRunSupport import buildSaveData, saveModelFile
from mw4.logic.modelBuild.modelTypes import ModelRunConfig, ModelTiming
from pathlib import Path
from PySide6.QtCore import QTimer
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mw4.gui.mainWindow.mainWindow import MainWindow


class Model(TabAddon):
    CLEAR_WAIT_MS = 1000

    def __init__(self, mainW: "MainWindow") -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.modelDoneConnected: bool = False
        self.modelData = ModelData(self.app)

        self.ui.runModel.clicked.connect(self.runBatch)
        self.ui.pauseModel.clicked.connect(self.pauseBatch)
        self.ui.cancelModel.clicked.connect(self.cancelBatch)
        self.ui.endModel.clicked.connect(self.endBatch)
        self.ui.dataModel.clicked.connect(self.runFileModel)
        self.app.operationRunning.connect(self.setModelOperationMode)
        self.ui.waitTimeMountFlip.valueChanged.connect(self.setWaitTimeFlip)
        self.modelData.statusSolve.connect(self.showStatusSolve)
        self.modelData.statusExpose.connect(self.showStatusExposure)
        self.modelData.statusSlew.connect(self.showStatusSlew)
        self.modelData.statusRetry.connect(self.showStatusRetry)
        self.modelData.progress.connect(self.showProgress)
        self.modelData.finished.connect(self.finishBatch)
        self.modelData.pointStatus.connect(self.setPointStatus)
        self.modelData.pointMarkersChanged.connect(self.app.updatePointMarker)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.ui.retriesReverse.setChecked(config.get("retriesReverse", False))
        self.ui.parkMountAfterModel.setChecked(config.get("parkMountAfterModel", False))
        self.ui.numberBuildRetries.setValue(config.get("numberBuildRetries", 0))
        self.ui.progressiveTiming.setChecked(config.get("progressiveTiming", False))
        self.ui.normalTiming.setChecked(config.get("normalTiming", False))
        self.ui.conservativeTiming.setChecked(config.get("conservativeTiming", True))
        self.ui.waitTimeMountFlip.setValue(config.get("waitTimeFlip", 0))
        self.ui.waitTimeExposure.setValue(config.get("waitTimeExposure", 0))

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["retriesReverse"] = self.ui.retriesReverse.isChecked()
        config["parkMountAfterModel"] = self.ui.parkMountAfterModel.isChecked()
        config["numberBuildRetries"] = self.ui.numberBuildRetries.value()
        config["progressiveTiming"] = self.ui.progressiveTiming.isChecked()
        config["normalTiming"] = self.ui.normalTiming.isChecked()
        config["conservativeTiming"] = self.ui.conservativeTiming.isChecked()
        config["waitTimeFlip"] = self.ui.waitTimeMountFlip.value()
        config["waitTimeExposure"] = self.ui.waitTimeExposure.value()

    def setupIcons(self) -> None:
        self.mainW.wIcon(self.ui.cancelModel, "cross-circle")
        self.mainW.wIcon(self.ui.runModel, "start")
        self.mainW.wIcon(self.ui.pauseModel, "pause")
        self.mainW.wIcon(self.ui.endModel, "stop_m")
        self.mainW.wIcon(self.ui.dataModel, "choose")

    def setWaitTimeFlip(self) -> None:
        self.app.dReg["mount"].instance.waitTimeFlip = self.ui.waitTimeMountFlip.value()

    def cancelBatch(self) -> None:
        self.modelData.cancelRun()

    def shutdown(self) -> None:
        if self.app.statusOperationRunning != OperationStatus.MODEL_BATCH:
            return
        self.msg.emit(1, "Model", "Run", "Model build cancelled on close")
        self.cancelBatch()

    def pauseBatch(self) -> None:
        self.modelData.pauseBatch = not self.modelData.pauseBatch
        changeStyleDynamic(self.ui.pauseModel, "pause", self.modelData.pauseBatch)

    def endBatch(self) -> None:
        self.modelData.endRun()

    def setModelOperationMode(self, status: int) -> None:
        if status == OperationStatus.MODEL_BATCH:
            self.ui.runModelGroup.setEnabled(True)
            self.ui.dataModel.setEnabled(False)
            self.ui.cancelModel.setEnabled(True)
            self.ui.endModel.setEnabled(True)
            self.ui.pauseModel.setEnabled(True)
            self.ui.runModel.setEnabled(False)
            changeStyleDynamic(self.ui.runModel, "run", "true")
            changeStyleDynamic(self.ui.cancelModel, "stop", "true")
            changeStyleDynamic(self.ui.endModel, "stop", "true")
        elif status == OperationStatus.MODEL_FILE:
            self.ui.runModelGroup.setEnabled(False)
        elif status == OperationStatus.MODEL_SYNC:
            self.ui.runModelGroup.setEnabled(False)
            self.ui.dataModel.setEnabled(False)
            self.ui.cancelModel.setEnabled(False)
            self.ui.endModel.setEnabled(False)
            self.ui.pauseModel.setEnabled(False)
        else:
            self.ui.dataModel.setEnabled(True)
            self.ui.runModel.setEnabled(True)
            changeStyleDynamic(self.ui.runModel, "run", "false")
            changeStyleDynamic(self.ui.cancelModel, "stop", "false")
            changeStyleDynamic(self.ui.endModel, "stop", "false")
            changeStyleDynamic(self.ui.pauseModel, "pause", "false")

    def getSaveMeta(self) -> dict[str, Any]:
        mount = self.app.dReg["mount"]
        return {
            "version": f"{self.app.__version__}",
            "profile": self.ui.profileName.text(),
            "firmware": mount.instance.firmware.vString,
            "latitude": mount.obsSite.location.latitude.degrees,
        }

    def setPointStatus(self, index: int, status: int) -> None:
        self.app.buildPoint.setStatusBuildP(index, status)

    def programModelToMountFinish(self) -> None:
        self.app.dReg["mount"].signals.getModelDone.disconnect(self.programModelToMountFinish)
        self.modelDoneConnected = False
        self.msg.emit(1, "Model", "Writing model", f"[{self.modelData.modelName}]")
        mount = self.app.dReg["mount"]
        saveData = buildSaveData(
            self.modelData.modelBuildData, self.getSaveMeta(), mount.model
        )
        if saveData is None:
            t = "Model data inconsistent with mount model, model file not saved"
            self.msg.emit(2, "Model", "Run error", t)
        else:
            modelPath = self.app.mwGlob["modelDir"] / (self.modelData.modelName + ".model")
            saveModelFile(modelPath, saveData)
        mount.model.storeName("actual")

    def programModelToMount(self) -> None:
        if not self.modelData.modelProgData:
            self.msg.emit(3, "Model", "Run error", "No sufficient model data available")
            return
        if not self.app.dReg["mount"].model.programModelFromStarList(
            self.modelData.modelProgData
        ):
            self.msg.emit(3, "Model", "Run error", f"{'Program':12s} Failed - error")
            return
        self.msg.emit(1, "Model", "Program", f"[{self.modelData.modelName}] with success")
        if not self.modelDoneConnected:
            self.app.dReg["mount"].signals.getModelDone.connect(self.programModelToMountFinish)
            self.modelDoneConnected = True
        self.app.refreshModel.emit()

    def checkMountTimeSync(self) -> bool:
        if self.app.dReg["mount"].config.syncTimeNone:
            return True
        col = self.mainW.rgb2hex(self.mainW.M_YELLOW)
        question = f"<b><font color={col}>Reminder:</font></b>"
        question += "<br></b><br>Modeling while time synchronization is active."
        question += "<br>This might lead into model quality problems!</b>"
        question += "<br></b><br>Would you still like to proceed?<br>"
        buttons = ["Cancel", "Proceed"]
        reply = MWMessageDialog.question(self.mainW, "Modeling Start", question, buttons)
        return reply == 1

    def checkModelRunConditions(self) -> bool:
        if len(self.app.buildPoint.buildP) < 3:
            t = "No modeling start because less than 3 points"
            self.msg.emit(2, "Model", "Run error", t)
            return False
        if len(self.app.buildPoint.buildP) > 99:
            t = "No modeling start because more than 99 points"
            self.msg.emit(2, "Model", "Run error", t)
            return False
        return True

    def clearAlignAndBackup(self, continuation: Callable[[], None]) -> bool:
        if not self.app.dReg["mount"].model.clearModel():
            self.msg.emit(2, "Model", "Run error", "Actual model cannot be cleared")
            self.msg.emit(2, "", "", "Model build cancelled")
            return False

        self.msg.emit(1, "Model", "Clear model", "Waiting 1s ...")
        QTimer.singleShot(self.CLEAR_WAIT_MS, partial(self.backupAfterClear, continuation))
        return True

    def backupAfterClear(self, continuation: Callable[[], None]) -> None:
        self.msg.emit(1, "Model", "Clear model", "Actual model is cleared")
        if not self.app.dReg["mount"].model.storeName("backup"):
            t = "Cannot save backup model on mount, proceeding with model run"
            self.msg.emit(2, "Model", "Run error", t)
        continuation()

    def setupFilenamesAndDirectories(self, prefix: str = "", postfix: str = "") -> Path:
        nameTime = self.app.dReg["mount"].obsSite.timeJD.utc_strftime("%Y-%m-%d-%H-%M-%S")
        name = f"{prefix}-{nameTime}-{postfix}"
        imageDir = self.app.mwGlob["imageDir"] / name
        imageDir.mkdir(parents=True, exist_ok=True)
        return imageDir

    @staticmethod
    def formatDuration(seconds: float) -> str:
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def showProgress(self, progressData: dict) -> None:
        timeFinished = datetime.now().astimezone() + timedelta(
            seconds=progressData["secondsEstimated"]
        )
        self.ui.timeElapsed.setText(self.formatDuration(progressData["secondsElapsed"]))
        self.ui.timeEstimated.setText(self.formatDuration(progressData["secondsEstimated"]))
        self.ui.timeFinished.setText(timeFinished.strftime("%H:%M:%S"))
        self.ui.modelProgress.setValue(progressData["modelPercent"])
        self.ui.numberPoints.setText(f"{progressData['count']} / {progressData['number']}")

    def showStatusExposure(self, statusData: list) -> None:
        t = f"[{statusData[0]}], ExpTime: [{statusData[1]}s], Binning: [{statusData[2]:.0f}] "
        self.msg.emit(0, "Model", "Exposure", t)

    def showStatusSlew(self, statusData: list) -> None:
        t = f"[{statusData[0]}], Alt: [{statusData[1]:3.2f}], Az: [{statusData[2]:3.2f}]"
        self.msg.emit(0, "Model", "Slewing", t)

    def showStatusRetry(self, statusData: int) -> None:
        t = f"Retry run # [{statusData:02d}] for model run"
        self.msg.emit(1, "Model", "Retry start", t)

    def showStatusSolve(self, item: dict) -> None:
        if item["success"]:
            t = f"[{item['imagePath'].stem}], Error: [{item['errorRMS_S']:.2f}]"
            t += f", Angle: [{item['angleS'].degrees:.2f}], Scale: [{item['scaleS']:.2f}]"
            self.msg.emit(0, "Model", "Solving result", t)
        else:
            t = f"[{item['imagePath'].stem}], {item['message']}"
            self.msg.emit(2, "Model", "Solving error", t)

    def setupModelInputData(self) -> None:
        self.modelData.modelInputData = []
        for point in self.app.buildPoint.buildP:
            self.modelData.modelInputData.append(point)

    def getModelTiming(self) -> ModelTiming:
        if self.ui.progressiveTiming.isChecked():
            return ModelTiming.PROGRESSIVE
        if self.ui.normalTiming.isChecked():
            return ModelTiming.NORMAL
        return ModelTiming.CONSERVATIVE

    def setupBatchData(self) -> ModelRunConfig:
        imageDir = self.setupFilenamesAndDirectories(prefix="m", postfix="build")
        self.modelData.modelName = imageDir.stem
        return ModelRunConfig(
            imageDir=imageDir,
            numberRetries=self.ui.numberBuildRetries.value(),
            retriesReverse=self.ui.retriesReverse.isChecked(),
            waitTimeExposure=self.ui.waitTimeExposure.value(),
            modelTiming=self.getModelTiming(),
            plateSolveApp=self.app.dReg["plateSolve"].framework,
        )

    def runBatch(self) -> None:
        self.modelData.resetBatchFlags()
        if not self.checkModelRunConditions() or not self.checkMountTimeSync():
            return
        self.app.operationRunning.emit(OperationStatus.MODEL_BATCH)
        if not self.clearAlignAndBackup(self.startBatch):
            self.app.operationRunning.emit(OperationStatus.IDLE)

    def startBatch(self) -> None:
        config = self.setupBatchData()
        self.msg.emit(1, "Model", "Run", f"[{self.modelData.modelName}]")
        self.setupModelInputData()
        self.modelData.runModel(config)

    def finishBatch(self, cancelled: bool) -> None:
        if cancelled:
            self.msg.emit(1, "Model", "Run", "Model build cancelled by user")
        else:
            self.programModelToMount()
            if self.ui.parkMountAfterModel.isChecked():
                self.msg.emit(1, "Model", "Run", "Park mount after model build")
                self.app.dReg["mount"].obsSite.park()
        self.app.playSound.emit("RunFinished")
        self.app.operationRunning.emit(OperationStatus.IDLE)

    def runFileModel(self) -> None:
        self.msg.emit(1, "Model", "Run", "Model from file")
        folder = self.app.mwGlob["modelDir"]
        modelFilesPath = MWFileDialog.getOpenFileNames(
            self.mainW, "Open model file(s)", folder, "Model files (*.model)"
        )
        if len(modelFilesPath) > 1:
            self.msg.emit(0, "Model", "Run", f"Combination of {len(modelFilesPath)} files")
            imageDir = self.setupFilenamesAndDirectories(prefix="m", postfix="add")
            self.modelData.modelName = imageDir.stem
        elif len(modelFilesPath) == 1:
            self.modelData.modelName = modelFilesPath[0].stem
        else:
            self.msg.emit(1, "Model", "Run", "Model from file cancelled - no files selected")
            return

        self.app.operationRunning.emit(OperationStatus.MODEL_FILE)
        if not self.clearAlignAndBackup(partial(self.programFileModel, modelFilesPath)):
            self.app.operationRunning.emit(OperationStatus.IDLE)

    def programFileModel(self, modelFilesPath: list[Path]) -> None:
        message = self.modelData.loadFromFiles(modelFilesPath)
        if self.modelData.modelBuildData:
            self.programModelToMount()
        else:
            self.msg.emit(3, "Model", "Run error", message)
        self.app.playSound.emit("RunFinished")
        self.app.operationRunning.emit(OperationStatus.IDLE)
