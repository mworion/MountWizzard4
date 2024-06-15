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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import logging

# external packages
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QListView

# local import
from logic.databaseProcessing.dataWriter import DataWriter
from gui.extWindows.downloadPopupW import DownloadPopup
from gui.extWindows.uploadPopupW import UploadPopup


class AstroObjects(QObject):
    """
    """
    log = logging.getLogger(__name__)

    dataLoaded = Signal()

    def __init__(self, window,
                 app, objectText, sourceUrls, uiObjectList,
                 uiSourceList, uiSourceGroup, processFunc):
        super().__init__()
        self.window = window
        self.app = app
        self.msg = app.msg
        self.dest = None
        self.objectText = objectText
        self.sourceUrls = sourceUrls
        self.uiObjectList = uiObjectList
        self.uiSourceList = uiSourceList
        self.uiSourceGroup = uiSourceGroup
        self.processFunc = processFunc

        self.objects = None
        self.uploadPopup = None
        self.downloadPopup = None
        self.tempDir = self.app.mwGlob['tempDir']
        self.dataDir = self.app.mwGlob['dataDir']
        self.loader = self.app.mount.obsSite.loader
        self.dbProc = DataWriter(self.app)
        self.buildSourceListDropdown()
        self.uiSourceList.currentIndexChanged.connect(self.loadSourceUrl)

    def buildSourceListDropdown(self):
        """
        """
        self.uiSourceList.clear()
        self.uiSourceList.setView(QListView())
        for name in self.sourceUrls.keys():
            self.uiSourceList.addItem(name)
        self.uiSourceList.setCurrentIndex(-1)

    def setAge(self, age):
        """
        """
        t = f'{self.objectText} data - age: {age:2.1f}d'
        self.uiSourceGroup.setTitle(t)

    def procSourceData(self):
        """
        """
        self.processFunc()
        self.dataLoaded.emit()

    def loadSourceUrl(self):
        """
        """
        self.objects = None
        key = self.uiSourceList.currentText()
        url = self.sourceUrls[key]['url']
        fileName = self.sourceUrls[key]['file']
        unzip = self.sourceUrls[key]['unzip']

        self.dest = os.path.normpath(f'{self.dataDir}/{fileName}')
        localSourceAvailable = os.path.isfile(self.dest)

        if localSourceAvailable:
            daysOld = self.loader.days_old(self.dest)
            self.setAge(daysOld)
            if daysOld < 1:
                self.procSourceData()
                self.log.info(f'{self.objectText} data loaded from local source')
                return

        self.setAge(0)
        self.msg.emit(1, self.objectText, 'Download', f'{url}')
        self.log.info(f'{self.objectText} data loaded from {url}')
        self.downloadPopup = DownloadPopup(self.window, url=url,
                                           dest=self.dest, unzip=unzip)
        self.downloadPopup.worker.signals.finished.connect(self.procSourceData)

    def setTableEntry(self, row, col, entry):
        """
        """
        self.ui.uiObjectList.setItem(row, col, entry)

    def finishProgObjects(self):
        """
        """
        if self.uploadPopup.returnValues['success']:
            self.msg.emit(1, self.objectText, 'Program', 'Successful uploaded')
        else:
            self.msg.emit(1, self.objectText, 'Program', 'Upload failed')

    def progObjects(self, objects):
        """
        """
        suc = self.dbProc.writeSatelliteTLE(
            objects, dataFilePath=self.tempDir)
        if not suc:
            self.msg.emit(2, self.objectText, 'Data error',
                          'Data could not be exported - stopping')
            return

        self.msg.emit(0, self.objectText, 'Program', 'Uploading to mount')
        url = self.app.mount.host[0]
        self.uploadPopup = UploadPopup(self, url=url, dataTypes=['tle'],
                                       dataFilePath=self.tempDir)
        self.uploadPopup.workerStatus.signals.finished.connect(
            self.finishProgObjects)

    def progGUI(self):
        """
        """
        source = self.ui.satelliteSource.currentText()
        self.msg.emit(1, 'TLE', 'Program', f'{source}')
        self.msg.emit(1, '', '', 'Exporting TLE data')

    def progObjectsSelected(self):
        """
        """
        self.progGUI()
        satSelectedIndexes = self.ui.listSatelliteNames.selectedIndexes()
        satSelected = []
        for entry in satSelectedIndexes:
            index = entry.row()
            satSelected.append(self.objects[index])
        self.progObjects(satSelected)

    def progObjectsFiltered(self):
        """
        """
        self.progGUI()
        filtered = self.satelliteFilter(self.objects)
        self.progObjects(filtered)

    def progObjectsFull(self):
        """
        """
        self.progGUI()
        self.progObjects(self.objects)
