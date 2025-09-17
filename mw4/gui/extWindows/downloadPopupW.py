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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
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
from gui.utilities.toolsQtWidget import MWidget
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.tpool import Worker
from gui.widgets.downloadPopup_ui import Ui_DownloadPopup


class DownloadPopup(MWidget):
    """ """

    signalProgress = Signal(object)
    signalStatus = Signal(object)
    signalProgressBarColor = Signal(object)

    def __init__(self, parentWidget: MWidget, url: str, dest: str, unzip: bool = False):
        super().__init__()
        self.parentWidget = parentWidget
        self.msg = parentWidget.app.msg
        self.threadPool = parentWidget.app.threadPool
        self.worker: Worker = None

        self.ui = Ui_DownloadPopup()
        self.ui.setupUi(self)
        self.setWindowTitle("Downloading from Web")
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)

        self.returnValues = {"success": False}
        self.signalStatus.connect(self.setStatusTextToValue)
        self.signalProgress.connect(self.setProgressBarToValue)
        self.signalProgressBarColor.connect(self.setProgressBarColor)

        self.setIcon()
        self.show()
        self.downloadFile(url, dest, unzip=unzip)

    def setIcon(self) -> None:
        """ """
        pixmap = self.svg2pixmap(":/icon/download_pop.svg", self.M_PRIM)
        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.icon.setPixmap(pixmap)

    def setProgressBarColor(self, color: str) -> None:
        """ """
        css = "QProgressBar::chunk {background-color: " + color + ";}"
        self.ui.progressBar.setStyleSheet(css)

    def setProgressBarToValue(self, progressPercent: int) -> None:
        """ """
        self.ui.progressBar.setValue(progressPercent)

    def setStatusTextToValue(self, statusText: str) -> bool:
        """ """
        self.ui.statusText.setText(statusText)

    def getFileFromUrl(self, url: str, dest: str) -> bool:
        """ """
        r = requests.get(url, stream=True, timeout=3)
        totalSizeBytes = int(r.headers.get("content-length", 1))
        if r.status_code != 200:
            return False

        with open(dest, "wb") as f:
            for n, chunk in enumerate(r.iter_content(512)):
                progressPercent = int(n * 512 / totalSizeBytes * 100)
                self.signalProgress.emit(progressPercent)
                if chunk:
                    f.write(chunk)
            self.signalProgress.emit(100)
        return True

    @staticmethod
    def unzipFile(downloadDest: str, dest: str) -> None:
        """ """
        with gzip.open(downloadDest, "rb") as f_in:
            with open(dest, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(downloadDest)

    def downloadFileWorker(self, url: str, dest: str, unzip: bool = False) -> bool:
        """ """
        if unzip:
            downloadDest = os.path.dirname(dest) + os.path.basename(url)
        else:
            downloadDest = dest

        try:
            self.signalStatus.emit(f"Downloading {os.path.basename(dest)}")
            suc = self.getFileFromUrl(url, downloadDest)
            if not suc:
                return False
        except TimeoutError:
            self.msg.emit(2, "Download", "Timeout", f"{url}")
            return False
        except Exception as e:
            self.msg.emit(2, "Download", "Error", f"{url}")
            self.log.warning(f"General error [{url}], {e}")
            return False

        if not unzip:
            return True

        try:
            self.unzipFile(downloadDest, dest)
        except Exception as e:
            self.msg.emit(2, "Download", "Unzip", f"{url}")
            self.log.warning(f"Error in unzip [{url}], {e}")
            return False
        return True

    def closePopup(self, result: bool) -> None:
        """ """
        self.signalProgress.emit(100)
        if result:
            self.signalProgressBarColor.emit("green")
            self.signalStatus.emit("Download successful")
        else:
            self.signalProgressBarColor.emit("red")
            self.signalStatus.emit("Download failed")

        self.returnValues["success"] = result
        sleepAndEvents(500)
        self.close()

    def downloadFile(self, url: str, dest: str, unzip: bool = False) -> None:
        """ """
        self.worker = Worker(self.downloadFileWorker, url=url, dest=dest, unzip=unzip)
        self.worker.signals.result.connect(self.closePopup)
        self.threadPool.start(self.worker)
