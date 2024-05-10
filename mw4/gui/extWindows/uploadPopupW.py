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

    def __init__(self, parentWidget, dataTypes, dataFilePath):
        super().__init__()
        self.ui = Ui_DownloadPopup()
        self.ui.setupUi(self)
        self.returnValues = {'success': False}
        self.parentWidget = parentWidget
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
        self.uploadFile(dataTypes=dataTypes, dataFilePath=dataFilePath)

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

    def uploadFileWorker(self, dataTypes, dataFilePath):
        """
        :param dataTypes:
        :param dataFilePath:
        :return:
        """
        dataNames = {'comet': 'minorPlanets.mpc',
                     'tle': 'satellites.tle',
                     'asteroid': 'minorPlanets.mpc',
                     'leapsec': 'CDFLeapSeconds.txt',
                     'finalsdata': 'finals.data'}

        files = {}
        for dataType in dataTypes:
            if dataType not in dataNames:
                return False
            fullDataFilePath = os.path.join(dataFilePath, dataNames[dataType])
            files[dataType] = (dataNames[dataType], open(fullDataFilePath, 'r'))
        self.log.debug(f'Data: {files} added')

        multipartE = MultipartEncoder(fields=files)
        monitor = MultipartEncoderMonitor(multipartE, self.setMultipartProgressBar)

        baseURL = self.app.mount.host[0]
        url = f'http://{baseURL}/bin/uploadst'
        self.setProgressBarToValue(0)
        r = requests.delete(url)
        if r.status_code != 200:
            self.log.debug(f'Error deleting files: {r.status_code}')
            self.setProgressBarToValue(100)
            self.setProgressBarColor('red')
            return False

        self.setProgressBarToValue(20)
        url = f'http://{baseURL}/bin/upload'
        r = requests.post(url, files=files)
        if r.status_code != 202:
            self.log.debug(f'Error uploading data: {r.status_code}')
            self.setProgressBarToValue(100)
            self.setProgressBarColor('red')
            return False

        self.setProgressBarToValue(100)
        return True

    def closePopup(self):
        """
        :return:
        """
        sleepAndEvents(2000)
        self.close()
        return True

    def uploadFile(self, dataTypes, dataFilePath):
        """
        :param dataTypes:
        :param dataFilePath:
        :return:
        """
        self.worker = Worker(self.uploadFileWorker, dataTypes, dataFilePath)
        self.worker.signals.result.connect(self.closePopup)
        self.threadPool.start(self.worker)
        return True
