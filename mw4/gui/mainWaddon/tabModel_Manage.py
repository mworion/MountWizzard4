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
import json
from pathlib import Path

# external packages
from PySide6.QtWidgets import QLineEdit, QInputDialog
from PySide6.QtCore import Qt, QObject
import numpy as np

# local import
from mountcontrol.model import Model
from logic.modelBuild.modelHandling import (
    writeRetrofitData,
    convertAngleToFloat,
    convertFloatToAngle,
    findFittingModel,
)
from gui.utilities.toolsQtWidget import changeStyleDynamic


class ModelManage(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.runningOptimize = False
        self.fittedModelPath = Path()
        self.plane = None

        ms = self.app.mount.signals
        ms.getModelDone.connect(self.showModelPosition)
        ms.getModelDone.connect(self.showErrorAscending)
        ms.getModelDone.connect(self.showErrorDistribution)
        ms.namesDone.connect(self.setNameList)

        self.ui.refreshName.clicked.connect(self.refreshName)
        self.ui.refreshModel.clicked.connect(self.refreshModel)
        self.ui.clearModel.clicked.connect(self.clearModel)
        self.ui.loadName.clicked.connect(self.loadName)
        self.ui.saveName.clicked.connect(self.saveName)
        self.ui.deleteName.clicked.connect(self.deleteName)
        self.ui.runOptimize.clicked.connect(self.runOptimize)
        self.ui.cancelOptimize.clicked.connect(self.cancelOptimize)
        self.ui.deleteWorstPoint.clicked.connect(self.deleteWorstPoint)
        self.ui.openAnalyseW.clicked.connect(self.sendAnalyseFileName)

        self.ui.targetRMS.valueChanged.connect(self.showModelPosition)
        self.ui.targetRMS.valueChanged.connect(self.showErrorAscending)
        self.ui.targetRMS.valueChanged.connect(self.showErrorDistribution)
        self.app.colorChange.connect(self.updateColorSet)
        self.app.refreshModel.connect(self.refreshModel)
        self.app.refreshName.connect(self.refreshName)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.targetRMS.setValue(config.get("targetRMS", 10))
        self.ui.optimizeOverall.setChecked(config.get("optimizeOverall", True))
        self.ui.optimizeSingle.setChecked(config.get("optimizeSingle", True))
        self.showModelPosition()
        self.showErrorAscending()
        self.showErrorDistribution()

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["targetRMS"] = self.ui.targetRMS.value()
        config["optimizeOverall"] = self.ui.optimizeOverall.isChecked()
        config["optimizeSingle"] = self.ui.optimizeSingle.isChecked()

    def setupIcons(self) -> None:
        """ """
        self.mainW.wIcon(self.ui.runOptimize, "start")
        self.mainW.wIcon(self.ui.cancelOptimize, "cross-circle")
        self.mainW.wIcon(self.ui.deleteWorstPoint, "circle-minus")
        self.mainW.wIcon(self.ui.clearModel, "trash")
        self.mainW.wIcon(self.ui.openAnalyseW, "bar-chart")
        self.mainW.wIcon(self.ui.loadName, "load")
        self.mainW.wIcon(self.ui.saveName, "save")
        self.mainW.wIcon(self.ui.deleteName, "trash")
        self.mainW.wIcon(self.ui.refreshName, "reload")
        self.mainW.wIcon(self.ui.refreshModel, "reload")

    def updateColorSet(self) -> None:
        """ """
        for plot in [
            self.ui.modelPositions,
            self.ui.errorDistribution,
            self.ui.errorAscending,
        ]:
            plot.colorChange()
        self.showModelPosition()
        self.showErrorAscending()
        self.showErrorDistribution()

    def setNameList(self, model: Model) -> None:
        """ """
        self.ui.nameList.clear()
        for name in model.nameList:
            self.ui.nameList.addItem(name)
        self.ui.nameList.sortItems()

    def showModelPosition(self) -> None:
        """ """
        model = self.app.mount.model
        if model.numberStars == 0 or len(model.starList) == 0:
            self.ui.modelPositions.p[0].clear()
            return
        altitude = np.array([x.alt.degrees for x in model.starList])
        azimuth = np.array([x.az.degrees for x in model.starList])
        error = np.array([x.errorRMS for x in model.starList])
        errorAngle = np.array([x.errorAngle.degrees for x in model.starList])
        index = np.array([star.number for star in model.starList])
        self.ui.modelPositions.barItem.setLabel("right", "Error [RMS]")
        self.ui.modelPositions.plot(
            azimuth,
            altitude,
            z=error,
            ang=errorAngle,
            range={"xMin": -91, "yMin": -91, "xMax": 91, "yMax": 91},
            bar=True,
            data=list(zip(index, error)),
            reverse=True,
            tip="PointNo: {data[0]}\nErrorRMS: {data[1]:0.1f}".format,
        )
        self.ui.modelPositions.plotLoc(self.app.mount.obsSite.location.latitude.degrees)
        self.ui.modelPositions.scatterItem.sigClicked.connect(self.pointClicked)

    def showErrorAscending(self) -> None:
        """ """
        model = self.app.mount.model
        error = np.array([star.errorRMS for star in model.starList])
        if len(error) == 0:
            self.ui.errorAscending.p[0].clear()
            return
        index = np.array([star.number for star in model.starList])
        self.ui.errorAscending.p[0].setLabel("bottom", "Starcount")
        self.ui.errorAscending.p[0].setLabel("left", "Error per Star [arcsec]")
        temp = sorted(zip(error))
        y = [x[0] for x in temp]
        self.ui.errorAscending.plot(
            index, y, color=self.mainW.M_GREEN, tip="ErrorRMS: {y:0.1f}".format
        )

    def showErrorDistribution(self) -> None:
        """ """
        model = self.app.mount.model
        error = np.array([x.errorRMS for x in model.starList])
        if len(error) == 0:
            self.ui.errorDistribution.p[0].clear()
            return
        errorAngle = np.array([x.errorAngle.degrees for x in model.starList])
        self.ui.errorDistribution.plot(
            errorAngle, error, color=self.mainW.M_GREEN, tip="ErrorRMS: {y:0.1f}".format
        )

    def clearRefreshName(self) -> None:
        """ """
        changeStyleDynamic(self.ui.refreshName, "running", False)
        changeStyleDynamic(self.ui.modelNameGroup, "running", False)
        self.ui.deleteName.setEnabled(True)
        self.ui.saveName.setEnabled(True)
        self.ui.loadName.setEnabled(True)
        self.app.mount.signals.namesDone.disconnect(self.clearRefreshName)
        self.msg.emit(0, "Model", "Manage", "Model names refreshed")

    def refreshName(self) -> None:
        """"""
        self.app.mount.signals.namesDone.connect(self.clearRefreshName)
        self.ui.deleteName.setEnabled(False)
        self.ui.saveName.setEnabled(False)
        self.ui.loadName.setEnabled(False)
        changeStyleDynamic(self.ui.refreshName, "running", True)
        changeStyleDynamic(self.ui.modelNameGroup, "running", True)
        self.app.mount.getNames()

    def loadName(self):
        """ """
        if self.ui.nameList.currentItem() is None:
            self.msg.emit(2, "Model", "Manage error", "No model name selected")
            return
        modelName = self.ui.nameList.currentItem().text()
        if not self.app.mount.model.loadName(modelName):
            self.msg.emit(2, "Model", "Manage error", f"Model load failed: [{modelName}]")
            return
        self.msg.emit(0, "Model", "Manage", f"Model loaded: [{modelName}]")
        self.refreshModel()

    def saveName(self) -> None:
        """ """
        dlg = QInputDialog()
        modelName, ok = dlg.getText(
            self.mainW, "Save model", "New model name", QLineEdit.EchoMode.Normal, ""
        )
        if modelName is None or not modelName or not ok:
            self.msg.emit(2, "Model", "Manage error", "No model name given")
            return

        if not self.app.mount.model.storeName(modelName):
            self.msg.emit(2, "Model", "Manage error", f"Model cannot be saved [{modelName}]")
            return
        self.msg.emit(0, "Model", "Manage", f"Model saved: [{modelName}]")
        self.refreshName()

    def deleteName(self) -> None:
        """ """
        if self.ui.nameList.currentItem() is None:
            self.msg.emit(2, "Model", "Manage error", "No model name selected")
            return

        modelName = self.ui.nameList.currentItem().text()
        if not self.mainW.messageDialog(
            self.mainW, "Delete model", f"Delete model [{modelName}] from database?"
        ):
            return

        if not self.app.mount.model.deleteName(modelName):
            self.msg.emit(2, "Model", "Manage error", f"Model cannot be deleted [{modelName}]")
            return
        self.msg.emit(0, "Model", "Manage", f"Model deleted: [{modelName}]")
        self.refreshName()

    def writeBuildModelOptimized(self, pointsOut) -> None:
        """ """
        if not pointsOut or self.fittedModelPath.is_dir():
            return
        newName = self.fittedModelPath.stem.replace("-opt", "") + "-opt"
        newPath = self.app.mwGlob["modelDir"] / (newName + ".model")

        try:
            with open(self.fittedModelPath) as actFile:
                actModel = convertFloatToAngle(json.load(actFile))
        except Exception as e:
            self.mainW.log.warning(
                f"Cannot load model file: {[self.fittedModelPath]}, error: {e}"
            )
            return

        newModel = []
        for element in actModel:
            if element["errorIndex"] in pointsOut:
                continue
            newModel.append(element)

        newModel = writeRetrofitData(self.app.mount.model, newModel)
        newModel = convertAngleToFloat(newModel)
        with open(newPath, "w+") as newFile:
            json.dump(newModel, newFile, sort_keys=True, indent=4)
        self.fittedModelPath = newPath

    def clearRefreshModel(self) -> None:
        """ """
        changeStyleDynamic(self.ui.refreshModel, "running", False)
        changeStyleDynamic(self.ui.modelGroup, "running", False)
        self.ui.deleteWorstPoint.setEnabled(True)
        self.ui.runOptimize.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.app.mount.signals.getModelDone.disconnect(self.clearRefreshModel)
        self.msg.emit(0, "Model", "Manage", "Align model data refreshed")
        self.fittedModelPath, pointsOut = findFittingModel(
            self.app.mount.model, self.app.mwGlob["modelDir"]
        )
        self.writeBuildModelOptimized(pointsOut)
        if self.fittedModelPath.is_file():
            self.msg.emit(
                0, "Model", "Manage", f"Found stored model:  [{self.fittedModelPath.stem}]"
            )
            self.ui.originalModel.setText(self.fittedModelPath.stem)

        else:
            self.ui.originalModel.setText("No fitting model file found")
        self.sendAnalyseFileName()

    def refreshModel(self) -> None:
        """ """
        changeStyleDynamic(self.ui.refreshModel, "running", True)
        changeStyleDynamic(self.ui.modelGroup, "running", True)
        self.app.mount.signals.getModelDone.connect(self.clearRefreshModel)
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.runOptimize.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.app.mount.getModel()

    def clearModel(self) -> None:
        """ """
        if not self.mainW.messageDialog(
            self.mainW, "Clear model", "Clear actual alignment model"
        ):
            return
        if not self.app.mount.model.clearModel():
            self.msg.emit(2, "Model", "Manage error", "Actual model cannot be cleared")
            return
        self.msg.emit(0, "Model", "Manage", "Actual model cleared")
        self.refreshModel()

    def deleteWorstPoint(self) -> None:
        """ """
        model = self.app.mount.model
        if not model.numberStars:
            return

        wIndex = model.starList.index(max(model.starList))
        wStar = model.starList[wIndex]
        error = wStar.errorRMS
        if not model.deletePoint(wStar.number):
            self.msg.emit(2, "Model", "Manage error", "Worst point cannot be deleted")
            return
        text = f"Point: {wIndex + 1:3.0f}, RMS of {error:5.1f}"
        text += " arcsec deleted."
        self.msg.emit(0, "Model", "Manage", text)
        self.refreshModel()

    def finishOptimize(self) -> None:
        """ " """
        if self.ui.optimizeOverall.isChecked():
            self.app.mount.signals.getModelDone.disconnect(self.runTargetRMS)
        else:
            self.app.mount.signals.getModelDone.disconnect(self.runSingleRMS)

        changeStyleDynamic(self.ui.runOptimize, "running", False)
        self.ui.deleteWorstPoint.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.ui.refreshModel.setEnabled(True)
        self.ui.cancelOptimize.setEnabled(False)
        self.msg.emit(0, "Model", "Manage", "Optimizing done")
        self.refreshModel()

    def runTargetRMS(self) -> None:
        """ """
        mount = self.app.mount
        if mount.model.errorRMS < self.ui.targetRMS.value():
            self.runningOptimize = False
        if mount.model.numberStars is None:
            numberStars = 0
        else:
            numberStars = mount.model.numberStars

        if self.runningOptimize and numberStars > 1:
            wIndex = mount.model.starList.index(max(mount.model.starList))
            wStar = mount.model.starList[wIndex]
            if not mount.model.deletePoint(wStar.number):
                self.runningOptimize = False
                self.msg.emit(
                    2,
                    "Model",
                    "Manage error",
                    f"Star [{wStar.number + 1:3.0f}] cannot be deleted",
                )
            else:
                text = f"Point: {wStar.number + 1:3.0f}: "
                text += f"RMS of {wStar.errorRMS:5.1f} arcsec deleted."
                self.msg.emit(0, "Model", "Manage", text)
            mount.getModel()
        else:
            self.finishOptimize()

    def runSingleRMS(self) -> None:
        """ """
        mount = self.app.mount
        if all([star.errorRMS < self.ui.targetRMS.value() for star in mount.model.starList]):
            self.runningOptimize = False
        if mount.model.numberStars is None:
            numberStars = 0
        else:
            numberStars = mount.model.numberStars

        if self.runningOptimize and numberStars > 1:
            wIndex = mount.model.starList.index(max(mount.model.starList))
            wStar = mount.model.starList[wIndex]
            suc = mount.model.deletePoint(wStar.number)
            if not suc:
                self.runningOptimize = False
                self.msg.emit(
                    2,
                    "Model",
                    "Manage error",
                    f"Point [{wStar.number + 1:3.0f}] cannot be deleted",
                )
            else:
                text = f"Point: {wStar.number + 1:3.0f}, RMS of {wStar.errorRMS:5.1f}"
                text += " arcsec deleted."
                self.msg.emit(0, "Model", "Manage", text)
            mount.getModel()
        else:
            self.finishOptimize()

    def runOptimize(self) -> None:
        """ """
        self.msg.emit(1, "Model", "Manage", "Start optimizing model")
        self.runningOptimize = True
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.ui.refreshModel.setEnabled(False)
        self.ui.cancelOptimize.setEnabled(True)
        changeStyleDynamic(self.ui.runOptimize, "running", True)

        if self.ui.optimizeOverall.isChecked():
            self.app.mount.signals.getModelDone.connect(self.runTargetRMS)
            self.runTargetRMS()
        else:
            self.app.mount.signals.getModelDone.connect(self.runSingleRMS)
            self.runSingleRMS()

    def cancelOptimize(self) -> None:
        """ """
        self.runningOptimize = False

    def sendAnalyseFileName(self) -> None:
        """ """
        if not self.fittedModelPath.is_file():
            return
        self.app.showAnalyse.emit(self.fittedModelPath)

    def pointClicked(self, scatterPlotItem, points, event) -> None:
        """ """
        if event.double() or event.button() != Qt.MouseButton.LeftButton:
            return
        if len(points[0].data()) == 0:
            return

        index = points[0].data()[0]
        error = self.app.mount.model.starList[index].errorRMS
        text = f"Do you want to delete \npoint {index + 1:3.0f}"
        text += f"\nRMS of {error:5.1f} arcsec"

        if not self.mainW.messageDialog(self.mainW, "Deleting point", text):
            return
        if not self.app.mount.model.deletePoint(index):
            self.msg.emit(
                2, "Model", "Manage error", f"Point {index + 1:3.0f} cannot be deleted"
            )
            return

        text = f"Point: {index + 1:3.0f}, RMS of {error:5.1f}"
        text += " arcsec deleted."
        self.msg.emit(0, "Model", "Manage", text)
        self.refreshModel()
