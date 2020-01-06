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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import queue
import os
import time
import shutil
import json
import copy
from datetime import datetime, timedelta
# external packages
import PyQt5.uic
from mountcontrol.alignStar import AlignStar
# local import
from mw4.base import transform


class QMultiWait(PyQt5.QtCore.QObject):
    """
    QMultiWaitable implements a signal collection class for waiting of entering multiple
    signals before firing the "AND" relation of all signals.
    derived from:

    https://stackoverflow.com/questions/21108407/qt-how-to-wait-for-multiple-signals

    in addition all received signals could be reset
    """

    ready = PyQt5.QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.waitable = set()
        self.waitready = set()

    def addWaitableSignal(self, signal):
        if signal not in self.waitable:
            self.waitable.add(signal)
            signal.connect(self.checkSignal)

    def checkSignal(self):
        sender = self.sender()
        self.waitready.add(sender)
        if len(self.waitready) == len(self.waitable):
            self.ready.emit()

    def resetSignals(self):
        self.waitready = set()

    def clear(self):
        for signal in self.waitable:
            signal.disconnect(self.checkSignal)
        self.waitable = set()
        self.waitready = set()


class Model(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    # define a max error which throws point out of queue in arcsec
    MAX_ERROR_MODEL_POINT = 99999

    def __init__(self):

        self.slewQueue = queue.Queue()
        self.imageQueue = queue.Queue()
        self.solveQueue = queue.Queue()
        self.resultQueue = queue.Queue()
        self.modelQueue = queue.Queue()
        self.collector = QMultiWait()
        self.startModeling = None
        self.modelName = ''
        self.model = []
        self.imageDir = ''

        # func signals
        ms = self.app.mount.signals
        ms.alignDone.connect(self.updateAlignGUI)
        ms.alignDone.connect(self.updateTurnKnobsGUI)

        # ui signals
        self.ui.runModel.clicked.connect(self.modelBuild)
        self.ui.cancelModel.clicked.connect(self.cancelBuild)
        self.ui.batchModel.clicked.connect(self.loadProgramModel)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        # config = self.app.config['mainW']
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        # config = self.app.config['mainW']
        return True

    def updateAlignGUI(self, model):
        """
        updateAlignGUI shows the data which is received through the getain command. this is
        mainly polar and ortho errors as well as basic model data.

        :param model:
        :return:    True if ok for testing
        """

        if model.numberStars is not None:
            text = str(model.numberStars)
        else:
            text = '-'
        self.ui.numberStars.setText(text)
        self.ui.numberStars1.setText(text)

        if model.terms is not None:
            text = str(model.terms)
        else:
            text = '-'
        self.ui.terms.setText(text)

        if model.errorRMS is not None:
            text = str(model.errorRMS)
        else:
            text = '-'
        self.ui.errorRMS.setText(text)
        self.ui.errorRMS1.setText(text)

        if model.positionAngle is not None:
            text = f'{model.positionAngle.degrees:5.1f}'
        else:
            text = '-'
        self.ui.positionAngle.setText(text)

        if model.polarError is not None:
            text = f'{model.polarError.degrees * 60:5.2f}'
        else:
            text = '-'
        self.ui.polarError.setText(text)

        if model.orthoError is not None:
            text = f'{model.orthoError.degrees * 60:5.2f}'
        else:
            text = '-'
        self.ui.orthoError.setText(text)

        if model.azimuthError is not None:
            text = f'{model.azimuthError.degrees:5.1f}'
        else:
            text = '-'
        self.ui.azimuthError.setText(text)

        if model.altitudeError is not None:
            text = f'{model.altitudeError.degrees:5.1f}'
        else:
            text = '-'
        self.ui.altitudeError.setText(text)

        return True

    def updateTurnKnobsGUI(self, model):
        """
        updateTurnKnobsGUI shows the data which is received through the getain command.
        this is mainly polar and ortho errors as well as basic model data.

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

    def updateProgress(self, number=0, count=0, modelingDone=False):
        """
        updateProgress calculated from the elapsed time and number of point with taking
        actual processing time into account a estimation of duration and finishing time
        of the modeling process and updates this in the gui

        :param number: total number of model points
        :param count: index of the actual processed point
        :param modelingDone: state for the last point
        :return: success
        """

        if not 0 <= count < number:
            return False
        if not number:
            return False

        modelPercent = (count + 1) / number
        timeElapsed = time.time() - self.startModeling

        if modelingDone:
            timeEstimation = 0
        else:
            timeEstimation = (1 / modelPercent * timeElapsed) * (1 - modelPercent)
        finished = timedelta(seconds=timeEstimation) + datetime.now()

        self.ui.timeToFinish.setText(time.strftime('%M:%S', time.gmtime(timeEstimation)))
        self.ui.timeElapsed.setText(time.strftime('%M:%S', time.gmtime(timeElapsed)))
        self.ui.timeFinished.setText(finished.strftime('%H:%M:%S'))
        self.ui.modelProgress.setValue(modelPercent * 100)

        return True

    def modelSolveDone(self, result):
        """
        modelSolveDone is called when a point is solved by astrometry. if called it takes
        the model point out of the queue and adds the solving data for later model build.
        as the solving takes place in J2000 epoch, but we need fpr die model build JNow
        epoch, the transformation is done as well.

        in addition as it is the last step before a model point could be used, the
        it checks for the end of the modeling process.

        :param result: true for test purpose
        :return: success
        """

        if self.resultQueue.empty():
            self.log.warning('empty result queue')
            return False

        mPoint = self.resultQueue.get()
        number = mPoint["lenSequence"]
        count = mPoint["countSequence"]
        modelingDone = (number == count + 1)

        if not result:
            self.log.info('Solving result is missing')
            return False

        mPoint.update(result)

        if mPoint['success']:
            # processing only the model points which are OK
            raJNowS, decJNowS = transform.J2000ToJNow(mPoint['raJ2000S'],
                                                      mPoint['decJ2000S'],
                                                      mPoint['julianDate'])
            mPoint['raJNowS'] = raJNowS
            mPoint['decJNowS'] = decJNowS

            if mPoint['errorRMS_S'] < self.MAX_ERROR_MODEL_POINT:
                self.modelQueue.put(mPoint)
            else:
                text = f'Solving failed for image-{count:03d}'
                self.app.message.emit(text, 2)

            text = f'Solved   image-{count:03d}: '
            text += f'Ra: {transform.convertToHMS(mPoint["raJ2000S"])} '
            text += f'({mPoint["raJ2000S"].hours:4.3f}), '
            text += f'Dec: {transform.convertToDMS(mPoint["decJ2000S"])} '
            text += f'({mPoint["decJ2000S"].degrees:4.3f}), '
            self.app.message.emit(text, 0)
            text = f'                    '
            text += f'Angle: {mPoint["angleS"]:3.0f}, '
            text += f'Scale: {mPoint["scaleS"]:4.3f}, '
            text += f'Error: {mPoint["errorRMS_S"]:4.1f}'
            self.app.message.emit(text, 0)
        else:
            text = f'Solving  image-{count:03d}: solving error: {mPoint.get("message")}'
            self.app.message.emit(text, 2)

        self.updateProgress(number=number,
                            count=count,
                            modelingDone=modelingDone)

        if modelingDone:
            self.modelFinished()

        return True

    def modelSolve(self):
        """
        modelSolve is the method called from the signal image saved and starts the solving
        process for this image. therefore it takes the model point from the queue and uses
        the parameters stored. if the queue is empty (which should be to the case), it
        just returns.

        after starting the solving process in a threaded way (should run in parallel to gui)
        it puts the model point to the next queue, the result queue.

        in addition if the image window is present, it send a signal for displaying the
        actual captured image.

        it shows the actual processed point index in GUI

        :return: success
        """

        if self.solveQueue.empty():
            self.log.warning('empty solve queue')
            return False

        mPoint = self.solveQueue.get()

        # showing the expose image in the image window
        imageWObj = self.app.uiWindows['showImageW']['classObj']
        if imageWObj:
            imageWObj.signals.showImage.emit(mPoint["imagePath"])

        self.app.astrometry.solveThreading(fitsPath=mPoint["imagePath"],
                                           radius=mPoint["searchRadius"],
                                           timeout=mPoint["solveTimeout"],
                                           updateFits=False,
                                           )
        self.resultQueue.put(mPoint)

        text = f'Solving  image-{mPoint["countSequence"]:03d}: '
        text += f'path: {os.path.basename(mPoint["imagePath"])}'
        self.app.message.emit(text, 0)
        self.ui.mSolve.setText(f'{mPoint["countSequence"] + 1:2d}')

        return True

    def modelImage(self):
        """
        modelImage is the method called from the signal mount and dome slewed finish and
        starts the imaging for the model point. therefore it takes the model point from
        the queue and uses the parameters stored. if the queue is empty (which should be to
        the case), it just returns.

        as we are combining the reception of multiple signals for detecting that all slew
        actions are finished, we have to reset the collector Class for preparing a new
        cycle.

        after the imaging with parameters started, the actual mount data (coordinates,
        time, pierside) is added to the model point as this information is later needed for
        solving and building the model itself.

        it shows the actual processed point index in GUI

        :return: success
        """

        if self.imageQueue.empty():
            self.log.warning('empty image queue')
            return False

        mPoint = self.imageQueue.get()
        self.collector.resetSignals()

        self.app.camera.expose(imagePath=mPoint['imagePath'],
                               expTime=mPoint['exposureTime'],
                               binning=mPoint['binning'],
                               subFrame=mPoint['subFrame'],
                               fastReadout=mPoint['fastReadout'],
                               )

        mPoint['raJNowM'] = self.app.mount.obsSite.raJNow
        mPoint['decJNowM'] = self.app.mount.obsSite.decJNow
        mPoint['siderealTime'] = self.app.mount.obsSite.timeSidereal
        mPoint['julianDate'] = self.app.mount.obsSite.timeJD
        mPoint['pierside'] = self.app.mount.obsSite.pierside

        self.solveQueue.put(mPoint)

        text = f'Exposing image-{mPoint["countSequence"]:03d}: '
        text += f'path: {os.path.basename(mPoint["imagePath"])}'
        self.app.message.emit(text, 0)
        self.ui.mImage.setText(f'{mPoint["countSequence"] + 1 :2d}')

        return True

    def modelSlew(self):
        """
        modelSlew is the method called from the model core method and is the beginning of
        the modeling chain. it starts with taking a first model point from the initial
        slew queue and starts slewing mount (and dome if present).if the queue is empty
        (which should be to the case), it just returns.

        it shows the actual processed point index in GUI

        :return: success

        """

        if self.slewQueue.empty():
            return False

        mPoint = self.slewQueue.get()
        suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=mPoint['altitude'],
                                                    az_degrees=mPoint['azimuth'],
                                                    )
        if not suc:
            return False
        self.app.dome.slewDome(altitude=mPoint['altitude'],
                               azimuth=mPoint['azimuth'],
                               )
        self.app.mount.obsSite.startSlewing()
        self.imageQueue.put(mPoint)

        text = f'Slewing  mount:     point: {mPoint["countSequence"]:03d}, '
        text += f'altitude: {mPoint["altitude"]:3.0f}, '
        text += f'azimuth: {mPoint["azimuth"]:3.0f}'
        self.app.message.emit(text, 0)
        self.ui.mPoints.setText(f'{mPoint["lenSequence"]:2d}')
        self.ui.mSlew.setText(f'{mPoint["countSequence"] + 1:2d}')

        return True

    def clearQueues(self):
        """
        clearQueues ensures that all used queues will be emptied.

        :return: true for test purpose
        """

        self.slewQueue.queue.clear()
        self.imageQueue.queue.clear()
        self.solveQueue.queue.clear()
        self.resultQueue.queue.clear()
        self.modelQueue.queue.clear()

        return True

    def prepareGUI(self):
        """
        prepareGUI sets GUI elements to state, whereas there will be no influence for
        running actions. this is valid for imaging window if present as well.

        :return: true for test purpose
        """

        self.ui.batchModel.setEnabled(False)
        # disable stacking and auto solve when modeling if imageWindow is present
        if self.app.uiWindows['showImageW']['classObj']:
            self.app.uiWindows['showImageW']['classObj'].ui.checkAutoSolve.setChecked(False)
            self.app.uiWindows['showImageW']['classObj'].ui.checkStackImages.setChecked(False)
        return True

    def defaultGUI(self):
        """
        defaultGUI will reset all gui elements to the idle or default state and new actions
        could be started again

        :return: true for test purpose
        """

        self.changeStyleDynamic(self.ui.runModel, 'running', False)
        self.changeStyleDynamic(self.ui.cancelModel, 'cancel', False)
        self.ui.runModel.setEnabled(True)
        self.ui.cancelModel.setEnabled(False)
        self.ui.batchModel.setEnabled(True)
        self.ui.plateSolveSync.setEnabled(True)
        self.ui.runFlexure.setEnabled(True)
        self.ui.runHysteresis.setEnabled(True)
        self.ui.timeToFinish.setText('00:00')
        self.ui.timeElapsed.setText('00:00')
        self.ui.timeFinished.setText('00:00:00')
        self.ui.mPoints.setText('0')
        self.ui.mSlew.setText('0')
        self.ui.mImage.setText('0')
        self.ui.mSolve.setText('0')
        self.ui.modelProgress.setValue(0)

        return True

    def prepareSignals(self):
        """
        prepareSignals establishes the signals chain. as we have multiple actions running
        at the same time, the synchronisation by the right link of the signals.

        first we link the two slew finished signals to modelImage. that means as soon as
        both slew finished signals are received, the imaging will be started
        when download of an image starts, we could slew to another point
        when image is saved, we could start with solving

        :return: true for test purpose
        """

        self.collector.addWaitableSignal(self.app.mount.signals.slewFinished)
        if self.app.mainW.deviceStat['dome']:
            self.collector.addWaitableSignal(self.app.dome.signals.slewFinished)

        self.collector.ready.connect(self.modelImage)
        self.app.camera.signals.integrated.connect(self.modelSlew)
        self.app.camera.signals.saved.connect(self.modelSolve)
        self.app.astrometry.signals.done.connect(self.modelSolveDone)

        return True

    def defaultSignals(self):
        """
        defaultSignals clears the signal queue and removes the signal connections

        :return: true for test purpose
        """

        self.app.camera.signals.saved.disconnect(self.modelSolve)
        self.app.camera.signals.integrated.disconnect(self.modelSlew)
        self.app.astrometry.signals.done.disconnect(self.modelSolveDone)
        self.collector.ready.disconnect(self.modelImage)
        self.collector.clear()

        return True

    def cancelBuild(self):
        """
        cancelBuild aborts imaging and stops all modeling queues and actions and restores
        them to default values.

        :return: true for test purpose
        """

        self.app.camera.abort()
        self.app.astrometry.abort()
        self.defaultSignals()
        self.clearQueues()
        self.defaultGUI()
        self.app.message.emit('Modeling cancelled', 2)

        return True

    def retrofitModel(self):
        """
        retrofitModel reads the actual model points and results out of the mount computer
        and adds the optimized (recalculated) error values to the point. that's necessary,
        because when imaging and solving a point the error is related to this old model.
        when programming a new model, all point will be recalculated be the mount
        computer an get a new error value which is based on the new model.

        :return: True for test purpose
        """

        starList = self.app.mount.model.starList

        if len(starList) != len(self.model):
            text = f'length starList [{len(starList)}] and length '
            text += f'model [{len(self.model)}] is different'
            self.log.info(text)
            self.model = []

        for i, mPoint in enumerate(self.model):
            mPoint['errorRMS'] = starList[i].errorRMS
            mPoint['errorRA'] = starList[i].errorRA()
            mPoint['errorDEC'] = starList[i].errorDEC()

        return True

    def generateSaveModel(self):
        """
        generateSaveModel builds from the model file a format which could be serialized
        in json. this format will be used for storing model on file.

        :return: save model format
        """

        modelDataForSave = list()
        for mPoint in self.model:
            sPoint = dict()
            sPoint.update(mPoint)
            sPoint['raJNowM'] = sPoint['raJNowM'].hours
            sPoint['decJNowM'] = sPoint['decJNowM'].degrees
            sPoint['raJNowS'] = sPoint['raJNowS'].hours
            sPoint['decJNowS'] = sPoint['decJNowS'].degrees
            sPoint['raJ2000S'] = sPoint['raJ2000S'].hours
            sPoint['decJ2000S'] = sPoint['decJ2000S'].radians
            sPoint['siderealTime'] = sPoint['siderealTime'].hours
            sPoint['julianDate'] = sPoint['julianDate'].utc_iso()

            modelDataForSave.append(sPoint)
        return modelDataForSave

    def saveModelFinish(self):
        """
        saveModelFinish is the callback after the new model data is loaded from the mount
        computer. first is disables the signals. New we have the original model build data
        which was programmed to the mount and the retrieved model data after the mount
        optimized the model. retrofitModel() combines this data to a signal data structure.
        after that it saves the model data for later use.

        with this data, the model could be reprogrammed without doing some imaging,
        it could be added with other data to extend the model to a broader base.

        :return: True for test purpose
        """

        # remove signal connection
        self.app.mount.signals.alignDone.disconnect(self.saveModelFinish)

        # write model data back from m9utn to model to be saved
        self.retrofitModel()

        # now saving the model
        self.app.message.emit(f'Writing model:      {self.modelName} ', 1)

        saveData = self.generateSaveModel()
        modelPath = f'{self.app.mwGlob["modelDir"]}/{self.modelName}.model'
        with open(modelPath, 'w') as outfile:
            json.dump(saveData,
                      outfile,
                      sort_keys=True,
                      indent=4)

        return True

    def saveModelPrepare(self):
        """
        saveModelPrepare checks boundaries for model save and prepares the signals.
        the save a model we need the calculated parameters from the mount after the new
        points are programmed in an earlier step. the new model data is retrieved from
        the mount by refreshModel() call. this call needs some time and has a callback
        which is set here. the calculations and the saving is done in the callback.

        :return: success
        """

        if len(self.model) < 3:
            self.log.info(f'only {len(self.model)} points available')
            return False

        # setting signal for callback when the model in memory is refreshed
        self.app.mount.signals.alignDone.connect(self.saveModelFinish)

        # starting refreshment thread
        self.refreshModel()

        return True

    @staticmethod
    def generateBuildData(model=[]):
        """
        generateBuildData takes the model data and generates from it a data structure
        needed for programming the model into the mount computer.

        :param model:
        :return: build
        """

        build = list()
        for mPoint in model:
            programmingPoint = AlignStar(mCoord=(mPoint['raJNowM'], mPoint['decJNowM']),
                                         sCoord=(mPoint['raJNowS'], mPoint['decJNowS']),
                                         sidereal=mPoint['siderealTime'],
                                         pierside=mPoint['pierside'],
                                         )
            build.append(programmingPoint)
        return build

    def modelFinished(self):
        """
        modelFinished is called when tha last point was processed. it empties the solution
        queue restores the default gui elements an signals. after that it programs the
        resulting model to the mount and saves it to disk.

        is the flag delete images after modeling is set, the entire directory will be
        deleted

        :return: true for test purpose
        """

        # getting models before deleting queues
        self.model = list()

        while not self.modelQueue.empty():
            mPoint = self.modelQueue.get()
            self.model.append(mPoint)

        # stopping other activities
        self.defaultSignals()
        self.clearQueues()
        self.defaultGUI()

        # finally do it
        self.app.message.emit('Programming model to mount', 0)
        build = self.generateBuildData(model=self.model)
        suc = self.app.mount.model.programAlign(build)

        if suc:
            self.saveModelPrepare()
            self.app.message.emit('Model programmed with success', 0)
        else:
            self.app.message.emit('Model programming error', 2)

        # cleaning up the disk space
        if not self.ui.checkKeepImages.isChecked():
            self.app.message.emit('Deleting model images', 0)
            shutil.rmtree(self.imageDir, ignore_errors=True)

        self.app.message.emit(f'Modeling finished:  {self.modelName}', 1)
        self.playSound('ModelingFinished')

        return True

    def modelCore(self, points=None):
        """
        modelCore is the main method for preparing a model run. in addition it checks
        necessary components and prepares all the parameters.
        the modeling queue will be filled with point and the queue is started. the overall
        modeling process consists of a set of queues which are handled by events running
        in the gui event queue.

        :param points:
        :return: true for test purpose
        """

        if not points:
            return False

        # looking for solving application
        astrometryApp = self.app.mainW.ui.astrometryDevice.currentText()

        if astrometryApp.startswith('No device'):
            return False

        # collection locations for files and generate directories if necessary
        nameTime = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        self.modelName = f'm-{self.lastGenerator}-{nameTime}'
        self.imageDir = f'{self.app.mwGlob["imageDir"]}/{self.modelName}'

        if not os.path.isdir(self.imageDir):
            os.mkdir(self.imageDir)
        if not os.path.isdir(self.imageDir):
            return False

        # now everything is prepared and we could start modeling
        self.clearQueues()
        self.app.message.emit(f'Modeling start:     {self.modelName}', 1)

        # setting overall parameters
        self.app.mount.settlingTime = self.app.mainW.ui.settleTimeMount.value()
        self.app.dome.settlingTime = self.app.mainW.ui.settleTimeDome.value()

        # collection all necessary information
        exposureTime = self.app.mainW.ui.expTime.value()
        binning = self.app.mainW.ui.binning.value()
        subFrame = self.app.mainW.ui.subFrame.value()
        fastReadout = self.app.mainW.ui.checkFastDownload.isChecked()
        solveTimeout = self.ui.solveTimeout.value()
        searchRadius = self.ui.searchRadius.value()
        lenSequence = len(points)

        # preparation of signals and gui
        self.prepareGUI()
        self.prepareSignals()
        self.startModeling = time.time()

        # queuing modeling points
        for countSequence, point in enumerate(points):

            modelSet = dict()

            # define the path to the image file
            imagePath = f'{self.imageDir}/image-{countSequence:03d}.fits'

            # populating the parameters
            modelSet['imagePath'] = imagePath
            modelSet['exposureTime'] = exposureTime
            modelSet['binning'] = binning
            modelSet['subFrame'] = subFrame
            modelSet['fastReadout'] = fastReadout
            modelSet['lenSequence'] = lenSequence
            modelSet['countSequence'] = countSequence
            modelSet['modelName'] = self.modelName
            modelSet['imagePath'] = imagePath
            modelSet['astrometryApp'] = astrometryApp
            modelSet['solveTimeout'] = solveTimeout
            modelSet['searchRadius'] = searchRadius
            modelSet['altitude'] = point[0]
            modelSet['azimuth'] = point[1]

            # putting to queue
            self.slewQueue.put(copy.copy(modelSet))

        # kick off modeling
        self.modelSlew()

        return True

    def modelBuild(self):
        """
        modelBuild sets the adequate gui elements, selects the model points and calls the
        core modeling method.

        :return: true for test purpose
        """

        if not 2 < len(self.app.data.buildP) < 100:
            return False

        self.changeStyleDynamic(self.ui.runModel, 'running', True)
        self.changeStyleDynamic(self.ui.cancelModel, 'cancel', True)
        self.ui.cancelModel.setEnabled(True)
        self.ui.plateSolveSync.setEnabled(False)
        self.ui.runFlexure.setEnabled(False)
        self.ui.runHysteresis.setEnabled(False)
        self.ui.cancelModel.setEnabled(True)

        suc = self.modelCore(points=self.app.data.buildP)
        if not suc:
            self.defaultGUI()
            return False

        return True

    def loadProgramModel(self):
        """
        loadProgramModel selects one or more models from the files system, combines them
        if more than one was selected and programs them into the mount computer.

        :return: success
        """

        folder = self.app.mwGlob['modelDir']
        loadFilePath, fileName, ext = self.openFile(self,
                                                    'Open model file',
                                                    folder,
                                                    'Model files (*.model)',
                                                    multiple=True,
                                                    )
        if not loadFilePath:
            return False

        if isinstance(loadFilePath, str):
            loadFilePath = [loadFilePath]

        self.app.message.emit('Programing models', 1)

        modelJSON = list()
        for index, file in enumerate(loadFilePath):
            self.app.message.emit(f'Loading model [{os.path.basename(file)}]', 0)
            with open(file, 'r') as infile:
                model = json.load(infile)
                modelJSON += model

        # preparing the text
        if index:
            postFix = 's'
        else:
            postFix = ''

        if len(modelJSON) > 99:
            self.app.message.emit(f'Model{postFix} has more than 99 points', 2)
            return False

        # finally do it
        self.app.message.emit(f'Programming {index + 1} model{postFix} to mount', 0)

        build = self.generateBuildData(modelJSON)
        suc = self.app.mount.model.programAlign(build)

        if suc:
            self.app.message.emit(f'Model{postFix} programmed with success', 1)
            self.refreshModel()
        else:
            self.app.message.emit('Programming error', 2)

        return suc
