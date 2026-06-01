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
# License APL2.0
#
###########################################################
import re
import requests
from mw4.base.threadUtils import mainThreadSleep
from mw4.base.tpool import Worker
from mw4.gui.utilities.qtHelpers import svg2pixmap
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.uploadPopup_ui import Ui_UploadPopup
from pathlib import Path
from PySide6.QtCore import Qt, Signal


class UploadPopup(MWidget):
    signalProgress = Signal(object)
    signalStatus = Signal(object)
    signalProgressBarColor = Signal(object)
    dataNames = {
        "comet": {
            "file": "comets.mpc",
            "attr": "comet",
        },
        "satellite": {
            "file": "satellites.tle",
            "attr": "tle",
        },
        "asteroid": {
            "file": "asteroids.mpc",
            "attr": "asteroid",
        },
        "leapsec": {
            "file": "CDFLeapSeconds.txt",
            "attr": "leapsec",
        },
        "finalsdata": {
            "file": "finals.data",
            "attr": "finalsdata",
        },
    }

    def __init__(
        self, parentWidget: MWidget, url: str, dataTypes: list[str], dataFilePath: Path
    ):
        super().__init__()
        self.ui = Ui_UploadPopup()
        self.ui.setupUi(self.ws)
        self.setWindowTitle("Mount Upload")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.returnValues = {"success": False, "successMount": False}
        self.parentWidget = parentWidget
        self.msg = parentWidget.app.msg
        self.threadPool = parentWidget.app.threadPool
        self.worker: Worker | None = None
        self.workerStatus: Worker | None = None
        self.url: Path = url
        self.dataTypes: list[str] = dataTypes
        self.dataFilePath: Path = dataFilePath

        self.pollStatusRunState: bool = False
        self.timeoutCounter: int = 0
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)
        self.setWindowTitle("Uploading to mount")
        self.signalStatus.connect(self.setStatusTextToValue)
        self.signalProgress.connect(self.setProgressBarToValue)
        self.signalProgressBarColor.connect(self.setProgressBarColor)
        self.setIcon()

    def setIcon(self) -> None:
        pixmap = svg2pixmap("assets/icon/upload_pop.svg", self.M_PRIM)
        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.icon.setPixmap(pixmap)

    def setProgressBarColor(self, colorstr: str) -> None:
        css = "QProgressBar::chunk {background-color: " + colorstr + ";}"
        self.ui.progressBar.setStyleSheet(css)

    def setProgressBarToValue(self, progressPercent: int) -> None:
        self.ui.progressBar.setValue(progressPercent)

    def setStatusTextToValue(self, statusText: str) -> None:
        self.ui.statusText.setText(statusText)

    def sendProgressValue(self, text: str) -> None:
        progressValue = int(re.search(r"\d+", text).group())
        self.signalProgress.emit(progressValue)

    def pollDispatcherHelper(self, text: str) -> None:
        self.sendProgressValue("100")
        self.signalStatus.emit(text)
        self.pollStatusRunState = False

    def sendProgressStatus(self, text: list) -> None:
        if text == [""]:
            return
        single = len(text) == 1
        multiple = len(text) > 1

        if single and text[0].split()[0] in ["Uploading", "Processing"]:
            self.signalStatus.emit(text[0])
        elif multiple and text[-1].split()[-1] in ["file.", "failed"]:
            self.pollDispatcherHelper(text[-1])
            self.returnValues["successMount"] = False
        elif multiple and text[-1].split()[-1] in ["saved.", "updated."]:
            self.pollDispatcherHelper(text[-1])
            self.returnValues["successMount"] = True
            self.pollStatusRunState = False
        elif multiple and text[-1][0].isdigit():
            self.sendProgressValue(text[-1])

    def generateURLStatus(self) -> str:
        return f"http://{str(self.url)}/bin/uploadst"

    def getStatus(self) -> list[str]:
        returnValues = requests.get(self.generateURLStatus(), timeout=1)
        self.returnValues["successMount"] = True
        if returnValues.status_code != 200:
            self.log.debug(f"Error status: {returnValues.status_code}")
            self.pollStatusRunState = False
            self.returnValues["successMount"] = False
        return returnValues.text.strip("\n").split("\n")

    def pollStatus(self) -> None:
        self.signalStatus.emit("Uploading data to mount...")
        while self.pollStatusRunState:
            text = self.getStatus()
            self.sendProgressStatus(text)

    def prepareFiles(self) -> dict:
        files = {}
        for dataType in self.dataTypes:
            if dataType not in self.dataNames:
                return {}
            fullDataFilePath = self.dataFilePath / self.dataNames[dataType]["file"]
            with open(fullDataFilePath, "rb") as fh:
                files[self.dataNames[dataType]["attr"]] = (
                    self.dataNames[dataType]["file"],
                    fh.read(),
                )
        self.log.debug(f"Data: {list(files.items())}")
        return files

    def generateURL(self) -> str:
        return f"http://{str(self.url)}/bin/upload"

    def deleteHostData(self) -> bool:
        returnValues = requests.delete(self.generateURL(), timeout=10)  # SEC-4
        if returnValues.status_code not in [200, 204]:
            self.msg.emit(0, "Upload", "Error", f"Deleting File: {returnValues.status_code}")
            return False
        return True

    def postHostData(self, files: dict) -> bool:
        returnValues = requests.post(self.generateURL(), files=files, timeout=10)  # SEC-4
        if returnValues.status_code != 202:
            self.msg.emit(0, "Upload", "Error", f"Data: {returnValues.status_code}")
            return False
        return True

    def uploadFileWorker(self) -> bool:
        if not self.deleteHostData():
            return False
        files = self.prepareFiles()
        self.pollStatusRunState = True
        self.threadPool.start(self.workerStatus)
        return self.postHostData(files)

    def closePopup(self, result: bool) -> None:
        self.returnValues["success"] = result
        if not result:
            self.pollStatusRunState = False
            self.signalProgressBarColor.emit("red")
        else:
            while self.pollStatusRunState:
                mainThreadSleep(100)
            if self.returnValues["successMount"]:
                self.signalProgressBarColor.emit("green")
            else:
                self.signalProgressBarColor.emit("red")
                self.msg.emit(2, "Upload", "Error", "Uploaded but mount failed to save data")
        mainThreadSleep(500)
        self.close()

    def uploadFile(self) -> None:
        self.worker = Worker(self.uploadFileWorker)
        self.workerStatus = Worker(self.pollStatus)
        self.worker.signals.result.connect(self.closePopup)
        self.threadPool.start(self.worker)
