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
# Python  v3.7.3
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
from datetime import datetime, timedelta
# external packages
import PyQt5.QtWidgets
import PyQt5.uic
import skyfield.api
from mountcontrol.model import APoint
# local import
from mw4.definitions import Point, MPoint, IParam, MParam, MData, RData, Solve, Solution
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


class BuildModel(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):

        self.slewQueue = queue.Queue()
        self.imageQueue = queue.Queue()
        self.solveQueue = queue.Queue()
        self.resultQueue = queue.Queue()
        self.modelQueue = queue.Queue()
        self.collector = QMultiWait()
        self.startModeling = None
        self.modelName = ''
        self.imageDir = ''
        self.lastModelType = ''

        self.ui.genBuildGrid.clicked.connect(self.genBuildGrid)
        self.ui.numberGridPointsCol.valueChanged.connect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.connect(self.genBuildGrid)
        self.ui.genBuildMax.clicked.connect(self.genBuildMax)
        self.ui.genBuildMed.clicked.connect(self.genBuildMed)
        self.ui.genBuildNorm.clicked.connect(self.genBuildNorm)
        self.ui.genBuildMin.clicked.connect(self.genBuildMin)
        self.ui.genBuildFile.clicked.connect(self.genBuildFile)
        self.ui.genBuildDSO.clicked.connect(self.genBuildDSO)
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.ui.durationDSO.valueChanged.connect(self.genBuildDSO)
        self.ui.timeShiftDSO.valueChanged.connect(self.genBuildDSO)
        self.ui.saveBuildPoints.clicked.connect(self.saveBuildFile)
        self.ui.saveBuildPointsAs.clicked.connect(self.saveBuildFileAs)
        self.ui.loadBuildPoints.clicked.connect(self.loadBuildFile)
        self.ui.numberSpiralPoints.valueChanged.connect(self.genBuildGoldenSpiral)
        self.ui.genBuildGoldenSpiral.clicked.connect(self.genBuildGoldenSpiral)
        self.ui.runFullModel.clicked.connect(self.modelFull)
        self.ui.cancelFullModel.clicked.connect(self.cancelFull)
        self.ui.runAlignModel.clicked.connect(self.modelAlign)
        self.ui.cancelAlignModel.clicked.connect(self.cancelFull)
        self.ui.batchModel.clicked.connect(self.loadProgramModel)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']

        self.ui.numberGridPointsCol.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberDSOPoints.valueChanged.disconnect(self.genBuildDSO)
        self.ui.durationDSO.valueChanged.disconnect(self.genBuildDSO)
        self.ui.timeShiftDSO.valueChanged.disconnect(self.genBuildDSO)

        self.ui.buildPFileName.setText(config.get('buildPFileName', ''))
        self.lastModelType = config.get('lastModelType', '')
        self.ui.numberGridPointsRow.setValue(config.get('numberGridPointsRow', 5))
        self.ui.numberGridPointsCol.setValue(config.get('numberGridPointsCol', 6))
        self.ui.altitudeMin.setValue(config.get('altitudeMin', 30))
        self.ui.altitudeMax.setValue(config.get('altitudeMax', 75))
        self.ui.numberDSOPoints.setValue(config.get('numberDSOPoints', 20))
        self.ui.durationDSO.setValue(config.get('durationDSO', 5))
        self.ui.timeShiftDSO.setValue(config.get('timeShiftDSO', 0))

        # initialising the signal slot connections after the value are set, because
        # otherwise we get a first value changed signal just when populating
        # the initial data. this should not happen.
        self.ui.numberGridPointsCol.valueChanged.connect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.connect(self.genBuildGrid)
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.ui.durationDSO.valueChanged.connect(self.genBuildDSO)
        self.ui.timeShiftDSO.valueChanged.connect(self.genBuildDSO)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['buildPFileName'] = self.ui.buildPFileName.text()
        config['lastModelType'] = self.lastModelType
        config['numberGridPointsRow'] = self.ui.numberGridPointsRow.value()
        config['numberGridPointsCol'] = self.ui.numberGridPointsCol.value()
        config['altitudeMin'] = self.ui.altitudeMin.value()
        config['altitudeMax'] = self.ui.altitudeMax.value()
        config['numberDSOPoints'] = self.ui.numberDSOPoints.value()
        config['durationDSO'] = self.ui.durationDSO.value()
        config['timeShiftDSO'] = self.ui.timeShiftDSO.value()

        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True for test purpose
        """

        self.wIcon(self.ui.genBuildGrid, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMax, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMed, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildNorm, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildMin, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.genBuildDSO, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)

        return True

    def genBuildGrid(self):
        """
        genBuildGrid generates a grid of point for model build based on gui data. the cols
        have to be on even numbers.

        :return: success
        """

        self.lastModelType = 'grid'
        row = self.ui.numberGridPointsRow.value()
        col = self.ui.numberGridPointsCol.value()
        minAlt = self.ui.altitudeMin.value()
        maxAlt = self.ui.altitudeMax.value()
        suc = self.app.data.genGrid(minAlt=minAlt,
                                    maxAlt=maxAlt,
                                    numbRows=row,
                                    numbCols=col)
        if not suc:
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def genBuildMax(self):
        """
        genBuildMax generates the point pattern based on greater circles for model build.
        the point are calculated for the observers position. max goes for approx 100 points
        effectively when removing the horizon.

        :return: success
        """

        self.lastModelType = 'circle-max'
        suc = self.app.data.genGreaterCircle(selection='max')
        if not suc:
            self.app.message.emit('Build points [max] cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def genBuildMed(self):
        """
        genBuildMed generates the point pattern based on greater circles for model build.
        the point are calculated for the observers position. max goes for approx 70 points
        effectively when removing the horizon.

        :return: success
        """

        self.lastModelType = 'circle-med'
        suc = self.app.data.genGreaterCircle(selection='med')
        if not suc:
            self.app.message.emit('Build points [med] cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def genBuildNorm(self):
        """
        genBuildNorm generates the point pattern based on greater circles for model build.
        the point are calculated for the observers position. max goes for approx 40 points
        effectively when removing the horizon.

        :return: success
        """

        self.lastModelType = 'circle-norm'
        suc = self.app.data.genGreaterCircle(selection='norm')
        if not suc:
            self.app.message.emit('Build points [norm] cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def genBuildMin(self):
        """
        genBuildMin generates the point pattern based on greater circles for model build.
        the point are calculated for the observers position. min goes for approx 25 points
        effectively when removing the horizon.

        :return: success
        """

        self.lastModelType = 'circle-min'
        suc = self.app.data.genGreaterCircle(selection='min')
        if not suc:
            self.app.message.emit('Build points [min] cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def genBuildDSO(self):
        """
        genBuildDSO generates points along the actual tracking path

        :return: success
        """

        self.lastModelType = 'DSO'
        ra = self.app.mount.obsSite.raJNow
        dec = self.app.mount.obsSite.decJNow
        timeJD = self.app.mount.obsSite.timeJD
        location = self.app.mount.obsSite.location

        if ra is None or dec is None or location is None:
            self.app.message.emit('DSO Path cannot be generated', 2)
            return False

        numberPoints = self.ui.numberDSOPoints.value()
        duration = self.ui.durationDSO.value()
        timeShift = self.ui.timeShiftDSO.value()

        suc = self.app.data.generateDSOPath(ra=ra,
                                            dec=dec,
                                            timeJD=timeJD,
                                            location=location,
                                            numberPoints=numberPoints,
                                            duration=duration,
                                            timeShift=timeShift,
                                            )

        if not suc:
            self.app.message.emit('DSO Path cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def genBuildGoldenSpiral(self):
        """
        genBuildGoldenSpiral generates points along the actual tracking path

        :return: success
        """

        self.lastModelType = 'spiral'
        numberPoints = self.ui.numberSpiralPoints.value()

        suc = self.app.data.generateGoldenSpiral(numberPoints=numberPoints)
        if not suc:
            self.app.message.emit('Golden spiral cannot be generated', 2)
            return False

        self.autoDeletePoints()
        self.autoSortPoints()

        return True

    def loadBuildFile(self):
        """
        loadBuildFile calls a file selector box and selects the filename to be loaded

        :return: success
        """

        folder = self.app.mwGlob['configDir']
        loadFilePath, fileName, ext = self.openFile(self,
                                                    'Open build point file',
                                                    folder,
                                                    'Build point files (*.bpts)',
                                                    )
        if not loadFilePath:
            return False

        suc = self.app.data.loadBuildP(fileName=fileName)
        if suc:
            self.ui.buildPFileName.setText(fileName)
            self.app.message.emit('Build file [{0}] loaded'.format(fileName), 0)
        else:
            self.app.message.emit('Build file [{0}] cannot no be loaded'.format(fileName), 2)

        return True

    def saveBuildFile(self):
        """
        saveBuildFile calls saving the build file

        :return: success
        """

        fileName = self.ui.buildPFileName.text()
        if not fileName:
            self.app.message.emit('Build points file name not given', 2)
            return False

        suc = self.app.data.saveBuildP(fileName=fileName)

        if suc:
            self.app.message.emit('Build file [{0}] saved'.format(fileName), 0)
        else:
            self.app.message.emit('Build file [{0}] cannot no be saved'.format(fileName), 2)

        return True

    def saveBuildFileAs(self):
        """
        saveBuildFileAs calls a file selector box and selects the filename to be save

        :return: success
        """

        folder = self.app.mwGlob['configDir']
        saveFilePath, fileName, ext = self.saveFile(self,
                                                    'Save build point file',
                                                    folder,
                                                    'Build point files (*.bpts)',
                                                    )
        if not saveFilePath:
            return False

        suc = self.app.data.saveBuildP(fileName=fileName)

        if suc:
            self.ui.buildPFileName.setText(fileName)
            self.app.message.emit('Build file [{0}] saved'.format(fileName), 0)
        else:
            self.app.message.emit('Build file [{0}] cannot no be saved'.format(fileName), 2)

        return True

    def genBuildFile(self):
        """
        genBuildFile tries to load a give build point file and displays it for usage.

        :return: success
        """

        fileName = self.ui.buildPFileName.text()
        if not fileName:
            self.app.message.emit('Build points file name not given', 2)
            return False

        self.lastModelType = 'file'
        suc = self.app.data.loadBuildP(fileName=fileName)
        if not suc:
            text = 'Build points file [{0}] could not be loaded'.format(fileName)
            self.app.message.emit(text, 2)
            return False

        self.autoDeletePoints()

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

    @staticmethod
    def addResultToModel(mPoint=None, result=None):
        """
        addResultToModel takes the result of the solving process and add the data to the
        actual model point. as the coordinates for programming the model need to be in
        JNow and the solving process gives J2000 coordinates, it does the transform as
        well.

        :param mPoint:
        :param result:
        :return: model
        """

        rData = result.solve
        raJNow, decJNow = transform.J2000ToJNow(rData.raJ2000,
                                                rData.decJ2000,
                                                mPoint.mData.julian)

        mData = MData(raMJNow=mPoint.mData.raMJNow,
                      decMJNow=mPoint.mData.decMJNow,
                      raSJNow=raJNow,
                      decSJNow=decJNow,
                      sidereal=mPoint.mData.sidereal,
                      julian=mPoint.mData.julian,
                      pierside=mPoint.mData.pierside,
                      )
        mPoint = MPoint(mParam=mPoint.mParam,
                        iParam=mPoint.iParam,
                        point=mPoint.point,
                        mData=mData,
                        rData=mPoint.rData,
                        )

        return mPoint

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
            self.logger.error('empty result queue')
            return False

        mPoint = self.resultQueue.get()
        number = mPoint.mParam.number
        count = mPoint.mParam.count
        modelingDone = (number == count + 1)

        if not isinstance(result, Solution):
            self.logger.info(f'Solving result is malformed: {result}')
            self.logger.error('empty result queue')
            return False
        if not isinstance(result.solve, Solve):
            self.logger.info(f'Solving result is malformed: {result}')
            self.logger.error('empty result queue')
            return False

        # processing only the model point which are OK
        if result.success:
            mPoint = self.addResultToModel(mPoint=mPoint, result=result)
            self.modelQueue.put(mPoint)

            text = f'Solved   image-{mPoint.mParam.count:03d} ->   '
            text += f'Ra: {transform.convertToHMS(result.solve.raJ2000)}, '
            text += f'Dec: {transform.convertToDMS(result.solve.decJ2000)}, '
            text += f'Error: {result.solve.error:5.2f}, Angle: {result.solve.angle:3.0f}, '
            text += f'Scale: {result.solve.scale:4.6f}'
            self.app.message.emit(text, 0)
        else:
            text = f'Solving error for image-{mPoint.mParam.count:03d}'
            self.app.message.emit(text, 2)

        self.updateProgress(number=number, count=count, modelingDone=modelingDone)

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

        :return: true for test purpose
        """

        if self.solveQueue.empty():
            self.logger.error('empty solve queue')
            return False

        mPoint = self.solveQueue.get()

        if self.app.imageW:
            self.app.imageW.signals.showExt.emit(mPoint.mParam.path)

        self.app.astrometry.solveThreading(app=mPoint.mParam.astrometry,
                                           fitsPath=mPoint.mParam.path,
                                           radius=mPoint.mParam.radius,
                                           timeout=mPoint.mParam.timeout,
                                           updateFits=False,
                                           )
        self.resultQueue.put(mPoint)

        text = f'Solving  image-{mPoint.mParam.count:03d} ->   '
        text += f'{os.path.basename(mPoint.mParam.path)}'
        self.app.message.emit(text, 0)
        self.ui.mSolve.setText(f'{mPoint.mParam.count + 1:2d}')

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

        :return: true for test purpose
        """

        if self.imageQueue.empty():
            self.logger.error('empty image queue')
            return False

        mPoint = self.imageQueue.get()
        self.collector.resetSignals()

        self.app.imaging.expose(imagePath=mPoint.mParam.path,
                                expTime=mPoint.iParam.expTime,
                                binning=mPoint.iParam.binning,
                                subFrame=mPoint.iParam.subFrame,
                                fastReadout=mPoint.iParam.fastReadout,
                                )

        mPoint = MPoint(mParam=mPoint.mParam,
                        iParam=mPoint.iParam,
                        point=mPoint.point,
                        mData=MData(raMJNow=self.app.mount.obsSite.raJNow,
                                    decMJNow=self.app.mount.obsSite.decJNow,
                                    raSJNow=None,
                                    decSJNow=None,
                                    sidereal=self.app.mount.obsSite.timeSidereal,
                                    julian=self.app.mount.obsSite.timeJD,
                                    pierside=self.app.mount.obsSite.pierside,
                                    ),
                        rData=None,
                        )

        self.solveQueue.put(mPoint)

        text = f'Exposing image-{mPoint.mParam.count:03d} ->   '
        text += f'path: {os.path.basename(mPoint.mParam.path)}'
        self.app.message.emit(text, 0)
        self.ui.mImage.setText(f'{mPoint.mParam.count + 1 :2d}')

        return True

    def modelSlew(self):
        """
        modelSlew is the method called from the model core method and is the beginning of
        the modeling chain. it starts with taking a first model point from the initial
        slew queue and starts slewing mount (and dome if present).if the queue is empty
        (which should be to the case), it just returns.

        it shows the actual processed point index in GUI

        :return: true for test purpose

        """

        if self.slewQueue.empty():
            return False

        mPoint = self.slewQueue.get()

        self.app.dome.slewToAltAz(azimuth=mPoint.point.azimuth)
        self.app.mount.obsSite.slewAltAz(alt_degrees=mPoint.point.altitude,
                                         az_degrees=mPoint.point.azimuth,
                                         )

        self.imageQueue.put(mPoint)

        text = f'Slewing  image-{mPoint.mParam.count:03d} ->   '
        text += f'altitude: {mPoint.point.altitude:3.0f}, '
        text += f'azimuth: {mPoint.point.azimuth:3.0f}'
        self.app.message.emit(text, 0)
        self.ui.mPoints.setText(f'{mPoint.mParam.number:2d}')
        self.ui.mSlew.setText(f'{mPoint.mParam.count + 1:2d}')

        return True

    def clearQueues(self):
        """
        clearQueues ensures that all used queues will be emptied before starting

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
        running actions

        :return: true for test purpose
        """

        self.ui.batchModel.setEnabled(False)

        return True

    def defaultGUI(self):
        """
        defaultGUI will reset all gui elements to the idle or default state and new actions
        could be started again

        :return: true for test purpose
        """

        self.changeStyleDynamic(self.ui.runFullModel, 'running', False)
        self.changeStyleDynamic(self.ui.cancelFullModel, 'cancel', False)
        self.changeStyleDynamic(self.ui.runAlignModel, 'running', False)
        self.changeStyleDynamic(self.ui.cancelAlignModel, 'cancel', False)
        self.ui.runFullModel.setEnabled(True)
        self.ui.cancelFullModel.setEnabled(False)
        self.ui.runAlignModel.setEnabled(True)
        self.ui.cancelAlignModel.setEnabled(False)
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
        if self.app.dome.device is not None:
            self.collector.addWaitableSignal(self.app.dome.signals.slewFinished)

        self.collector.ready.connect(self.modelImage)
        self.app.imaging.signals.integrated.connect(self.modelSlew)
        self.app.imaging.signals.saved.connect(self.modelSolve)
        self.app.astrometry.signals.done.connect(self.modelSolveDone)

        return True

    def defaultSignals(self):
        """
        defaultSignals clears the signal queue and removes the connections

        :return: true for test purpose
        """

        self.app.imaging.signals.saved.disconnect(self.modelSolve)
        self.app.imaging.signals.integrated.disconnect(self.modelSlew)
        self.app.astrometry.signals.done.disconnect(self.modelSolveDone)
        self.collector.ready.disconnect(self.modelImage)
        self.collector.clear()

        return True

    def cancelFull(self):
        """
        cancelFull aborts imaging and stops all modeling queues and actions

        :return: true for test purpose
        """

        self.app.imaging.abort()
        self.app.astrometry.abort()
        self.defaultSignals()
        self.clearQueues()
        self.defaultGUI()
        self.app.message.emit('Modeling cancelled', 2)

        return True

    def retrofitModel(self, model=None):
        """
        retrofitModel reads the actual model points and results out of the mount computer
        and adds the optimized (recalculated) error values to the point. that's necessary,
        because when imaging and solving a point the error is related to this old model.
        when programming a new model, all point will be recalculated be the mount
        computer an get a new error value which is based on the new model.

        :param model:
        :return: updated model
        """

        if model is None:
            self.logger.debug('model is None')
            return list()

        starList = self.app.mount.model.starList

        if len(starList) != len(model):
            text = f'length starList [{len(starList)}] and length '
            text += f'model [{len(model)}] is different'
            self.logger.debug(text)
            return list()

        for i, mPoint in enumerate(model):
            rData = RData(errorRMS=starList[i].errorRMS,
                          errorRA=starList[i].errorRA(),
                          errorDEC=starList[i].errorDEC(),
                          )
            mPoint = MPoint(mParam=mPoint.mParam,
                            iParam=mPoint.iParam,
                            point=mPoint.point,
                            mData=mPoint.mData,
                            rData=rData,
                            )
            model[i] = mPoint

        return model

    @staticmethod
    def generateSaveModel(model=None):
        """
        generateSaveModel builds from the model file a format which could be serialized
        in json. this format will be used for storing model on file

        :param model:
        :return: save model format
        """

        saveModel = list()
        for mPoint in model:
            sPoint = {'name': mPoint.mParam.name,
                      'path': mPoint.mParam.path,
                      'number': mPoint.mParam.number,
                      'count': mPoint.mParam.count,
                      'expTime': mPoint.iParam.expTime,
                      'binning': mPoint.iParam.binning,
                      'subFrame': mPoint.iParam.subFrame,
                      'fastReadout': mPoint.iParam.fastReadout,
                      'altitude': mPoint.point.altitude,
                      'azimuth': mPoint.point.azimuth,
                      'raMJNow': mPoint.mData.raMJNow.hours,
                      'decMJNow': mPoint.mData.decMJNow.degrees,
                      'raSJNow': mPoint.mData.raSJNow.hours,
                      'decSJNow': mPoint.mData.decSJNow.degrees,
                      'sidereal': mPoint.mData.sidereal,
                      'julian': mPoint.mData.julian.utc_iso(),
                      'pierside': mPoint.mData.pierside,
                      'errorRMS': mPoint.rData.errorRMS,
                      'errorRa': mPoint.rData.errorRA,
                      'errorDEC': mPoint.rData.errorDEC,
                      }
            saveModel.append(sPoint)
        return saveModel

    def saveModel(self, model=None):
        """
        saveModel saves the model data for later use. with this data, the model could
        be reprogrammed without doing some imaging, it could be added with other data to
        extend the model to a broader base.
        in addition it should be possible to make som analyses with this data.

        :param model:
        :return: success
        """

        if model is None:
            return False
        if len(model) < 3:
            self.logger.debug(f'only {len(model)} points available')
            return False

        saveModel = self.generateSaveModel(model)

        self.app.message.emit(f'writing model [{self.modelName}]', 0)

        modelPath = f'{self.app.mwGlob["modelDir"]}/{self.modelName}.model'
        with open(modelPath, 'w') as outfile:
            json.dump(saveModel,
                      outfile,
                      sort_keys=True,
                      indent=4)
        return True

    def collectModelData(self):
        """
        collectModelData writes all model point from the queue to a data structure for
        later use.

        :return: model
        """

        model = list()
        while not self.modelQueue.empty():
            mPoint = self.modelQueue.get()
            model.append(mPoint)

        return model

    @staticmethod
    def generateBuildDataFromJSON(loadModel=None):
        """
        generateBuildData takes the model data and generates from it a data structure
        needed for programming the model into the mount computer.

        :param loadModel:
        :return: build
        """

        build = list()

        for mPoint in loadModel:
            # prepare data
            mCoord = skyfield.api.Star(ra_hours=mPoint['raMJNow'],
                                       dec_degrees=mPoint['decMJNow'])
            sCoord = skyfield.api.Star(ra_hours=mPoint['raSJNow'],
                                       dec_degrees=mPoint['decSJNow'])
            sidereal = mPoint['sidereal']
            pierside = mPoint['pierside']

            # combine data into structure
            programmingPoint = APoint(mCoord=mCoord,
                                      sCoord=sCoord,
                                      sidereal=sidereal,
                                      pierside=pierside,
                                      )
            build.append(programmingPoint)

        return build

    @staticmethod
    def generateBuildData(model=None):
        """
        generateBuildData takes the model data and generates from it a data structure
        needed for programming the model into the mount computer.

        :param model:
        :return: build
        """

        build = list()

        for mPoint in model:
            # prepare data
            mCoord = skyfield.api.Star(ra=mPoint.mData.raMJNow,
                                       dec=mPoint.mData.decMJNow)
            sCoord = skyfield.api.Star(ra=mPoint.mData.raSJNow,
                                       dec=mPoint.mData.decSJNow)
            sidereal = mPoint.mData.sidereal
            pierside = mPoint.mData.pierside

            # combine data into structure
            programmingPoint = APoint(mCoord=mCoord,
                                      sCoord=sCoord,
                                      sidereal=sidereal,
                                      pierside=pierside,
                                      )
            build.append(programmingPoint)

        return build

    def modelFinished(self):
        """
        modelFinished is called when tha last point was solved. in addition the saving
        of the model and the programming is done here.

        is the flag delete images after modeling is set, the entire directory will be
        deleted

        :return: true for test purpose
        """

        model = self.collectModelData()
        build = self.generateBuildData(model=model)

        # stopping other activities
        self.defaultSignals()
        self.clearQueues()
        self.defaultGUI()

        # finally do it
        self.app.message.emit('Programming model to mount', 0)
        suc = self.app.mount.model.programAlign(build)

        if suc:
            self.app.message.emit('Model programmed with success', 0)
            self.refreshModel()
            model = self.retrofitModel(model=model)
            self.saveModel(model=model)
        else:
            self.app.message.emit('Model programming error', 2)

        # cleaning up the disk space
        if not self.ui.checkKeepImages.isChecked():
            self.app.message.emit('Deleting model images', 0)
            shutil.rmtree(self.imageDir, ignore_errors=True)

        self.app.message.emit('Modeling finished', 1)
        self.playAudioModelFinished()

        return True

    def modelCore(self, points=None):
        """
        modelCore is the main method for preparing a model run. in addition it checks
        necessary components and prepares all the parameters.
        the modeling queue will be filled with point and the queue is started.

        :param points:
        :return: true for test purpose
        """

        app = self.app.mainW.ui.astrometryDevice.currentText()
        if app.startswith('No device'):
            return False

        # collection locations for files
        nameTime = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        self.modelName = f'm-{self.lastModelType}-{nameTime}'
        self.imageDir = f'{self.app.mwGlob["imageDir"]}/{self.modelName}'
        os.mkdir(self.imageDir)
        if not os.path.isdir(self.imageDir):
            return False

        self.clearQueues()
        self.app.message.emit(f'Modeling {self.modelName} started', 1)

        # collection all necessary information
        expTime = self.app.mainW.ui.expTime.value()
        binning = self.app.mainW.ui.binning.value()
        subFrame = self.app.mainW.ui.subFrame.value()
        fastReadout = self.app.mainW.ui.checkFastDownload.isChecked()
        solveTimeout = self.ui.solveTimeout.value()
        searchRadius = self.ui.searchRadius.value()

        # setting overall parameters
        settleMount = self.app.mainW.ui.settleTimeMount.value()
        settleDome = self.app.mainW.ui.settleTimeDome.value()
        self.app.mount.settlingTime = settleMount
        self.app.dome.settlingTime = settleDome

        self.prepareGUI()
        self.prepareSignals()
        self.startModeling = time.time()

        # queuing modeling points
        number = len(points)
        for count, point in enumerate(points):
            # define the path to the image file
            path = f'{self.imageDir}/image-{count:03d}.fits'

            iParam = IParam(expTime=expTime,
                            binning=binning,
                            subFrame=subFrame,
                            fastReadout=fastReadout,
                            )
            mParam = MParam(number=number,
                            count=count,
                            path=path,
                            name=self.modelName,
                            astrometry=app,
                            timeout=solveTimeout,
                            radius=searchRadius,
                            )

            # transfer to working in a queue with necessary data
            self.slewQueue.put(MPoint(iParam=iParam,
                                      mParam=mParam,
                                      point=Point(altitude=point[0],
                                                  azimuth=point[1]),
                                      mData=None,
                                      rData=None,
                                      )
                               )
        # kick off modeling
        self.modelSlew()

        return True

    def modelFull(self):
        """
        modelFull sets the adequate gui elements, selects the model points and calls the
        core modeling method

        :return: true for test purpose
        """

        # checking constraints for modeling
        points = self.app.data.buildP
        number = len(points)
        if not 2 < number < 100:
            return False

        self.changeStyleDynamic(self.ui.runFullModel, 'running', True)
        self.changeStyleDynamic(self.ui.cancelFullModel, 'cancel', True)
        self.ui.cancelFullModel.setEnabled(True)
        self.ui.runAlignModel.setEnabled(False)
        self.ui.plateSolveSync.setEnabled(False)
        self.ui.runFlexure.setEnabled(False)
        self.ui.runHysteresis.setEnabled(False)
        self.ui.cancelFullModel.setEnabled(True)

        suc = self.modelCore(points=points)
        if not suc:
            self.defaultGUI()

        return True

    def modelAlign(self):
        """
        modelAlign sets the adequate gui elements, selects the model points and calls the
        core modeling method

        :return: true for test purpose
        """

        # checking constraints for modeling
        points = self.app.data.buildP
        number = len(points)
        if not 2 < number < 100:
            return False

        self.changeStyleDynamic(self.ui.runAlignModel, 'running', True)
        self.changeStyleDynamic(self.ui.cancelAlignModel, 'cancel', True)
        self.ui.cancelAlignModel.setEnabled(True)
        self.ui.runFullModel.setEnabled(False)
        self.ui.plateSolveSync.setEnabled(False)
        self.ui.runFlexure.setEnabled(False)
        self.ui.runHysteresis.setEnabled(False)

        suc = self.modelCore(points=points)
        if not suc:
            self.defaultGUI()

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

        self.app.message.emit('Programing stored models', 1)
        modelJSON = list()
        for file in loadFilePath:
            self.app.message.emit(f'Using model [{file}]', 0)
            with open(file, 'r') as infile:
                model = json.load(infile)
                modelJSON += model

        if len(modelJSON) > 99:
            self.app.message.emit('Combined models have more than 99 points', 2)
            return False

        build = self.generateBuildDataFromJSON(modelJSON)

        # finally do it
        self.app.message.emit('Programming model to mount', 0)
        suc = self.app.mount.model.programAlign(build)

        if suc:
            self.app.message.emit('Model programmed with success', 0)
            self.refreshModel()
        else:
            self.app.message.emit('Model programming error', 2)

        return suc
