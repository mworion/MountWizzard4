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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import json
import os

# external packages
from PyQt5.QtWidgets import QListView

# local import
from logic.databaseProcessing.dataWriter import DataWriter
from gui.extWindows.downloadPopupW import DownloadPopup


class MinorPlanetTime:
    """
    """

    def __init__(self):
        self.installPath = ''
        self.databaseProcessing = DataWriter(self.app)
        self.minorPlanets = {}
        self.minorPlanet = None
        self.listMinorPlanetNamesProxy = None

        self.mpcPrefix = 'https://www.minorplanetcenter.net/Extended_Files/'
        self.minorPlanetSourceURLs = {
            'Please select': '',
            'Comets Current': 'cometels.json.gz',
            # 'Asteroids MPC5000 (large! >100 MB)': 'mpcorb_extended.json.gz',
            'Asteroids Daily': 'daily_extended.json.gz',
            'Asteroids Near Earth Position': 'nea_extended.json.gz',
            'Asteroids Potential Hazardous': 'pha_extended.json.gz',
            'Asteroids TNO, Centaurus, SDO': 'distant_extended.json.gz',
            'Asteroids Unusual e>0.5 or q>6 au': 'unusual_extended.json.gz',
        }

        self.iersSourceURLs = {
            'Datacenter from IERS': 'https://datacenter.iers.org/data/8/',
            'Maia from usno.navy.mil': 'https://maia.usno.navy.mil/ser7',
        }

        self.ui.listMinorPlanetNames.doubleClicked.connect(self.progMinorPlanetsSingle)
        self.ui.progMinorPlanetsFull.clicked.connect(self.progMinorPlanetsFull)
        self.ui.progMinorPlanetsFiltered.clicked.connect(self.progMinorPlanetsFiltered)
        self.ui.progEarthRotationData.clicked.connect(self.startProgEarthRotationDataToMount)
        self.ui.downloadIERS.clicked.connect(self.loadTimeDataFromSourceURLs)
        self.ui.filterMinorPlanet.textChanged.connect(self.filterMinorPlanetNamesList)
        self.ui.minorPlanetSource.currentIndexChanged.connect(self.loadMPCDataFromSourceURLs)
        self.ui.isOnline.stateChanged.connect(self.loadMPCDataFromSourceURLs)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to
        the gui elements. if some initialisations have to be proceeded with the
        loaded persistent data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.filterMinorPlanet.setText(config.get('filterMinorPlanet'))
        self.setupMinorPlanetSourceURLsDropDown()
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
        config['filterMinorPlanet'] = self.ui.filterMinorPlanet.text()
        config['iersSource'] = self.ui.iersSource.currentIndex()
        return True

    def setupMinorPlanetSourceURLsDropDown(self):
        """
        setupMinorPlanetSourceURLsDropDown handles the dropdown list for the
        satellite data online sources. therefore we add the necessary entries to
        populate the list.

        :return: success for test
        """
        self.ui.minorPlanetSource.clear()
        self.ui.minorPlanetSource.setView(QListView())
        for name in self.minorPlanetSourceURLs:
            self.ui.minorPlanetSource.addItem(name)
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

    def filterMinorPlanetNamesList(self):
        """
        :return: true for test purpose
        """
        listMinorPlanet = self.ui.listMinorPlanetNames
        filterStr = self.ui.filterMinorPlanet.text()
        for row in range(listMinorPlanet.model().rowCount()):
            listItemText = listMinorPlanet.model().index(row).data().lower()
            isFound = filterStr.lower() in listItemText
            isVisible = isFound or not filterStr
            if isVisible:
                listMinorPlanet.setRowHidden(row, False)

            else:
                listMinorPlanet.setRowHidden(row, True)
        return True

    @staticmethod
    def generateName(index, mp):
        """
        :param index:
        :param mp:
        :return:
        """
        if 'Designation_and_name' in mp:
            name = f'{index:5d}: {mp["Designation_and_name"]}'
        elif 'Name' in mp and 'Principal_desig' in mp:
            name = f'{index:5d}: {mp["Principal_desig"]} - {mp["Name"]} {mp["Number"]}'
        elif 'Principal_desig' in mp:
            name = f'{index:5d}: {mp["Principal_desig"]}'
        elif 'Name' in mp:
            name = f'{index:5d}: {mp["Name"]} {mp["Number"]}'
        else:
            name = ''

        return name[:40]

    def setupMinorPlanetNameList(self):
        """
        :return: success for test
        """
        self.ui.listMinorPlanetNames.clear()
        for index, mp in enumerate(self.minorPlanets):
            text = self.generateName(index, mp)
            if not text:
                continue

            self.ui.listMinorPlanetNames.addItem(text)

        self.ui.listMinorPlanetNames.sortItems()
        self.ui.listMinorPlanetNames.update()
        self.filterMinorPlanetNamesList()
        return True

    def processSourceData(self):
        """
        :return:
        """
        source = self.ui.minorPlanetSource.currentText()
        dest = self.app.mwGlob['dataDir'] + '/' + self.minorPlanetSourceURLs[source]
        destUnzip = dest[:-3]

        if not os.path.isfile(destUnzip):
            self.msg.emit(2, 'MPC', 'Data error', f'{source}')
            return False

        with open(destUnzip) as inFile:
            try:
                self.minorPlanets = json.load(inFile)
            except Exception:
                self.minorPlanets = {}

            self.msg.emit(1, 'MPC', 'Data loaded', f'{source}')

        self.setupMinorPlanetNameList()
        return True

    def loadMPCDataFromSourceURLs(self):
        """
        :return: success
        """
        source = self.ui.minorPlanetSource.currentText()
        if source not in self.minorPlanetSourceURLs:
            return False
        if source == 'Please select':
            return False

        self.ui.listMinorPlanetNames.clear()

        url = self.mpcPrefix + self.minorPlanetSourceURLs[source]
        dest = self.app.mwGlob['dataDir'] + '/' + self.minorPlanetSourceURLs[source]

        isOnline = self.ui.isOnline.isChecked()
        if isOnline:
            self.msg.emit(1, 'MPC', 'Download', f'{source}')
            DownloadPopup(self, url=url, dest=dest, callBack=self.processSourceData)
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
        if isOnline:
            source = 'finals.data'
            url = 'https://datacenter.iers.org/data/8/' + source
            dest = self.app.mwGlob['dataDir'] + '/' + source
            self.msg.emit(1, 'IERS', 'Download', f'{source}')
            DownloadPopup(self, url=url, dest=dest, unzip=False,
                          callBack=self.progEarthRotationData)
        else:
            self.progEarthRotationData()
        return True

    def loadTimeDataFromSourceURLs(self):
        """
        :return: success
        """
        isOnline = self.ui.isOnline.isChecked()
        if not isOnline:
            return False

        source = 'finals2000A.all'
        url = 'https://datacenter.iers.org/data/9/' + source
        dest = self.app.mwGlob['dataDir'] + '/' + source
        self.msg.emit(1, 'IERS', 'Download', f'{source}')
        DownloadPopup(self, url=url, dest=dest, unzip=False)

        source = 'finals.data'
        url = 'https://datacenter.iers.org/data/8/' + source
        dest = self.app.mwGlob['dataDir'] + '/' + source
        self.msg.emit(1, 'IERS', 'Download', f'{source}')
        DownloadPopup(self, url=url, dest=dest, unzip=False)
        return True

    def progMinorPlanets(self, mpc):
        """
        :param mpc:
        :return:
        """
        isComet = self.ui.minorPlanetSource.currentText().startswith('Comet')
        if isComet:
            suc = self.databaseProcessing.writeCometMPC(mpc, self.installPath)
        else:
            suc = self.databaseProcessing.writeAsteroidMPC(mpc, self.installPath)

        if not suc:
            self.msg.emit(2, 'MPC', 'Data',
                          'Data could not be exported - stopping')
            return False

        self.msg.emit(0, 'MPC', 'Program', 'Uploading to mount')
        suc = self.app.automation.uploadMPCData(comets=isComet)
        if not suc:
            self.msg.emit(2, 'MPC', 'Program error',
                          'Uploading error but files available')
        else:
            self.msg.emit(1, 'MPC', 'Program', 'Successful uploaded')
        return suc

    def mpcFilter(self, mpcRaw):
        """
        :param mpcRaw:
        :return:
        """
        filterStr = self.ui.filterMinorPlanet.text().lower()
        filtered = list()
        for index, mp in enumerate(mpcRaw):
            text = self.generateName(index, mp)

            if filterStr.lower() not in text.lower():
                continue

            filtered.append(mp)
        return filtered

    def mpcGUI(self):
        """
        :return:
        """
        source = self.ui.minorPlanetSource.currentText()
        if source.startswith('Please'):
            return False

        suc = self.checkUpdaterOK()
        if not suc:
            return False

        question = '<b>Filtered MPC Data programming</b>'
        question += '<br><br>The 10micron updater will be used.'
        question += '<br>Selected source: '
        question += f'<font color={self.M_BLUE}>{source}</font>'
        question += '<br>Would you like to start?<br>'
        question += f'<br><i><font color={self.M_YELLOW}>'
        question += 'Please wait until updater is closed!</font></i>'
        suc = self.messageDialog(self, 'Program with 10micron Updater', question)
        if not suc:
            return False

        self.msg.emit(1, 'MPC', 'Program', f'{source}')
        self.msg.emit(1, '', '', 'Exporting MPC data')
        return True

    def progMinorPlanetsSingle(self):
        """
        :return: success
        """
        suc = self.mpcGUI()
        if not suc:
            return False

        source = self.ui.listMinorPlanetNames.currentItem().text()
        number = int(source.split(':')[0])
        mpcFiltered = [self.minorPlanets[number]]
        self.progMinorPlanets(mpcFiltered)
        return True

    def progMinorPlanetsFiltered(self):
        """
        :return: success
        """
        suc = self.mpcGUI()
        if not suc:
            return False

        mpcFiltered = self.mpcFilter(self.minorPlanets)
        self.progMinorPlanets(mpcFiltered)
        return True

    def progMinorPlanetsFull(self):
        """
        :return: success
        """
        suc = self.mpcGUI()
        if not suc:
            return False

        self.progMinorPlanets(self.minorPlanets)
        return True
