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
from mw4.gui.extWindows.downloadPopupW import DownloadPopup
from mw4.gui.extWindows.uploadPopupW import UploadPopup
from mw4.logic.databaseProcessing.dataWriter import DataWriter
from pathlib import Path
from PySide6.QtWidgets import QListView


class IERSTime:
    """ """

    def __init__(self, mainW):
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.tempDir: Path = self.app.mwGlob["tempDir"]
        self.uploadPopup = None
        self.downloadPopup = None
        self.databaseProcessing = DataWriter(self.app)
        self.iersSourceURLs = {
            "Datacenter from IERS": "https://datacenter.iers.org/products/eop/rapid/standard/",
            "Maia from usno.navy.mil": "https://maia.usno.navy.mil/ser7/",
        }
        self.ui.progEarthRotationData.clicked.connect(self.progEarthRotationData)
        self.ui.downloadIERS.clicked.connect(self.loadTimeDataFromSourceURLs)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.setupIERSSourceURLsDropDown()
        self.ui.iersSource.setCurrentIndex(config.get("iersSource", 0))

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["iersSource"] = self.ui.iersSource.currentIndex()

    def setupIcons(self) -> None:
        """ """
        self.mainW.wIcon(self.ui.progEarthRotationData, "run")
        self.mainW.wIcon(self.ui.downloadIERS, "run")

    def setupIERSSourceURLsDropDown(self) -> None:
        """ """
        self.ui.iersSource.clear()
        self.ui.iersSource.setView(QListView())
        for name in self.iersSourceURLs:
            self.ui.iersSource.addItem(name)

    def finishProgEarthRotationData(self) -> None:
        """ """
        if self.uploadPopup.returnValues["success"]:
            self.msg.emit(1, "IERS", "Upload", "Successfully uploaded")
        else:
            self.msg.emit(2, "IERS", "Upload", "Upload failed")

    def progEarthRotationData(self) -> None:
        """ """
        self.msg.emit(1, "IERS", "Program", "Earth rotation data")
        self.msg.emit(0, "", "", "finals.data, CDFLeapSeconds.txt")

        suc = self.databaseProcessing.writeEarthRotationData(self.tempDir)
        if not suc:
            self.msg.emit(2, "IERS", "Data error", "Data could not be exported - stopping")
            return

        dataTypes = ["finalsdata", "leapsec"]
        url = self.app.mount.host[0]
        self.msg.emit(0, "IERS", "Uploading", "Upload to mount running")
        self.uploadPopup = UploadPopup(
            self.mainW, url=url, dataTypes=dataTypes, dataFilePath=self.tempDir
        )
        self.uploadPopup.show()
        self.uploadPopup.workerStatus.signals.finished.connect(
            self.finishProgEarthRotationData
        )

    def finishLoadTimeDataFromSourceURLs(self) -> None:
        """ """
        if self.downloadPopup.returnValues["success"]:
            self.msg.emit(0, "IERS", "Download", "Received [finals.data]")
            self.msg.emit(1, "IERS", "Download", "Downloaded complete")
        else:
            self.msg.emit(2, "IERS", "Download", "Download failed")

    def finishLoadFinalsFromSourceURLs(self) -> None:
        """ """
        if not self.downloadPopup.returnValues["success"]:
            self.msg.emit(2, "IERS", "Download", "Download failed")
            return

        self.msg.emit(0, "IERS", "Download", "Received [finals2000A.all]")

        sourceURL = self.ui.iersSource.currentText()
        urlMain = self.iersSourceURLs[sourceURL]

        source = "finals.data"
        url = urlMain + source
        dest = self.app.mwGlob["dataDir"] / source
        self.downloadPopup = DownloadPopup(self.mainW, url=url, dest=dest)
        self.downloadPopup.show()
        self.downloadPopup.downloadFile()
        self.downloadPopup.worker.signals.finished.connect(
            self.finishLoadTimeDataFromSourceURLs
        )

    def loadTimeDataFromSourceURLs(self) -> None:
        """ """
        if not self.ui.isOnline.isChecked():
            return

        sourceURL = self.ui.iersSource.currentText()
        urlMain = self.iersSourceURLs[sourceURL]
        self.msg.emit(1, "IERS", "Download", f"Source: [{sourceURL}]")
        source = "finals2000A.all"
        url = urlMain + source
        dest = self.app.mwGlob["dataDir"] / source
        self.downloadPopup = DownloadPopup(self.mainW, url=url, dest=dest)
        self.downloadPopup.show()
        self.downloadPopup.downloadFile()
        self.downloadPopup.worker.signals.finished.connect(self.finishLoadFinalsFromSourceURLs)
