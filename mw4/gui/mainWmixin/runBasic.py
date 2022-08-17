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
import shutil
import os

# external packages
from mountcontrol.convert import convertToHMS, convertToDMS

# local import
from base.transform import JNowToJ2000, J2000ToJNow
from gui.utilities.toolsQtWidget import QMultiWait, sleepAndEvents


class BasicRun:
    """
    """

    def __init__(self):
        self.slewQueue = queue.Queue()
        self.imageQueue = queue.Queue()
        self.solveQueue = queue.Queue()
        self.resultQueue = queue.Queue()
        self.modelQueue = queue.Queue()
        self.retryQueue = queue.Queue()
        self.collector = QMultiWait()
        self.runProgressCB = None
        self.processDataCB = None
        self.keepImages = None
        self.performanceTimingSignal = None
        self.retryCounter = 0
        self.runType = ''
        self.imageDir = ''

        self.ui.cancelModel.clicked.connect(self.cancelRun)
        self.ui.endModel.clicked.connect(self.processDataAndFinishRun)

    def runSolveDone(self, result):
        """
        runSolveDone is called when a point is solved by plateSolve. if called
        it takes the model point out of the queue and adds the solving data for
        later model build. as the solving takes place in J2000 epoch, but we need
        fpr die model build JNow epoch, the transformation is done as well.

        in addition, as it is the last step before a model point could be used,
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
            self.msg.emit(2, self.runType, 'Build error', 'Out of sync exception')
            self.cancelRun()
            return False

        self.log.debug('Processing plate solving result')
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

        if isSuccess:
            raJNowS, decJNowS = J2000ToJNow(mPoint['raJ2000S'],
                                            mPoint['decJ2000S'],
                                            mPoint['julianDate'])
            mPoint['raJNowS'] = raJNowS
            mPoint['decJNowS'] = decJNowS
            t = f'Queued to model [{mPoint["countSequence"]:03d}]: [{mPoint}]'
            self.log.debug(t)
            self.modelQueue.put(mPoint)
            self.app.data.setStatusBuildP(pointNumber - 1, 0)

            text = f'RA: {convertToHMS(mPoint["raJ2000S"])} '
            text += f'({result["raJ2000S"].hours:4.3f}), '
            self.msg.emit(0, 'Image', 'Solving', text)
            text = f'DEC: {convertToDMS(mPoint["decJ2000S"])} '
            text += f'({mPoint["decJ2000S"].degrees:4.3f}), '
            self.msg.emit(0, '', '', text)
            text = f'Angle: {mPoint["angleS"]:3.0f}, '
            self.msg.emit(0, '', '', text)
            text = f'Scale: {mPoint["scaleS"]:4.3f}, '
            self.msg.emit(0, '', '', text)
            text = f'Error: {mPoint["errorRMS_S"]:4.1f}'
            self.msg.emit(0, '', '', text)

        else:
            text = f'Solving failed for image-{count:03d}'
            self.msg.emit(2, self.runType, 'Solving error', text)
            self.retryQueue.put(mPoint)
            self.app.data.setStatusBuildP(pointNumber - 1, 2)

        self.app.updatePointMarker.emit()
        self.runProgressCB(mPoint)
        self.log.debug(f'Processing {[count]} from {[lenSequence]}')
        if lenSequence == count:
            self.cycleThroughPointsFinished()

        return True

    def runSolve(self):
        """
        runSolve is the method called from the signal image saved and starts
        the solving process for this image. therefore, it takes the model point
        from the queue and uses the parameters stored. if the queue is empty (
        which should be to the case), it just returns. after starting the solving
        process in a threaded way (should run in parallel to gui) it puts the
        model point to the next queue, the result queue. in addition, if the image
        window is present, it sends a signal for displaying the actual captured
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
            self.msg.emit(2, self.runType, 'Build error', 'Out of sync exception')
            self.cancelRun()
            return False

        self.log.info('Solving started')
        mPoint = self.solveQueue.get()
        self.app.showImage.emit(mPoint["imagePath"])
        self.resultQueue.put(mPoint)
        self.log.debug(f'Queued to result [{mPoint["countSequence"]:03d}]: [{mPoint}]')
        self.app.plateSolve.solveThreading(fitsPath=mPoint['imagePath'],
                                           updateFits=False)
        text = f'Solving  image-{mPoint["countSequence"]:03d}:'
        self.msg.emit(0, self.runType, 'Solving', text)
        return True

    def runImage(self):
        """
        runImage is the method called from the signal mount and dome slewed
        finish and starts the imaging for the model point. therefore, it takes the
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

        if noImagesLeft and slewsLeft:
            t = f'Slews left: [{self.slewQueue.qsize()}] '
            self.log.error(f'Empty image queue: {t}')
            self.msg.emit(2, self.runType, 'Build error', 'Out of sync exception')
            self.cancelRun()
            return False

        self.log.info('Imaging started')
        mPoint = self.imageQueue.get()
        self.collector.resetSignals()
        waitTime = 2 * mPoint.get('waitTime', 0)
        self.log.info(f'Waiting time is {mPoint.get("waitTime", 0)}')

        while self.ui.pauseModel.property('pause') or waitTime > 0:
            color = '' if waitTime % 2 else 'yellow'
            self.changeStyleDynamic(self.ui.pauseModel, 'color', color)
            sleepAndEvents(500)
            waitTime -= 1

        mPoint['raJNowM'] = self.app.mount.obsSite.raJNow
        mPoint['decJNowM'] = self.app.mount.obsSite.decJNow
        mPoint['angularPosRA'] = self.app.mount.obsSite.angularPosRA
        mPoint['angularPosDEC'] = self.app.mount.obsSite.angularPosDEC
        mPoint['siderealTime'] = self.app.mount.obsSite.timeSidereal
        mPoint['julianDate'] = self.app.mount.obsSite.timeJD
        mPoint['pierside'] = self.app.mount.obsSite.pierside
        mPoint['raJ2000M'], mPoint['decJ2000M'] = JNowToJ2000(mPoint['raJNowM'],
                                                              mPoint['decJNowM'],
                                                              mPoint['julianDate'])

        self.app.camera.expose(imagePath=mPoint['imagePath'],
                               expTime=mPoint['exposureTime'],
                               binning=mPoint['binning'],
                               subFrame=mPoint['subFrame'],
                               fastReadout=mPoint['fastReadout'],
                               focalLength=mPoint['focalLength'])

        self.solveQueue.put(mPoint)
        self.log.debug(f'Queued to solve [{mPoint["countSequence"]:03d}]: [{mPoint}]')

        text = f'Exposing image-{mPoint["countSequence"]:03d}'
        self.msg.emit(0, self.runType, 'Imaging', text)
        return True

    def runSlew(self):
        """
        runSlew is the method called from the model core method and is the
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

        self.log.info('Slew started')
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

            text = f'{geoStat}'
            text += ', az: {azimuthT:3.1f} delta: {delta:3.1f}'
            self.msg.emit(0, self.runType, 'Slewing dome', text)

        self.app.mount.obsSite.startSlewing()
        self.imageQueue.put(mPoint)
        self.log.debug(f'Queued to image [{mPoint["countSequence"]:03d}]: [{mPoint}]')

        text = f'Point: {mPoint["countSequence"]:03d}, '
        text += f'altitude: {mPoint["altitude"]:3.0f}, '
        text += f'azimuth: {mPoint["azimuth"]:3.0f}'
        self.msg.emit(0, self.runType, 'Slewing mount', text)
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

    def setupSignalsForRun(self):
        """
        setupSignalsForRun establishes the signals chain. as we have
        multiple actions running at the same time, the synchronisation by the
        right link of the signals.

        first we link the two slew finished signals to runImage. that means
        as soon as both slew finished signals are received, the imaging will be
        started when download of an image starts, we could slew to another point
        when image is saved, we could start with solving

        :return: true for test purpose
        """
        self.collector.addWaitableSignal(self.app.mount.signals.slewFinished)
        self.collector.addWaitableSignal(self.app.camera.signals.exposeReady)

        hasDome = self.deviceStat.get('dome', False)
        hasAzimuth = 'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION' in self.app.dome.data

        if hasDome and hasAzimuth:
            self.collector.addWaitableSignal(self.app.dome.signals.slewFinished)
        elif hasDome and not hasAzimuth:
            self.msg.emit(2, self.runType, 'Run',
                          'Dome without azimuth value used')

        t = f'Modeling config dome:[{hasDome}], hasAzimuth:[{hasAzimuth}]'
        self.log.debug(t)

        self.collector.ready.connect(self.runImage)
        self.app.camera.signals.saved.connect(self.runSolve)
        self.app.plateSolve.signals.done.connect(self.runSolveDone)
        self.app.camera.signals.exposeReady.emit()

        if self.ui.progressiveTiming.isChecked():
            self.performanceTimingSignal = self.app.camera.signals.exposed
        elif self.ui.normalTiming.isChecked():
            self.performanceTimingSignal = self.app.camera.signals.downloaded
        else:
            self.performanceTimingSignal = self.app.camera.signals.saved

        self.performanceTimingSignal.connect(self.runSlew)
        return True

    def restoreModelDefaultContextAndGuiStatus(self):
        """
        restoreModelDefaultContextAndGuiStatus will reset all gui elements to
        the idle or default state and new actions could be started again

        :return: true for test purpose
        """
        self.changeStyleDynamic(self.ui.runModel, 'running', False)
        self.changeStyleDynamic(self.ui.pauseModel, 'pause', False)
        self.ui.runModel.setEnabled(True)
        self.ui.cancelModel.setEnabled(False)
        self.ui.endModel.setEnabled(False)
        self.ui.pauseModel.setEnabled(False)
        self.ui.timeEstimated.setText('00:00:00')
        self.ui.timeElapsed.setText('00:00:00')
        self.ui.timeFinished.setText('00:00:00')
        self.ui.numberPoints.setText('-')
        self.ui.modelProgress.setValue(0)
        return True

    def cancelRun(self):
        """
        cancelRun aborts imaging and stops all modeling queues and actions
        and restores them to default values.

        :return: true for test purpose
        """
        self.restoreModelDefaultContextAndGuiStatus()
        self.app.camera.abort()
        self.app.plateSolve.abort()
        self.restoreSignalsRunDefault()
        self.clearQueues()
        self.app.operationRunning.emit(0)
        self.msg.emit(2, self.runType, 'Run', 'Cancelled')
        return True

    def generateSaveData(self):
        """
        generateSaveData builds from the model file a format which could be
        serialized in json. this format will be used for storing model on file.

        :return: save model format
        """
        modelDataForSave = list()
        for mPoint in self.model:
            sPoint = dict()
            sPoint.update(mPoint)
            sPoint['raJNowM'] = sPoint['raJNowM'].hours
            sPoint['decJNowM'] = sPoint['decJNowM'].degrees
            sPoint['raJ2000M'] = sPoint['raJ2000M'].hours
            sPoint['decJ2000M'] = sPoint['decJ2000M'].degrees
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

    def restoreSignalsRunDefault(self):
        """
        restoreSignalsRunDefault clears the signal queue and removes the
        signal connections

        :return: true for test purpose
        """
        self.performanceTimingSignal.disconnect(self.runSlew)
        self.app.camera.signals.saved.disconnect(self.runSolve)
        self.app.plateSolve.signals.done.disconnect(self.runSolveDone)
        self.collector.ready.disconnect(self.runImage)
        self.collector.clear()
        return True

    def collectingRunOutput(self):
        """
        :return:
        """
        runResult = list()
        while not self.modelQueue.empty():
            point = self.modelQueue.get()
            runResult.append(point)
        self.log.info(f'Collected model points: [{len(runResult)}]')
        return runResult

    def processDataAndFinishRun(self):
        """
        :return:
        """
        resultData = self.collectingRunOutput()
        self.restoreSignalsRunDefault()
        self.restoreModelDefaultContextAndGuiStatus()
        self.clearQueues()

        if self.ui.parkMountAfterModel.isChecked():
            self.msg.emit(0, self.runType, 'Run', 'Parking mount after run')
            suc = self.app.mount.obsSite.park()
            if not suc:
                self.msg.emit(2, self.runType, 'Run error', 'Cannot park mount')
            else:
                self.msg.emit(0, self.runType, 'Run', 'Mount parked')

        if not self.keepImages:
            self.msg.emit(0, self.runType, 'Run', 'Deleting images')
            shutil.rmtree(self.imageDir, ignore_errors=True)

        self.processDataCB(resultData)
        return True

    def cycleThroughPointsFinished(self):
        """
        cycleThroughPointsFinished is called when tha last point was
        processed. it empties the solution queue restores the default gui elements
        and signals. after that it programs the resulting model to the mount and
        saves it to disk.

        is the flag delete images after modeling is set, the entire directory
        will be deleted

        :return: true for test purpose
        """
        if self.retryQueue.qsize() == 0:
            self.processDataAndFinishRun()
            return True
        if self.retryCounter == 0:
            self.processDataAndFinishRun()
            return True

        self.msg.emit(1, self.runType, 'Run', 'Starting retry failed points')
        maxRetries = self.ui.numberBuildRetries.value()
        retryNumber = maxRetries - self.retryCounter + 1

        self.msg.emit(1, '', '', f'Retry run number: {retryNumber}')
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

        self.retryCounter -= 1
        self.runSlew()
        return True

    def cycleThroughPoints(self, modelPoints=None, retryCounter=0, runType=None,
                           processData=None, progress=None,
                           imgDir=None, keepImages=False):
        """
        cycleThroughPoints is the main method for preparing a model
        run. in addition it checks necessary components and prepares all the
        parameters. the modeling queue will be filled with point and the queue is
        started. the overall modeling process consists of a set of queues which
        are handled by events running in the gui event queue.

        :param modelPoints:
        :param retryCounter:
        :param runType:
        :param processData:
        :param progress:
        :param imgDir:
        :param keepImages:
        :return: true for test purpose
        """
        self.runProgressCB = progress
        self.processDataCB = processData
        self.retryCounter = retryCounter
        self.keepImages = keepImages
        self.imageDir = imgDir
        self.runType = runType
        self.clearQueues()
        self.setupSignalsForRun()
        for point in modelPoints:
            self.slewQueue.put(point)

        self.app.dome.avoidFirstOvershoot()
        self.runSlew()
        return True

    def setupFilenamesAndDirectories(self, prefix='', postfix=''):
        """
        :return:
        """
        nameTime = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        name = f'{prefix}-{nameTime}-{postfix}'
        imageDir = f'{self.app.mwGlob["imageDir"]}/{name}'

        if not os.path.isdir(imageDir):
            os.mkdir(imageDir)

        return name, imageDir

    def setupRunPoints(self, data=[], imgDir='', name='', waitTime=0):
        """
        :param data:
        :param imgDir:
        :param name:
        :param waitTime:
        :return:
        """
        plateSolveApp = self.ui.plateSolveDevice.currentText()
        exposureTime = self.ui.expTime.value()
        binning = int(self.ui.binning.value())
        subFrame = self.ui.subFrame.value()
        fastReadout = self.ui.fastDownload.isChecked()
        focalLength = self.ui.focalLength.value()
        lenSequence = len(data)
        framework = self.app.plateSolve.framework
        solveTimeout = self.app.plateSolve.run[framework].timeout
        searchRadius = self.app.plateSolve.run[framework].searchRadius
        modelPoints = list()
        for index, point in enumerate(data):
            m = dict()
            imagePath = f'{imgDir}/image-{index + 1:03d}.fits'
            m['imagePath'] = imagePath
            m['exposureTime'] = exposureTime
            m['binning'] = binning
            m['subFrame'] = subFrame
            m['fastReadout'] = fastReadout
            m['lenSequence'] = lenSequence
            m['countSequence'] = index + 1
            m['pointNumber'] = index + 1
            m['name'] = name
            m['imagePath'] = imagePath
            m['plateSolveApp'] = plateSolveApp
            m['solveTimeout'] = solveTimeout
            m['searchRadius'] = searchRadius
            m['focalLength'] = focalLength
            m['altitude'] = point[0]
            m['azimuth'] = point[1]
            m['waitTime'] = waitTime
            modelPoints.append(m)
        return modelPoints
