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
from PyQt5.QtWidgets import QListView, QMessageBox

# local import
from base.tpool import Worker


class MinorPlanetTime:
    """
    the MinorPlanetTime window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.minorPlanets = dict()
        self.minorPlanet = None
        self.listMinorPlanetNamesProxy = None

        self.mpcPrefix = 'https://www.minorplanetcenter.net/Extended_Files/'
        self.minorPlanetSourceURLs = {
            'Please select': '',
            'Comets Current': 'cometels.json.gz',
            'Asteroids MPC5000 (large! >100 MB)': 'mpcorb_extended.json.gz',
            'Asteroids Near Earth Position': 'nea_extended.json.gz',
            'Asteroids Potential Hazardous': 'pha_extended.json.gz',
            'Asteroids TNO, Centaurus, SDO': 'distant_extended.json.gz',
            'Asteroids Unusual e>0.5 or q>6 au': 'unusual_extended.dat.gz',
        }

        self.timeSourceURLs = {
            'FTP IERS': 'ftp://cddis.nasa.gov/products/iers',
        }

        self.ui.listMinorPlanetNames.doubleClicked.connect(self.progMinorPlanetToMount)
        self.ui.progMinorPlanetsFull.clicked.connect(self.progMinorPlanetsFull)
        self.ui.progEarthRotationData.clicked.connect(self.progEarthRotationDataToMount)
        self.ui.filterMinorPlanet.textChanged.connect(self.filterMinorPlanetNamesList)
        self.ui.minorPlanetSource.currentIndexChanged.connect(
            self.loadMinorPlanetDataFromSourceURLs)
        self.ui.isOnline.stateChanged.connect(self.loadMinorPlanetDataFromSourceURLs)

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

    def setupAsteroidSourceURLsDropDown(self):
        """
        setupAsteroidSourceURLsDropDown handles the dropdown list for the satellite data
        online sources. therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        self.ui.asteroidSource.clear()
        self.ui.asteroidSource.setView(QListView())
        for name in self.asteroidSourceURLs.keys():
            self.ui.asteroidSource.addItem(name)

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

    def setupMinorPlanetNameList(self):
        """

        :return: success for test
        """

        self.ui.listMinorPlanetNames.clear()
        for index, mp in enumerate(self.minorPlanets):
            if 'Designation_and_name' in mp:
                text = f'{index:5d}: {mp["Designation_and_name"]}'

            elif 'Name' in mp and 'Principal_desig' in mp:
                text = f'{index:5d}: {mp["Principal_desig"]} - {mp["Name"]} {mp["Number"]}'

            elif 'Principal_desig' in mp:
                text = f'{index:5d}: {mp["Principal_desig"]}'

            elif 'Name' in mp:
                text = f'{index:5d}: {mp["Name"]} {mp["Number"]}'

            else:
                print(mp)
                continue

            self.ui.listMinorPlanetNames.addItem(text)

        self.ui.listMinorPlanetNames.sortItems()
        self.ui.listMinorPlanetNames.update()
        self.filterMinorPlanetNamesList()

        return True

    def downloadFile(self, source, url, dest):
        """

        :param source:
        :param url:
        :param dest:
        :return:
        """
        self.app.message.emit(f'Download data from:  [{source}]', 0)

        r = requests.get(url, stream=True)
        with open(dest, 'wb') as f:
            for n, chunk in enumerate(r.iter_content(128 * 1024)):
                if chunk:
                    f.write(chunk)

    @staticmethod
    def unzipFile(dest):
        with gzip.open(dest, 'rb') as f_in:
            with open(dest[:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def loadMinorPlanetDataFromSourceURLsWorker(self, source='', isOnline=False):
        """

        :return: success
        """

        if not source:
            return False

        url = self.mpcPrefix + self.minorPlanetSourceURLs[source]
        dest = self.app.mwGlob['dataDir'] + '/' + self.minorPlanetSourceURLs[source]

        self.ui.listMinorPlanetNames.clear()

        if isOnline:
            self.downloadFile(source, url, dest)
            self.unzipFile(dest)

        if not os.path.isfile(dest[:-3]):
            return False

        with open(dest[:-3]) as inFile:
            self.minorPlanets = json.load(inFile)

        self.app.message.emit(f'Data loaded for:     [{source}]', 0)

        return True

    def loadMinorPlanetDataFromSourceURLs(self):
        """

        :return: success
        """

        source = self.ui.minorPlanetSource.currentText()

        if source not in self.minorPlanetSourceURLs:
            return False

        if source == 'Please select':
            return False

        isOnline = self.ui.isOnline.isChecked()
        worker = Worker(self.loadMinorPlanetDataFromSourceURLsWorker,
                        source=source,
                        isOnline=isOnline)
        worker.signals.finished.connect(self.setupMinorPlanetNameList)
        self.threadPool.start(worker)

        return True

    def programDialog(self, question):
        """

        :param question:
        :return: OK
        """

        msg = QMessageBox
        reply = msg.question(self, 'Program with QCI Updater', question, msg.Yes | msg.No,
                             msg.No)

        if reply != msg.Yes:
            return False

        else:
            return True

    def progEarthRotationDataToMount(self):
        """

        :return: success
        """

        text = 'Should \n\n[Earth Rotation Data]\n\nbe programmed to mount ?'
        suc = self.programDialog(text)

        if not suc:
            return False

        self.app.message.emit('Program to mount:    [earth rotation data]', 1)
        self.app.message.emit('Copy files: finals.data, tai-utc.dat', 0)

        if not self.app.automation:
            self.app.message.emit('Not running windows, no updater available', 2)
            return False

        suc = self.app.automation.writeEarthRotationData()

        if not suc:
            self.app.message.emit('Data could not be copied - stopping', 2)
            return False

        self.app.message.emit('Uploading to mount', 0)
        suc = self.app.automation.uploadEarthRotationData()

        if not suc:
            self.app.message.emit('Uploading error', 2)

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
        suc = self.programDialog(text)

        if not suc:
            return False

        if not self.app.automation:
            self.app.message.emit('Not running windows, no updater available', 2)
            return False

        self.app.message.emit(f'Program to mount:    [{source}]', 1)
        self.app.message.emit('Exporting MPC data', 0)

        if isComet:
            suc = self.app.automation.writeCometMPC(mpc)

        if isAsteroid:
            suc = self.app.automation.writeAsteroidMPC(mpc)

        if not suc:
            self.app.message.emit('Data could not be exported - stopping', 2)
            return False

        self.app.message.emit('Uploading to mount', 0)
        suc = self.app.automation.uploadMPCData(comets=isComet)

        if not suc:
            self.app.message.emit('Uploading error', 2)

        self.app.message.emit('Programming success', 1)

        return True

    def progMinorPlanetsFull(self):
        """

        :return: success
        """

        source = self.ui.minorPlanetSource.currentText()
        isComet = self.ui.minorPlanetSource.currentText().startswith('Comet')
        isAsteroid = not isComet

        text = f'Should\n\n[{source}]\n\n be programmed to mount ?'
        suc = self.programDialog(text)

        if not suc:
            return False

        if not self.app.automation:
            self.app.message.emit('Not running windows, no updater available', 2)
            return False

        self.app.message.emit(f'Program database:    [{source}]', 1)
        self.app.message.emit('Exporting MPC data', 0)

        if isComet:
            suc = self.app.automation.writeCometMPC(self.minorPlanets)

        if isAsteroid:
            suc = self.app.automation.writeAsteroidMPC(self.minorPlanets)

        if not suc:
            self.app.message.emit('Data could not be exported - stopping', 2)
            return False

        self.app.message.emit('Uploading to mount', 0)
        suc = self.app.automation.uploadMPCData(comets=isComet)

        if not suc:
            self.app.message.emit('Uploading error', 2)

        self.app.message.emit('Programming success', 1)

        return True
