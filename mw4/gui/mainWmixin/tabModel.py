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
from PyQt5.QtTest import QTest
from mountcontrol.alignStar import AlignStar
from mountcontrol.convert import convertToHMS, convertToDMS

# local import
from base import transform
from gui.utilities.toolsQtWidget import QMultiWait
from logic.modeldata.modelHandling import writeRetrofitData


class Model:
    """
    """

    # define a max error which throws point out of queue in arcsec (this is
    # 10 degrees
    MAX_ERROR_MODEL_POINT = 10 * 60 * 60

    def __init__(self):
        self.slewQueue = queue.Queue()
        self.imageQueue = queue.Queue()
        self.solveQueue = queue.Queue()
        self.resultQueue = queue.Queue()
        self.modelQueue = queue.Queue()
        self.retryQueue = queue.Queue()
        self.collector = QMultiWait()
        self.startModeling = None
        self.modelName = ''
        self.model = []
        self.imageDir = ''
        self.modelBuildRetryCounter = 0

        ms = self.app.mount.signals
        ms.alignDone.connect(self.updateAlignGUI)
        ms.alignDone.connect(self.updateTurnKnobsGUI)

        self.ui.runModel.clicked.connect(self.modelBuild)
        self.ui.cancelModel.clicked.connect(self.cancelBuild)
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
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['retriesReverse'] = self.ui.retriesReverse.isChecked()
        config['parkMountAfterModel'] = self.ui.parkMountAfterModel.isChecked()
        config['numberBuildRetries'] = self.ui.numberBuildRetries.value()
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

    def updateProgress(self, number=0, count=0):
        """
        updateProgress calculated from the elapsed time and number of point
        with taking actual processing time into account a estimation of duration
        and finishing time of the modeling process and updates this in the gui

        :param number: total number of model points
        :param count: index of the actual processed point
        :return: success
        """
        if not 0 < count <= number:
            return False

        fraction = count / number

        secondsElapsed = time.time() - self.startModeling
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

    def modelSolveDone(self, result):
        """
        modelSolveDone is called when a point is solved by astrometry. if called
        it takes the model point out of the queue and adds the solving data for
        later model build. as the solving takes place in J2000 epoch, but we need
        fpr die model build JNow epoch, the transformation is done as well.

        in addition as it is the last step before a model point could be used, the
        it checks for the end of the modeling process.

        :param result: true for test purpose
        :return: success
        """
        noResultsLeft = self.resultQueue.empty()
        slewsLeft = not self.slewQueue.empty()
        imagesLeft = not self.imageQueue.empty()
        solvesLeft = not self.solveQueue.empty()
        stillToWork = slewsLeft or imagesLeft or solvesLeft

        if noResultsLeft and stillToWork:
            self.log.error('Empty result queue -> error')
            t = f'Slews left: [{self.slewQueue.qsize()}] '
            t += f'Images left: [{self.imageQueue.qsize()}] '
            t += f'Solves left: [{self.solveQueue.qsize()}] '
            self.log.error(t)
            return False

        self.log.debug('Processing astrometry result')
        mPoint = self.resultQueue.get()
        self.log.debug(f'Result from queue [{mPoint["countSequence"]:03d}]: [{mPoint}]')

        lenSequence = mPoint["lenSequence"]
        count = mPoint["countSequence"]
        pointNumber = mPoint["pointNumber"]

        if not result:
            self.log.debug('Solving result is missing')
            return False

        mPoint.update(result)
        isSuccess = mPoint['success']

        isInRange = mPoint.get('errorRMS_S', 0) < self.MAX_ERROR_MODEL_POINT
        if isSuccess and isInRange:
            raJNowS, decJNowS = transform.J2000ToJNow(mPoint['raJ2000S'],
                                                      mPoint['decJ2000S'],
                                                      mPoint['julianDate'])
            mPoint['raJNowS'] = raJNowS
            mPoint['decJNowS'] = decJNowS
            t = f'Queued to model [{mPoint["countSequence"]:03d}]: [{mPoint}]'
            self.log.debug(t)
            self.modelQueue.put(mPoint)
            self.app.data.setStatusBuildP(pointNumber - 1, False)
            self.app.updatePointMarker.emit()

            text = f'Solved   image-{count:03d}:  '
            text += f'Ra: {convertToHMS(mPoint["raJ2000S"])} '
            text += f'({mPoint["raJ2000S"].hours:4.3f}), '
            text += f'Dec: {convertToDMS(mPoint["decJ2000S"])} '
            text += f'({mPoint["decJ2000S"].degrees:4.3f}), '
            self.app.message.emit(text, 0)

            text = '                     '
            text += f'Angle: {mPoint["angleS"]:3.0f}, '
            text += f'Scale: {mPoint["scaleS"]:4.3f}, '
            text += f'Error: {mPoint["errorRMS_S"]:4.1f}'
            self.app.message.emit(text, 0)

        else:
            text = f'Solving failed for image-{count:03d}'
            self.app.message.emit(text, 2)
            self.retryQueue.put(mPoint)

        self.updateProgress(number=lenSequence, count=count)
        if lenSequence == count:
            self.modelCycleThroughBuildPointsFinished()

        return True

    def modelSolve(self):
        """
        modelSolve is the method called from the signal image saved and starts
        the solving process for this image. therefore it takes the model point
        from the queue and uses the parameters stored. if the queue is empty (
        which should be to the case), it just returns. after starting the solving
        process in a threaded way (should run in parallel to gui) it puts the
        model point to the next queue, the result queue. in addition if the image
        window is present, it send a signal for displaying the actual captured
        image. it shows the actual processed point
        index in GUI

        :return: success
        """
        noSolvesLeft = self.solveQueue.empty()
        slewsLeft = not self.slewQueue.empty()
        imagesLeft = not self.imageQueue.empty()
        stillToWork = slewsLeft or imagesLeft

        if noSolvesLeft and stillToWork:
            t = f'Slews left: [{self.slewQueue.qsize()}] '
            t += f'Images left: [{self.imageQueue.qsize()}] '
            self.log.error(f'Empty solve queue: {t}')
            return False

        self.log.debug('Solving started')
        mPoint = self.solveQueue.get()
        self.app.showImage.emit(mPoint["imagePath"])
        self.resultQueue.put(mPoint)
        self.log.debug(f'Queued to result [{mPoint["countSequence"]:03d}]: [{mPoint}]')
        self.app.astrometry.solveThreading(fitsPath=mPoint["imagePath"],
                                           updateFits=False)
        text = f'Solving  image-{mPoint["countSequence"]:03d}:  '
        text += f'path: {os.path.basename(mPoint["imagePath"])}'
        self.app.message.emit(text, 0)
        self.ui.mSolve.setText(f'{mPoint["countSequence"]:2d}')

        return True

    def modelImage(self):
        """
        modelImage is the method called from the signal mount and dome slewed
        finish and starts the imaging for the model point. therefore it takes the
        model point from the queue and uses the parameters stored. if the queue
        is empty (which should be to the case), it just returns.
        as we are combining the reception of multiple signals for detecting that
        all slew actions are finished, we have to reset the collector Class for
        preparing a new cycle.

        after the imaging with parameters started, the actual mount data
        (coordinates, time, pierside) is added to the model point as this
        information is later needed for solving and building the model itself.

        it shows the actual processed point index in GUI

        :return: success
        """
        noImagesLeft = self.imageQueue.empty()
        slewsLeft = not self.slewQueue.empty()
        stillToWork = slewsLeft

        if noImagesLeft and stillToWork:
            t = f'Slews left: [{self.slewQueue.qsize()}] '
            self.log.error(f'Empty image queue: {t}')
            return False

        self.log.debug('Imaging started')
        mPoint = self.imageQueue.get()
        self.collector.resetSignals()
        while self.ui.pauseModel.property('pause'):
            QTest.qWait(100)

        self.app.camera.expose(imagePath=mPoint['imagePath'],
                               expTime=mPoint['exposureTime'],
                               binning=mPoint['binning'],
                               subFrame=mPoint['subFrame'],
                               fastReadout=mPoint['fastReadout'],
                               focalLength=mPoint['focalLength'])

        mPoint['raJNowM'] = self.app.mount.obsSite.raJNow
        mPoint['decJNowM'] = self.app.mount.obsSite.decJNow
        mPoint['angularPosRA'] = self.app.mount.obsSite.angularPosRA
        mPoint['angularPosDEC'] = self.app.mount.obsSite.angularPosDEC
        mPoint['siderealTime'] = self.app.mount.obsSite.timeSidereal
        mPoint['julianDate'] = self.app.mount.obsSite.timeJD
        mPoint['pierside'] = self.app.mount.obsSite.pierside

        self.solveQueue.put(mPoint)
        self.log.debug(f'Queued to solve [{mPoint["countSequence"]:03d}]: [{mPoint}]')

        text = f'Exposing image-{mPoint["countSequence"]:03d}:  '
        text += f'path: {os.path.basename(mPoint["imagePath"])}'
        self.app.message.emit(text, 0)
        self.ui.mImage.setText(f'{mPoint["countSequence"]:2d}')

        return True

    def modelSlew(self):
        """
        modelSlew is the method called from the model core method and is the
        beginning of the modeling chain. it starts with taking a first model
        point from the initial slew queue and starts slewing mount (and dome if
        present).if the queue is empty (which should be to the case), it just
        returns.

        it shows the actual processed point index in GUI

        :return: success

        """
        if self.slewQueue.empty():
            self.log.info('Empty slew queue- model sequence finished')
            return False

        self.log.debug('Slew started')
        mPoint = self.slewQueue.get()
        suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=mPoint['altitude'],
                                                    az_degrees=mPoint['azimuth'])
        if not suc:
            return False

        if self.deviceStat['dome']:
            alt = mPoint['altitude']
            az = mPoint['azimuth']
            delta = self.app.dome.slewDome(altitude=alt, azimuth=az)
            geoStat = 'Geometry corrected' if delta else 'Equal mount'
            text = f'Slewing  dome:       point: {mPoint["countSequence"]:03d}, '
            text += f'{geoStat}, az: {az:3.1f} delta: {delta:3.1f}'
            self.app.message.emit(text, 0)

        self.app.mount.obsSite.startSlewing()
        self.imageQueue.put(mPoint)
        self.log.debug(f'Queued to image [{mPoint["countSequence"]:03d}]: [{mPoint}]')

        text = 'Slewing  mount:      point in sequence: '
        text += f'{mPoint["countSequence"]:03d}, '
        text += f'altitude: {mPoint["altitude"]:3.0f}, '
        text += f'azimuth: {mPoint["azimuth"]:3.0f}'
        self.app.message.emit(text, 0)

        self.ui.mPoints.setText(f'{mPoint["lenSequence"]:2d}')
        self.ui.mSlew.setText(f'{mPoint["countSequence"]:2d}')

        return True

    def clearQueues(self):
        """
        :return: true for test purpose
        """
        self.slewQueue.queue.clear()
        self.imageQueue.queue.clear()
        self.solveQueue.queue.clear()
        self.resultQueue.queue.clear()
        self.modelQueue.queue.clear()
        self.retryQueue.queue.clear()
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
        self.app.enableEditPoints.emit(False)

        winImage = self.app.uiWindows['showImageW']['classObj']
        if not winImage:
            return False

        winImage.ui.checkAutoSolve.setChecked(False)
        winImage.ui.checkStackImages.setChecked(False)

        if not winImage.deviceStat['expose']:
            return False
        if not winImage.deviceStat['exposeN']:
            return False

        winImage.abortImage()
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
        self.app.enableEditPoints.emit(True)
        return True

    def setupSignalsForModelRun(self):
        """
        setupSignalsForModelRun establishes the signals chain. as we have
        multiple actions running at the same time, the synchronisation by the
        right link of the signals.

        first we link the two slew finished signals to modelImage. that means
        as soon as both slew finished signals are received, the imaging will be
        started when download of an image starts, we could slew to another point
        when image is saved, we could start with solving

        :return: true for test purpose
        """
        self.collector.addWaitableSignal(self.app.mount.signals.slewFinished)

        hasDome = self.deviceStat.get('dome', False)
        hasAzimuth = 'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION' in self.app.dome.data

        if hasDome and hasAzimuth:
            self.collector.addWaitableSignal(self.app.dome.signals.slewFinished)
        elif hasDome and not hasAzimuth:
            self.app.message.emit('Dome without azimuth value used', 2)

        self.collector.ready.connect(self.modelImage)
        self.app.camera.signals.integrated.connect(self.modelSlew)
        self.app.camera.signals.saved.connect(self.modelSolve)
        self.app.astrometry.signals.done.connect(self.modelSolveDone)
        return True

    def restoreSignalsModelDefault(self):
        """
        restoreSignalsModelDefault clears the signal queue and removes the
        signal connections

        :return: true for test purpose
        """
        self.app.camera.signals.saved.disconnect(self.modelSolve)
        self.app.camera.signals.integrated.disconnect(self.modelSlew)
        self.app.astrometry.signals.done.disconnect(self.modelSolveDone)
        self.collector.ready.disconnect(self.modelImage)
        self.collector.clear()
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

    def cancelBuild(self):
        """
        cancelBuild aborts imaging and stops all modeling queues and actions
        and restores them to default values.

        :return: true for test purpose
        """
        self.app.camera.abort()
        self.app.astrometry.abort()
        self.restoreSignalsModelDefault()
        self.clearQueues()
        self.restoreModelDefaultContextAndGuiStatus()
        self.app.message.emit('Modeling cancelled', 2)
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

    def generateSaveModel(self):
        """
        generateSaveModel builds from the model file a format which could be
        serialized in json. this format will be used for storing model on file.

        :return: save model format
        """
        modelDataForSave = list()
        for mPoint in self.model:
            sPoint = dict()
            sPoint.update(mPoint)
            sPoint['raJNowM'] = sPoint['raJNowM'].hours
            sPoint['decJNowM'] = sPoint['decJNowM'].degrees
            sPoint['angularPosRA'] = sPoint['angularPosRA'].degrees
            sPoint['angularPosDEC'] = sPoint['angularPosDEC'].degrees
            sPoint['raJNowS'] = sPoint['raJNowS'].hours
            sPoint['decJNowS'] = sPoint['decJNowS'].degrees
            sPoint['raJ2000S'] = sPoint['raJ2000S'].hours
            sPoint['decJ2000S'] = sPoint['decJ2000S'].radians
            sPoint['siderealTime'] = sPoint['siderealTime'].hours
            sPoint['julianDate'] = sPoint['julianDate'].utc_iso()
            sPoint['version'] = f'{self.app.__version__}'
            sPoint['profile'] = self.ui.profile.text()
            sPoint['firmware'] = self.ui.vString.text()
            sPoint['latitude'] = self.app.mount.obsSite.location.latitude.degrees
            modelDataForSave.append(sPoint)

        return modelDataForSave

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
        self.app.message.emit(f'Writing model:       [{self.modelName}]', 0)
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

    def collectingModelRunOutput(self):
        """
        :return:
        """
        self.model = list()
        while not self.modelQueue.empty():
            point = self.modelQueue.get()
            self.model.append(point)

        self.restoreSignalsModelDefault()
        self.clearQueues()
        self.restoreModelDefaultContextAndGuiStatus()
        if len(self.model) < 3:
            return False

        return True

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

    def processModelData(self):
        """
        :return:
        """
        suc = self.collectingModelRunOutput()
        if not suc:
            self.app.message.emit(f'Modeling error:       {self.modelName}', 2)
            self.app.message.emit('Not enough valid model points available', 2)
            return False

        self.app.message.emit('Programming model to mount', 0)
        suc = self.programModelToMount(self.model)
        if suc:
            self.app.message.emit('Model programmed with success', 0)
        else:
            self.app.message.emit('Model programming error', 2)

        if not self.ui.checkKeepImages.isChecked():
            self.app.message.emit('Deleting model images', 0)
            shutil.rmtree(self.imageDir, ignore_errors=True)

        self.app.message.emit(f'Modeling finished:    {self.modelName}', 1)
        self.playSound('ModelingFinished')
        self.renewHemisphereView()
        if self.ui.parkMountAfterModel.isChecked():
            self.app.message.emit('Parking mount after model run', 0)
            suc = self.app.mount.obsSite.park()

            if not suc:
                self.app.message.emit('Cannot park mount', 2)
            else:
                self.app.message.emit('Mount parked', 0)

        return True

    def modelCycleThroughBuildPointsFinished(self):
        """
        modelCycleThroughBuildPointsFinished is called when tha last point was
        processed. it empties the solution queue restores the default gui elements
        an signals. after that it programs the resulting model to the mount and
        saves it to disk.

        is the flag delete images after modeling is set, the entire directory
        will be deleted

        :return: true for test purpose
        """
        if self.retryQueue.qsize() == 0:
            self.processModelData()
            return True
        if self.modelBuildRetryCounter == 0:
            self.processModelData()
            return True

        self.app.message.emit('Starting retry failed points', 1)
        maxRetries = self.ui.numberBuildRetries.value()
        retryNumber = maxRetries - self.modelBuildRetryCounter + 1
        self.app.message.emit(f'Retry run number: {retryNumber}', 1)
        numberPointsRetry = self.retryQueue.qsize()
        countPointsRetry = 0

        points = list()
        while not self.retryQueue.empty():
            points.append(self.retryQueue.get())

        if self.ui.retriesReverse.isChecked():
            points = reversed(points)

        for point in points:
            point['lenSequence'] = numberPointsRetry
            point['countSequence'] = countPointsRetry + 1
            countPointsRetry += 1
            self.slewQueue.put(point)

        self.modelBuildRetryCounter -= 1
        self.modelSlew()
        self.ui.modelProgress.setValue(0)
        return True

    def checkModelRunConditions(self):
        """
        :return:
        """
        if len(self.app.data.buildP) < 2:
            t = 'No modeling start because less than 3 points'
            self.app.message.emit(t, 2)
            return False

        if len(self.app.data.buildP) > 99:
            t = 'No modeling start because more than 99 points'
            self.app.message.emit(t, 2)
            return False

        excludeDonePoints = self.ui.excludeDonePoints.isChecked()
        if len([x for x in self.app.data.buildP if x[2]]) < 3 and excludeDonePoints:
            t = 'No modeling start because less than 3 points left over'
            self.app.message.emit(t, 2)
            return False

        if self.ui.astrometryDevice.currentText().startswith('No device'):
            self.app.message.emit('No plate solver selected', 2)
            return False

        sucApp, sucIndex = self.app.astrometry.checkAvailability()
        if not (sucApp and sucIndex):
            self.app.message.emit('No valid configuration for plate solver', 2)
            return False

        return True

    def clearAlignAndBackup(self):
        """
        :return:
        """
        suc = self.app.mount.model.clearAlign()
        if not suc:
            self.app.message.emit('Actual model cannot be cleared', 2)
            self.app.message.emit('Model build cancelled', 2)
            return False
        else:
            self.app.message.emit('Actual model clearing, waiting 1s', 0)
            QTest.qWait(1000)
            self.app.message.emit('Actual model cleared', 0)
            self.refreshModel()

        suc = self.app.mount.model.deleteName('backup')
        if not suc:
            self.log.debug('Cannot delete backup model on mount')

        suc = self.app.mount.model.storeName('backup')
        if not suc:
            t = 'Cannot save backup model on mount, proceeding with model run'
            self.app.message.emit(t, 2)

        return True

    def setupModelPointsAndContextData(self):
        """
        :return:
        """
        astrometryApp = self.ui.astrometryDevice.currentText()
        exposureTime = self.ui.expTime.value()
        binning = self.ui.binning.value()
        subFrame = self.ui.subFrame.value()
        fastReadout = self.ui.checkFastDownload.isChecked()
        focalLength = self.ui.focalLength.value()
        lenSequence = len(self.app.data.buildP)
        framework = self.app.astrometry.framework
        solveTimeout = self.app.astrometry.run[framework].timeout
        searchRadius = self.app.astrometry.run[framework].searchRadius
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
            m['astrometryApp'] = astrometryApp
            m['solveTimeout'] = solveTimeout
            m['searchRadius'] = searchRadius
            m['focalLength'] = focalLength
            m['altitude'] = point[0]
            m['azimuth'] = point[1]
            modelPoints.append(m)
        return modelPoints

    def modelCycleThroughBuildPoints(self, modelPoints=None):
        """
        modelCycleThroughBuildPoints is the main method for preparing a model
        run. in addition it checks necessary components and prepares all the
        parameters. the modeling queue will be filled with point and the queue is
        started. the overall modeling process consists of a set of queues which
        are handled by events running in the gui event queue.

        :param modelPoints:
        :return: true for test purpose
        """
        self.clearQueues()
        self.setupSignalsForModelRun()
        self.startModeling = time.time()
        for point in modelPoints:
            self.slewQueue.put(point)

        self.app.dome.avoidFirstOvershoot()
        self.modelSlew()
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
            self.app.message.emit('Modeling cancelled, no valid points', 2)
            return False

        self.setupModelRunContextAndGuiStatus()
        self.app.message.emit(f'Modeling start:      {self.modelName}', 1)
        self.modelBuildRetryCounter = self.ui.numberBuildRetries.value()
        self.modelCycleThroughBuildPoints(modelPoints=modelPoints)
        return True

    def loadProgramModel(self):
        """
        loadProgramModel selects one or more models from the files system,
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

        self.app.message.emit('Programing models', 1)
        modelJSON = list()
        for index, file in enumerate(loadFilePath):
            self.app.message.emit(f'Loading model [{os.path.basename(file)}]', 0)
            with open(file, 'r') as infile:
                model = json.load(infile)
                modelJSON += model

        if len(modelJSON) > 99:
            self.app.message.emit('Model(s) exceed(s) limit of 99 points', 2)
            return False

        self.app.message.emit(f'Programming {index + 1} model(s) to mount', 0)
        suc = self.programModelToMount(modelJSON)

        if suc:
            self.app.message.emit('Model programmed with success', 0)
        else:
            self.app.message.emit('Model programming error', 2)

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
        self.app.astrometry.signals.done.disconnect(self.solveDone)

        if not result:
            self.app.message.emit('Solving error, result missing', 2)
            return False

        if result['success']:
            text = 'Solved :             '
            text += f'RA: {convertToHMS(result["raJ2000S"])} '
            text += f'({result["raJ2000S"].hours:4.3f}), '
            text += f'DEC: {convertToDMS(result["decJ2000S"])} '
            text += f'({result["decJ2000S"].degrees:4.3f}), '
            self.app.message.emit(text, 0)
            text = '                     '
            text += f'Angle: {result["angleS"]:3.0f}, '
            text += f'Scale: {result["scaleS"]:4.3f}, '
            text += f'Error: {result["errorRMS_S"]:4.1f}'
            self.app.message.emit(text, 0)

        else:
            text = f'Solving error:       {result.get("message")}'
            self.app.message.emit(text, 2)
            return False

        self.app.showImage.emit(result['solvedPath'])

        obs = self.app.mount.obsSite
        timeJD = obs.timeJD
        raJNow, decJNow = transform.J2000ToJNow(result['raJ2000S'],
                                                result['decJ2000S'],
                                                timeJD)
        obs.setTargetRaDec(raJNow, decJNow)
        suc = obs.syncPositionToTarget()
        if suc:
            t = 'Successfully synced model in mount to coordinates'
            self.app.message.emit(t, 1)
        else:
            t = 'No sync, match failed because coordinates to far off for model'
            self.app.message.emit(t, 2)
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

        self.app.astrometry.signals.done.connect(self.solveDone)
        self.app.astrometry.solveThreading(fitsPath=imagePath)
        text = f'Solving:             [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)
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

        text = f'Exposing:            [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)
        text = f'Duration:{expTime:3.0f}s  '
        text += f'Bin:{binning:1.0f}  Sub:{subFrame:3.0f}%'
        self.app.message.emit(f'                     {text}', 0)
        return True

    def exposeImageDone(self, imagePath=''):
        """
        :param imagePath:
        :return: True for test purpose
        """
        self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        text = f'Exposed:             [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)
        self.solveImage(imagePath)
        return True

    def exposeImage(self):
        """
        :return: success
        """
        expTime = self.ui.expTime.value()
        binning = self.ui.binning.value()
        subFrame = self.ui.subFrame.value()
        fastReadout = self.ui.checkFastDownload.isChecked()
        focalLength = self.ui.focalLength.value()
        self.app.camera.signals.saved.connect(self.exposeImageDone)
        self.exposeRaw(expTime, binning, subFrame, fastReadout, focalLength)
        return True

    def plateSolveSync(self):
        """
        :return:
        """
        self.app.message.emit('Starting plate solve and sync model in mount', 1)
        sucApp, sucIndex = self.app.astrometry.checkAvailability()
        if not (sucApp and sucIndex):
            self.app.message.emit('No valid configuration for plate solver', 2)
            return False

        self.ui.runModel.setEnabled(False)
        self.ui.batchModel.setEnabled(False)
        self.ui.plateSolveSync.setEnabled(False)
        self.ui.runFlexure.setEnabled(False)
        self.ui.runHysteresis.setEnabled(False)
        self.exposeImage()
        return True
