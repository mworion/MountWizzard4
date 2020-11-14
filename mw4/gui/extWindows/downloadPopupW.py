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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import time

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

    def __init__(self,
                 parentWidget,
                 url='',
                 dest='',
                 callBack=None,
                 ):

        super().__init__()
        self.ui = Ui_DownloadPopup()
        self.ui.setupUi(self)
        self.initUI()
        self.callBack = callBack
        self.setWindowModality(Qt.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)

        baseName = os.path.basename(url)
        self.setWindowTitle(f'Downloading [{baseName}]')

        self.threadPool = parentWidget.threadPool
        self.ui.cancel.clicked.connect(self.close)
        self.signalProgress.connect(self.setProgress)
        self.downloadFile(url, dest)
        self.show()

    def setProgress(self, progressPercent):
        """

        :param progressPercent:
        :return: True for test purpose
        """
        self.ui.progressBar.setValue(progressPercent)
        return True

    def downloadFileWorker(self, url, dest):
        """

        :param url:
        :param dest:
        :return:
        """

        if not os.path.dirname(dest):
            return False

        r = requests.get(url, stream=True, timeout=1)
        totalSizeBytes = int(r.headers.get('content-length', 1))

        with open(dest, 'wb') as f:
            for n, chunk in enumerate(r.iter_content(512)):
                progressPercent = int(n * 512 / totalSizeBytes * 100)
                self.signalProgress.emit(progressPercent)

                if chunk:
                    f.write(chunk)
            self.signalProgress.emit(100)

        time.sleep(1)
        return True

    def downloadFile(self, url, dest):
        """
        :param url:
        :param dest:
        :return:
        """
        worker = Worker(self.downloadFileWorker,
                        url=url,
                        dest=dest)
        worker.signals.result.connect(self.close)

        if self.callBack:
            worker.signals.result.connect(self.callBack)

        self.threadPool.start(worker)

        return True
