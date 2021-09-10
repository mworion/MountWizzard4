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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import time
import gzip
import shutil

# external packages
from PyQt5.QtCore import Qt, pyqtSignal
import requests

# local import
from gui.utilities import toolsQtWidget
from base.tpool import Worker
from gui.widgets.downloadPopup_ui import Ui_DownloadPopup


class DownloadPopup(toolsQtWidget.MWidget):
    """
    the DevicePopup window class handles

    """

    __all__ = ['DownloadPopup',
               ]

    signalProgress = pyqtSignal(object)
    signalProgressBarColor = pyqtSignal(object)

    def __init__(self,
                 parentWidget,
                 url='',
                 dest='',
                 unzip=True,
                 callBack=None,
                 ):

        super().__init__()
        self.ui = Ui_DownloadPopup()
        self.ui.setupUi(self)
        self.returnValues = {'success': False}
        self.callBack = callBack
        self.parentWidget = parentWidget
        self.worker = None
        self.setWindowModality(Qt.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)

        baseName = os.path.basename(url)
        self.setWindowTitle(f'Downloading [{baseName}]')

        self.threadPool = parentWidget.threadPool
        self.signalProgress.connect(self.setProgressBarToValue)
        self.signalProgressBarColor.connect(self.setProgressBarColor)
        self.downloadFile(url, dest, unzip=unzip)
        self.show()

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
        r = requests.get(url, stream=True, timeout=1)
        totalSizeBytes = int(r.headers.get('content-length', 1))

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
        if not os.path.dirname(dest):
            return False
        if os.path.isfile(dest):
            os.remove(dest)

        try:
            self.getFileFromUrl(url, dest)
        except TimeoutError:
            t = f'Download [{url}] timed out!'
            self.parentWidget.app.message.emit(t, 2)
            self.signalProgressBarColor.emit('red')
            time.sleep(1)
            return False
        except Exception as e:
            t = f'Error in unzip [{url}]'
            self.parentWidget.app.message.emit(t, 2)
            t = f'Error in unzip [{url}], {e}'
            self.log.warning(t)
            self.signalProgressBarColor.emit('red')
            time.sleep(1)
            return False
        else:
            self.signalProgressBarColor.emit('green')
        finally:
            time.sleep(1)

        if not unzip:
            return True

        try:
            self.unzipFile(dest)
        except Exception as e:
            t = f'Error in unzip [{url}]'
            self.parentWidget.app.message.emit(t, 2)
            t = f'Error in unzip [{url}], {e}'
            self.log.warning(t)
            return False
        return True

    def processResult(self, result):
        """
        :return:
        """
        self.setVisible(False)
        if result:
            self.callBack()

        self.close()
        return True

    def downloadFile(self, url, dest, unzip=True):
        """
        :param url:
        :param dest:
        :param unzip:
        :return:
        """
        self.worker = Worker(self.downloadFileWorker, url=url, dest=dest,
                             unzip=unzip)
        if self.callBack:
            self.worker.signals.result.connect(self.processResult)
        else:
            self.worker.signals.result.connect(self.close)

        self.threadPool.start(self.worker)
        return True
