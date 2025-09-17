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
import os
import time
from datetime import datetime
from pathlib import Path

# external packages
from PySide6.QtCore import QObject

# local import
from gui.utilities.toolsQtWidget import sleepAndEvents
from logic.modelBuild.modelHandling import loadModelsFromFile
from logic.modelBuild.modelData import ModelData
from gui.utilities.toolsQtWidget import changeStyleDynamic


class Model(QObject):
    """ """

    STATUS_IDLE = 0
    STATUS_MODEL_BATCH = 1
    STATUS_MODEL_FILE = 2
    STATUS_MODEL_SYNC = 3
    STATUS_MODEL_ITERATIVE = 4
    STATUS_EXPOSE_1 = 5
    STATUS_EXPOSE_N = 6
    STATUS_SOLVE = 7

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.timeStartModeling = None
        self.model: list = []
        self.modelData: ModelData = None

        self.ui.runModel.clicked.connect(self.runBatch)
        self.ui.pauseModel.clicked.connect(self.pauseBatch)
        self.ui.cancelModel.clicked.connect(self.cancelBatch)
        self.ui.endModel.clicked.connect(self.endBatch)
        self.ui.dataModel.clicked.connect(self.runFileModel)
        self.app.operationRunning.connect(self.setModelOperationMode)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.retriesReverse.setChecked(config.get("retriesReverse", False))
        self.ui.parkMountAfterModel.setChecked(config.get("parkMountAfterModel", False))
        self.ui.numberBuildRetries.setValue(config.get("numberBuildRetries", 0))
        self.ui.progressiveTiming.setChecked(config.get("progressiveTiming", False))
        self.ui.normalTiming.setChecked(config.get("normalTiming", False))
        self.ui.conservativeTiming.setChecked(config.get("conservativeTiming", True))

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["retriesReverse"] = self.ui.retriesReverse.isChecked()
        config["parkMountAfterModel"] = self.ui.parkMountAfterModel.isChecked()
        config["numberBuildRetries"] = self.ui.numberBuildRetries.value()
        config["progressiveTiming"] = self.ui.progressiveTiming.isChecked()
        config["normalTiming"] = self.ui.normalTiming.isChecked()
        config["conservativeTiming"] = self.ui.conservativeTiming.isChecked()

    def setupIcons(self) -> None:
        """ """
        self.mainW.wIcon(self.ui.cancelModel, "cross-circle")
        self.mainW.wIcon(self.ui.runModel, "start")
        self.mainW.wIcon(self.ui.pauseModel, "pause")
        self.mainW.wIcon(self.ui.endModel, "stop_m")
        self.mainW.wIcon(self.ui.dataModel, "choose")

    def cancelBatch(self) -> None:
        """ """
        if not self.modelData:
            return
        self.modelData.cancelBatch = True

    def pauseBatch(self) -> None:
        """ """
        if not self.modelData:
            return
        self.modelData.pauseBatch = not self.modelData.pauseBatch

    def endBatch(self) -> None:
        """ """
        if not self.modelData:
            return
        self.modelData.endBatch = True

    def setModelOperationMode(self, status: int) -> None:
        """ """
        if status == self.STATUS_MODEL_BATCH:
            self.ui.runModelGroup.setEnabled(False)
            self.ui.dataModelGroup.setEnabled(False)
            self.ui.cancelModel.setEnabled(True)
            self.ui.endModel.setEnabled(True)
            self.ui.pauseModel.setEnabled(True)
        elif status == self.STATUS_MODEL_FILE:
            self.ui.runModelGroup.setEnabled(False)
        elif status == self.STATUS_MODEL_SYNC:
            self.ui.runModelGroup.setEnabled(True)
            self.ui.dataModelGroup.setEnabled(True)
            self.ui.cancelModel.setEnabled(False)
            self.ui.endModel.setEnabled(False)
            self.ui.pauseModel.setEnabled(False)
        else:
            self.ui.runModelGroup.setEnabled(False)
            self.ui.dataModelGroup.setEnabled(False)

    def updateModelProgress(self, mPoint) -> None:
        """ """
        number = mPoint.get("lenSequence", 0)
        count = mPoint.get("countSequence", 0)

        if not 0 < count <= number:
            return

        fraction = count / number
        modelPercent = int(100 * fraction)

        secondsElapsed = time.time() - self.timeStartModeling
        secondsBase = secondsElapsed / fraction
        secondsEstimated = secondsBase * (1 - fraction)

        timeElapsed = time.gmtime(secondsElapsed)
        timeEstimated = time.gmtime(secondsEstimated)
        timeFinished = time.localtime(time.time() + secondsEstimated)

        self.ui.timeElapsed.setText(datetime(*timeElapsed[:6]).strftime("%H:%M:%S"))
        self.ui.timeEstimated.setText(datetime(*timeEstimated[:6]).strftime("%H:%M:%S"))
        self.ui.timeFinished.setText(datetime(*timeFinished[:6]).strftime("%H:%M:%S"))
        self.ui.numberPoints.setText(f"{count} / {number}")
        self.ui.modelProgress.setValue(modelPercent)

    def setupModelRunContextAndGuiStatus(self) -> None:
        """ """
        changeStyleDynamic(self.ui.runModel, "running", True)
        self.ui.cancelModel.setEnabled(True)
        self.ui.endModel.setEnabled(True)
        self.ui.pauseModel.setEnabled(True)

    def pauseBuild(self) -> None:
        """ """
        if not self.ui.pauseModel.property("pause"):
            changeStyleDynamic(self.ui.pauseModel, "color", "yellow")
            changeStyleDynamic(self.ui.pauseModel, "pause", True)
        else:
            changeStyleDynamic(self.ui.pauseModel, "color", "")
            changeStyleDynamic(self.ui.pauseModel, "pause", False)

    def programModelToMountFinish(self) -> None:
        """ """
        self.app.mount.signals.getModelDone.disconnect(self.programModelToMountFinish)
        self.msg.emit(0, "Model", "Run", f"Writing model [{self.modelData.name}]")
        self.modelData.generateSaveData()
        modelPath = self.app.mwGlob["modelDir"] / (self.modelData.name + ".model")
        self.modelData.saveModelData(modelPath)
        self.app.mount.model.storeName("actual")

    def programModelToMount(self) -> bool:
        """ """
        self.msg.emit(0, "Model", "Run", f"Programming {self.modelData.name}")
        if not self.modelData.modelProgData:
            self.msg.emit(3, "Model", "Run error", "No sufficient model data available")
            return
        suc = self.app.mount.model.programModelFromStarList(self.modelData.modelProgData)
        if not suc:
            self.msg.emit(3, "Model", "Run error", "Programming to mount error")
            return

        self.msg.emit(0, "Model", "Run", f"Programmed {self.modelData.name} with success")
        self.app.mount.signals.getModelDone.connect(self.programModelToMountFinish)
        self.app.refreshModel.emit()

    def checkModelRunConditions(self, excludeDonePoints: bool) -> bool:
        """ """
        if len(self.app.data.buildP) < 3:
            t = "No modeling start because less than 3 points"
            self.msg.emit(2, "Model", "Run error", t)
            return False

        if len(self.app.data.buildP) > 99:
            t = "No modeling start because more than 99 points"
            self.msg.emit(2, "Model", "Run error", t)
            return False

        if len([x for x in self.app.data.buildP if x[2]]) < 3 and excludeDonePoints:
            t = "No modeling start because less than 3 points"
            self.msg.emit(2, "Model", "Run error", t)
            return False

        return True

    def clearAlignAndBackup(self):
        """ """
        if not self.app.mount.model.clearModel():
            self.msg.emit(2, "Model", "Run error", "Actual model cannot be cleared")
            self.msg.emit(2, "", "", "Model build cancelled")
            return False

        self.msg.emit(0, "Model", "Run", "Actual model clearing, waiting 1s")
        sleepAndEvents(1000)
        self.msg.emit(0, "", "", "Actual model cleared")
        if not self.app.mount.model.storeName("backup"):
            t = "Cannot save backup model on mount, proceeding with model run"
            self.msg.emit(2, "Model", "Run error", t)
        return True

    def setupFilenamesAndDirectories(
        self, prefix: str = "", postfix: str = ""
    ) -> [Path, Path]:
        """ """
        nameTime = self.app.mount.obsSite.timeJD.utc_strftime("%Y-%m-%d-%H-%M-%S")
        name = f"{prefix}-{nameTime}-{postfix}"
        imageDir = self.app.mwGlob["imageDir"] / name

        if not imageDir.is_dir():
            os.mkdir(imageDir)

        return name, imageDir

    def showProgress(self, progressData):
        """ """
        timeElapsed = time.gmtime(progressData["secondsElapsed"])
        timeEstimated = time.gmtime(progressData["secondsEstimated"])
        timeFinished = time.localtime(time.time() + progressData["secondsEstimated"])
        self.ui.timeElapsed.setText(datetime(*timeElapsed[:6]).strftime("%H:%M:%S"))
        self.ui.timeEstimated.setText(datetime(*timeEstimated[:6]).strftime("%H:%M:%S"))
        self.ui.timeFinished.setText(datetime(*timeFinished[:6]).strftime("%H:%M:%S"))
        self.ui.modelProgress.setValue(progressData["modelPercent"])
        self.ui.numberPoints.setText(f"{progressData['count']} / {progressData['number']}")

    def setupModelInputData(self, excludeDonePoints: bool) -> None:
        """ """
        data = []
        for point in self.app.data.buildP:
            if excludeDonePoints and not point[2]:
                continue
            data.append(point)
        self.modelData.modelInputData = data

    def setupBatchData(self) -> None:
        """ """
        name, imageDir = self.setupFilenamesAndDirectories(prefix="m")
        self.modelData.progress.connect(self.showProgress)
        self.modelData.imageDir = imageDir
        self.modelData.name = name
        self.modelData.numberRetries = self.ui.numberBuildRetries.value()
        self.modelData.version = f"{self.app.__version__}"
        self.modelData.profile = self.ui.profile.text()
        self.modelData.firmware = self.ui.vString.text()
        self.modelData.latitude = self.app.mount.obsSite.location.latitude.degrees
        self.modelData.plateSolveApp = self.ui.plateSolveDevice.currentText()

    def setModelTiming(self) -> None:
        """ """
        if self.ui.progressiveTiming.isChecked():
            self.modelData.timing = self.modelData.PROGRESSIVE
        elif self.ui.normalTiming.isChecked():
            self.modelData.timing = self.modelData.NORMAL
        elif self.ui.conservativeTiming.isChecked():
            self.modelData.timing = self.modelData.CONSERVATIVE

    def runBatch(self) -> None:
        """ """
        excludeDonePoints = self.ui.excludeDonePoints.isChecked()
        if not self.checkModelRunConditions(excludeDonePoints):
            return
        if not self.clearAlignAndBackup():
            return

        self.app.operationRunning.emit(self.STATUS_MODEL_BATCH)
        self.modelData = ModelData(self.app)
        self.setModelTiming()
        self.setupBatchData()
        self.msg.emit(1, "Model", "Run", f"Model {self.modelData.name}")
        self.setupModelInputData(excludeDonePoints)
        self.modelData.runModel()
        self.programModelToMount()
        self.app.playSound.emit("RunFinished")
        self.app.operationRunning.emit(self.STATUS_IDLE)

    def runFileModel(self):
        """ """
        self.app.operationRunning.emit(self.STATUS_MODEL_FILE)
        self.modelData = ModelData(self.app)
        self.msg.emit(1, "Model", "Run", "Model from file")
        folder = self.app.mwGlob["modelDir"]
        modelFilesPath = self.mainW.openFile(
            self.mainW, "Open model file(s)", folder, "Model files (*.model)", multiple=True
        )
        if len(modelFilesPath) > 1:
            self.msg.emit(0, "Model", "Run", "Combination of len(modelFilesPath) files")
            self.modelData.name, _ = self.setupFilenamesAndDirectories(
                prefix="m", postfix="add"
            )
        elif len(modelFilesPath) == 1:
            self.modelData.name = modelFilesPath[0].stem
        else:
            self.msg.emit(1, "Model", "Run", "Model from file cancelled - no files selected")
            self.app.operationRunning.emit(self.STATUS_IDLE)
            return

        if not self.clearAlignAndBackup():
            self.app.operationRunning.emit(self.STATUS_IDLE)
            return

        self.modelData.modelBuildData, message = loadModelsFromFile(modelFilesPath)
        self.modelData.buildProgModel()
        if self.modelData.modelBuildData:
            self.programModelToMount()
        else:
            self.msg.emit(3, "Model", "Run error", message)
        self.app.playSound.emit("RunFinished")
        self.app.operationRunning.emit(self.STATUS_IDLE)
