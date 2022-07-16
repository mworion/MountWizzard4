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

    def checkAnalysisConditions(self):
        """
        :return:
        """
        if self.ui.plateSolveDevice.currentText().startswith('No device'):
            self.msg.emit(2, 'Analysis', 'Run error',
                          'No plate solver selected')
            return False

        sucApp, sucIndex = self.app.plateSolve.checkAvailability()
        if not (sucApp and sucIndex):
            self.msg.emit(2, 'Analysis', 'Run error',
                          'No valid configuration for plate solver')
            return False

        return True

    def runFlexure(self):
        """
        :return:
        """
        if not self.checkAnalysisConditions():
            self.app.operationRunning.emit(0)
            return False

        self.app.operationRunning.emit(4)
        self.analysisRunning = True

        prefix = 'a'
        postfix = self.lastGenerator

        self.analysisName, imgDir = self.setupFilenamesAndDirectories(
            prefix=prefix, postfix=postfix)

        data = self.app.data.buildP
        analysisPoints = self.setupRunPoints(data=data, imgDir=imgDir,
                                             name=self.analysisName)

        self.msg.emit(1, 'Analysis', 'Run', f'Starting [{self.analysisName}]')
        runType = 'Analysis'
        keepImages = self.ui.keepAnalysisImages.isChecked()
        self.timeStartAnalysis = time.time()
        self.cycleThroughPoints(modelPoints=analysisPoints,
                                retryCounter=0,
                                runType=runType,
                                processData=self.processModelData,
                                progress=self.updateModelProgress,
                                imgDir=imgDir,
                                keepImages=keepImages)
        self.app.operationRunning.emit(0)
        return True
