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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtWidgets import QListView

# local import
from gui.extWindows.downloadPopupW import DownloadPopup


class IERSTime:
    """
    """

    def __init__(self):
        self.installPath = ''

        self.iersSourceURLs = {
            'Datacenter from IERS': 'https://datacenter.iers.org/products/eop/rapid/standard/',
            'Maia from usno.navy.mil': 'https://maia.usno.navy.mil/ser7/',
        }

        self.ui.progEarthRotationData.clicked.connect(self.startProgEarthRotationDataToMount)
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
        if not self.app.automation:
            self.installPath = self.app.mwGlob['dataDir']
        elif self.app.automation.installPath:
            self.installPath = self.app.automation.installPath
        else:
            self.installPath = self.app.mwGlob['dataDir']
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

    def progEarthRotationGUI(self):
        """
        :return:
        """
        updaterApp = self.checkUpdaterOK()
        if not updaterApp:
            return ''

        question = '<b>Earth Rotation Data programming</b>'
        question += '<br><br>The 10micron updater will be used.'
        question += '<br>Would you like to start?<br>'
        question += f'<br><i><font color={self.M_YELLOW}>'
        question += 'Please wait until updater is closed!</font></i>'
        suc = self.messageDialog(self, 'Program with 10micron Updater', question)
        if not suc:
            return ''

        self.msg.emit(1, 'IERS', 'Program', 'Earth rotation data')
        self.msg.emit(1, '', '', 'finals.data, tai-utc.dat')
        return updaterApp

    def progEarthRotationData(self):
        """
        :return: success
        """
        updaterApp = self.progEarthRotationGUI()
        if not updaterApp:
            return False

        suc = self.databaseProcessing.writeEarthRotationData(self.installPath,
                                                             updaterApp)
        if not suc:
            self.msg.emit(2, 'IERS', 'Data error',
                          'Data could not be exported - stopping')
            return False

        self.msg.emit(0, 'IERS', 'Program', 'Uploading to mount')
        suc = self.app.automation.uploadEarthRotationData()
        if not suc:
            self.msg.emit(2, 'IERS', 'Program error',
                          'Uploading error but files available')
        else:
            self.msg.emit(1, 'IERS', 'Program', 'Successful uploaded')
        return suc

    def startProgEarthRotationDataToMount(self):
        """
        :return:
        """
        isOnline = self.ui.isOnline.isChecked()
        if not isOnline:
            return False

        sourceURL = self.ui.iersSource.currentText()
        urlMain = self.iersSourceURLs[sourceURL]

        source = 'finals.data'
        url = urlMain + source
        dest = self.app.mwGlob['dataDir'] + '/' + source
        self.msg.emit(1, 'IERS', 'Download', f'{source}')
        DownloadPopup(self, url=url, dest=dest, unzip=False,
                      callBack=self.progEarthRotationData)
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
