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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import re

# external packages
from PySide6.QtCore import Qt, Signal
import requests

# local import
from gui.utilities import toolsQtWidget
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.tpool import Worker
from gui.widgets.uploadPopup_ui import Ui_UploadPopup


class UploadPopup(toolsQtWidget.MWidget):
    """
    """
    __all__ = ['UploadPopup']

    PROGRESS_DONE = 100
    CYCLES_WAIT = 20
    signalProgress = Signal(object)
    signalStatus = Signal(object)
    signalProgressBarColor = Signal(object)

    def __init__(self, parentWidget, url, dataTypes, dataFilePath):
        super().__init__()
        self.ui = Ui_UploadPopup()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.returnValues = {'success': False, 'successMount': False}
        self.parentWidget = parentWidget
        self.url = url
        self.dataTypes = dataTypes
        self.dataFilePath = dataFilePath
        self.worker = None
        self.workerStatus = None
        self.pollStatusRunState = False
        self.timeoutCounter = 0
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)
        self.setWindowTitle('Uploading to mount')
        self.threadPool = parentWidget.threadPool
        self.signalStatus.connect(self.setStatusTextToValue)
        self.signalProgress.connect(self.setProgressBarToValue)
        self.signalProgressBarColor.connect(self.setProgressBarColor)
        self.show()
        self.uploadFile()

    def setProgressBarColor(self, color):
        """
        :param color:
        :return:
        """
        css = 'QProgressBar::chunk {background-color: ' + color + ';}'
        self.ui.progressBar.setStyleSheet(css)
        return True

    def setProgressBarToValue(self, progressPercent):
        """
        :param progressPercent:
        :return: True for test purpose
        """
        self.ui.progressBar.setValue(progressPercent)
        return True

    def setStatusTextToValue(self, statusText):
        """
        :param statusText:
        :return: True for test purpose
        """
        self.ui.statusText.setText(statusText)
        return True

    def uploadFileWorker(self):
        """
        :return:
        """
        dataNames = {'comet': 'minorPlanets.mpc',
                     'tle': 'satellites.tle',
                     'asteroid': 'minorPlanets.mpc',
                     'leapsec': 'CDFLeapSeconds.txt',
                     'finalsdata': 'finals.data'}

        files = {}
        for dataType in self.dataTypes:
            if dataType not in dataNames:
                return False
            fullDataFilePath = os.path.join(self.dataFilePath, dataNames[dataType])
            files[dataType] = (dataNames[dataType], open(fullDataFilePath, 'r'))

        self.log.debug(f'Data: {files.keys()} added')
        url = f'http://{self.url}/bin/uploadst'
        returnValues = requests.delete(url)
        if returnValues.status_code != 200:
            self.log.debug(f'Error deleting files: {returnValues.status_code}')
            return False

        self.pollStatusRunState = True
        self.threadPool.start(self.workerStatus)
        url = f'http://{self.url}/bin/upload'
        returnValues = requests.post(url, files=files)
        if returnValues.status_code != 202:
            self.log.debug(f'Error uploading data: {returnValues.status_code}')
            return False

        return True

    def sendProgressValue(self, text):
        """
        :param text:
        :return:
        """
        progressValue = int(re.search(r'\d+', text).group())
        self.signalProgress.emit(progressValue)
        return True

    def pollDispatcher(self, text):
        """
        :param text:
        :return:
        """
        single = len(text) == 1
        multiple = len(text) > 1

        if single and text[0].startswith('Uploading'):
            self.signalStatus.emit(text[0])

        elif single and text[0].startswith('Processing'):
            self.signalStatus.emit(text[0])

        elif multiple and text[-1].endswith('elements file.'):
            self.pollStatusRunState = False
            self.sendProgressValue('100')
            self.signalStatus.emit(text[-1])
            self.returnValues['successMount'] = False

        elif multiple and text[-1].endswith('file failed'):
            self.pollStatusRunState = False
            self.sendProgressValue('100')
            self.signalStatus.emit(text[-1])
            self.returnValues['successMount'] = False

        elif multiple and text[-1].endswith('elements saved.'):
            self.returnValues['successMount'] = True
            self.returnValues['success'] = True
            self.sendProgressValue('100')
            self.signalStatus.emit(text[-1])
            self.pollStatusRunState = False

        elif multiple and text[-1].endswith('data updated.'):
            self.returnValues['successMount'] = True
            self.returnValues['success'] = True
            self.sendProgressValue('100')
            self.signalStatus.emit(text[-1])
            self.pollStatusRunState = False

        elif multiple and text[-1][0].isdigit():
            self.sendProgressValue(text[-1])

        else:
            return False
        return True

    def pollStatus(self):
        """
        :return:
        """
        self.timeoutCounter = 10
        self.signalStatus.emit('Uploading data to mount...')
        while self.pollStatusRunState:
            url = f'http://{self.url}/bin/uploadst'
            returnValues = requests.get(url)
            if returnValues.status_code != 200:
                self.log.debug(f'Error status: {returnValues.status_code}')
                self.pollStatusRunState = False
                self.returnValues['successMount'] = False
                return False

            tRaw = returnValues.text
            text = tRaw.strip('\n').split('\n')

            if not self.pollDispatcher(text):
                self.timeoutCounter -= 1
                if self.timeoutCounter < 0:
                    self.pollStatusRunState = False
                    self.returnValues['successMount'] = False

            sleepAndEvents(500)
        return True

    def closePopup(self, result):
        """
        :param result:
        :return:
        """
        self.returnValues['success'] = result
        if not result:
            self.pollStatusRunState = False
            self.signalProgressBarColor.emit('red')
        else:
            while self.pollStatusRunState:
                sleepAndEvents(250)
            if self.returnValues['successMount']:
                self.signalProgressBarColor.emit('green')
            else:
                self.signalProgressBarColor.emit('red')
                sleepAndEvents(2000)

        sleepAndEvents(1000)
        self.close()
        return True

    def uploadFile(self):
        """
        :return:
        """
        self.worker = Worker(self.uploadFileWorker)
        self.worker.signals.result.connect(self.closePopup)
        self.threadPool.start(self.worker)
        self.workerStatus = Worker(self.pollStatus)
        return True
