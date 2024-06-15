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
        if not key:
            return
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
        self.downloadPopup = DownloadPopup(self.window,
                                           url=url,
                                           dest=self.dest,
                                           unzip=unzip)
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
        funcs = {
            'satellite': self.dbProc.writeSatelliteTLE,
            'asteroid': self.dbProc.writeAsteroidMPC,
            'comet': self.dbProc.writeCometMPC,
        }

        suc = funcs[self.objectText](objects, dataFilePath=self.tempDir)
        if not suc:
            self.msg.emit(2, self.objectText, 'Data error',
                          'Data could not be exported - stopping')
            return

        self.msg.emit(0, self.objectText, 'Program', 'Uploading to mount')
        url = self.app.mount.host[0]
        self.uploadPopup = UploadPopup(self.window,
                                       url=url,
                                       dataTypes=[self.objectText],
                                       dataFilePath=self.tempDir)
        self.uploadPopup.workerStatus.signals.finished.connect(
            self.finishProgObjects)

    def progGUI(self):
        """
        """
        source = self.uiSourceList.currentText()
        self.msg.emit(1, self.objectText, 'Program', f'{source}')
        self.msg.emit(1, '', '', 'Exporting data')

    def progSelected(self):
        """
        """
        self.progGUI()
        selectedItems = self.uiObjectList.selectedItems()
        selectedObjects = []
        for entry in selectedItems:
            if not entry.column() == 1:
                continue
            name = entry.text()
            selectedObjects.append(self.objects[name])
        self.progObjects(selectedObjects)

    def progFiltered(self):
        """
        """
        self.progGUI()
        filteredObjects = []
        for row in range(self.uiObjectList.model().rowCount()):
            entry = self.uiObjectList.model().index(row, 1)
            if self.uiObjectList.isIndexHidden(entry):
                continue
            name = entry.data()
            filteredObjects.append(self.objects[name])
        self.progObjects(filteredObjects)

    def progFull(self):
        """
        """
        self.progGUI()
        fullObjects = [self.objects[name] for name in self.objects]
        self.progObjects(fullObjects)
