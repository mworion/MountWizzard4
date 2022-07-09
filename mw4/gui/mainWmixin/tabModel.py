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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import queue
import os
import time
import shutil
import json
from datetime import datetime

# external packages
from mountcontrol.alignStar import AlignStar
from mountcontrol.convert import convertToHMS, convertToDMS

# local import
from base.transform import JNowToJ2000, J2000ToJNow
from gui.utilities.toolsQtWidget import QMultiWait, sleepAndEvents
from logic.modeldata.modelHandling import writeRetrofitData


class Model:
    """
    """

    def __init__(self):
        self.timeStartModeling = None
        self.modelName = ''
        self.model = []
        self.imageDir = ''

        ms = self.app.mount.signals
        ms.alignDone.connect(self.updateAlignGUI)
        ms.alignDone.connect(self.updateTurnKnobsGUI)

        self.ui.runModel.clicked.connect(self.modelBuild)
        self.ui.cancelModel.clicked.connect(self.cancelRun)
        self.ui.endModel.clicked.connect(self.processModelData)
        self.ui.pauseModel.clicked.connect(self.pauseBuild)
        self.ui.batchModel.clicked.connect(self.loadProgramModel)
        self.ui.plateSolveSync.clicked.connect(self.plateSolveSync)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.retriesReverse.setChecked(config.get('retriesReverse', False))
        self.ui.parkMountAfterModel.setChecked(config.get('parkMountAfterModel', False))
        self.ui.numberBuildRetries.setValue(config.get('numberBuildRetries', 0))
        self.ui.progressiveTiming.setChecked(config.get('progressiveTiming', False))
        self.ui.normalTiming.setChecked(config.get('normalTiming', False))
        self.ui.conservativeTiming.setChecked(config.get('conservativeTiming', True))

        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['retriesReverse'] = self.ui.retriesReverse.isChecked()
        config['parkMountAfterModel'] = self.ui.parkMountAfterModel.isChecked()
        config['numberBuildRetries'] = self.ui.numberBuildRetries.value()
        config['progressiveTiming'] = self.ui.progressiveTiming.isChecked()
        config['normalTiming'] = self.ui.normalTiming.isChecked()
        config['conservativeTiming'] = self.ui.conservativeTiming.isChecked()
        return True

    def updateAlignGUI(self, model):
        """
        updateAlignGUI shows the data which is received through the getain
        command. this is mainly polar and ortho errors as well as basic model
        data.

        :param model:
        :return:    True if ok for testing
        """
        self.guiSetText(self.ui.numberStars, '2.0f', model.numberStars)
        self.guiSetText(self.ui.numberStars1, '2.0f', model.numberStars)
        self.guiSetText(self.ui.errorRMS, '5.1f', model.errorRMS)
        self.guiSetText(self.ui.errorRMS1, '5.1f', model.errorRMS)
        self.guiSetText(self.ui.terms, '2.0f', model.terms)
        val = model.positionAngle.degrees if model.positionAngle is not None else None
        self.guiSetText(self.ui.positionAngle, '5.1f', val)
        val = model.polarError.degrees * 3600 if model.polarError is not None else None
        self.guiSetText(self.ui.polarError, '5.0f', val)
        val = model.orthoError.degrees * 3600 if model.orthoError is not None else None
        self.guiSetText(self.ui.orthoError, '5.0f', val)
        val = model.azimuthError.degrees if model.azimuthError is not None else None
        self.guiSetText(self.ui.azimuthError, '5.1f', val)
        val = model.altitudeError.degrees if model.altitudeError is not None else None
        self.guiSetText(self.ui.altitudeError, '5.1f', val)

        return True

    def updateTurnKnobsGUI(self, model):
        """
        :param model:
        :return:    True if ok for testing
        """
        if model.azimuthTurns is not None:
            if model.azimuthTurns > 0:
                text = '{0:3.1f} revs left'.format(abs(model.azimuthTurns))
            else:
                text = '{0:3.1f} revs right'.format(abs(model.azimuthTurns))
        else:
            text = '-'

        self.ui.azimuthTurns.setText(text)
        if model.altitudeTurns is not None:
            if model.altitudeTurns > 0:
                text = '{0:3.1f} revs down'.format(abs(model.altitudeTurns))
            else:
                text = '{0:3.1f} revs up'.format(abs(model.altitudeTurns))
        else:
            text = '-'

        self.ui.altitudeTurns.setText(text)
        return True

    def updateModelProgress(self, number=0, count=0):
        """
        updateModelProgress calculated from the elapsed time and number of point
        with taking actual processing time into account a estimation of duration
        and finishing time of the modeling process and updates this in the gui

        :param number: total number of model points
        :param count: index of the actual processed point
        :return: success
        """
        if not 0 < count <= number:
            return False

        fraction = count / number

        secondsElapsed = time.time() - self.timeStartModeling
        secondsBase = secondsElapsed / fraction
        secondsEstimated = secondsBase * (1 - fraction)

        timeElapsed = time.gmtime(secondsElapsed)
        timeEstimated = time.gmtime(secondsEstimated)
        timeFinished = time.localtime(time.time() + secondsEstimated)

        self.ui.timeElapsed.setText(datetime(*timeElapsed[:6]).strftime('%H:%M:%S'))
        self.ui.timeEstimated.setText(datetime(*timeEstimated[:6]).strftime('%H:%M:%S'))
        self.ui.timeFinished.setText(datetime(*timeFinished[:6]).strftime('%H:%M:%S'))

        modelPercent = int(100 * fraction)
        self.ui.modelProgress.setValue(modelPercent)
        return True

    def setupModelRunContextAndGuiStatus(self):
        """
        :return:
        """
        self.changeStyleDynamic(self.ui.runModel, 'running', True)
        self.changeStyleDynamic(self.ui.cancelModel, 'cancel', True)
        self.changeStyleDynamic(self.ui.cancelModel, 'pause', False)
        self.ui.cancelModel.setEnabled(True)
        self.ui.endModel.setEnabled(True)
        self.ui.pauseModel.setEnabled(True)
        self.ui.plateSolveSync.setEnabled(False)
        self.ui.runFlexure.setEnabled(False)
        self.ui.runHysteresis.setEnabled(False)
        self.ui.batchModel.setEnabled(False)
        self.app.operationRunning.emit(True)
        return True

    def restoreModelDefaultContextAndGuiStatus(self):
        """
        restoreModelDefaultContextAndGuiStatus will reset all gui elements to
        the idle or default state and new actions could be started again

        :return: true for test purpose
        """
        self.changeStyleDynamic(self.ui.runModel, 'running', False)
        self.changeStyleDynamic(self.ui.cancelModel, 'cancel', False)
        self.changeStyleDynamic(self.ui.pauseModel, 'pause', False)
        self.ui.runModel.setEnabled(True)
        self.ui.cancelModel.setEnabled(False)
        self.ui.endModel.setEnabled(False)
        self.ui.pauseModel.setEnabled(False)
        self.ui.batchModel.setEnabled(True)
        self.ui.plateSolveSync.setEnabled(True)
        self.ui.runFlexure.setEnabled(True)
        self.ui.runHysteresis.setEnabled(True)
        self.ui.timeEstimated.setText('00:00:00')
        self.ui.timeElapsed.setText('00:00:00')
        self.ui.timeFinished.setText('00:00:00')
        self.ui.mPoints.setText('-')
        self.ui.mSlew.setText('-')
        self.ui.mImage.setText('-')
        self.ui.mSolve.setText('-')
        self.ui.modelProgress.setValue(0)
        self.app.operationRunning.emit(False)
        return True

    def pauseBuild(self):
        """
        :return: True for test purpose
        """
        if self.ui.pauseModel.property('pause'):
            self.changeStyleDynamic(self.ui.pauseModel, 'pause', False)
            self.ui.runModel.setEnabled(True)
        else:
            self.changeStyleDynamic(self.ui.pauseModel, 'pause', True)
            self.ui.runModel.setEnabled(False)

        return True

    def retrofitModel(self):
        """
        retrofitModel reads the actual model points and results out of the mount
        computer and adds the optimized (recalculated) error values to the point.
        that's necessary, because when imaging and solving a point the error is
        related to this old model. when programming a new model, all point will
        be recalculated be the mount computer an get a new error value which is
        based on the new model.

        :return: True for test purpose
        """
        mountModel = self.app.mount.model
        if len(mountModel.starList) != len(self.model):
            text = f'length starList [{len(mountModel.starList)}] and length '
            text += f'model [{len(self.model)}] is different'
            self.log.debug(text)
            self.model = []

        self.model = writeRetrofitData(mountModel, self.model)
        return True

    def saveModelFinish(self):
        """
        saveModelFinish is the callback after the new model data is loaded from
        the mount computer. first is disables the signals. New we have the
        original model build data which was programmed to the mount and the
        retrieved model data after the mount optimized the model. retrofitModel()
        combines this data to a signal data structure. after that it saves the
        model data for later use.

        with this data, the model could be reprogrammed without doing some imaging,
        it could be added with other data to extend the model to a broader base.

        :return: True for test purpose
        """
        self.app.mount.signals.alignDone.disconnect(self.saveModelFinish)
        self.retrofitModel()
        self.msg.emit(0, self.runType, 'Run',
                      f'Writing model [{self.modelName}]')
        saveData = self.generateSaveModel()
        modelPath = f'{self.app.mwGlob["modelDir"]}/{self.modelName}.model'
        with open(modelPath, 'w') as outfile:
            json.dump(saveData, outfile, sort_keys=True, indent=4)

        return True

    def saveModelPrepare(self):
        """
        saveModelPrepare checks boundaries for model save and prepares the
        signals. the save a model we need the calculated parameters from the
        mount after the new points are programmed in an earlier step. the new
        model data is retrieved from the mount by refreshModel() call. this call
        needs some time and has a callback which is set here. the calculations
        and the saving is done in the callback.

        :return: success
        """
        if len(self.model) < 3:
            self.log.debug(f'Only {len(self.model)} points available')
            return False

        self.app.mount.signals.alignDone.connect(self.saveModelFinish)
        return True

    @staticmethod
    def generateBuildData(model=None):
        """
        generateBuildData takes the model data and generates from it a data
        structure needed for programming the model into the mount computer.

        :param model:
        :return: build
        """
        if model is None:
            model = []

        build = list()
        for mPoint in model:
            programmingPoint = AlignStar(mCoord=(mPoint['raJNowM'],
                                                 mPoint['decJNowM']),
                                         sCoord=(mPoint['raJNowS'],
                                                 mPoint['decJNowS']),
                                         sidereal=mPoint['siderealTime'],
                                         pierside=mPoint['pierside'],
                                         )
            build.append(programmingPoint)
        return build

    def programModelToMount(self, model):
        """
        :param model:
        :return: True for test purpose
        """
        build = self.generateBuildData(model=model)
        suc = self.app.mount.model.programAlign(build)
        if not suc:
            return False

        self.saveModelPrepare()
        self.app.mount.model.storeName('actual')
        self.refreshName()
        self.refreshModel()
        return True

    def renewHemisphereView(self):
        """
        :return: True for test purpose
        """
        for i in range(0, len(self.app.data.buildP)):
            self.app.data.setStatusBuildP(i, True)

        self.app.updatePointMarker.emit()
        return True

    def processModelData(self, runResult):
        """
        :return:
        """
        self.restoreModelDefaultContextAndGuiStatus()
        if len(runResult) < 3:
            self.msg.emit(2, 'Model', 'Run error',
                          f'{self.modelName} Not enough valid model points')
            return False

        self.msg.emit(0, 'Model', 'Run',
                      'Programming model to mount')
        suc = self.programModelToMount(runResult)
        if suc:
            self.msg.emit(0, 'Model', 'Run',
                          'Model programmed with success')
        else:
            self.msg.emit(2, 'Model', 'Run error',
                          'Model programming error')

        self.msg.emit(1, self.runType, 'Run',
                      f'Modeling finished [{self.modelName}]')
        self.playSound('ModelingFinished')
        self.renewHemisphereView()

        return True

    def checkModelRunConditions(self):
        """
        :return:
        """
        if len(self.app.data.buildP) < 2:
            t = 'No modeling start because less than 3 points'
            self.msg.emit(2, 'Model', 'Run error', t)
            return False

        if len(self.app.data.buildP) > 99:
            t = 'No modeling start because more than 99 points'
            self.msg.emit(2, 'Model', 'Run error', t)
            return False

        excludeDonePoints = self.ui.excludeDonePoints.isChecked()
        if len([x for x in self.app.data.buildP if x[2]]) < 3 and excludeDonePoints:
            t = 'No modeling start because less than 3 points left over'
            self.msg.emit(2, 'Model', 'Run error', t)
            return False

        if self.ui.plateSolveDevice.currentText().startswith('No device'):
            self.msg.emit(2, 'Model', 'Run error',
                          'No plate solver selected')
            return False

        sucApp, sucIndex = self.app.plateSolve.checkAvailability()
        if not (sucApp and sucIndex):
            self.msg.emit(2, 'Model', 'Run error',
                          'No valid configuration for plate solver')
            return False

        return True

    def clearAlignAndBackup(self):
        """
        :return:
        """
        suc = self.app.mount.model.clearAlign()
        if not suc:
            self.msg.emit(2, 'Model', 'Run error',
                          'Actual model cannot be cleared')
            self.msg.emit(2, '', '', 'Model build cancelled')
            return False
        else:
            self.msg.emit(0, 'Model', 'Run',
                          'Actual model clearing, waiting 1s')
            sleepAndEvents(1000)
            self.msg.emit(0, '', '', 'Actual model cleared')
            self.refreshModel()

        suc = self.app.mount.model.deleteName('backup')
        if not suc:
            self.log.warning('Cannot delete backup model on mount')

        suc = self.app.mount.model.storeName('backup')
        if not suc:
            t = 'Cannot save backup model on mount, proceeding with model run'
            self.msg.emit(2, 'Model', 'Run error', t)

        return True

    def setupModelFilenamesAndDirectories(self):
        """
        :return:
        """
        nameTime = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        self.modelName = f'm-{nameTime}-{self.lastGenerator}'
        self.imageDir = f'{self.app.mwGlob["imageDir"]}/{self.modelName}'

        if not os.path.isdir(self.imageDir):
            os.mkdir(self.imageDir)

        return True

    def setupModelPointsAndContextData(self):
        """
        :return:
        """
        plateSolveApp = self.ui.plateSolveDevice.currentText()
        exposureTime = self.ui.expTime.value()
        binning = int(self.ui.binning.value())
        subFrame = self.ui.subFrame.value()
        fastReadout = self.ui.fastDownload.isChecked()
        focalLength = self.ui.focalLength.value()
        lenSequence = len(self.app.data.buildP)
        framework = self.app.plateSolve.framework
        solveTimeout = self.app.plateSolve.run[framework].timeout
        searchRadius = self.app.plateSolve.run[framework].searchRadius
        modelPoints = list()
        for index, point in enumerate(self.app.data.buildP):
            if self.ui.excludeDonePoints.isChecked() and not point[2]:
                continue

            m = dict()
            imagePath = f'{self.imageDir}/image-{index + 1:03d}.fits'
            m['imagePath'] = imagePath
            m['exposureTime'] = exposureTime
            m['binning'] = binning
            m['subFrame'] = subFrame
            m['fastReadout'] = fastReadout
            m['lenSequence'] = lenSequence
            m['countSequence'] = index + 1
            m['pointNumber'] = index + 1
            m['modelName'] = self.modelName
            m['imagePath'] = imagePath
            m['plateSolveApp'] = plateSolveApp
            m['solveTimeout'] = solveTimeout
            m['searchRadius'] = searchRadius
            m['focalLength'] = focalLength
            m['altitude'] = point[0]
            m['azimuth'] = point[1]
            modelPoints.append(m)
        return modelPoints

    def modelBuild(self):
        """
        modelBuild sets the adequate gui elements, selects the model points and
        calls the core modeling method.

        :return: true for test purpose
        """
        if not self.checkModelRunConditions():
            return False
        if not self.clearAlignAndBackup():
            return False

        self.setupModelFilenamesAndDirectories()
        modelPoints = self.setupModelPointsAndContextData()
        if not modelPoints:
            self.msg.emit(2, 'Model', 'Run error',
                          'Modeling cancelled, no valid points')
            return False

        self.setupModelRunContextAndGuiStatus()
        self.msg.emit(1, 'Model', 'Run',
                      f'Modeling start [{self.modelName}]')
        retryCounter = self.ui.numberBuildRetries.value()
        runType = 'Model'
        self.timeStartModeling = time.time()
        self.cycleThroughPoints(modelPoints=modelPoints,
                                retryCounter=retryCounter,
                                runType=runType,
                                processData=self.processModelData,
                                progress=self.updateModelProgress)
        return True

    def loadProgramModel(self):
        """
        loadProgramModel selects one or more models from the file system,
        combines them if more than one was selected and programs them into the
        mount computer.

        :return: success
        """
        folder = self.app.mwGlob['modelDir']
        ret = self.openFile(self, 'Open model file', folder, 'Model files (*.model)',
                            multiple=True)
        loadFilePath, _, _ = ret

        if not loadFilePath:
            return False
        if isinstance(loadFilePath, str):
            loadFilePath = [loadFilePath]
        if not self.clearAlignAndBackup():
            return False

        self.msg.emit(1, 'Model', 'Run',
                      'Programing models')
        modelJSON = list()
        for index, file in enumerate(loadFilePath):
            self.msg.emit(0, '', '',
                          f'Loading model [{os.path.basename(file)}]')
            with open(file, 'r') as infile:
                model = json.load(infile)
                modelJSON += model

        if len(modelJSON) > 99:
            self.msg.emit(2, 'Model', 'Run error',
                          'Model(s) exceed(s) limit of 99 points')
            return False

        self.msg.emit(0, 'Model', 'Run',
                      f'Programming {index + 1} model(s) to mount')
        suc = self.programModelToMount(modelJSON)

        if suc:
            self.msg.emit(0, 'Model', 'Run',
                          'Model programmed with success')
        else:
            self.msg.emit(2, 'Model', 'Run error',
                          'Model programming error')

        return suc

    def syncMountAndClearUp(self):
        """
        :return:
        """
        self.ui.runModel.setEnabled(True)
        self.ui.batchModel.setEnabled(True)
        self.ui.plateSolveSync.setEnabled(True)
        self.ui.runFlexure.setEnabled(True)
        self.ui.runHysteresis.setEnabled(True)
        return True

    def solveDone(self, result=None):
        """
        :param result: result (named tuple)
        :return: success
        """
        self.app.plateSolve.signals.done.disconnect(self.solveDone)

        if not result:
            self.msg.emit(2, 'Model', 'Solving error',
                          'Result missing')
            return False

        if result['success']:
            text = f'RA: {convertToHMS(result["raJ2000S"])} '
            text += f'({result["raJ2000S"].hours:4.3f}), '
            self.msg.emit(0, 'Model', 'Solved ', text)
            text = f'DEC: {convertToDMS(result["decJ2000S"])} '
            text += f'({result["decJ2000S"].degrees:4.3f}), '
            self.msg.emit(0, '', '', text)
            text = f'Angle: {result["angleS"]:3.0f}, '
            self.msg.emit(0, '', '', text)
            text = f'Scale: {result["scaleS"]:4.3f}, '
            self.msg.emit(0, '', '', text)
            text = f'Error: {result["errorRMS_S"]:4.1f}'
            self.msg.emit(0, '', '', text)

        else:
            self.msg.emit(2, 'Model', 'Solve error',
                          f'{result.get("message")}')
            return False

        self.app.showImage.emit(result['solvedPath'])

        obs = self.app.mount.obsSite
        timeJD = obs.timeJD
        raJNow, decJNow = J2000ToJNow(result['raJ2000S'],
                                      result['decJ2000S'],
                                      timeJD)
        obs.setTargetRaDec(raJNow, decJNow)
        suc = obs.syncPositionToTarget()
        if suc:
            t = 'Successfully synced model in mount to coordinates'
            self.msg.emit(1, 'Model', 'Run', t)
        else:
            t = 'No sync, match failed because coordinates to far off for model'
            self.msg.emit(2, 'Model', 'Run error', t)
        return suc

    def solveImage(self, imagePath=''):
        """
        :param imagePath:
        :return:
        """
        if not imagePath:
            return False
        if not os.path.isfile(imagePath):
            return False

        self.app.plateSolve.signals.done.connect(self.solveDone)
        self.app.plateSolve.solveThreading(fitsPath=imagePath)
        t = f'[{os.path.basename(imagePath)}]'
        self.msg.emit(0, 'Model', 'Solving', t)
        return True

    def exposeRaw(self, expTime, binning, subFrame, fastReadout, focalLength):
        """
        :param expTime:
        :param binning:
        :param subFrame:
        :param fastReadout:
        :param focalLength:
        :return: True for test purpose
        """
        time = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        fileName = time + '-sync.fits'
        imagePath = self.app.mwGlob['imageDir'] + '/' + fileName

        self.app.camera.expose(imagePath=imagePath,
                               expTime=expTime,
                               binning=binning,
                               subFrame=subFrame,
                               fastReadout=fastReadout,
                               focalLength=focalLength
                               )
        text = f'{os.path.basename(imagePath)}'
        self.msg.emit(0, 'Model', 'Exposing', text)
        text = f'Duration:{expTime:3.0f}s  '
        self.msg.emit(0, '', '', f'{text}')
        text = f'Bin:{binning:1.0f}'
        self.msg.emit(0, '', '', f'{text}')
        text = f'Sub:{subFrame:3.0f}%'
        self.msg.emit(0, '', '', f'{text}')
        return True

    def exposeImageDone(self, imagePath=''):
        """
        :param imagePath:
        :return: True for test purpose
        """
        self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        text = f'{os.path.basename(imagePath)}'
        self.msg.emit(0, 'Model', 'Exposed', text)
        self.solveImage(imagePath)
        return True

    def exposeImage(self):
        """
        :return: success
        """
        expTime = self.ui.expTime.value()
        binning = self.ui.binning.value()
        subFrame = self.ui.subFrame.value()
        fastReadout = self.ui.fastDownload.isChecked()
        focalLength = self.ui.focalLength.value()
        self.app.camera.signals.saved.connect(self.exposeImageDone)
        self.exposeRaw(expTime, binning, subFrame, fastReadout, focalLength)
        return True

    def plateSolveSync(self):
        """
        :return:
        """
        self.msg.emit(1, 'Model', 'Sync',
                      'Starting plate solve and sync model in mount')
        sucApp, sucIndex = self.app.plateSolve.checkAvailability()
        if not (sucApp and sucIndex):
            self.msg.emit(2, 'Model', 'Sync error',
                          'No valid configuration for plate solver')
            return False

        self.ui.runModel.setEnabled(False)
        self.ui.batchModel.setEnabled(False)
        self.ui.plateSolveSync.setEnabled(False)
        self.ui.runFlexure.setEnabled(False)
        self.ui.runHysteresis.setEnabled(False)
        self.exposeImage()
        return True
