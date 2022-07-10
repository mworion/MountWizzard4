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

# external packages

# local import
from gui.utilities.toolsQtWidget import sleepAndEvents


class Analysis(object):
    """
    """

    def __init__(self):
        self.ui.hysteresisProgress.setValue(0)
        self.ui.flexureProgress.setValue(0)
        self.app.operationRunning.emit(0)
        self.imageDirAnalyse = ''
        self.analyseName = ''
        self.analysisRunning = False
        self.ui.runFlexure.clicked.connect(self.runFlexure)
        self.ui.runHysteresis.clicked.connect(self.runHysteresis)
        self.ui.cancelAnalysis.clicked.connect(self.cancelAnalysis)
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

    def runFlexure(self):
        """
        :return:
        """
        self.app.operationRunning.emit(4)
        self.analysisRunning = True
        while self.analysisRunning:
            sleepAndEvents(100)
        self.app.operationRunning.emit(0)
        return True

    def runHysteresis(self):
        """
        :return:
        """
        self.app.operationRunning.emit(5)
        self.analysisRunning = True
        while self.analysisRunning:
            sleepAndEvents(100)
        self.app.operationRunning.emit(0)
        return True

    def cancelAnalysis(self):
        """
        :return:
        """
        self.analysisRunning = False
        return True
