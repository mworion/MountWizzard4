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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os

# external packages
import PyQt5
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtWidgets import QApplication, QAbstractItemView
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView
import numpy as np
from sgp4.exporter import export_tle
from skyfield import almanac

# local import
from base.tpool import Worker
from logic.databaseProcessing.dataWriter import DataWriter


class SatSearch(object):
    """
    Satellite has five parts:
    1. When mount is connected it will automatically search for a stored
    satellite in the mount. If so, the satellite reference is fetched, the data
    is read out of the TLE database, the orbit data are calculate and the gui is
    populated. If the satellite window is open, data will be sent to gui drawing
    as well.

    2. When a satellite is chosen from a drop down list by double click, it
    selects the corresponding TLE data, programs is to the mount and follows the
    steps of 1.

    3. If a new satellite database is selected, is downloads the database and
    updates the drop down menus with the satellite entries.

    4. If a satellite is to be tracked, it takes the satellite TLE data, the user
    gui input and calculates the satellite trajectory. In case of built in
    command it only pushes the command if explicit, it calculates the trajectory
    with alt/az positions and programs it to the mount. afterward a tracking
    could be started.

    5. If a mount upload is chosen (only available on windows) if prepares the
    data in the necessary mount format and calls the updater.
    """
    sigSetSatTableEntry = pyqtSignal(int, int, object)

    def __init__(self):
        self.satellites = dict()
        self.satellite = None
        self.satSourceValid = False
        self.satTableBaseValid = False
        self.satTableDynamicValid = False
        self.databaseProcessing = DataWriter(self.app)
        self.installPath = ''

        baseUrl = 'http://www.celestrak.com/NORAD/elements/'
        self.satelliteSourceURLs = {
            '100 brightest': baseUrl + 'visual.txt',
            'Active': baseUrl + 'active.txt',
            'Space Stations': baseUrl + 'stations.txt',
            'NOAA': baseUrl + 'noaa.txt',
            'GEOS': baseUrl + 'goes.txt',
            'Weather': baseUrl + 'weather.txt',
            'Earth Resources': baseUrl + 'resource.txt',
            'TDRSS Tracking & Data Relay': baseUrl + 'tdrss.txt',
            'ARGOS': baseUrl + 'argos.txt',
            'Amateur Radio': baseUrl + 'amateur.txt',
            'Space & Earth Science': baseUrl + 'science.txt',
            'Engineering': baseUrl + 'engineering.txt',
            'Last 30 days launch': baseUrl + 'tle-new.txt',
        }

        self.passUI = {
            0: {'rise': self.ui.satRise_1,
                'culminate': self.ui.satCulminate_1,
                'settle': self.ui.satSettle_1,
                'flip': self.ui.satFlip_1,
                'date': self.ui.satDate_1},
            1: {'rise': self.ui.satRise_2,
                'culminate': self.ui.satCulminate_2,
                'settle': self.ui.satSettle_2,
                'flip': self.ui.satFlip_2,
                'date': self.ui.satDate_2},
            2: {'rise': self.ui.satRise_3,
                'culminate': self.ui.satCulminate_3,
                'settle': self.ui.satSettle_3,
                'flip': self.ui.satFlip_3,
                'date': self.ui.satDate_3}
        }
        self.satOrbits = dict()

        msig = self.app.mount.signals
        msig.firmwareDone.connect(self.enableGuiFunctions)

        self.ui.progSatellitesFull.clicked.connect(self.progSatellitesFull)
        self.ui.progSatellitesFiltered.clicked.connect(self.progSatellitesFiltered)
        self.ui.listSatelliteNames.doubleClicked.connect(self.chooseSatellite)
        self.ui.satelliteSource.activated.connect(self.loadDataFromSourceURLs)
        self.ui.filterSatellite.textChanged.connect(self.filterSatelliteNamesList)
        self.ui.satIsSunlit.clicked.connect(self.filterSatelliteNamesList)
        self.ui.satIsUp.clicked.connect(self.filterSatelliteNamesList)
        self.sigSetSatTableEntry.connect(self.setSatTableEntry)

        self.app.update1s.connect(self.satCalcDynamicTable)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.satelliteSource.clear()
        self.ui.satelliteSource.setView(PyQt5.QtWidgets.QListView())
        for name in self.satelliteSourceURLs.keys():
            self.ui.satelliteSource.addItem(name)
        self.ui.satelliteSource.setCurrentIndex(config.get('satelliteSource', 0))
        self.loadDataFromSourceURLs()

        self.ui.filterSatellite.setText(config.get('filterSatellite'))
        self.ui.switchToTrackingTab.setChecked(config.get('switchToTrackingTab',
                                                          False))
        self.ui.satCyclicUpdates.setChecked(config.get('satCyclicUpdates', False))
        self.ui.satIsSunlit.setChecked(config.get('satIsSunlit', False))
        self.ui.satIsUp.setChecked(config.get('satIsUp', False))
        self.ui.satUpTimeWindow.setValue(config.get('satUpTimeWindow', 2))
        self.ui.satAltitudeMin.setValue(config.get('satAltitudeMin', 30))

        if not self.app.automation:
            self.installPath = self.app.mwGlob['dataDir']
        elif self.app.automation.installPath:
            self.installPath = self.app.automation.installPath
        else:
            self.installPath = self.app.mwGlob['dataDir']
        return True

    def storeConfig(self):
        """
        :return:
        """
        config = self.app.config['mainW']
        config['satelliteSource'] = self.ui.satelliteSource.currentIndex()
        config['filterSatellite'] = self.ui.filterSatellite.text()
        config['switchToTrackingTab'] = self.ui.switchToTrackingTab.isChecked()
        config['satCyclicUpdates'] = self.ui.satCyclicUpdates.isChecked()
        config['satIsSunlit'] = self.ui.satIsSunlit.isChecked()
        config['satIsUp'] = self.ui.satIsUp.isChecked()
        config['satUpTimeWindow'] = self.ui.satUpTimeWindow.value()
        config['satAltitudeMin'] = self.ui.satAltitudeMin.value()
        return True

    def enableGuiFunctions(self):
        """
        :return:
        """
        useInternal = self.ui.useInternalSatCalc.isChecked()
        availableInternal = self.app.mount.firmware.checkNewer(21699)
        if availableInternal is None:
            return False

        progAvailable = availableInternal and useInternal
        self.ui.trackingSim.setEnabled(progAvailable)
        self.ui.trajectoryProgress.setEnabled(progAvailable)
        self.ui.progTrajectory.setEnabled(progAvailable)
        return True

    def chooseSatellite(self):
        """
        :return: True for test purpose
        """
        satTab = self.ui.listSatelliteNames
        satName = satTab.item(satTab.currentRow(), 1).text()
        if self.app.deviceStat['mount']:
            self.programDataToMount(satName=satName)
        else:
            self.extractSatelliteData(satName=satName)
            self.showSatPasses()
        if self.ui.switchToTrackingTab.isChecked():
            self.ui.satTabWidget.setCurrentIndex(1)
        return True

    @staticmethod
    def findSunlit(sat, ephemeris, tEvent):
        """
        :param sat:
        :param ephemeris:
        :param tEvent:
        :return:
        """
        sunlit = sat.at(tEvent).is_sunlit(ephemeris)
        return sunlit

    @staticmethod
    def findSatUp(sat, loc, tStart, tEnd, alt):
        """
        :param sat:
        :param loc:
        :param tStart:
        :param tEnd:
        :param alt:
        :return:
        """
        t, events = sat.find_events(loc, tStart, tEnd, altitude_degrees=alt)
        if 1 in events:
            return True, t[np.equal(events, 1)]
        else:
            return False, []

    @staticmethod
    def findRangeRate(sat, loc, tEv):
        """
        :param sat:
        :param loc:
        :param tEv:
        :return:
        """
        pos = (sat - loc).at(tEv)
        _, _, satRange, latRate, lonRate, radRate = pos.frame_latlon_and_rates(loc)
        return (satRange.km,
                radRate.km_per_s,
                latRate.degrees.per_second,
                lonRate.degrees.per_second)

    def setSatTableEntry(self, row, col, entry):
        """
        :param row:
        :param col:
        :param entry:
        :return:
        """
        self.ui.listSatelliteNames.setItem(row, col, entry)
        return True

    def updateTableEntries(self, row, satParam, isUp=None, isSunlit=None):
        """
        :param row:
        :param satParam:
        :param isUp:
        :param isSunlit:
        :return:
        """
        entry = QTableWidgetItem(f'{satParam[0]:5.0f}')
        entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sigSetSatTableEntry.emit(row, 2, entry)

        entry = QTableWidgetItem(f'{satParam[1]:+2.2f}')
        entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sigSetSatTableEntry.emit(row, 3, entry)

        entry = QTableWidgetItem(f'{satParam[2]:+2.2f}')
        entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sigSetSatTableEntry.emit(row, 4, entry)

        entry = QTableWidgetItem(f'{satParam[3]:+2.2f}')
        entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sigSetSatTableEntry.emit(row, 5, entry)

        if isUp is None:
            return False

        if isUp[0]:
            t1 = f'{isUp[1][0].tt_strftime("%m-%d")}'
            t2 = f'{isUp[1][0].tt_strftime("%H:%M:%S")}'
        else:
            t1 = t2 = ''

        entry = QTableWidgetItem(t1)
        entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sigSetSatTableEntry.emit(row, 6, entry)

        entry = QTableWidgetItem(t2)
        entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sigSetSatTableEntry.emit(row, 7, entry)

        entry = QTableWidgetItem('*' if isSunlit else ' ')
        entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sigSetSatTableEntry.emit(row, 8, entry)
        return True

    def satCalcDynamicTable(self):
        """
        :return:
        """
        if not self.satTableDynamicValid:
            return False
        if self.ui.satTabWidget.currentIndex() != 0:
            return False
        if self.ui.mainTabWidget.currentIndex() != 6:
            return False

        satTab = self.ui.listSatelliteNames
        loc = self.app.mount.obsSite.location
        ts = self.app.mount.obsSite.ts
        timeNow = ts.now()
        viewPortRect = QRect(QPoint(0, 0), satTab.viewport().size())

        for row in range(satTab.rowCount()):
            rect = satTab.visualRect(satTab.model().index(row, 0))
            isVisible = viewPortRect.intersects(rect)

            if not isVisible:
                continue
            if satTab.isRowHidden(row):
                continue

            name = satTab.model().index(row, 1).data()
            sat = self.satellites[name]
            satParam = self.findRangeRate(sat, loc, timeNow)
            self.updateTableEntries(row, satParam)
        return True

    def filterSatelliteNamesList(self):
        """
        :return: true for test purpose
        """
        satTab = self.ui.listSatelliteNames
        filterStr = self.ui.filterSatellite.text()
        satIsUp = self.ui.satIsUp
        satIsSunlit = self.ui.satIsSunlit

        checkIsUp = satIsUp.isChecked() and satIsUp.isEnabled()
        checkIsSunlit = satIsSunlit.isChecked() and satIsSunlit.isEnabled()

        for row in range(satTab.model().rowCount()):
            name = satTab.model().index(row, 1).data()
            show = filterStr.lower() in name.lower()
            if checkIsUp:
                show = show and satTab.model().index(row, 7).data() != ''
            if checkIsSunlit:
                show = show and satTab.model().index(row, 8).data() == '*'
            satTab.setRowHidden(row, not show)
        return True

    def workerSatCalcTable(self):
        """
        :return:
        """
        satTab = self.ui.listSatelliteNames
        loc = self.app.mount.obsSite.location
        ts = self.app.mount.obsSite.ts
        timeNow = ts.now()
        timeWin = self.ui.satUpTimeWindow.value()
        timeNext = ts.tt_jd(timeNow.tt + timeWin * 3600 / 86400)
        altMin = self.ui.satAltitudeMin.value()
        eph = self.app.ephemeris
        numSats = satTab.rowCount()

        for row in range(numSats):
            QApplication.processEvents()
            if not self.satTableBaseValid:
                break
            name = satTab.model().index(row, 1).data()
            sat = self.satellites[name]
            satParam = self.findRangeRate(sat, loc, timeNow)
            isSunlit = self.findSunlit(sat, eph, timeNow)
            isUp = self.findSatUp(sat, loc, timeNow, timeNext, altMin)
            finished = (row + 1) / numSats * 100
            t = f'Filter - processed: {finished:3.0f}%'
            self.ui.satFilterGroup.setTitle(t)
            self.updateTableEntries(row, satParam, isUp, isSunlit)
        else:
            self.satTableDynamicValid = True
            self.ui.satIsUp.setEnabled(True)
            self.ui.satIsSunlit.setEnabled(True)
            return True
        return False

    def satCalcTable(self):
        """
        :return:
        """
        if not self.satTableBaseValid:
            return False

        self.satTableDynamicValid = False
        self.ui.satIsUp.setEnabled(False)
        self.ui.satIsSunlit.setEnabled(False)
        worker = Worker(self.workerSatCalcTable)
        worker.signals.finished.connect(self.filterSatelliteNamesList)
        self.threadPool.start(worker)
        return True

    def prepareSatTable(self):
        """
        :return:
        """
        satTab = self.ui.listSatelliteNames
        satTab.setRowCount(0)
        satTab.setColumnCount(9)
        hl = ['ID', 'Name', 'Dist\n[km]', 'Radial\n[km/s]', 'Lat\n[deg/s]',
              'Lon\n[deg/s]', 'Date\n[m-d]', 'Time\n[H:M:S]', 'Sun']
        satTab.setHorizontalHeaderLabels(hl)
        satTab.setColumnWidth(0, 50)
        satTab.setColumnWidth(1, 155)
        satTab.setColumnWidth(2, 50)
        satTab.setColumnWidth(3, 50)
        satTab.setColumnWidth(4, 50)
        satTab.setColumnWidth(5, 50)
        satTab.setColumnWidth(6, 45)
        satTab.setColumnWidth(7, 65)
        satTab.setColumnWidth(8, 30)
        satTab.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        satTab.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        satTab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        satTab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return True

    def setupSatelliteNameList(self):
        """
        :return: success for test
        """
        satTab = self.ui.listSatelliteNames
        self.prepareSatTable()

        for name in self.satellites:
            if not self.satSourceValid:
                break
            number = self.satellites[name].model.satnum
            satTab.insertRow(satTab.rowCount())
            row = satTab.rowCount() - 1
            entry = QTableWidgetItem(f'{number:5d}')
            entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            satTab.setItem(row, 0, entry)
            entry = QTableWidgetItem(name)
            entry.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            satTab.setItem(row, 1, entry)

        else:
            self.filterSatelliteNamesList()
            self.ui.satFilterGroup.setEnabled(True)
            self.ui.satProgDatabaseGroup.setEnabled(True)
            self.satTableBaseValid = True
            self.satCalcTable()
            return True
        return False

    def workerLoadDataFromSourceURLs(self, source='', isOnline=False):
        """
        :return: success
        """
        if not source:
            return False

        fileName = os.path.basename(source)
        dirPath = self.app.mwGlob['dataDir']
        filePath = f'{dirPath}/{fileName}'

        satellites = self.app.mount.obsSite.loader.tle_file(source, reload=isOnline)
        self.satellites = {sat.name: sat for sat in satellites}

        if not os.path.isfile(filePath):
            return False

        self.satSourceValid = True
        return True

    def loadDataFromSourceURLs(self):
        """
        :return: success
        """
        self.satSourceValid = False
        self.satTableBaseValid = False
        self.satTableDynamicValid = False
        self.satellites = None
        self.ui.satFilterGroup.setEnabled(False)
        self.ui.satIsUp.setEnabled(False)
        self.ui.satIsSunlit.setEnabled(False)
        self.ui.satFilterGroup.setEnabled(False)
        self.ui.satProgDatabaseGroup.setEnabled(False)

        key = self.ui.satelliteSource.currentText()
        if key not in self.satelliteSourceURLs:
            return False

        source = self.satelliteSourceURLs[key]
        isOnline = self.ui.isOnline.isChecked()
        worker = Worker(self.workerLoadDataFromSourceURLs,
                        source=source,
                        isOnline=isOnline)
        worker.signals.finished.connect(self.setupSatelliteNameList)
        self.threadPool.start(worker)
        return True

    def progSatellitesFiltered(self):
        """
        :return: success
        """
        source = self.ui.satelliteSource.currentText()
        text = f'Should filtered database\n\n[{source}]\n\nbe programmed to mount ?'
        suc = self.messageDialog(self, 'Program with QCI Updater', text)

        if not suc:
            return False

        self.app.message.emit(f'Program database:    [{source}]', 1)
        self.app.message.emit('Exporting TLE data', 0)

        filterStr = self.ui.filterSatellite.text().lower()
        filtered = dict()
        for name, _ in self.satellites.items():
            if not isinstance(name, str):
                continue

            text = f'{name}'
            if filterStr.lower() not in text.lower():
                continue

            filtered[name] = self.satellites[name]

        suc = self.databaseProcessing.writeSatelliteTLE(filtered,
                                                        self.installPath)

        if not suc:
            self.app.message.emit('Data could not be exported - stopping', 2)
            return False

        if not self.app.automation:
            t = 'Not running windows - upload not possible'
            self.app.message.emit(t, 2)
            return False

        if not self.app.automation.installPath:
            t = 'No QCI updater available - upload not possible'
            self.app.message.emit(t, 2)
            return False

        self.app.message.emit('Uploading TLE data to mount', 0)
        suc = self.app.automation.uploadTLEData()

        if not suc:
            self.app.message.emit('Uploading error', 2)
        else:
            self.app.message.emit('Programming success', 1)
        return suc

    def progSatellitesFull(self):
        """
        :return: success
        """
        source = self.ui.satelliteSource.currentText()
        text = f'Should full database\n\n[{source}]\n\nbe programmed to mount ?'
        suc = self.messageDialog(self, 'Program with QCI Updater', text)

        if not suc:
            return False

        self.app.message.emit(f'Program database:    [{source}]', 1)
        self.app.message.emit('Exporting TLE data', 0)

        suc = self.databaseProcessing.writeSatelliteTLE(self.satellites,
                                                        self.installPath)
        if not suc:
            self.app.message.emit('Data could not be exported - stopping', 2)
            return False

        if not self.app.automation:
            t = 'Not running windows - upload not possible'
            self.app.message.emit(t, 2)
            return False

        if not self.app.automation.installPath:
            t = 'No QCI updater available - upload not possible'
            self.app.message.emit(t, 2)
            return False

        self.app.message.emit('Uploading TLE data to mount', 0)
        suc = self.app.automation.uploadTLEData()
        if not suc:
            self.app.message.emit('Uploading error', 2)
        else:
            self.app.message.emit('Programming success', 1)

        return suc