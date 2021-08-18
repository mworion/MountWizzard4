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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import glob
import json
import os

# external packages
from PyQt5.QtWidgets import QMessageBox, QLineEdit, QInputDialog
import numpy as np
import matplotlib.pyplot

# local import
from logic.modeldata.modelHandling import writeRetrofitData


class ManageModel(object):
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

        self.ui.showErrorValues.clicked.connect(self.showModelPosition)
        self.ui.showNumbers.clicked.connect(self.showModelPosition)
        self.ui.showNoAnnotation.clicked.connect(self.showModelPosition)
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

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.showErrorValues.setChecked(config.get('showErrorValues', False))
        self.ui.showNumbers.setChecked(config.get('showNumbers', False))
        self.ui.showNoAnnotation.setChecked(config.get('showNoAnnotation', True))
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
        config['showErrorValues'] = self.ui.showErrorValues.isChecked()
        config['showNumbers'] = self.ui.showNumbers.isChecked()
        config['showNoAnnotation'] = self.ui.showNoAnnotation.isChecked()
        config['targetRMS'] = self.ui.targetRMS.value()
        config['optimizeOverall'] = self.ui.optimizeOverall.isChecked()
        config['optimizeSingle'] = self.ui.optimizeSingle.isChecked()
        config['autoUpdateActualAnalyse'] = self.ui.autoUpdateActualAnalyse.isChecked()
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

        modelFileList = glob.glob(self.app.mwGlob['modelDir'] + '/*.model')

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
        showModelPosition draws a polar plot of the align model stars and their
        errors in color. the basic setup of the plot is taking place in the
        central widget class. which is instantiated from there. important: the
        coordinate in model is in HA and DEC  and not in RA and DEC. using
        skyfield is a little bit misleading, because you address the hour angle
         as .ra.hours

        :return:    True if ok for testing
        """
        model = self.app.mount.model
        if model is None:
            hasNoStars = True

        else:
            hasNoStars = model.starList is None or not model.starList

        axe, fig = self.generatePolar(widget=self.modelPositionPlot)

        axe.set_yticks(range(0, 90, 10))
        axe.set_ylim(0, 90)
        yLabel = ['', '', '', '', '', '', '', '', '']
        axe.set_yticklabels(yLabel)

        if hasNoStars:
            axe.figure.canvas.draw()
            return False

        altitude = np.asarray([x.alt.degrees for x in model.starList])
        azimuth = np.asarray([x.az.degrees for x in model.starList])
        error = np.asarray([x.errorRMS for x in model.starList])
        self.plane = [(alt, az) for alt, az in zip(altitude, azimuth)]

        # and plot it
        cm = matplotlib.pyplot.cm.get_cmap('RdYlGn_r')
        colors = np.asarray(error)
        scaleErrorMax = max(colors)
        scaleErrorMin = min(colors)
        area = [200 if x >= max(colors) else 60 for x in error]
        theta = azimuth / 180.0 * np.pi
        r = 90 - altitude
        scatter = axe.scatter(theta,
                              r,
                              c=colors,
                              vmin=scaleErrorMin,
                              vmax=scaleErrorMax,
                              s=area,
                              cmap=cm,
                              zorder=0,
                              )

        if self.ui.showErrorValues.isChecked():
            for star in model.starList:
                text = f'{star.errorRMS:3.1f}'
                axe.annotate(text,
                             xy=(theta[star.number - 1],
                                 r[star.number - 1]),
                             color=self.M_BLUE,
                             fontsize=9,
                             fontweight='bold',
                             zorder=1,
                             )

        elif self.ui.showNumbers.isChecked():
            for star in model.starList:
                text = f'{star.number:3.0f}'
                axe.annotate(text,
                             xy=(theta[star.number - 1],
                                 r[star.number - 1]),
                             color=self.M_BLUE,
                             fontsize=9,
                             fontweight='bold',
                             zorder=1,
                             )
        self.generateColorbar(scatter=scatter, figure=fig, label='Error [arcsec]')
        axe.figure.canvas.draw()
        return True

    def showErrorAscending(self):
        """
        showErrorAscending draws a plot of the align model stars and their
        errors in ascending order.

        :return:    True if ok for testing
        """
        model = self.app.mount.model
        if model is None:
            hasNoStars = True

        else:
            hasNoStars = model.starList is None or not model.starList

        axe, _ = self.generateFlat(widget=self.errorAscendingPlot,
                                   title='Model Point Errors in ascending order')

        if hasNoStars:
            axe.figure.canvas.draw()
            return False

        axe.set_xlabel('Star',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Error per Star [RMS]',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        errors = [star.errorRMS for star in model.starList]
        errors.sort()
        index = range(0, len(errors))
        axe.plot(index,
                 errors,
                 marker='.',
                 markersize=5,
                 linestyle='none',
                 color=self.M_GREEN)

        value = self.ui.targetRMS.value()
        axe.plot([0, len(index) - 1],
                 [value, value],
                 lw=3,
                 color=self.M_PINK_H)

        axe.figure.canvas.draw()

        return True

    def showErrorDistribution(self):
        """
        showErrorDistribution draws a polar plot of the align model stars and
        their errors in color. the basic setup of the plot is taking place in the
        central widget class. which is instantiated from there. important: the
        coordinate in model is in HA and DEC  and not in RA and DEC. using
        skyfield is a little bit misleading, because you address the hour
        angle as ra.hours

        :return:    True if ok for testing
        """

        model = self.app.mount.model
        if model is None:
            hasNoStars = True

        else:
            hasNoStars = model.starList is None or not model.starList

        axe, _ = self.generatePolar(widget=self.errorDistributionPlot,
                                    title='Error Distribution')

        if hasNoStars:
            axe.figure.canvas.draw()
            return False

        angles = [star.errorAngle.degrees / 180.0 * np.pi for star in model.starList]
        errors = [star.errorRMS for star in model.starList]

        axe.plot(angles,
                 errors,
                 marker='.',
                 markersize=5,
                 linestyle='none',
                 color=self.M_GREEN)

        values = [self.ui.targetRMS.value()] * 73
        angles = np.arange(0, 365 / 180.0 * np.pi, 5 / 180.0 * np.pi)
        axe.plot(angles,
                 values,
                 lw=3,
                 color=self.M_PINK_H)

        axe.figure.canvas.draw()

        return True

    def clearRefreshName(self):
        """
        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.refreshName, 'running', 'false')
        self.ui.deleteName.setEnabled(True)
        self.ui.saveName.setEnabled(True)
        self.ui.loadName.setEnabled(True)
        self.app.mount.signals.namesDone.disconnect(self.clearRefreshName)
        self.app.message.emit('Model names refreshed', 0)
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
        self.changeStyleDynamic(self.ui.refreshName, 'running', 'true')
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
            self.app.message.emit('No model name selected', 2)
            return False
        modelName = self.ui.nameList.currentItem().text()
        suc = self.app.mount.model.loadName(modelName)
        if not suc:
            self.app.message.emit('Model [{0}] cannot be loaded'.format(modelName), 2)
            return False
        else:
            self.app.message.emit('Model [{0}] loaded'.format(modelName), 0)
            self.refreshModel()
            return True

    def saveName(self):
        """
        saveName take the given name and saves the actual alignment model to the model
        database in the mount computer. after that it refreshes the list of the alignment
        model names in mountwizzard.

        :return: success
        """
        dlg = QInputDialog()
        modelName, ok = dlg.getText(self,
                                    'Save model',
                                    'New model name',
                                    QLineEdit.Normal,
                                    '',
                                    )
        if modelName is None or not modelName:
            self.app.message.emit('No model name given', 2)
            return False
        if not ok:
            return False

        suc = self.app.mount.model.storeName(modelName)
        if not suc:
            self.app.message.emit('Model [{0}] cannot be saved'.format(modelName), 2)
            return False
        else:
            self.app.message.emit('Model [{0}] saved'.format(modelName), 0)
            self.refreshName()
            return True

    def deleteName(self):
        """
        deleteName take the given name and deletes it from the model database in the
        mount computer. after that it refreshes the list of the alignment model names in
        mountwizzard.

        :return: success
        """
        if self.ui.nameList.currentItem() is None:
            self.app.message.emit('No model name selected', 2)
            return False

        modelName = self.ui.nameList.currentItem().text()
        msg = QMessageBox
        reply = msg.question(self,
                             'Delete model',
                             f'Delete model [{modelName}] from database?',
                             msg.Yes | msg.No,
                             msg.No,
                             )
        if reply != msg.Yes:
            return False

        suc = self.app.mount.model.deleteName(modelName)
        if not suc:
            self.app.message.emit('Model [{0}] cannot be deleted'.format(modelName), 2)
            return False
        else:
            self.app.message.emit('Model [{0}] deleted'.format(modelName), 0)
            self.refreshName()
            return True

    def writeBuildModelOptimized(self, foundModel, pointsIn, pointsOut):
        """
        :param foundModel:
        :param pointsIn:
        :param pointsOut:
        :return: true for test purpose
        """
        actPath = self.app.mwGlob['modelDir'] + '/' + foundModel + '.model'
        newPath = self.app.mwGlob['modelDir'] + '/' + foundModel + '-opt.model'

        with open(actPath) as actFile:
            actModel = json.load(actFile)

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
        self.changeStyleDynamic(self.ui.refreshModel, 'running', 'false')
        self.ui.deleteWorstPoint.setEnabled(True)
        self.ui.runOptimize.setEnabled(True)
        self.ui.cancelOptimize.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.app.mount.signals.alignDone.disconnect(self.clearRefreshModel)
        self.app.message.emit('Align model data refreshed', 0)

        foundModel, pointsIn, pointsOut = self.findFittingModel()

        if foundModel:
            self.app.message.emit(f'Found stored model:  [{foundModel}]', 0)
            self.ui.originalModel.setText(foundModel)
            self.writeBuildModelOptimized(foundModel, pointsIn, pointsOut)

        else:
            self.ui.originalModel.setText('No fitting model file found')

        if self.ui.autoUpdateActualAnalyse.isChecked():
            self.showActualModelAnalyse()

        return True

    def refreshModel(self):
        """
        refreshModel disables interfering functions in gui and start reloading the
        alignment model from the mount computer. it connects a link to clearRefreshModel
        which enables the former disabled gui buttons and removes the link to the method.
        after it triggers the refresh of names, it finished, because behaviour is event
        driven

        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.refreshModel, 'running', 'true')
        self.app.mount.signals.alignDone.connect(self.clearRefreshModel)
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.runOptimize.setEnabled(False)
        self.ui.cancelOptimize.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.app.mount.getAlign()

        return True

    def clearModel(self):
        """
        :return:
        """
        msg = QMessageBox
        reply = msg.question(self,
                             'Clear model',
                             'Clear actual alignment model?',
                             msg.Yes | msg.No,
                             msg.No,
                             )
        if reply == msg.No:
            return False

        suc = self.app.mount.model.clearAlign()
        if not suc:
            self.app.message.emit('Actual model cannot be cleared', 2)
            return False

        else:
            self.app.message.emit('Actual model cleared', 0)
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
            self.app.message.emit('Worst point cannot be deleted', 2)
            return False

        else:
            text = f'Point: {wIndex + 1:3.0f}, RMS of {error:5.1f}'
            text += ' arcsec deleted.'
            self.app.message.emit(text, 0)
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
                self.app.message.emit(f'Star [{wStar.number + 1:3.0f}] cannot be deleted', 2)

            else:
                text = f'Point: {wStar.number + 1:3.0f}: '
                text += f'RMS of {wStar.errorRMS:5.1f} arcsec deleted.'
                self.app.message.emit(text, 0)

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
                self.app.message.emit(f'Point {wStar.number + 1:3.0f} cannot be deleted', 2)

            else:
                text = f'Point: {wStar.number + 1:3.0f}, RMS of {wStar.errorRMS:5.1f}'
                text += ' arcsec deleted.'
                self.app.message.emit(text, 0)

            mount.getAlign()

        else:
            self.finishOptimize()
        return True

    def runOptimize(self):
        """
        :return: true for test purpose
        """
        self.app.message.emit('Start optimizing model', 2)
        self.runningOptimize = True
        self.ui.deleteWorstPoint.setEnabled(False)
        self.ui.clearModel.setEnabled(False)
        self.ui.refreshModel.setEnabled(False)
        self.changeStyleDynamic(self.ui.runOptimize, 'running', 'true')
        self.changeStyleDynamic(self.ui.cancelOptimize, 'cancel', 'true')

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

        self.changeStyleDynamic(self.ui.runOptimize, 'running', 'false')
        self.ui.deleteWorstPoint.setEnabled(True)
        self.ui.clearModel.setEnabled(True)
        self.ui.refreshModel.setEnabled(True)
        self.changeStyleDynamic(self.ui.cancelOptimize, 'cancel', 'false')
        self.app.message.emit('Optimizing done', 2)

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
        actualPath = temp[0] + '-opt' + temp[1]
        if not os.path.isfile(actualPath):
            return False

        self.app.showAnalyse.emit(actualPath)
        return True

    def deleteDialog(self, question):
        """
        :param question:
        :return: OK
        """
        msg = QMessageBox
        reply = msg.question(self, 'Deleting point', question, msg.Yes | msg.No, msg.No)
        if reply != msg.Yes:
            return False

        else:
            return True

    def onMouseEdit(self, event):
        """
        onMouseEdit handles the mouse event in normal mode. this means depending on the
        edit mode (horizon or model points) a left click adds a new point and right click
        deletes the selected point.

        :param event: mouse events
        :return: success
        """
        if not event.inaxes:
            return False

        if not self.plane:
            return False

        if not event.dblclick:
            return False

        event.xdata = (np.degrees(event.xdata) + 360) % 360
        event.ydata = 90 - event.ydata
        index = self.getIndexPoint(event=event, plane=self.plane, epsilon=5)
        if index is None:
            return False

        error = self.app.mount.model.starList[index].errorRMS
        text = f'Do you want to delete \npoint {index + 1:3.0f}'
        text += f'\nRMS of {error:5.1f} arcsec'
        isYes = self.deleteDialog(text)
        if not isYes:
            return False

        suc = self.app.mount.model.deletePoint(index)
        if not suc:
            self.app.message.emit(f'Point {index + 1:3.0f} cannot be deleted', 2)
            return False

        text = f'Point: {index + 1:3.0f}, RMS of {error:5.1f}'
        text += ' arcsec deleted.'
        self.app.message.emit(text, 0)
        self.refreshModel()

        return True
