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
import os
import time
import json
from datetime import datetime
from pathlib import Path

# external packages

# local import
from gui.utilities.toolsQtWidget import sleepAndEvents, MWidget
from logic.modelBuild.modelHandling import (
    writeRetrofitData,
    buildProgModel,
    loadModelsFromFile,
)
from logic.modelBuild.modelBatch import ModelBatch


class Model(MWidget):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.timeStartModeling = None
        self.modelName: str = ""
        self.model: list = []
        self.modelBatch: ModelBatch = None

        self.ui.runModel.clicked.connect(self.runBatch)
        self.ui.pauseModel.clicked.connect(self.pauseBatch)
        self.ui.cancelModel.clicked.connect(self.cancelBatch)
        self.ui.endModel.clicked.connect(self.endBatch)
        self.ui.dataModel.clicked.connect(self.loadProgramModel)
        self.app.operationRunning.connect(self.setModelOperationMode)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.retriesReverse.setChecked(config.get("retriesReverse", False))
        self.ui.parkMountAfterModel.setChecked(config.get("parkMountAfterModel", False))
        self.ui.numberBuildRetries.setValue(config.get("numberBuildRetries", 0))
        self.ui.progressiveTiming.setChecked(config.get("progressiveTiming", False))
        self.ui.normalTiming.setChecked(config.get("normalTiming", False))
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
        self.wIcon(self.ui.cancelModel, "cross-circle")
        self.wIcon(self.ui.runModel, "start")
        self.wIcon(self.ui.pauseModel, "pause")
        self.wIcon(self.ui.endModel, "stop_m")
        self.wIcon(self.ui.dataModel, "choose")

    def cancelBatch(self) -> None:
        """ """
        if not self.modelBatch:
            return
        self.modelBatch.cancelBatch = True

    def pauseBatch(self) -> None:
        """ """
        if not self.modelBatch:
            return
        self.modelBatch.pauseBatch = not self.modelBatch.pauseBatch

    def endBatch(self) -> None:
        """ """
        if not self.modelBatch:
            return
        self.modelBatch.endBatch = True

    def setModelOperationMode(self, status: int) -> None:
        """
            status 0: idle
            status 1: modeling build
            status 2: modeling with stored data
        """
        if status == 1:
            self.ui.runModelGroup.setEnabled(False)
            self.ui.dataModelGroup.setEnabled(False)
            self.ui.cancelModel.setEnabled(True)
            self.ui.endModel.setEnabled(True)
            self.ui.pauseModel.setEnabled(True)
        elif status == 2:
            self.ui.runModelGroup.setEnabled(False)
        elif status == 0:
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
        self.changeStyleDynamic(self.ui.runModel, "running", True)
        self.ui.cancelModel.setEnabled(True)
        self.ui.endModel.setEnabled(True)
        self.ui.pauseModel.setEnabled(True)

    def pauseBuild(self) -> None:
        """ """
        if not self.ui.pauseModel.property("pause"):
            self.changeStyleDynamic(self.ui.pauseModel, "color", "yellow")
            self.changeStyleDynamic(self.ui.pauseModel, "pause", True)
        else:
            self.changeStyleDynamic(self.ui.pauseModel, "color", "")
            self.changeStyleDynamic(self.ui.pauseModel, "pause", False)

    def retrofitModel(self) -> None:
        """ """
        mountModel = self.app.mount.model
        if len(mountModel.starList) != len(self.model):
            text = f"length starList [{len(mountModel.starList)}] and length "
            text += f"model [{len(self.model)}] is different"
            self.log.debug(text)
            self.model = []

        self.model = writeRetrofitData(mountModel, self.model)

    def saveModelFinish(self) -> None:
        """
        saveModelFinish is the callback after the new model data is loaded from
        the mount computer. first is disabling the signals. New we have the
        original model build data which was programmed to the mount and the
        retrieved model data after the mount optimized the model. retrofitModel()
        combines this data to a signal data structure. after that it saves the
        model data for later use.

        with this data, the model could be reprogrammed without doing some imaging,
        it could be added with other data to extend the model to a broader base.
        """
        self.app.mount.signals.getModelDone.disconnect(self.saveModelFinish)
        self.retrofitModel()
        self.msg.emit(0, "Model", "Run", f"Writing model [{self.modelName}]")
        saveData = self.generateSaveData()
        modelPath = self.app.mwGlob["modelDir"] / (self.modelName + ".model")
        with open(modelPath, "w") as outfile:
            json.dump(saveData, outfile, sort_keys=True, indent=4)

    def programModelToMount(self, buildModel: list[dict]) -> bool:
        """ """
        alignModel = buildProgModel(buildModel)
        if len(alignModel) < 3:
            self.log.debug(f"Only {len(alignModel)} points available")
            return False
        suc = self.app.mount.model.programModelFromStarList(alignModel)
        if not suc:
            self.log.debug("Program align failed")
            return False

        self.app.mount.signals.getModelDone.connect(self.saveModelFinish)
        self.app.mount.model.storeName("actual")
        self.app.refreshName.emit()
        self.app.refreshModel.emit()
        return True

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
        self.app.refreshModel.emit()
        if not self.app.mount.model.storeName("backup"):
            t = "Cannot save backup model on mount, proceeding with model run"
            self.msg.emit(2, "Model", "Run error", t)
        return True

    def loadProgramModel(self):
        """ """
        folder = self.app.mwGlob["modelDir"]
        modelFilesPath = self.openFile(
            self, "Open model file(s)", folder, "Model files (*.model)", multiple=True
        )

        alignModel, message = loadModelsFromFile(modelFilesPath)
        if not alignModel:
            self.msg.emit(2, "Model", "Run error", message)
            return

        self.app.operationRunning.emit(2)
        self.msg.emit(0, "Model", "Run", message)
        self.msg.emit(0, "Model", "Run", "Programing models")
        if not self.clearAlignAndBackup():
            return

        if self.programModelToMount(alignModel):
            self.msg.emit(0, "Model", "Run", "Model programmed with success")
        else:
            self.msg.emit(2, "Model", "Run error", "Model programming error")
        self.app.operationRunning.emit(0)

    def setupFilenamesAndDirectories(self, prefix: str = "", postfix: str = "") -> [Path, Path]:
        """ """
        nameTime = self.app.mount.obsSite.timeJD.utc_strftime("%Y-%m-%d-%H-%M-%S")
        name = f"{prefix}-{nameTime}{postfix}"
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
        self.ui.numberPoints.setText(f'{progressData["count"]} / {progressData["number"]}')

    def setupModelInputData(self, excludeDonePoints: bool) -> None:
        """ """
        data = []
        for point in self.app.data.buildP:
            if excludeDonePoints and not point[2]:
                continue
            data.append(point)
        self.modelBatch.modelInputData = data

    def setupBatchData(self) -> None:
        """ """
        name, imageDir = self.setupFilenamesAndDirectories(prefix="m")
        self.modelBatch.progress.connect(self.showProgress)
        self.modelBatch.imageDir = imageDir
        self.modelBatch.modelName = name
        self.modelBatch.numberRetries = self.ui.numberBuildRetries.value()
        self.modelBatch.version = f"{self.app.__version__}"
        self.modelBatch.profile = self.ui.profile.text()
        self.modelBatch.firmware = self.ui.vString.text()
        self.modelBatch.latitude = self.app.mount.obsSite.location.latitude.degrees
        self.modelBatch.plateSolveApp = self.ui.plateSolveDevice.currentText()

    def processModelData(self) -> None:
        """
        todo: prog to mount
        todo: retrieve from mount and add
        todo: save model on disk
        """
        self.msg.emit(0, "Model", "Run", "Programming model to mount")
        if self.programModelToMount():
            self.msg.emit(0, "Model", "Run", "Model programmed with success")

    def communicateModelBatchRun(self) -> None:
        """ """
        if len(self.modelBatch.modelBuildData) < 3:
            self.msg.emit(
                2,
                "Model",
                "Run error",
                f"{self.modelName} Not enough valid model points",
            )
        else:
            self.msg.emit(1, "Model", "Run", f"Model {self.modelName} with success")

    def runBatch(self) -> None:
        """ """
        excludeDonePoints = self.ui.excludeDonePoints.isChecked()
        if not self.checkModelRunConditions(excludeDonePoints):
            return
        if not self.clearAlignAndBackup():
            return

        self.modelBatch = ModelBatch(self.app)
        self.setupModelInputData(excludeDonePoints)
        self.setupBatchData()
        self.modelBatch.run()
        self.processModelData()
        self.communicateModelBatchRun()

        self.modelBatch = None
        self.app.playSound.emit("RunFinished")
        self.app.operationRunning.emit(0)
