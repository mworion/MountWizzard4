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
from mw4.gui.extWindows.downloadPopupW import DownloadPopup
from mw4.gui.extWindows.uploadPopupW import UploadPopup
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.logic.databaseProcessing.dataWriter import DataWriter
from pathlib import Path
from PySide6.QtWidgets import QListView
from collections.abc import Any


class IERSTime(TabAddon):
    iersSourceURLs: dict[str, str] = {
        "Datacenter from IERS": "https://datacenter.iers.org/products/eop/rapid/standard/",
        "Maia from usno.navy.mil": "https://maia.usno.navy.mil/ser7/",
    }

    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.tempDir: Path = self.app.mwGlob["tempDir"]
        self.databaseProcessing = DataWriter(self.app)
        self.ui.progEarthRotationData.clicked.connect(self.progEarthRotationData)
        self.ui.downloadIERS.clicked.connect(self.loadTimeDataFromSourceURLs)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.setupIERSSourceURLsDropDown()
        self.ui.iersSource.setCurrentIndex(config.get("iersSource", 0))

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["iersSource"] = self.ui.iersSource.currentIndex()

    def setupIcons(self) -> None:
        self.mainW.wIcon(self.ui.progEarthRotationData, "run")
        self.mainW.wIcon(self.ui.downloadIERS, "run")

    def setupIERSSourceURLsDropDown(self) -> None:
        self.ui.iersSource.clear()
        self.ui.iersSource.setView(QListView())
        for name in self.iersSourceURLs:
            self.ui.iersSource.addItem(name)

    def progEarthRotationData(self) -> None:
        self.msg.emit(1, "IERS", "Program", "Earth rotation data")
        suc = self.databaseProcessing.writeEarthRotationData(self.tempDir)
        if not suc:
            self.msg.emit(2, "IERS", "Data error", "Data could not be exported - stopping")
            return
        dataTypes = ["finalsdata", "leapsec"]
        url = self.app.dReg["mount"].instance.config.hostAddress
        self.msg.emit(0, "IERS", "Uploading", "Upload to mount running")
        suc = UploadPopup.upload(
            self.mainW, url=url, dataTypes=dataTypes, dataFilePath=self.tempDir
        )
        if suc:
            self.msg.emit(1, "IERS", "Upload", "Successfully uploaded")
        else:
            self.msg.emit(2, "IERS", "Upload", "Upload failed")

    def loadTimeDataFromSourceURLs(self) -> None:
        if not self.app.isOnline:
            return

        sourceKey = self.ui.iersSource.currentText()
        urlMain = self.iersSourceURLs[sourceKey]
        self.msg.emit(1, "IERS", "Download", f"Source: [{sourceKey}, {urlMain}]")

        source = "finals2000A.all"
        url = urlMain + source
        dest = self.app.mwGlob["dataDir"] / source
        if not DownloadPopup.download(self.mainW, url=url, dest=dest):
            self.msg.emit(2, "IERS", "Download", "Download failed")
            return

        self.msg.emit(0, "IERS", "Download", "Received [finals2000A.all]")
        source = "finals.data"
        url = urlMain + source
        dest = self.app.mwGlob["dataDir"] / source
        if DownloadPopup.download(self.mainW, url=url, dest=dest):
            self.msg.emit(0, "IERS", "Download", "Received [finals.data]")
            self.msg.emit(1, "IERS", "Download", "Downloaded complete")
        else:
            self.msg.emit(2, "IERS", "Download", "Download failed")
