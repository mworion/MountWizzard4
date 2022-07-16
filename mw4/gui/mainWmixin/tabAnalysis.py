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
import time
import os

# external packages

# local import


class Analysis(object):
    """
    """

    def __init__(self):
        self.ui.hysteresisProgress.setValue(0)
        self.ui.flexureProgress.setValue(0)
        self.app.operationRunning.emit(0)
        self.imageDirAnalysis = ''
        self.analysisName = ''
        self.analysisRunning = False
        self.timeStartAnalysis = None
        self.ui.runFlexure.clicked.connect(self.runFlexure)
        self.ui.runHysteresis.clicked.connect(self.runHysteresis)
        self.ui.cancelAnalysis.clicked.connect(self.cancel)
        self.app.operationRunning.connect(self.setAnalysisOperationMode)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.flexureAlt.setValue(config.get('flexureAlt', 45))
        self.ui.flexureAz.setValue(config.get('flexureAz', 45))
        self.ui.flexureDuration.setValue(config.get('flexureDuration', 60))
        self.ui.flexureTime.setValue(config.get('flexureTime', 30))
        self.ui.hysteresisMinAlt.setValue(config.get('hysteresisMinAlt', 45))
        self.ui.hysteresisRuns.setValue(config.get('hysteresisRuns', 1))
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['flexureAlt'] = self.ui.flexureAlt.value()
        config['flexureAz'] = self.ui.flexureAz.value()
        config['flexureDuration'] = self.ui.flexureDuration.value()
        config['flexureTime'] = self.ui.flexureTime.value()
        config['hysteresisMinAlt'] = self.ui.hysteresisMinAlt.value()
        config['hysteresisRuns'] = self.ui.hysteresisRuns.value()
        return True

    def setAnalysisOperationMode(self, status):
        """
        :param status:
        :return:
        """
        if status == 4:
            self.ui.hysteresisGroup.setEnabled(False)
            self.ui.runFlexure.setEnabled(False)
            self.ui.cancelAnalysis.setEnabled(True)
            self.ui.runFlexure.setEnabled(False)
        elif status == 5:
            self.ui.runHysteresis.setEnabled(False)
            self.ui.cancelAnalysis.setEnabled(True)
            self.ui.flexureGroup.setEnabled(False)
        elif status == 0:
            self.ui.runFlexure.setEnabled(True)
            self.ui.runHysteresis.setEnabled(True)
            self.ui.hysteresisGroup.setEnabled(True)
            self.ui.flexureGroup.setEnabled(True)
            self.ui.cancelAnalysis.setEnabled(False)
        else:
            self.ui.hysteresisGroup.setEnabled(False)
            self.ui.flexureGroup.setEnabled(False)
            self.ui.cancelAnalysis.setEnabled(False)
        return True

    def setupModelFilenamesAndDirectories(self):
        """
        :return:
        """
        nameTime = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        self.analysisName = f'a-{nameTime}-{self.lastGenerator}'
        self.imageDir = f'{self.app.mwGlob["imageDir"]}/{self.analysisName}'

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

    def runFlexure(self):
        """
        :return:
        """
        self.app.operationRunning.emit(4)
        self.analysisRunning = True

        self.setupModelFilenamesAndDirectories()
        analysisPoints = self.setupAnalysisPointsAndContextData()
        self.setupAnalysisRunContextAndGuiStatus()

        self.msg.emit(1, 'Analysis', 'Run', f'Starting [{self.analysisName}]')
        runType = 'Analysis'
        keepImages = self.ui.keepAnalysisImages.isChecked()
        self.timeStartAnalysis = time.time()
        self.cycleThroughPoints(modelPoints=analysisPoints,
                                retryCounter=0,
                                runType=runType,
                                processData=self.processModelData,
                                progress=self.updateModelProgress,
                                keepImages=keepImages)
        self.app.operationRunning.emit(0)
        return True
