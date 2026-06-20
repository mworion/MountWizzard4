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
import logging
from mw4.base.tpool import Worker
from mw4.gui.extWindows.downloadPopupW import DownloadPopup
from mw4.gui.extWindows.uploadPopupW import UploadPopup
from mw4.logic.databaseProcessing.dataWriter import DataWriter
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QListView


class AstroObjectSignals(QObject):
    dataLoaded = Signal()


class AstroObjects:
    log = logging.getLogger("MW4")

    def __init__(
        self,
        window,
        objectText,
        sourceUrls,
        uiObjectList,
        uiSourceList,
        uiSourceGroup,
        processSource,
    ):
        self.window = window
        self.app = window.app
        self.threadPool = window.app.threadPool
        self.msg = window.app.msg
        self.signals = AstroObjectSignals()
        self.dest: Path = Path()
        self.dataValid: bool = False
        self.objectText = objectText
        self.sourceUrls: dict = sourceUrls
        self.uiObjectList = uiObjectList
        self.uiSourceList = uiSourceList
        self.uiSourceGroup = uiSourceGroup
        self.processSource = processSource
        self.workerSource: Worker | None = None
        self.workerTable: Worker | None = None
        self.objects: dict = {}
        self.uploadPopup = None
        self.downloadPopup = None
        self.tempDir: Path = self.app.mwGlob["tempDir"]
        self.dataDir: Path = self.app.mwGlob["dataDir"]
        self.loader = self.app.dReg["mount"].obsSite.loader
        self.dbProc = DataWriter(self.app)
        self.buildSourceListDropdown()
        self.uiSourceList.currentIndexChanged.connect(self.loadSourceUrl)
        self.dbProcFuncs = {
            "satellite": self.dbProc.writeSatelliteTLE,
            "asteroid": self.dbProc.writeAsteroidMPC,
            "comet": self.dbProc.writeCometMPC,
        }

    def buildSourceListDropdown(self) -> None:
        self.uiSourceList.clear()
        self.uiSourceList.setView(QListView())
        self.uiSourceList.addItem("Please select")
        for name in self.sourceUrls:
            self.uiSourceList.addItem(name)
        self.uiSourceList.setCurrentIndex(0)

    def setAge(self, age: float) -> None:
        t = f"{self.objectText} data - age: {age:2.1f}d"
        self.uiSourceGroup.setTitle(t)

    def workerProcessSource(self) -> None:
        self.processSource()
        self.signals.dataLoaded.emit()

    def procSourceData(self) -> None:
        self.dataValid = False
        self.workerSource = Worker(self.workerProcessSource)
        self.threadPool.start(self.workerSource)

    def runDownloadPopup(self, url: Path, unzip: bool) -> None:
        self.downloadPopup = DownloadPopup(self.window, url, self.dest, unzip)
        suc = self.downloadPopup.exec()
        if suc:
            self.procSourceData()

    def checkFileAgeOK(self, fileName: Path) -> bool:
        if not fileName.is_file():
            return False
        daysOld = self.loader.days_old(fileName)
        self.setAge(daysOld)
        cfg = self.app.config.get("SettingUpdate", {})
        return daysOld < cfg.get("ageDatabases", 1)

    def loadSourceUrl(self) -> None:
        entry = self.uiSourceList.currentText()
        if entry == "Please select":
            return

        url = self.sourceUrls[entry]["url"]
        unzip = self.sourceUrls[entry]["unzip"]
        fileName = self.sourceUrls[entry]["file"]
        self.dest = self.dataDir / fileName

        if self.checkFileAgeOK(self.dest):
            self.procSourceData()
            self.log.info(f"Using local source data for {self.objectText}")
            return

        if not self.app.isOnline:
            self.msg.emit(2, self.objectText.capitalize(), "Download", "Offline mode active")
            return

        self.setAge(0)
        self.msg.emit(1, self.objectText.capitalize(), "Download", f"{entry}")
        self.log.info(f"Using data for {self.objectText}  {url}, {unzip}, {fileName}")
        self.runDownloadPopup(url, unzip)

    def runUploadPopup(self, url: Path) -> None:
        self.uploadPopup = UploadPopup(self.window, url, [self.objectText], self.tempDir)
        suc = self.uploadPopup.exec()
        if suc:
            self.msg.emit(1, self.objectText.capitalize(), "Mount upload", "Successful")
        else:
            self.msg.emit(2, self.objectText.capitalize(), "Mount upload", "Failed")


    def progObjects(self, objects: list) -> None:
        if len(objects) == 0:
            self.msg.emit(
                2,
                self.objectText.capitalize(),
                "Data export",
                "No data to export - stopping",
            )
            return
        self.dbProcFuncs[self.objectText](objects, dataFilePath=self.tempDir)
        url = Path(self.app.dReg["mount"].instance.config.hostAddress)
        self.runUploadPopup(url)

    def progGUI(self, text: str) -> None:
        source = self.uiSourceList.currentText()
        self.msg.emit(
            1, self.objectText.capitalize(), "Mount upload", f"[{text}] from [{source}]"
        )

    def progSelected(self) -> None:
        self.progGUI("Selected")
        selectedItems = self.uiObjectList.selectedItems()
        selectedObjects = []
        for entry in selectedItems:
            if entry.column() != 1:
                continue
            name = entry.text()
            selectedObjects.append(self.objects.get(name))
        self.progObjects(selectedObjects)

    def progFiltered(self) -> None:
        self.progGUI("Filtered")
        filteredObjects = []
        for row in range(self.uiObjectList.model().rowCount()):
            entry = self.uiObjectList.model().index(row, 1)
            if self.uiObjectList.isIndexHidden(entry):
                continue
            name = entry.data()
            filteredObjects.append(self.objects.get(name))
        self.progObjects(filteredObjects)

    def progFull(self) -> None:
        self.progGUI("All")
        fullObjects = [self.objects.get(name) for name in self.objects]
        self.progObjects(fullObjects)
