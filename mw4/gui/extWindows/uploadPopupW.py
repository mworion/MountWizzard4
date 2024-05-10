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

# external packages
from PyQt6.QtCore import Qt, pyqtSignal
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

# local import
from gui.utilities import toolsQtWidget
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.tpool import Worker
from gui.widgets.downloadPopup_ui import Ui_DownloadPopup


class UploadPopup(toolsQtWidget.MWidget):
    """
    the DevicePopup window class handles

    """

    __all__ = ['UploadPopup']

    signalProgress = pyqtSignal(object)
    signalProgressBarColor = pyqtSignal(object)

    def __init__(self, parentWidget, url, dataTypes, dataFilePath):
        super().__init__()
        self.ui = Ui_DownloadPopup()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.returnValues = {'success': False}
        self.parentWidget = parentWidget
        self.url = url
        self.dataTypes = dataTypes
        self.dataFilePath = dataFilePath
        self.worker = None
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)
        self.setWindowTitle('Uploading to mount')
        self.threadPool = parentWidget.threadPool
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

    def setMultipartProgressBar(self, monitor):
        """
        :param monitor:
        :return:
        """
        self.setProgressBarToValue(100)
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
        self.log.debug(f'Data: {files} added')

        multipartE = MultipartEncoder(fields=files)
        monitor = MultipartEncoderMonitor(multipartE, self.setMultipartProgressBar)

        url = f'http://{self.url}/bin/uploadst'
        r = requests.delete(url)
        if r.status_code != 200:
            self.log.debug(f'Error deleting files: {r.status_code}')
            return False

        self.signalProgress.emit(20)
        url = f'http://{self.url}/bin/upload'
        r = requests.post(url, files=files)
        if r.status_code != 202:
            self.log.debug(f'Error uploading data: {r.status_code}')
            return False
        return True

    def closePopup(self, result):
        """
        :param result:
        :return:
        """
        self.signalProgress.emit(100)
        if result:
            self.signalProgressBarColor.emit('green')
        else:
            self.signalProgressBarColor.emit('red')

        self.returnValues['success'] = result
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
        return True
