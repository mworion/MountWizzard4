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

# external packages
from PyQt6.QtWidgets import QListView

# local import
from gui.extWindows.downloadPopupW import DownloadPopup
from logic.databaseProcessing.dataWriter import DataWriter


class IERSTime:
    """
    """

    def __init__(self):
        self.tempDir = self.app.mwGlob['tempDir']
        self.databaseProcessing = DataWriter(self.app)
        self.iersSourceURLs = {
            'Datacenter from IERS': 'https://datacenter.iers.org/products/eop/rapid/standard/',
            'Maia from usno.navy.mil': 'https://maia.usno.navy.mil/ser7/',
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
        config = self.app.config['mainW']
        self.setupIERSSourceURLsDropDown()
        self.ui.iersSource.setCurrentIndex(config.get('iersSource', 0))
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['iersSource'] = self.ui.iersSource.currentIndex()
        return True

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

    def progEarthRotationData(self):
        """
        :return: success
        """
        self.msg.emit(1, 'IERS', 'Program', 'Earth rotation data')
        self.msg.emit(1, '', '', 'finals.data, CDFLeapSeconds.txt')

        suc = self.databaseProcessing.writeEarthRotationData(self.tempDir)
        if not suc:
            self.msg.emit(2, 'IERS', 'Data error',
                          'Data could not be exported - stopping')
            return False

        self.msg.emit(0, 'IERS', 'Program', 'Uploading to mount')
        suc = self.databaseProcessing.progDataToMount(
            dataTypes=['leapsec', 'finalsdata'],
            dataFilePath=self.tempDir)
        if not suc:
            self.msg.emit(2, 'IERS', 'Program error',
                          'Uploading error but files available')
        else:
            self.msg.emit(1, 'IERS', 'Program', 'Successful uploaded')
        return suc

    def loadTimeDataFromSourceURLs(self):
        """
        :return: success
        """
        isOnline = self.ui.isOnline.isChecked()
        if not isOnline:
            return False

        sourceURL = self.ui.iersSource.currentText()
        urlMain = self.iersSourceURLs[sourceURL]

        source = 'finals2000A.all'
        url = urlMain + source
        dest = self.app.mwGlob['dataDir'] + '/' + source
        self.msg.emit(1, 'IERS', 'Download', f'{source}')
        DownloadPopup(self, url=url, dest=dest, unzip=False)

        source = 'finals.data'
        url = urlMain + source
        dest = self.app.mwGlob['dataDir'] + '/' + source
        self.msg.emit(1, 'IERS', 'Download', f'{source}')
        DownloadPopup(self, url=url, dest=dest, unzip=False)
        return True
