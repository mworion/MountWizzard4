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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import gzip
import json
import shutil
import os

# external packages
import requests
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QListView

# local import
from base.tpool import Worker
from logic.automation.automationHelper import AutomationHelper


class MinorPlanetTime:
    """
    """

    signalProgress = pyqtSignal(object)

    def __init__(self):
        self.installPath = ''
        self.automationHelper = AutomationHelper(self.app)
        self.minorPlanets = dict()
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

        self.timeSourceURLs = {
            'FTP IERS': 'ftp://cddis.nasa.gov/products/iers',
        }

        self.ui.listMinorPlanetNames.doubleClicked.connect(self.progMinorPlanetToMount)
        self.ui.progMinorPlanetsFull.clicked.connect(self.progMinorPlanetsFull)
        self.ui.progMinorPlanetsFiltered.clicked.connect(self.progMinorPlanetsFiltered)
        self.ui.progEarthRotationData.clicked.connect(self.progEarthRotationDataToMount)
        self.ui.filterMinorPlanet.textChanged.connect(self.filterMinorPlanetNamesList)
        self.ui.minorPlanetSource.currentIndexChanged.connect(self.loadDataFromSourceURLs)
        self.ui.isOnline.stateChanged.connect(self.loadDataFromSourceURLs)
        self.signalProgress.connect(self.setProgress)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']

        self.ui.filterMinorPlanet.setText(config.get('filterMinorPlanet'))
        self.setupMinorPlanetSourceURLsDropDown()

        if self.app.automation:
            self.installPath = self.app.automation.installPath

        else:
            self.installPath = self.app.mwGlob['dataDir']

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']
        config['filterMinorPlanet'] = self.ui.filterMinorPlanet.text()

        return True

    def setupMinorPlanetSourceURLsDropDown(self):
        """
        setupMinorPlanetSourceURLsDropDown handles the dropdown list for the satellite data
        online sources. therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        self.ui.minorPlanetSource.clear()
        self.ui.minorPlanetSource.setView(QListView())
        for name in self.minorPlanetSourceURLs.keys():
            self.ui.minorPlanetSource.addItem(name)

        return True

    def filterMinorPlanetNamesList(self):
        """

        :return: true for test purpose
        """
        listMinorPlanet = self.ui.listMinorPlanetNames
        filterStr = self.ui.filterMinorPlanet.text()

        for row in range(listMinorPlanet.model().rowCount()):
            isFound = filterStr.lower() in listMinorPlanet.model().index(row).data().lower()
            isVisible = isFound or not filterStr

            if isVisible:
                listMinorPlanet.setRowHidden(row, False)

            else:
                listMinorPlanet.setRowHidden(row, True)

        return True

    @staticmethod
    def generateName(index, mp):

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

        return name

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

    def setProgress(self, progressPercent):
        """

        :param progressPercent:
        :return: True for test purpose
        """
        self.ui.downloadMinorPlanetProgress.setValue(progressPercent)
        return True

    def downloadFile(self, url, dest):
        """

        :param url:
        :param dest:
        :return:
        """

        if not os.path.dirname(dest):
            return False

        r = requests.get(url, stream=True, timeout=1)
        totalSizeBytes = int(r.headers.get('content-length', 0))

        with open(dest, 'wb') as f:
            for n, chunk in enumerate(r.iter_content(512)):
                progressPercent = int(n * 512 / totalSizeBytes * 100)
                self.signalProgress.emit(progressPercent)

                if chunk:
                    f.write(chunk)
            self.signalProgress.emit(100)

        return True

    @staticmethod
    def unzipFile(dest):
        """

        :param dest:
        :return: True for test purpose
        """
        with gzip.open(dest, 'rb') as f_in:
            with open(dest[:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        return True

    def loadDataFromSourceURLsWorker(self, source='', isOnline=False):
        """

        :return: success
        """

        if not source:
            return False

        url = self.mpcPrefix + self.minorPlanetSourceURLs[source]
        dest = self.app.mwGlob['dataDir'] + '/' + self.minorPlanetSourceURLs[source]

        if isOnline:
            self.app.message.emit(f'Download data for:   [{source}]', 1)
            self.downloadFile(url, dest)
            self.unzipFile(dest)

        if not os.path.isfile(dest[:-3]):
            self.app.message.emit(f'No data file for:    [{source}]', 2)
            return False

        with open(dest[:-3]) as inFile:
            self.minorPlanets = json.load(inFile)

        self.app.message.emit(f'Data loaded for:     [{source}]', 1)

        return True

    def loadDataFromSourceURLs(self):
        """

        :return: success
        """

        source = self.ui.minorPlanetSource.currentText()

        if source not in self.minorPlanetSourceURLs:
            return False

        if source == 'Please select':
            return False

        self.ui.listMinorPlanetNames.clear()
        self.ui.downloadMinorPlanetProgress.setValue(0)
        isOnline = self.ui.isOnline.isChecked()
        worker = Worker(self.loadDataFromSourceURLsWorker,
                        source=source,
                        isOnline=isOnline)
        worker.signals.finished.connect(self.setupMinorPlanetNameList)
        self.threadPool.start(worker)

        return True

    def progEarthRotationDataToMount(self):
        """

        :return: success
        """

        text = 'Should \n\n[Earth Rotation Data]\n\nbe programmed to mount ?'
        suc = self.messageDialog(self, 'Program with QCI Updater', text)

        if not suc:
            return False

        self.app.message.emit('Program to mount:    [earth rotation data]', 1)
        self.app.message.emit('Writing files: finals.data, tai-utc.dat', 0)

        suc = self.automationHelper.writeEarthRotationData(self.installPath)

        if not suc:
            self.app.message.emit('Data could not be copied - stopping', 2)
            return False

        if not self.app.automation:
            self.app.message.emit('Not running windows, no updater available', 2)
            return False

        self.app.message.emit('Uploading to mount', 0)
        suc = self.app.automation.uploadEarthRotationData()

        if not suc:
            self.app.message.emit('Uploading error', 2)
            return False

        self.app.message.emit('Programming success', 1)

        return True

    def progMinorPlanetToMount(self):
        """

        :return: success
        """

        source = self.ui.listMinorPlanetNames.currentItem().text()
        number = int(source.split(':')[0])
        mpc = [self.minorPlanets[number]]
        isComet = self.ui.minorPlanetSource.currentText().startswith('Comet')
        isAsteroid = not isComet

        text = f'Should \n\n[{source}]\n\nbe programmed to mount ?'
        suc = self.messageDialog(self, 'Program with QCI Updater', text)

        if not suc:
            return False

        self.app.message.emit(f'Program to mount:    [{source}]', 1)
        self.app.message.emit('Exporting MPC data', 0)

        if isComet:
            suc = self.automationHelper.writeCometMPC(mpc, self.installPath)

        if isAsteroid:
            suc = self.automationHelper.writeAsteroidMPC(mpc, self.installPath)

        if not suc:
            self.app.message.emit('Data could not be exported - stopping', 2)
            return False

        if not self.app.automation:
            self.app.message.emit('Not running windows, no updater available', 2)
            return False

        self.app.message.emit('Uploading to mount', 0)
        suc = self.app.automation.uploadMPCData(comets=isComet)

        if not suc:
            self.app.message.emit('Uploading error', 2)

        self.app.message.emit('Programming success', 1)

        return suc

    def progMinorPlanetsFiltered(self):
        """

        :return: success
        """

        source = self.ui.minorPlanetSource.currentText()
        isComet = self.ui.minorPlanetSource.currentText().startswith('Comet')
        isAsteroid = not isComet

        if source.startswith('Please'):
            return False

        text = f'Should filtered database\n\n[{source}]\n\nbe programmed to mount ?'
        suc = self.messageDialog(self, 'Program with QCI Updater', text)

        if not suc:
            return False

        self.app.message.emit(f'Program database:    [{source}]', 1)
        self.app.message.emit('Exporting MPC data', 0)

        filterStr = self.ui.filterMinorPlanet.text().lower()

        filtered = list()
        for index, mp in enumerate(self.minorPlanets):
            text = self.generateName(index, mp)

            if filterStr not in text:
                continue

            filtered.append(mp)

        if isComet:
            suc = self.automationHelper.writeCometMPC(filtered, self.installPath)

        if isAsteroid:
            suc = self.automationHelper.writeAsteroidMPC(filtered, self.installPath)

        if not suc:
            self.app.message.emit('Data could not be exported - stopping', 2)
            return False

        if not self.app.automation:
            self.app.message.emit('Not running windows, no updater available', 2)
            return False

        self.app.message.emit('Uploading to mount', 0)
        suc = self.app.automation.uploadMPCData(comets=isComet)

        if not suc:
            self.app.message.emit('Uploading error', 2)

        self.app.message.emit('Programming success', 1)

        return suc

    def progMinorPlanetsFull(self):
        """

        :return: success
        """

        source = self.ui.minorPlanetSource.currentText()
        isComet = self.ui.minorPlanetSource.currentText().startswith('Comet')
        isAsteroid = not isComet

        if source.startswith('Please'):
            return False

        text = f'Should full database\n\n[{source}]\n\nbe programmed to mount ?'
        suc = self.messageDialog(self, 'Program with QCI Updater', text)

        if not suc:
            return False

        self.app.message.emit(f'Program database:    [{source}]', 1)
        self.app.message.emit('Exporting MPC data', 0)

        if isComet:
            suc = self.automationHelper.writeCometMPC(self.minorPlanets, self.installPath)

        if isAsteroid:
            suc = self.automationHelper.writeAsteroidMPC(self.minorPlanets, self.installPath)

        if not suc:
            self.app.message.emit('Data could not be exported - stopping', 2)
            return False

        if not self.app.automation:
            self.app.message.emit('Not running windows, no updater available', 2)
            return False

        self.app.message.emit('Uploading to mount', 0)
        suc = self.app.automation.uploadMPCData(comets=isComet)

        if not suc:
            self.app.message.emit('Uploading error', 2)

        self.app.message.emit('Programming success', 1)

        return suc
