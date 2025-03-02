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

# external packages
from PySide6.QtWidgets import QListView
from PySide6.QtCore import QObject

# local import
from gui.extWindows.downloadPopupW import DownloadPopup
from gui.extWindows.uploadPopupW import UploadPopup
from logic.databaseProcessing.dataWriter import DataWriter


class IERSTime(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.tempDir = self.app.mwGlob["tempDir"]
        self.uploadPopup = None
        self.downloadPopup = None
        self.databaseProcessing = DataWriter(self.app)
        self.iersSourceURLs = {
            "Datacenter from IERS": "https://datacenter.iers.org/products/eop/rapid/standard/",
            "Maia from usno.navy.mil": "https://maia.usno.navy.mil/ser7/",
        }

        self.ui.progEarthRotationData.clicked.connect(self.progEarthRotationData)
        self.ui.downloadIERS.clicked.connect(self.loadTimeDataFromSourceURLs)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to
        the gui elements. if some initialisations have to be proceeded with the
        loaded persistent data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config["mainW"]
        self.setupIERSSourceURLsDropDown()
        self.ui.iersSource.setCurrentIndex(config.get("iersSource", 0))
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config["mainW"]
        config["iersSource"] = self.ui.iersSource.currentIndex()
        return True

    def setupIcons(self):
        self.mainW.wIcon(self.ui.progEarthRotationData, "run")
        self.mainW.wIcon(self.ui.downloadIERS, "run")

    def setupIERSSourceURLsDropDown(self):
        """
        setupMinorPlanetSourceURLsDropDown handles the dropdown list for the
        satellite data online sources. therefore we add the necessary entries to
        populate the list.

        :return: success for test
        """
        self.ui.iersSource.clear()
        self.ui.iersSource.setView(QListView())
        for name in self.iersSourceURLs:
            self.ui.iersSource.addItem(name)
        return True

    def finishProgEarthRotationData(self):
        """
        :return:
        """
        if self.uploadPopup.returnValues["success"]:
            self.msg.emit(1, "IERS", "Program", "Successfully uploaded")
        else:
            self.msg.emit(1, "IERS", "Program", "Upload failed")
        return True

    def progEarthRotationData(self):
        """
        :return: success
        """
        self.msg.emit(1, "IERS", "Program", "Earth rotation data")
        self.msg.emit(1, "", "", "finals.data, CDFLeapSeconds.txt")

        suc = self.databaseProcessing.writeEarthRotationData(self.tempDir)
        if not suc:
            self.msg.emit(2, "IERS", "Data error", "Data could not be exported - stopping")
            return False

        dataTypes = ["finalsdata", "leapsec"]
        url = self.app.mount.host[0]
        self.msg.emit(0, "IERS", "Program", "Uploading to mount")
        self.uploadPopup = UploadPopup(
            self.mainW, url=url, dataTypes=dataTypes, dataFilePath=self.tempDir
        )
        self.uploadPopup.workerStatus.signals.finished.connect(
            self.finishProgEarthRotationData
        )
        return True

    def finishLoadTimeDataFromSourceURLs(self):
        """
        :return:
        """
        if self.downloadPopup.returnValues["success"]:
            self.msg.emit(0, "IERS", "Program", "Downloaded finals.data")
            self.msg.emit(1, "IERS", "Program", "Downloaded complete")
        else:
            self.msg.emit(1, "IERS", "Program", "Download failed")
        return True

    def finishLoadFinalsFromSourceURLs(self):
        """
        :return:
        """
        if not self.downloadPopup.returnValues["success"]:
            self.msg.emit(0, "IERS", "Program", "Download failed")
            return False

        self.msg.emit(1, "IERS", "Program", "Downloaded finals2000A.all")
        sourceURL = self.ui.iersSource.currentText()
        urlMain = self.iersSourceURLs[sourceURL]

        source = "finals.data"
        url = urlMain + source
        dest = self.app.mwGlob["dataDir"] / source
        self.msg.emit(1, "IERS", "Download", f"File: {source}")
        self.downloadPopup = DownloadPopup(self.mainW, url=url, dest=dest)
        self.downloadPopup.worker.signals.finished.connect(
            self.finishLoadTimeDataFromSourceURLs
        )
        return True

    def loadTimeDataFromSourceURLs(self):
        """
        :return: success
        """
        isOnline = self.ui.isOnline.isChecked()
        if not isOnline:
            return False

        sourceURL = self.ui.iersSource.currentText()
        urlMain = self.iersSourceURLs[sourceURL]

        source = "finals2000A.all"
        url = urlMain + source
        dest = self.app.mwGlob["dataDir"] / source
        self.msg.emit(1, "IERS", "Download", f"File. {source}")
        self.downloadPopup = DownloadPopup(self.mainW, url=url, dest=dest)
        self.downloadPopup.worker.signals.finished.connect(self.finishLoadFinalsFromSourceURLs)
        return True
