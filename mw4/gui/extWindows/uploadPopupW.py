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
from gui.utilities.toolsQtWidget import MWidget
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.tpool import Worker
from gui.widgets.uploadPopup_ui import Ui_UploadPopup


class UploadPopup(MWidget):
    """
    """
    __all__ = ['UploadPopup']

    PROGRESS_DONE = 100
    CYCLES_WAIT = 20
    signalProgress = Signal(object)
    signalStatus = Signal(object)
    signalProgressBarColor = Signal(object)

    dataNames = {
        'comet': {
            'file': 'comets.mpc',
            'attr': 'comet',
        },
        'satellite': {
            'file': 'satellites.tle',
            'attr': 'tle',
        },
        'asteroid': {
            'file': 'asteroids.mpc',
            'attr': 'asteroid',
        },
        'leapsec': {
            'file': 'CDFLeapSeconds.txt',
            'attr': 'leapsec',
        },
        'finalsdata': {
            'file': 'finals.data',
            'attr': 'finalsdata',
        },
    }

    def __init__(self, parentWidget: MWidget, url: str, dataTypes: str,
                 dataFilePath: str):
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
        self.setIcon()
        self.show()
        self.uploadFile()

    def setIcon(self) -> None:
        """
        """
        pixmap = self.svg2pixmap(':/icon/upload_pop.svg', self.M_BLUE)
        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.icon.setPixmap(pixmap)

    def setProgressBarColor(self, color:str) -> None:
        """
        """
        css = 'QProgressBar::chunk {background-color: ' + color + ';}'
        self.ui.progressBar.setStyleSheet(css)

    def setProgressBarToValue(self, progressPercent: int) -> None:
        """
        """
        self.ui.progressBar.setValue(progressPercent)

    def setStatusTextToValue(self, statusText: str) -> None:
        """
        """
        self.ui.statusText.setText(statusText)

    def uploadFileWorker(self) -> bool:
        """
        """
        files = {}
        for dataType in self.dataTypes:
            if dataType not in self.dataNames:
                return False
            fullDataFilePath = os.path.join(self.dataFilePath,
                                            self.dataNames[dataType]['file'])
            files[self.dataNames[dataType]['attr']] = (self.dataNames[dataType]['file'],
                                                       open(fullDataFilePath, 'r'))

        self.log.debug(f'Data: {list(files.items())}')
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

    def sendProgressValue(self, text:str) -> None:
        """:
        """
        progressValue = int(re.search(r'\d+', text).group())
        self.signalProgress.emit(progressValue)

    def pollDispatcher(self, text:str) -> None:
        """
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

    def pollStatus(self) -> None:
        """
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
                return

            tRaw = returnValues.text
            text = tRaw.strip('\n').split('\n')

            if not self.pollDispatcher(text):
                self.timeoutCounter -= 1
                if self.timeoutCounter < 0:
                    self.pollStatusRunState = False
                    self.returnValues['successMount'] = False

            sleepAndEvents(500)

    def closePopup(self, result: dict) -> None:
        """
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

        sleepAndEvents(2500)
        self.close()

    def uploadFile(self) -> None:
        """
        """
        self.worker = Worker(self.uploadFileWorker)
        self.worker.signals.result.connect(self.closePopup)
        self.threadPool.start(self.worker)
        self.workerStatus = Worker(self.pollStatus)
