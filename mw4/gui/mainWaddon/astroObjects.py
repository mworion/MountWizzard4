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
import logging

# external packages
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QListView

# local import
from logic.databaseProcessing.dataWriter import DataWriter
from gui.extWindows.downloadPopupW import DownloadPopup
from gui.extWindows.uploadPopupW import UploadPopup


class AstroObjects(QObject):
    """ """

    log = logging.getLogger("MW4")

    dataLoaded = Signal()

    def __init__(
        self,
        window,
        objectText,
        sourceUrls,
        uiObjectList,
        uiSourceList,
        uiSourceGroup,
        prepareTable,
        processSource,
    ):
        super().__init__()
        self.window = window
        self.app = window.app
        self.msg = window.app.msg
        self.dest = None
        self.dataValid = False
        self.objectText = objectText
        self.sourceUrls = sourceUrls
        self.uiObjectList = uiObjectList
        self.uiSourceList = uiSourceList
        self.uiSourceGroup = uiSourceGroup
        self.prepareTable = prepareTable
        self.processSource = processSource

        self.objects = {}
        self.uploadPopup = None
        self.downloadPopup = None
        self.tempDir = self.app.mwGlob["tempDir"]
        self.dataDir = self.app.mwGlob["dataDir"]
        self.loader = self.app.mount.obsSite.loader
        self.dbProc = DataWriter(self.app)
        self.buildSourceListDropdown()
        self.prepareTable()
        self.uiSourceList.currentIndexChanged.connect(self.loadSourceUrl)

        self.dbProcFuncs = {
            "satellite": self.dbProc.writeSatelliteTLE,
            "asteroid": self.dbProc.writeAsteroidMPC,
            "comet": self.dbProc.writeCometMPC,
        }

    def buildSourceListDropdown(self) -> None:
        """ """
        self.uiSourceList.clear()
        self.uiSourceList.setView(QListView())
        for name in self.sourceUrls:
            self.uiSourceList.addItem(name)
        self.uiSourceList.setCurrentIndex(-1)

    def setAge(self, age: float) -> None:
        """ """
        t = f"{self.objectText} data - age: {age:2.1f}d"
        self.uiSourceGroup.setTitle(t)

    def procSourceData(self, direct: bool = False) -> None:
        """ """
        if not direct and not self.downloadPopup.returnValues["success"]:
            return
        self.dataValid = False
        self.processSource()
        self.dataLoaded.emit()

    def runDownloadPopup(self, url: str, unzip: bool) -> None:
        """ """
        if not self.window.ui.isOnline.isChecked():
            return
        self.downloadPopup = DownloadPopup(self.window, url=url, dest=self.dest, unzip=unzip)
        self.downloadPopup.worker.signals.finished.connect(self.procSourceData)

    def loadSourceUrl(self) -> None:
        """ """

        entry = self.uiSourceList.currentText()
        if not entry:
            return
        url = self.sourceUrls[entry]["url"]
        fileName = self.sourceUrls[entry]["file"]
        unzip = self.sourceUrls[entry]["unzip"]
        self.dest = self.dataDir / fileName

        if self.dest.is_file():
            daysOld = self.loader.days_old(fileName)
            self.setAge(daysOld)
            if daysOld < self.window.ui.ageDatabases.value():
                self.procSourceData(direct=True)
                self.log.info(f"Using local source data for {self.objectText}")
                return

        if not self.window.ui.isOnline.isChecked():
            self.msg.emit(2, self.objectText.capitalize(), "Download", "Offline mode active")
            return

        self.setAge(0)
        self.msg.emit(1, self.objectText, "Download", f"{entry}")
        self.log.info(f"Using data for {self.objectText}  {url}, {unzip}, {fileName}")
        self.runDownloadPopup(url, unzip)

    def finishProgObjects(self) -> None:
        """ """
        if self.uploadPopup.returnValues["success"]:
            self.msg.emit(1, self.objectText.capitalize(), "Program", "Successful uploaded")
        else:
            self.msg.emit(2, self.objectText.capitalize(), "Program", "Upload failed")

    def runUploadPopup(self, url: str) -> None:
        """ """
        self.uploadPopup = UploadPopup(self.window, url, [self.objectText], self.tempDir)
        self.uploadPopup.workerStatus.signals.finished.connect(self.finishProgObjects)

    def progObjects(self, objects: list) -> None:
        """ """
        if len(objects) == 0:
            self.msg.emit(
                2,
                self.objectText.capitalize(),
                "Data error",
                "No data to export - stopping",
            )
            return
        self.dbProcFuncs[self.objectText](objects, dataFilePath=self.tempDir)
        self.msg.emit(0, self.objectText.capitalize(), "Program", "Uploading to mount")
        url = self.app.mount.host[0]
        self.runUploadPopup(url)

    def progGUI(self, text: str) -> None:
        """ """
        source = self.uiSourceList.currentText()
        objectType = self.objectText.capitalize()
        self.msg.emit(1, objectType, "Program", f"{text} from {source}")
        self.msg.emit(1, "", "", "Exporting data")

    def progSelected(self) -> None:
        """ """
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
        """ """
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
        """ """
        self.progGUI("All")
        fullObjects = [self.objects.get(name) for name in self.objects]
        self.progObjects(fullObjects)
