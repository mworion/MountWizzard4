############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import gzip
import requests
import shutil
from mw4.base.tpool import Worker
from mw4.gui.utilities.toolsQtWidget import MWidget, sleepAndEvents
from mw4.gui.widgets.downloadPopup_ui import Ui_DownloadPopup
from pathlib import Path
from PySide6.QtCore import Qt, Signal


class DownloadPopup(MWidget):
    """ """

    signalProgress = Signal(object)
    signalStatus = Signal(object)
    signalProgressBarColor = Signal(object)

    def __init__(self, parentWidget: MWidget, url: Path, dest: Path, unzip: bool = False):
        super().__init__()
        self.parentWidget = parentWidget
        self.msg = parentWidget.app.msg
        self.threadPool = parentWidget.app.threadPool
        self.worker: Worker | None = None
        self.url = url
        self.dest = dest
        self.unzip = unzip
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

    def setStatusTextToValue(self, statusText: str) -> None:
        """ """
        self.ui.statusText.setText(statusText)

    def getFileFromUrl(self, url: Path, dest: Path) -> bool:
        """ """
        r = requests.get(str(url), stream=True, timeout=3)
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
    def unzipFile(downloadDest: Path, dest: Path) -> None:
        """ """
        with gzip.open(downloadDest, "rb") as f_in, open(dest, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        downloadDest.unlink()

    def downloadFileWorker(self, url: Path, dest: Path, unzip: bool = False) -> bool:
        """ """
        downloadDest = dest.parent / "temp.zip" if unzip else dest

        try:
            self.signalStatus.emit(f"Downloading {dest.stem}")
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

    def downloadFile(self) -> None:
        """ """
        self.worker = Worker(self.downloadFileWorker, self.url, self.dest, self.unzip)
        self.worker.signals.result.connect(self.closePopup)
        self.threadPool.start(self.worker)
