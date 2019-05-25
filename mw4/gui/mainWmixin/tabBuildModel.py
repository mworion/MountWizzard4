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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import queue
import os
import time
from datetime import datetime, timedelta
# external packages
import PyQt5.QtWidgets
import PyQt5.uic
# local import
from mw4.definitions import Point, MPoint, IParam, MParam, Result


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
        self.ui.numberGridPointsRow.setValue(config.get('numberGridPointsRow', 5))
        self.ui.numberGridPointsCol.setValue(config.get('numberGridPointsCol', 6))
        self.ui.altitudeMin.setValue(config.get('altitudeMin', 30))
        self.ui.altitudeMax.setValue(config.get('altitudeMax', 75))
        self.ui.numberDSOPoints.setValue(config.get('numberDSOPoints', 20))
        self.ui.durationDSO.setValue(config.get('durationDSO', 5))
        self.ui.timeShiftDSO.setValue(config.get('timeShiftDSO', 0))

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

        :return:    True if success for test
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

        numberPoints = self.ui.numberSpiralPoints.value()

        suc = self.app.data.generateGoldenSpiral(numberPoints=numberPoints,
                                                 )

        if not suc:
            self.app.message.emit('DSO Path cannot be generated', 2)
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
        suc = self.app.data.loadBuildP(fileName=fileName)
        if not suc:
            text = 'Build points file [{0}] could not be loaded'.format(fileName)
            self.app.message.emit(text, 2)
            return False
        self.autoDeletePoints()
        return True

    def modelSolveDone(self, result):
        """

        :param result:
        :return:
        """

        if self.resultQueue.empty():
            return False

        model = self.resultQueue.get()

        if not result[0]:
            self.app.message.emit('Solving error', 2)
            return False

        r = result[1]
        if not isinstance(r, tuple):
            return False

        text = f'Solved -> Ra: {r.raJ2000:4.1f}   Dec: {r.decJ2000:4.1f}'
        text = text + f'   Angle: {r.angle:4.1f}   Scale: {r.scale:3.1f}'
        self.app.message.emit(text, 0)

        model = MPoint(mParam=model.mParam,
                       iParam=model.iParam,
                       mPoint=model.mPoint,
                       mData=None,
                       )
        self.modelQueue.put(model)

        # here we update the estimation for modeling
        modelingDone = (model.mParam.number == model.mParam.count + 1)
        modelPercent = (model.mParam.count + 1) / model.mParam.number
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

        if modelingDone:
            self.modelFinished()

        return True

    def modelSolve(self):
        """

        :return:
        """

        if self.solveQueue.empty():
            return False

        model = self.solveQueue.get()
        self.app.astrometry.solveThreading(app=model.mParam.astrometry,
                                           fitsPath=model.mParam.path,
                                           timeout=10,
                                           updateFits=False,
                                           )

        text = f'Solving -> {os.path.basename(model.mParam.path)}'
        self.app.message.emit(text, 0)
        self.ui.mSolve.setText(f'{model.mParam.count + 1:2d}')
        self.resultQueue.put(model)
        return True

    def modelImage(self):
        """

        :return:
        """

        if self.imageQueue.empty():
            return False

        model = self.imageQueue.get()
        self.collector.resetSignals()
        self.app.imaging.expose(imagePath=model.mParam.path,
                                expTime=model.iParam.expTime,
                                binning=model.iParam.binning,
                                subFrame=model.iParam.subFrame,
                                fast=model.iParam.fast,
                                )

        text = f'Imaging: {os.path.basename(model.mParam.path)}'
        self.app.message.emit(text, 0)
        self.ui.mImage.setText(f'{model.mParam.count + 1 :2d}')
        self.solveQueue.put(model)

        return True

    def modelSlew(self):
        """

        :return:
        """

        if self.slewQueue.empty():
            return False

        model = self.slewQueue.get()
        self.app.dome.slewToAltAz(azimuth=model.mPoint.azimuth)
        self.app.mount.obsSite.slewAltAz(alt_degrees=model.mPoint.altitude,
                                         az_degrees=model.mPoint.azimuth,
                                         )

        text = f'Slewing -> Alt: {model.mPoint.altitude:2.0f}'
        text = text + f'   Az: {model.mPoint.azimuth:3.0f}'
        self.app.message.emit(text, 0)
        self.ui.mPoints.setText(f'{model.mParam.number:2d}')
        self.ui.mSlew.setText(f'{model.mParam.count + 1:2d}')
        self.imageQueue.put(model)

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

        return True

    def prepareGUI(self):
        """

        :return: true for test purpose
        """

        self.changeStyleDynamic(self.ui.runFullModel, 'running', True)
        self.ui.cancelFullModel.setEnabled(True)
        self.ui.combineModel.setEnabled(False)
        self.ui.batchModel.setEnabled(False)
        self.ui.runInitialModel.setEnabled(False)
        self.ui.plateSolveSync.setEnabled(False)
        self.ui.runFlexure.setEnabled(False)
        self.ui.runHysteresis.setEnabled(False)

        return True

    def defaultGUI(self):
        """

        :return: true for test purpose
        """

        self.changeStyleDynamic(self.ui.runFullModel, 'running', False)
        self.ui.cancelFullModel.setEnabled(False)
        self.ui.combineModel.setEnabled(True)
        self.ui.batchModel.setEnabled(True)
        self.ui.runInitialModel.setEnabled(True)
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

        :return: true for test purpose
        """

        self.collector.addWaitableSignal(self.app.dome.signals.slewFinished)
        self.collector.addWaitableSignal(self.app.mount.signals.slewFinished)
        self.collector.ready.connect(self.modelImage)

        self.app.imaging.signals.saved.connect(self.modelSolve)
        self.app.imaging.signals.integrated.connect(self.modelSlew)
        self.app.astrometry.signals.done.connect(self.modelSolveDone)

        return True

    def defaultSignals(self):
        """

        :return: true for test purpose
        """

        self.app.imaging.signals.saved.disconnect(self.modelSolve)
        self.app.imaging.signals.integrated.disconnect(self.modelSlew)
        self.app.astrometry.signals.done.disconnect(self.modelSolveDone)
        self.collector.clear()
        self.collector.ready.disconnect(self.modelImage)

        return True

    def cancelFull(self):
        """

        :return: true for test purpose
        """

        self.app.message.emit('Modeling cancelled', 2)
        self.app.imaging.abort()
        self.defaultSignals()
        self.clearQueues()
        self.defaultGUI()

        return True

    def modelFinished(self):
        """

        :return: true for test purpose
        """

        self.defaultSignals()
        self.defaultGUI()
        self.app.message.emit('Modeling finished', 1)
        while not self.modelQueue.empty():
            self.modelQueue.get()

        return True

    def modelFull(self):
        """

        :return: true for test purpose
        """

        # checking constraints for modeling
        points = self.app.data.buildP
        number = len(points)
        if number < 3:
            return False

        # collection locations for files
        dirTime = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        directory = f'{self.app.mwGlob["imageDir"]}/{dirTime}'
        os.mkdir(directory)
        if not os.path.isdir(directory):
            return False

        self.clearQueues()
        self.app.message.emit('Modeling started', 1)

        # collection all necessary information
        expTime = self.app.mainW.ui.expTime.value()
        binning = self.app.mainW.ui.binning.value()
        subFrame = self.app.mainW.ui.subFrame.value()
        fast = self.app.mainW.ui.checkFastDownload.isChecked()
        app = self.app.mainW.ui.astrometryDevice.currentText()

        # setting overall parameters
        settleMount = self.app.mainW.ui.settleTimeMount.value()
        settleDome = self.app.mainW.ui.settleTimeDome.value()
        self.app.mount.settlingTime = settleMount
        self.app.dome.settlingTime = settleDome

        self.prepareGUI()
        self.prepareSignals()
        self.startModeling = time.time()

        # queuing modeling points
        for count, point in enumerate(points):
            # define the path to the image file
            path = f'{directory}/image-{count:03d}.fits'

            iParam = IParam(expTime=expTime,
                            binning=binning,
                            subFrame=subFrame,
                            fast=fast,
                            )
            mParam = MParam(number=number,
                            count=count,
                            path=path,
                            astrometry=app,
                            )

            # transfer to working in a queue with necessary data
            self.slewQueue.put(MPoint(iParam=iParam,
                                      mParam=mParam,
                                      mPoint=Point(altitude=point[0],
                                                   azimuth=point[1]),
                                      mData=None,
                                      )
                               )
        # kick off modeling
        self.modelSlew()

        return True
