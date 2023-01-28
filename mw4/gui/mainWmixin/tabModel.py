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
import os
import time
import json
from datetime import datetime

# external packages
from mountcontrol.alignStar import AlignStar
from mountcontrol.convert import convertToHMS, convertToDMS

# local import
from base.transform import J2000ToJNow
from gui.utilities.toolsQtWidget import sleepAndEvents
from logic.modeldata.modelHandling import writeRetrofitData


class Model:
    """
    """

    def __init__(self):
        self.timeStartModeling = None
        self.modelName = ''
        self.model = []

        ms = self.app.mount.signals
        ms.alignDone.connect(self.updateAlignGUI)
        ms.alignDone.connect(self.updateTurnKnobsGUI)

        self.ui.runModel.clicked.connect(self.modelBuild)
        self.ui.pauseModel.clicked.connect(self.pauseBuild)
        self.ui.dataModel.clicked.connect(self.loadProgramModel)
        self.ui.plateSolveSync.clicked.connect(self.plateSolveSync)
        self.app.operationRunning.connect(self.setModelOperationMode)

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

    def setModelOperationMode(self, status):
        """
        :param status:
        :return:
        """
        if status == 1:
            self.ui.plateSolveSyncGroup.setEnabled(False)
            self.ui.dataModelGroup.setEnabled(False)
        elif status == 2:
            self.ui.runModelGroup.setEnabled(False)
            self.ui.dataModelGroup.setEnabled(False)
        elif status == 3:
            self.ui.runModelGroup.setEnabled(False)
            self.ui.plateSolveSyncGroup.setEnabled(False)
        elif status == 0:
            self.ui.runModelGroup.setEnabled(True)
            self.ui.plateSolveSyncGroup.setEnabled(True)
            self.ui.dataModelGroup.setEnabled(True)
            self.changeStyleDynamic(self.ui.plateSolveSync, 'running', False)
        else:
            self.ui.runModelGroup.setEnabled(False)
            self.ui.plateSolveSyncGroup.setEnabled(False)
            self.ui.dataModelGroup.setEnabled(False)

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

    def updateModelProgress(self, mPoint):
        """
        :param mPoint:
        :return: success
        """
        number = mPoint.get('lenSequence', 0)
        count = mPoint.get('countSequence', 0)

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
        self.ui.numberPoints.setText(f'{count} / {number}')
        self.ui.modelProgress.setValue(modelPercent)
        return True

    def setupModelRunContextAndGuiStatus(self):
        """
        :return:
        """
        self.changeStyleDynamic(self.ui.runModel, 'running', True)
        self.ui.cancelModel.setEnabled(True)
        self.ui.endModel.setEnabled(True)
        self.ui.pauseModel.setEnabled(True)
        return True

    def pauseBuild(self):
        """
        :return: True for test purpose
        """
        if not self.ui.pauseModel.property('pause'):
            self.changeStyleDynamic(self.ui.pauseModel, 'color', 'yellow')
            self.changeStyleDynamic(self.ui.pauseModel, 'pause', True)
        else:
            self.changeStyleDynamic(self.ui.pauseModel, 'color', '')
            self.changeStyleDynamic(self.ui.pauseModel, 'pause', False)

        return True

    def retrofitModel(self):
        """
        retrofitModel reads the actual model points and results out of the mount
        computer and adds the optimized (recalculated) error values to the point.
        that's necessary, because when imaging and solving a point the error is
        related to this old model. when programming a new model, all point will
        be recalculated be the mount computer and get a new error value which is
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
        self.msg.emit(0, 'Model', 'Run',
                      f'Writing model [{self.modelName}]')
        saveData = self.generateSaveData()
        modelPath = f'{self.app.mwGlob["modelDir"]}/{self.modelName}.model'
        with open(modelPath, 'w') as outfile:
            json.dump(saveData, outfile, sort_keys=True, indent=4)

        return True

    def generateBuildData(self):
        """
        generateBuildData takes the model data and generates from it a data
        structure needed for programming the model into the mount computer.
        :return: build
        """
        build = list()
        for mPoint in self.model:
            programmingPoint = AlignStar(mCoord=(mPoint['raJNowM'],
                                                 mPoint['decJNowM']),
                                         sCoord=(mPoint['raJNowS'],
                                                 mPoint['decJNowS']),
                                         sidereal=mPoint['siderealTime'],
                                         pierside=mPoint['pierside'])
            build.append(programmingPoint)
        return build

    def programModelToMount(self):
        """
        :return: True for test purpose
        """
        build = self.generateBuildData()
        if len(build) < 3:
            self.log.debug(f'Only {len(build)} points available')
            return False
        suc = self.app.mount.model.programAlign(build)
        if not suc:
            self.log.debug('Program align failed')
            return False

        self.app.mount.signals.alignDone.connect(self.saveModelFinish)
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

    def processModelData(self, model):
        """
        :return:
        """
        self.model = model
        if len(self.model) < 3:
            self.msg.emit(2, 'Model', 'Run error',
                          f'{self.modelName} Not enough valid model points')
            self.app.operationRunning.emit(0)
            return False

        self.msg.emit(0, 'Model', 'Run',
                      'Programming model to mount')
        suc = self.programModelToMount()
        if suc:
            self.msg.emit(0, 'Model', 'Run',
                          'Model programmed with success')
        else:
            self.msg.emit(2, 'Model', 'Run error',
                          'Model programming error')

        self.msg.emit(1, 'Model', 'Run',
                      f'Modeling finished [{self.modelName}]')
        self.app.playSound.emit('RunFinished')
        self.renewHemisphereView()
        self.app.operationRunning.emit(0)
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
            t = 'No modeling start because less than 3 points'
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

    def modelBuild(self):
        """
        modelBuild sets the adequate gui elements, selects the model points and
        calls the core modeling method.

        :return: true for test purpose
        """
        prefix = 'm'
        postfix = self.lastGenerator

        self.modelName, imgDir = self.setupFilenamesAndDirectories(
            prefix=prefix, postfix=postfix)
        self.msg.emit(1, 'Model', 'Run', f'Starting [{self.modelName}]')

        if not self.checkModelRunConditions():
            return False
        if not self.clearAlignAndBackup():
            return False

        self.app.operationRunning.emit(1)

        data = []
        for point in self.app.data.buildP:
            if self.ui.excludeDonePoints.isChecked() and not point[2]:
                continue
            data.append(point)

        modelPoints = self.setupRunPoints(data=data, imgDir=imgDir,
                                          name=self.modelName, waitTime=0)
        if not modelPoints:
            self.msg.emit(2, 'Model', 'Run error',
                          'Modeling cancelled, no valid points')
            self.app.operationRunning.emit(0)
            return False

        self.setupModelRunContextAndGuiStatus()
        retryCounter = self.ui.numberBuildRetries.value()
        runType = 'Model'
        keepImages = self.ui.keepModelImages.isChecked()
        self.timeStartModeling = time.time()
        self.cycleThroughPoints(modelPoints=modelPoints,
                                retryCounter=retryCounter,
                                runType=runType,
                                processData=self.processModelData,
                                progress=self.updateModelProgress,
                                imgDir=imgDir,
                                keepImages=keepImages)
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

        self.app.operationRunning.emit(3)
        if not self.clearAlignAndBackup():
            self.app.operationRunning.emit(0)
            return False

        self.msg.emit(1, 'Model', 'Run',
                      'Programing models')
        modelJSON = list()
        for index, file in enumerate(loadFilePath):
            self.msg.emit(0, '', '',
                          f'Loading model [{os.path.basename(file)}]')
            try:
                with open(file, 'r') as infile:
                    model = json.load(infile)
                    modelJSON += model
            except Exception as e:
                self.log.warning(f'Cannot load model file: {[file]}, error: {e}')
                continue

        if len(modelJSON) > 99:
            self.msg.emit(2, 'Model', 'Run error',
                          'Model(s) exceed(s) limit of 99 points')
            self.app.operationRunning.emit(0)
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
        self.app.operationRunning.emit(0)
        return suc

    def solveDone(self, result=None):
        """
        :param result: result (named tuple)
        :return: success
        """
        self.app.plateSolve.signals.done.disconnect(self.solveDone)
        if not result:
            self.msg.emit(2, 'Model', 'Solving error', 'Result missing')
            self.app.operationRunning.emit(0)
            return False
        if not result['success']:
            self.msg.emit(2, 'Model', 'Solve error', f'{result.get("message")}')
            self.app.operationRunning.emit(0)
            return False

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
        self.app.operationRunning.emit(0)
        return suc

    def solveImage(self, imagePath=''):
        """
        :param imagePath:
        :return:
        """
        if not os.path.isfile(imagePath):
            self.app.operationRunning.emit(0)
            return False

        self.app.plateSolve.signals.done.connect(self.solveDone)
        self.app.plateSolve.solveThreading(fitsPath=imagePath)
        t = f'{os.path.basename(imagePath)}'
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
        timeTag = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        fileName = timeTag + '-sync.fits'
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

        self.app.operationRunning.emit(2)
        self.changeStyleDynamic(self.ui.plateSolveSync, 'running', True)
        self.exposeImage()
        return True
