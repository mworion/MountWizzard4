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
# written in python 3, (c) 2019, 2020 by mworion
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
from datetime import datetime

# external packages
import PyQt5.uic
from PyQt5.QtTest import QTest
from mountcontrol.alignStar import AlignStar
from mountcontrol.convert import convertToHMS, convertToDMS

# local import
from base import transform


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


class Model:
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    # define a max error which throws point out of queue in arcsec
    MAX_ERROR_MODEL_POINT = 99999

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

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
        self.statusDAT = None

        # func signals
        ms = self.app.mount.signals
        ms.alignDone.connect(self.updateAlignGUI)
        ms.alignDone.connect(self.updateTurnKnobsGUI)

        # ui signals
        self.ui.runModel.clicked.connect(self.modelBuild)
        self.ui.cancelModel.clicked.connect(self.cancelBuild)
        self.ui.endModel.clicked.connect(self.modelFinished)
        self.ui.pauseModel.clicked.connect(self.pauseBuild)
        self.ui.batchModel.clicked.connect(self.loadProgramModel)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.checkDisableDAT.setChecked(config.get('checkDisableDAT', False))
        self.ui.checkEnableBackup.setChecked(config.get('checkEnableBackup', False))
        self.ui.parkMountAfterModel.setChecked(config.get('parkMountAfterModel', False))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['checkDisableDAT'] = self.ui.checkDisableDAT.isChecked()
        config['checkEnableBackup'] = self.ui.checkEnableBackup.isChecked()
        config['parkMountAfterModel'] = self.ui.parkMountAfterModel.isChecked()

        return True

    def updateAlignGUI(self, model):
        """
        updateAlignGUI shows the data which is received through the getain command. this is
        mainly polar and ortho errors as well as basic model data.

        :param model:
        :return:    True if ok for testing
        """

        if model.numberStars is not None:
            text = f'{model.numberStars:3.0f}'
        else:
            text = '-'
        self.ui.numberStars.setText(text)
        self.ui.numberStars1.setText(text)

        if model.terms is not None:
            text = f'{model.terms:2.0f}'
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
            text = f'{model.polarError.degrees * 3600:5.0f}'
        else:
            text = '-'
        self.ui.polarError.setText(text)

        if model.orthoError is not None:
            text = f'{model.orthoError.degrees * 3600:5.0f}'
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
                text = '{0:3.2f} revs left'.format(abs(model.azimuthTurns))
            else:
                text = '{0:3.2f} revs right'.format(abs(model.azimuthTurns))
        else:
            text = '-'
        self.ui.azimuthTurns.setText(text)

        if model.altitudeTurns is not None:
            if model.altitudeTurns > 0:
                text = '{0:3.2f} revs down'.format(abs(model.altitudeTurns))
            else:
                text = '{0:3.2f} revs up'.format(abs(model.altitudeTurns))
        else:
            text = '-'
        self.ui.altitudeTurns.setText(text)

        return True

    def updateProgress(self, number=0, count=0):
        """
        updateProgress calculated from the elapsed time and number of point with taking
        actual processing time into account a estimation of duration and finishing time
        of the modeling process and updates this in the gui

        :param number: total number of model points
        :param count: index of the actual processed point
        :return: success
        """

        if not 0 <= count < number:
            return False

        fraction = (count + 1) / number

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
        modelSolveDone is called when a point is solved by astrometry. if called it takes
        the model point out of the queue and adds the solving data for later model build.
        as the solving takes place in J2000 epoch, but we need fpr die model build JNow
        epoch, the transformation is done as well.

        in addition as it is the last step before a model point could be used, the
        it checks for the end of the modeling process.

        :param result: true for test purpose
        :return: success
        """

        self.log.info('Processing astrometry result')

        if self.resultQueue.empty():
            self.log.warning('empty result queue')
            return False

        mPoint = self.resultQueue.get()
        number = mPoint["lenSequence"]
        count = mPoint["countSequence"]

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
                self.log.info(f'Queued to model [{mPoint["countSequence"]:03d}]: [{mPoint}]')
                self.modelQueue.put(mPoint)

            else:
                text = f'Solving failed for image-{count:03d}'
                self.app.message.emit(text, 2)

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
            text = f'Solving  image-{count:03d}:  {mPoint.get("message")}'
            self.app.message.emit(text, 2)

        self.updateProgress(number=number,
                            count=count)

        if number == count + 1:
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

        self.log.info('Solving started')

        if self.solveQueue.empty():
            self.log.warning('empty solve queue')
            return False

        mPoint = self.solveQueue.get()

        self.app.showImage.emit(mPoint["imagePath"])

        self.resultQueue.put(mPoint)
        self.log.info(f'Queued to result [{mPoint["countSequence"]:03d}]: [{mPoint}]')
        self.app.astrometry.solveThreading(fitsPath=mPoint["imagePath"],
                                           updateFits=False,
                                           )

        text = f'Solving  image-{mPoint["countSequence"]:03d}:  '
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

        self.log.info('Imaging started')

        if self.imageQueue.empty():
            self.log.warning('empty image queue')
            return False

        mPoint = self.imageQueue.get()
        self.collector.resetSignals()

        while self.ui.pauseModel.property('pause'):
            QTest.qWait(100)

        self.app.camera.expose(imagePath=mPoint['imagePath'],
                               expTime=mPoint['exposureTime'],
                               binning=mPoint['binning'],
                               subFrame=mPoint['subFrame'],
                               fastReadout=mPoint['fastReadout'],
                               focalLength=mPoint['focalLength'],
                               )

        mPoint['raJNowM'] = self.app.mount.obsSite.raJNow
        mPoint['decJNowM'] = self.app.mount.obsSite.decJNow
        mPoint['angularPosRA'] = self.app.mount.obsSite.angularPosRA
        mPoint['angularPosDEC'] = self.app.mount.obsSite.angularPosDEC
        mPoint['siderealTime'] = self.app.mount.obsSite.timeSidereal
        mPoint['julianDate'] = self.app.mount.obsSite.timeJD
        mPoint['pierside'] = self.app.mount.obsSite.pierside

        self.solveQueue.put(mPoint)
        self.log.info(f'Queued to solve [{mPoint["countSequence"]:03d}]: [{mPoint}]')

        text = f'Exposing image-{mPoint["countSequence"]:03d}:  '
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

        self.log.info('Slew started')

        if self.slewQueue.empty():
            self.log.warning('Empty slew queue')
            return False

        mPoint = self.slewQueue.get()
        suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=mPoint['altitude'],
                                                    az_degrees=mPoint['azimuth'],
                                                    )

        if not suc:
            return False

        if self.deviceStat['dome']:
            useGeometry = self.ui.checkDomeGeometry.isChecked()
            alt = mPoint['altitude']
            az = mPoint['azimuth']

            if useGeometry:
                haT = self.app.mount.obsSite.haJNowTarget
                decT = self.app.mount.obsSite.decJNowTarget
                piersideT = self.app.mount.obsSite.piersideTarget
                lat = self.app.mount.obsSite.location.latitude
                delta = self.app.dome.slewDome(altitude=alt,
                                               azimuth=az,
                                               piersideT=piersideT,
                                               haT=haT,
                                               decT=decT,
                                               lat=lat)

            else:
                delta = self.app.dome.slewDome(altitude=alt,
                                               azimuth=az)

            geoStat = 'Geometry corrected' if useGeometry else 'Equal mount'
            text = f'Slewing  dome:       point: {mPoint["countSequence"]:03d}, '
            text += f'{geoStat}, az: {az:3.1f} delta: {delta:3.1f}'
            self.app.message.emit(text, 0)

        self.app.mount.obsSite.startSlewing()
        self.imageQueue.put(mPoint)
        self.log.info(f'Queued to image [{mPoint["countSequence"]:03d}]: [{mPoint}]')

        text = f'Slewing  mount:      point: {mPoint["countSequence"]:03d}, '
        text += f'altitude: {mPoint["altitude"]:3.0f}, '
        text += f'azimuth: {mPoint["azimuth"]:3.0f}'
        self.app.message.emit(text, 0)

        self.ui.mPoints.setText(f'{mPoint["lenSequence"]:2d}')
        self.ui.mSlew.setText(f'{mPoint["countSequence"] + 1:2d}')

        return True

    def changeStatusDAT(self):
        """

        :return: True for test purpose
        """

        if not self.ui.checkDisableDAT.isChecked():
            return False

        if self.statusDAT is None:
            self.statusDAT = self.app.mount.setting.statusDualAxisTracking

        self.statusDAT = self.app.mount.setting.statusDualAxisTracking
        self.app.mount.setting.setDualAxisTracking(False)
        self.changeStyleDynamic(self.ui.statusDualAxisTracking, 'color', 'yellow')

        return True

    def restoreStatusDAT(self):
        """

        :return: true for test purpose
        """

        if not self.ui.checkDisableDAT.isChecked():
            return False

        if self.statusDAT is None:
            return False

        self.app.mount.setting.setDualAxisTracking(self.statusDAT)
        self.changeStyleDynamic(self.ui.statusDualAxisTracking, 'color', '')

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

    def pauseBuild(self):
        """

        :return: True for test purpose
        """
        if self.ui.pauseModel.property('pause'):
            self.changeStyleDynamic(self.ui.pauseModel, 'pause', False)
        else:
            self.changeStyleDynamic(self.ui.pauseModel, 'pause', True)

        return True

    def cancelBuild(self):
        """
        cancelBuild aborts imaging and stops all modeling queues and actions and restores
        them to default values.

        :return: true for test purpose
        """

        self.restoreStatusDAT()
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

        model = self.app.mount.model

        if len(model.starList) != len(self.model):
            text = f'length starList [{len(model.starList)}] and length '
            text += f'model [{len(self.model)}] is different'
            self.log.info(text)
            self.model = []

        for i, mPoint in enumerate(self.model):
            mPoint['errorRMS'] = model.starList[i].errorRMS
            mPoint['errorAngle'] = model.starList[i].errorAngle.degrees
            mPoint['haMountModel'] = model.starList[i].coord.ra.hours
            mPoint['decMountModel'] = model.starList[i].coord.dec.degrees
            mPoint['errorRA'] = model.starList[i].errorRA()
            mPoint['errorDEC'] = model.starList[i].errorDEC()
            mPoint['errorIndex'] = model.starList[i].number
            mPoint['modelTerms'] = model.terms
            mPoint['modelErrorRMS'] = model.errorRMS
            mPoint['modelOrthoError'] = model.orthoError.degrees * 3600
            mPoint['modelPolarError'] = model.polarError.degrees * 3600

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
        saveModelFinish is the callback after the new model data is loaded from the mount
        computer. first is disables the signals. New we have the original model build data
        which was programmed to the mount and the retrieved model data after the mount
        optimized the model. retrofitModel() combines this data to a signal data structure.
        after that it saves the model data for later use.

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
            self.log.info(f'Only {len(self.model)} points available')
            return False

        self.app.mount.signals.alignDone.connect(self.saveModelFinish)
        self.refreshModel()

        return True

    @staticmethod
    def generateBuildData(model=None):
        """
        generateBuildData takes the model data and generates from it a data structure
        needed for programming the model into the mount computer.

        :param model:
        :return: build
        """

        if model is None:
            model = []

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

        self.model = list()

        while not self.modelQueue.empty():
            mPoint = self.modelQueue.get()
            self.model.append(mPoint)

        if len(self.model) < 3:
            self.app.message.emit(f'Modeling finished:    {self.modelName}', 2)
            self.app.message.emit('Model not enough valid model point', 2)
            return False

        self.defaultSignals()
        self.clearQueues()
        self.defaultGUI()
        self.restoreStatusDAT()

        if self.ui.checkEnableBackup.isChecked():
            self.app.message.emit('Backing up models', 0)
            self.app.mount.model.storeName('temp')
            self.app.mount.model.loadName('back2')
            self.app.mount.model.storeName('back3')
            self.app.mount.model.loadName('back1')
            self.app.mount.model.storeName('back2')
            self.app.mount.model.loadName('back0')
            self.app.mount.model.storeName('back1')
            self.app.mount.model.loadName('temp')
            self.app.mount.model.storeName('back0')
            self.app.mount.model.deleteName('temp')

        self.app.message.emit('Programming model to mount', 0)
        build = self.generateBuildData(model=self.model)
        suc = self.app.mount.model.programAlign(build)

        if suc:
            self.saveModelPrepare()
            self.app.mount.model.storeName('actual')
            self.app.message.emit('Model programmed with success', 0)

        else:
            self.app.message.emit('Model programming error', 2)

        # cleaning up the disk space
        if not self.ui.checkKeepImages.isChecked():
            self.app.message.emit('Deleting model images', 0)
            shutil.rmtree(self.imageDir, ignore_errors=True)

        self.app.message.emit(f'Modeling finished:    {self.modelName}', 1)
        self.playSound('ModelingFinished')
        self.refreshName()

        if self.ui.parkMountAfterModel.isChecked():
            self.app.message.emit('Parking mount after model run', 0)
            suc = self.app.mount.obsSite.park()

            if not suc:
                self.app.message.emit('Cannot park mount', 2)

            else:
                self.app.message.emit('Mount parked', 0)

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
        if len(points) < 3:
            return False

        astrometryApp = self.ui.astrometryDevice.currentText()

        if astrometryApp.startswith('No device'):
            return False

        self.changeStatusDAT()

        nameTime = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        self.modelName = f'm-{nameTime}-{self.lastGenerator}'
        self.imageDir = f'{self.app.mwGlob["imageDir"]}/{self.modelName}'

        if not os.path.isdir(self.imageDir):
            os.mkdir(self.imageDir)

        if not os.path.isdir(self.imageDir):
            return False

        self.clearQueues()
        self.app.message.emit(f'Modeling start:      {self.modelName}', 1)

        exposureTime = self.ui.expTime.value()
        binning = self.ui.binning.value()
        subFrame = self.ui.subFrame.value()
        fastReadout = self.ui.checkFastDownload.isChecked()
        solveTimeout = self.app.astrometry.run['astap'].timeout
        searchRadius = self.app.astrometry.run['astap'].searchRadius
        focalLength = self.ui.focalLength.value()
        lenSequence = len(points)

        self.prepareGUI()
        self.prepareSignals()
        self.startModeling = time.time()

        for countSequence, point in enumerate(points):

            modelSet = dict()
            imagePath = f'{self.imageDir}/image-{countSequence:03d}.fits'
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
            modelSet['focalLength'] = focalLength
            modelSet['altitude'] = point[0]
            modelSet['azimuth'] = point[1]
            self.slewQueue.put(copy.copy(modelSet))

        self.modelSlew()

        return True

    def modelBuild(self):
        """
        modelBuild sets the adequate gui elements, selects the model points and calls the
        core modeling method.

        :return: true for test purpose
        """

        if len(self.app.data.buildP) < 2:
            self.app.message.emit('No modeling start because less than 3 points', 2)
            return False

        if len(self.app.data.buildP) > 99:
            self.app.message.emit('No modeling start because more than 99 points', 2)
            return False

        sucApp, sucIndex = self.app.astrometry.checkAvailability()
        if not (sucApp and sucIndex):
            self.app.message.emit('No valid configuration for plate solver', 2)
            return False

        self.app.mount.model.deleteName('backup')
        self.app.mount.model.storeName('backup')

        suc = self.app.mount.model.clearAlign()
        if not suc:
            self.app.message.emit('Actual model cannot be cleared', 2)
            return False

        else:
            self.app.message.emit('Actual model clearing, waiting 3s', 0)
            QTest.qWait(3000)
            self.app.message.emit('Actual model cleared', 0)
            self.refreshModel()

        value = self.ui.settleTimeMount.value()
        if value < 2:
            self.app.message.emit(f'Mount settling time short [{value}]s', 2)

        if self.app.uiWindows['showImageW']['classObj']:
            winImage = self.app.uiWindows['showImageW']['classObj']
            if winImage.deviceStat['expose'] or winImage.deviceStat['exposeN']:
                winImage.abortImage()

        self.changeStyleDynamic(self.ui.runModel, 'running', True)
        self.changeStyleDynamic(self.ui.cancelModel, 'cancel', True)
        self.changeStyleDynamic(self.ui.cancelModel, 'pause', False)
        self.ui.cancelModel.setEnabled(True)
        self.ui.endModel.setEnabled(True)
        self.ui.pauseModel.setEnabled(True)
        self.ui.plateSolveSync.setEnabled(False)
        self.ui.runFlexure.setEnabled(False)
        self.ui.runHysteresis.setEnabled(False)

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

        self.app.mount.model.deleteName('backup')
        self.app.mount.model.storeName('backup')

        suc = self.app.mount.model.clearAlign()
        if not suc:
            self.app.message.emit('Actual model cannot be cleared', 2)
            return False

        else:
            self.app.message.emit('Actual model clearing, waiting 1s', 0)
            QTest.qWait(1000)
            self.app.message.emit('Actual model cleared', 0)

        modelJSON = list()
        for index, file in enumerate(loadFilePath):
            self.app.message.emit(f'Loading model [{os.path.basename(file)}]', 0)
            with open(file, 'r') as infile:
                model = json.load(infile)
                modelJSON += model

        if index:
            postFix = 's'

        else:
            postFix = ''

        if len(modelJSON) > 99:
            self.app.message.emit(f'Model{postFix} has more than 99 points', 2)
            return False

        self.app.message.emit(f'Programming {index + 1} model{postFix} to mount', 0)

        build = self.generateBuildData(modelJSON)
        suc = self.app.mount.model.programAlign(build)

        if suc:
            self.app.message.emit(f'Model{postFix} programmed with success', 1)
            self.refreshModel()

        else:
            self.app.message.emit('Programming error', 2)

        return suc
