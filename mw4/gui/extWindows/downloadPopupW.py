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
import gzip
import shutil

# external packages
from PySide6.QtCore import Qt, Signal
import requests

# local import
from gui.utilities import toolsQtWidget
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.tpool import Worker
from gui.widgets.downloadPopup_ui import Ui_DownloadPopup


class DownloadPopup(toolsQtWidget.MWidget):
    """
    """
    __all__ = ['DownloadPopup']

    signalProgress = Signal(object)
    signalProgressBarColor = Signal(object)

    def __init__(self, parentWidget, url='', dest='', unzip=True):
        super().__init__()
        self.ui = Ui_DownloadPopup()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.returnValues = {'success': False}
        self.parentWidget = parentWidget
        self.msg = parentWidget.app.msg
        self.worker = None
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)

        baseName = os.path.basename(url)
        self.setWindowTitle(f'Downloading {baseName}')

        self.threadPool = parentWidget.threadPool
        self.signalProgress.connect(self.setProgressBarToValue)
        self.signalProgressBarColor.connect(self.setProgressBarColor)
        self.show()
        self.downloadFile(url, dest, unzip=unzip)

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

    def getFileFromUrl(self, url, dest):
        """
        :param url:
        :param dest:
        :return:
        """
        r = requests.get(url, stream=True, timeout=3)
        totalSizeBytes = int(r.headers.get('content-length', 1))
        if r.status_code != 200:
            return False

        with open(dest, 'wb') as f:
            for n, chunk in enumerate(r.iter_content(512)):
                progressPercent = int(n * 512 / totalSizeBytes * 100)
                self.signalProgress.emit(progressPercent)
                if chunk:
                    f.write(chunk)
            self.signalProgress.emit(100)
        return True

    @staticmethod
    def unzipFile(dest):
        """
        :param dest:
        :return: True for test purpose
        """
        destUnzip = dest[:-3]
        with gzip.open(dest, 'rb') as f_in:
            with open(destUnzip, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        if os.path.isfile(dest):
            os.remove(dest)

        return True

    def downloadFileWorker(self, url, dest, unzip=True):
        """
        :param url:
        :param dest:
        :param unzip:
        :return:
        """
        dest = os.path.normpath(dest)
        if not os.path.dirname(dest):
            return False
        if os.path.isfile(dest):
            os.remove(dest)

        try:
            suc = self.getFileFromUrl(url, dest)
            if not suc:
                raise FileNotFoundError
        except TimeoutError:
            self.msg.emit(2, 'Download', 'Timeout', f'{url}')
            return False
        except Exception as e:
            self.msg.emit(2, 'Download', 'Error', f'{url}')
            self.log.warning(f'General error [{url}], {e}')
            return False

        if not unzip:
            return True

        try:
            self.unzipFile(dest)
        except Exception as e:
            self.msg.emit(2, 'Download', 'Unzip', f'{url}')
            self.log.warning(f'Error in unzip [{url}], {e}')
            return False
        return True

    def closePopup(self, result):
        """
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

    def downloadFile(self, url, dest, unzip=True):
        """
        :param url:
        :param dest:
        :param unzip:
        :return:
        """
        self.worker = Worker(self.downloadFileWorker,
                             url=url, dest=dest, unzip=unzip)
        self.worker.signals.result.connect(self.closePopup)
        self.threadPool.start(self.worker)
        return True
