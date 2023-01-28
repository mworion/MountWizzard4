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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import glob
import json
import os

# external packages
from PyQt5.QtWidgets import QLineEdit, QInputDialog
from PyQt5.QtCore import Qt
import numpy as np

# local import
from logic.modeldata.modelHandling import writeRetrofitData


class ManageModel:
    """
    """

    def __init__(self):
        self.runningOptimize = False
        self.fittedModelPoints = []
        self.fittedModelPath = ''
        self.plane = None

        ms = self.app.mount.signals
        ms.alignDone.connect(self.showModelPosition)
        ms.alignDone.connect(self.showErrorAscending)
        ms.alignDone.connect(self.showErrorDistribution)
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
        self.ui.showActualModelAnalyse.clicked.connect(self.showActualModelAnalyse)
        self.ui.showOriginalModelAnalyse.clicked.connect(self.showOriginalModelAnalyse)

        self.ui.targetRMS.valueChanged.connect(self.showModelPosition)
        self.ui.targetRMS.valueChanged.connect(self.showErrorAscending)
        self.ui.targetRMS.valueChanged.connect(self.showErrorDistribution)
        self.app.colorChange.connect(self.colorChangeManageModel)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.targetRMS.setValue(config.get('targetRMS', 10))
        self.ui.optimizeOverall.setChecked(config.get('optimizeOverall', True))
        self.ui.optimizeSingle.setChecked(config.get('optimizeSingle', True))
        self.ui.autoUpdateActualAnalyse.setChecked(config.get('autoUpdateActualAnalyse', False))
        self.showModelPosition()
        self.showErrorAscending()
        self.showErrorDistribution()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['targetRMS'] = self.ui.targetRMS.value()
        config['optimizeOverall'] = self.ui.optimizeOverall.isChecked()
        config['optimizeSingle'] = self.ui.optimizeSingle.isChecked()
        config['autoUpdateActualAnalyse'] = self.ui.autoUpdateActualAnalyse.isChecked()
        return True

    def colorChangeManageModel(self):
        """
        :return:
        """
        for plot in [self.ui.modelPositions, self.ui.errorDistribution,
                     self.ui.errorAscending]:
            plot.colorChange()
        self.showModelPosition()
        self.showErrorAscending()
        self.showErrorDistribution()
        return True

    def setNameList(self, model):
        """
        setNameList populates the list of model names in the main window. before
        adding the data, the existent list will be deleted.

        :return:    True if ok for testing
        """
        self.ui.nameList.clear()
        for name in model.nameList:
            self.ui.nameList.addItem(name)
        self.ui.nameList.sortItems()
        self.ui.nameList.update()
        return True

    @staticmethod
    def findKeysFromSourceInDest(buildModel, mountModel):
        """
        :param buildModel:
        :param mountModel:
        :return: success
        """
        pointsIn = []
        pointsOut = []
        for buildPoint in buildModel:
            for mountPoint in mountModel:
                dHA = mountModel[mountPoint]['ha'] - buildModel[buildPoint]['ha']
                dHA = dHA / mountModel[mountPoint]['ha']
                dDEC = mountModel[mountPoint]['dec'] - buildModel[buildPoint]['dec']
                dDEC = dDEC / mountModel[mountPoint]['dec']

                fitHA = abs(dHA) < 1e-4
                fitDEC = abs(dDEC) < 1e-4

                if fitHA and fitDEC:
                    pointsIn.append(buildPoint)
                    break

            else:
                pointsOut.append(buildPoint)
        return pointsIn, pointsOut

    def compareModel(self, buildModelData, mountModel):
        """
        :param buildModelData:
        :param mountModel:
        :return:
        """
        buildModel = {}
        for star in buildModelData:
            index = star.get('errorIndex', 0)
            mount = {'ha': star.get('haMountModel', 0),
                     'dec': star.get('decMountModel', 0)}
            buildModel[index] = mount

        pointsIn, pointsOut = self.findKeysFromSourceInDest(buildModel, mountModel)
        return pointsIn, pointsOut

    def findFittingModel(self):
        """
        findFittingModel takes the actual loaded model from the mount and tries
        to find the fitting model run data. therefore it compares up to 5 points
        to find out. all optimized model files (containing opt in filename) are
        ignored.

        :return: success
        """
        mountModel = {}
        for star in self.app.mount.model.starList:
            mountModel[star.number] = {'ha': star.coord.ra.hours,
                                       'dec': star.coord.dec.degrees}

        searchPath = os.path.normpath(self.app.mwGlob['modelDir'] + '/*.model')
        modelFileList = glob.glob(searchPath)

        for modelFilePath in modelFileList:
            if 'opt' in modelFilePath:
                continue

            with open(modelFilePath, 'r') as inFile:
                try:
                    buildModelData = json.load(inFile)
                except Exception as e:
                    self.log.warning(f'Cannot load model file: {[inFile]}, error: {e}')
                    continue

            pointsIn, pointsOut = self.compareModel(buildModelData, mountModel)
            if len(pointsIn) > 2:
                self.fittedModelPoints = pointsIn
                self.fittedModelPath = modelFilePath
                break
        else:
            self.fittedModelPoints = []
            self.fittedModelPath = ''
            pointsIn = []
            pointsOut = []

        name = os.path.splitext(os.path.basename(self.fittedModelPath))[0]
        return name, pointsIn, pointsOut

    def showModelPosition(self):
        """
        :return:    True if ok for testing
        """
        model = self.app.mount.model
        altitude = np.array([x.alt.degrees for x in model.starList])
        if len(altitude) == 0:
            return False
        azimuth = np.array([x.az.degrees for x in model.starList])
        error = np.array([x.errorRMS for x in model.starList])
        errorAngle = np.array([x.errorAngle.degrees for x in model.starList])
        index = np.array([star.number for star in model.starList])
        self.ui.modelPositions.barItem.setLabel('right', 'Error [RMS]')
        self.ui.modelPositions.plot(
            azimuth, altitude, z=error, ang=errorAngle,
            range={'xMin': -91, 'yMin': -91, 'xMax': 91, 'yMax': 91},
            bar=True, data=list(zip(index, error)), reverse=True,
            tip='PointNo: {data[0]}\nErrorRMS: {data[1]:0.1f}'.format)
        self.ui.modelPositions.plotLoc(
            self.app.mount.obsSite.location.latitude.degrees)
        self.ui.modelPositions.scatterItem.sigClicked.connect(self.pointClicked)
        return True

    def showErrorAscending(self):
        """
        :return:    True if ok for testing
        """
        model = self.app.mount.model
        error = np.array([star.errorRMS for star in model.starList])
        if len(error) == 0:
            return False

        index = np.array([star.number for star in model.starList])
        self.ui.errorAscending.p[0].setLabel('bottom', 'Starcount')
        self.ui.errorAscending.p[0].setLabel('left', 'Error per Star [arcsec]')
        temp = sorted(zip(error))
        y = [x[0] for x in temp]
        self.ui.errorAscending.plot(
            index, y, color=self.M_GREEN,
            tip='ErrorRMS: {y:0.1f}'.format)
        return True

    def showErrorDistribution(self):
        """
        :return:    True if ok for testing
        """
        model = self.app.mount.model
        error = np.array([x.errorRMS for x in model.starList])
        if len(error) == 0:
            return False
        errorAngle = np.array([x.errorAngle.degrees for x in model.starList])
        self.ui.errorDistribution.plot(
            errorAngle, error, color=self.M_GREEN,
            tip='ErrorRMS: {y:0.1f}'.format)
        return True

    def clearRefreshName(self):
        """
        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.refreshName, 'running', False)
        self.changeStyleDynamic(self.ui.modelNameGroup, 'running', False)
        self.ui.deleteName.setEnabled(True)
        self.ui.saveName.setEnabled(True)
        self.ui.loadName.setEnabled(True)
        self.app.mount.signals.namesDone.disconnect(self.clearRefreshName)
        self.msg.emit(0, 'Model', 'Manage', 'Model names refreshed')
        return True

    def refreshName(self):
        """
        refreshName disables interfering functions in gui and start reloading the
        names list for model in the mount computer. it connects a link to clearRefreshNames
        which enables the former disabled gui buttons and removes the link to the method.
        after it triggers the refresh of names, it finished, because behaviour is event
        driven

        :return: True for test purpose
        """
        self.app.mount.signals.namesDone.connect(self.clearRefreshName)
        self.ui.deleteName.setEnabled(False)
        self.ui.saveName.setEnabled(False)
        self.ui.loadName.setEnabled(False)
        self.changeStyleDynamic(self.ui.refreshName, 'running', True)
        self.changeStyleDynamic(self.ui.modelNameGroup, 'running', True)
        self.app.mount.getNames()
        return True

    def loadName(self):
        """
        loadName take the given name and loads the stored model as the actual alignment
        model for the mount. after that it refreshes the alignment model data in
        mountwizzard

        :return: success
        """
        if self.ui.nameList.currentItem() is None:
            self.msg.emit(2, 'Model', 'Manage error',
                          'No model name selected')
            return False
        modelName = self.ui.nameList.currentItem().text()
        suc = self.app.mount.model.loadName(modelName)
        if not suc:
            self.msg.emit(2, 'Model', 'Manage error',
                          f'Model load failed: [{modelName}]')
            return False
        else:
            self.msg.emit(0, 'Model', 'Manage',
                          f'Model loaded: [{modelName}]')
            self.refreshModel()
            return True

    def saveName(self):
        """
        saveName take the given name and saves the actual alignment model to the
        model database in the mount computer. after that it refreshes the list of
        the alignment model names in mountwizzard.

        :return: success
        """
        dlg = QInputDialog()
        modelName, ok = dlg.getText(self,
                                    'Save model', 'New model name',
                                    QLineEdit.Normal, '')
        if modelName is None or not modelName:
            self.msg.emit(2, 'Model', 'Manage error',
                          'No model name given')
            return False
        if not ok:
            return False

        suc = self.app.mount.model.storeName(modelName)
        if not suc:
            self.msg.emit(2, 'Model', 'Manage error',
                          f'Model cannot be saved [{modelName}]')
            return False
        else:
            self.msg.emit(0, 'Model', 'Manage',
                          f'Model saved: [{modelName}]')
            self.refreshName()
            return True

    def deleteName(self):
        """
        deleteName take the given name and deletes it from the model database in
        the mount computer. after that it refreshes the list of the alignment
        model names in mountwizzard.

        :return: success
        """
        if self.ui.nameList.currentItem() is None:
            self.msg.emit(2, 'Model', 'Manage error',
                          'No model name selected')
            return False

        modelName = self.ui.nameList.currentItem().text()
        suc = self.messageDialog(
            self, 'Delete model', f'Delete model [{modelName}] from database?')
        if not suc:
            return False

        suc = self.app.mount.model.deleteName(modelName)
        if not suc:
            self.msg.emit(2, 'Model', 'Manage error',
                          f'Model cannot be deleted [{modelName}]')
            return False
        else:
            self.msg.emit(0, 'Model', 'Manage',
                          f'Model deleted: [{modelName}]')
            self.refreshName()
            return True

    def writeBuildModelOptimized(self, foundModel, pointsOut):
        """
        :param foundModel:
        :param pointsOut:
        :return: true for test purpose
        """
        actPath = self.app.mwGlob['modelDir'] + '/' + foundModel + '.model'
        newPath = self.app.mwGlob['modelDir'] + '/' + foundModel + '-opt.model'

        try:
            with open(actPath) as actFile:
                actModel = json.load(actFile)
        except Exception as e:
            self.log.warning(f'Cannot load model file: {[actFile]}, error: {e}')
            return False

        newModel = []
        for element in actModel:
            if element['errorIndex'] in pointsOut:
                continue
            newModel.append(element)

        newModel = writeRetrofitData(self.app.mount.model, newModel)
        with open(newPath, 'w+') as newFile:
            json.dump(newModel, newFile, sort_keys=True, indent=4)

        return True

    def clearRefreshModel(self):
        """
        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.refreshModel, 'running', False)
        self.changeStyleDynamic(self.ui.modelGroup, 'running', False)
        self.ui.deleteWorstPoint.setEnabled(True)
        self.ui.runOptimize.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.app.mount.signals.alignDone.disconnect(self.clearRefreshModel)
        self.msg.emit(0, 'Model', 'Manage', 'Align model data refreshed')
        foundModel, _, pointsOut = self.findFittingModel()

        if foundModel:
            self.msg.emit(0, 'Model', 'Manage',
                          f'Found stored model:  [{foundModel}]')
            self.ui.originalModel.setText(foundModel)
            self.writeBuildModelOptimized(foundModel, pointsOut)

        else:
            self.ui.originalModel.setText('No fitting model file found')

        if self.ui.autoUpdateActualAnalyse.isChecked():
            self.showActualModelAnalyse()

        return True

    def refreshModel(self):
        """
        refreshModel disables interfering functions in gui and start reloading
        the alignment model from the mount computer. it connects a link to
        clearRefreshModel which enables the former disabled gui buttons and
        removes the link to the method. after it triggers the refresh of names,
        it finished, because behaviour is event driven

        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.refreshModel, 'running', True)
        self.changeStyleDynamic(self.ui.modelGroup, 'running', True)
        self.app.mount.signals.alignDone.connect(self.clearRefreshModel)
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.runOptimize.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.app.mount.getAlign()

        return True

    def clearModel(self):
        """
        :return:
        """
        suc = self.messageDialog(
            self, 'Clear model', 'Clear actual alignment model')
        if not suc:
            return False

        suc = self.app.mount.model.clearAlign()
        if not suc:
            self.msg.emit(2, 'Model', 'Manage error',
                          'Actual model cannot be cleared')
            return False
        else:
            self.msg.emit(0, 'Model', 'Manage',
                          'Actual model cleared')
            self.refreshModel()
            return True

    def deleteWorstPoint(self):
        """
        :return:
        """
        model = self.app.mount.model
        if not model.numberStars:
            return False

        wIndex = model.starList.index(max(model.starList))
        wStar = model.starList[wIndex]
        error = wStar.errorRMS
        suc = model.deletePoint(wStar.number)
        if not suc:
            self.msg.emit(2, 'Model', 'Manage error',
                          'Worst point cannot be deleted')
            return False
        else:
            text = f'Point: {wIndex + 1:3.0f}, RMS of {error:5.1f}'
            text += ' arcsec deleted.'
            self.msg.emit(0, 'Model', 'Manage error', text)
            self.refreshModel()

        return True

    def runTargetRMS(self):
        """
        :return: True for test purpose
        """
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
            suc = mount.model.deletePoint(wStar.number)
            if not suc:
                self.runningOptimize = False
                self.msg.emit(2, 'Model', 'Manage error',
                              f'Star [{wStar.number + 1:3.0f}] cannot be '
                              f'deleted')
            else:
                text = f'Point: {wStar.number + 1:3.0f}: '
                text += f'RMS of {wStar.errorRMS:5.1f} arcsec deleted.'
                self.msg.emit(0, 'Model', 'Manage', text)
            mount.getAlign()

        else:
            self.finishOptimize()
        return True

    def runSingleRMS(self):
        """
        :return: True for test purpose
        """
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
                self.msg.emit(2, 'Model', 'Manage error',
                              f'Point [{wStar.number + 1:3.0f}] cannot be deleted')
            else:
                text = f'Point: {wStar.number + 1:3.0f}, RMS of {wStar.errorRMS:5.1f}'
                text += ' arcsec deleted.'
                self.msg.emit(0, 'Model', 'Manage', text)
            mount.getAlign()
        else:
            self.finishOptimize()
        return True

    def runOptimize(self):
        """
        :return: true for test purpose
        """
        self.msg.emit(1, 'Model', 'Manage', 'Start optimizing model')
        self.runningOptimize = True
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.ui.refreshModel.setEnabled(False)
        self.ui.cancelOptimize.setEnabled(True)
        self.changeStyleDynamic(self.ui.runOptimize, 'running', True)

        if self.ui.optimizeOverall.isChecked():
            self.app.mount.signals.alignDone.connect(self.runTargetRMS)
            self.runTargetRMS()
        else:
            self.app.mount.signals.alignDone.connect(self.runSingleRMS)
            self.runSingleRMS()
        return True

    def finishOptimize(self):
        """
        :return:
        """
        if self.ui.optimizeOverall.isChecked():
            self.app.mount.signals.alignDone.disconnect(self.runTargetRMS)
        else:
            self.app.mount.signals.alignDone.disconnect(self.runSingleRMS)

        self.changeStyleDynamic(self.ui.runOptimize, 'running', False)
        self.ui.deleteWorstPoint.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.ui.refreshModel.setEnabled(True)
        self.ui.cancelOptimize.setEnabled(False)
        self.msg.emit(0, 'Model', 'Manage', 'Optimizing done')

        return True

    def cancelOptimize(self):
        """
        :return: true for test purpose
        """
        self.runningOptimize = False
        return True

    def showOriginalModelAnalyse(self):
        """
        :return: True for test purpose
        """
        if not self.fittedModelPath:
            return False
        if not os.path.isfile(self.fittedModelPath):
            return False

        self.app.showAnalyse.emit(self.fittedModelPath)
        return True

    def showActualModelAnalyse(self):
        """
        :return: True for test purpose
        """
        if not self.fittedModelPath:
            return False

        temp = os.path.splitext(self.fittedModelPath)
        actualPath = os.path.normpath(temp[0] + '-opt' + temp[1])
        if not os.path.isfile(actualPath):
            return False

        self.app.showAnalyse.emit(actualPath)
        return True

    def pointClicked(self, scatterPlotItem, points, event):
        """
        :param scatterPlotItem:
        :param points:
        :param event: mouse events
        :return: success
        """
        if event.double():
            return False
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        if len(points[0].data()) == 0:
            return False
        index = points[0].data()[0]

        error = self.app.mount.model.starList[index].errorRMS
        text = f'Do you want to delete \npoint {index + 1:3.0f}'
        text += f'\nRMS of {error:5.1f} arcsec'
        isYes = self.messageDialog(self, 'Deleting point', text)
        if not isYes:
            return False

        suc = self.app.mount.model.deletePoint(index)
        if not suc:
            self.msg.emit(2, 'Model', 'Manage error',
                          f'Point {index + 1:3.0f} cannot be deleted')
            return False

        text = f'Point: {index + 1:3.0f}, RMS of {error:5.1f}'
        text += ' arcsec deleted.'
        self.msg.emit(0, 'Model', 'Manage', text)
        self.refreshModel()
        return True
