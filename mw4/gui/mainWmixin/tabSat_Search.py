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
import os

# external packages
import PyQt5
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtWidgets import QApplication, QAbstractItemView
from PyQt5.QtWidgets import QTableWidgetItem
import numpy as np
from skyfield import almanac

# local import
from base.tpool import Worker
from logic.databaseProcessing.dataWriter import DataWriter
from gui.utilities.toolsQtWidget import QCustomTableWidgetItem


class SatSearch(object):
    """
    Satellite has five parts:
    1. When mount is connected it will automatically search for a stored
    satellite in the mount. If so, the satellite reference is fetched, the data
    is read out of the TLE database, the orbit data are calculate and the gui is
    populated. If the satellite window is open, data will be sent to gui drawing
    as well.

    2. When a satellite is chosen from a drop-down list by double click, it
    selects the corresponding TLE data, programs is to the mount and follows the
    steps of 1.

    3. If a new satellite database is selected, is downloads the database and
    updates the drop-down menus with the satellite entries.

    4. If a satellite is to be tracked, it takes the satellite TLE data, the user
    gui input and calculates the satellite trajectory. In case of built-in
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

        baseUrl = 'http://www.celestrak.org/NORAD/elements/'
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
            'Custom': 'custom.txt',
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
        self.ui.satRemoveSO.clicked.connect(self.filterSatelliteNamesList)
        self.ui.satTwilight.activated.connect(self.filterSatelliteNamesList)
        self.sigSetSatTableEntry.connect(self.setSatTableEntry)

        self.app.update1s.connect(self.satCalcDynamicTable)
        self.app.update10m.connect(self.updateSatTable)
        self.ui.unitTimeUTC.toggled.connect(self.satCalcTable)

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
        self.ui.satTwilight.setCurrentIndex(config.get('satTwilight', 4))
        self.loadDataFromSourceURLs()
        self.ui.filterSatellite.setText(config.get('filterSatellite'))
        self.ui.switchToTrackingTab.setChecked(config.get('switchToTrackingTab',
                                                          False))
        self.ui.satCyclicUpdates.setChecked(config.get('satCyclicUpdates', False))
        self.ui.satIsSunlit.setChecked(config.get('satIsSunlit', False))
        self.ui.satRemoveSO.setChecked(config.get('satRemoveSO', False))
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
        config['satTwilight'] = self.ui.satTwilight.currentIndex()
        config['filterSatellite'] = self.ui.filterSatellite.text()
        config['switchToTrackingTab'] = self.ui.switchToTrackingTab.isChecked()
        config['satCyclicUpdates'] = self.ui.satCyclicUpdates.isChecked()
        config['satIsSunlit'] = self.ui.satIsSunlit.isChecked()
        config['satRemoveSO'] = self.ui.satRemoveSO.isChecked()
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
    def checkTwilight(ephemeris, loc, data):
        """
        :param ephemeris:
        :param loc:
        :param data:
        :return:
        """
        isUp = data[0]
        if not isUp:
            return 4

        satTime = data[1][0]
        f = almanac.dark_twilight_day(ephemeris, loc)
        twilight = int(f(satTime))
        return twilight

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

    @staticmethod
    def calcSatSunPhase(sat, loc, ephemeris, tEv):
        """
        https://stackoverflow.com/questions/19759501
            /calculating-the-phase-angle-between-the-sun-iss-and-an-observer-on-the
            -earth
        https://space.stackexchange.com/questions/26286
            /how-to-calculate-cone-angle-between-two-satellites-given-their-look-angles
        :param sat:
        :param loc:
        :param ephemeris:
        :param tEv:
        :return:
        """
        earth = ephemeris['earth']

        vecObserverSat = (sat - loc).at(tEv)
        vecSunSat = (earth + sat).at(tEv)
        phase = vecObserverSat.separation_from(vecSunSat)
        return phase

    def calcAppMag(self, sat, loc, ephemeris, satRange, tEv):
        """
        solution base on the work from:
        https://astronomy.stackexchange.com/questions/28744
            /calculating-the-apparent-magnitude-of-a-satellite/28765#28765
        https://astronomy.stackexchange.com/q/28744/7982
        https://www.researchgate.net/publication
            /268194552_Large_phase_angle_observations_of_GEO_satellites
        https://amostech.com/TechnicalPapers/2013/POSTER/COGNION.pdf
        https://apps.dtic.mil/dtic/tr/fulltext/u2/785380.pdf

        :param sat:
        :param loc:
        :param ephemeris:
        :param sat:
        :param satRange:
        :param tEv:
        :return:
        """
        phase = self.calcSatSunPhase(sat, loc, ephemeris, tEv).radians
        intMag = -1.3

        term1 = intMag
        term2 = +5.0 * np.log10(satRange / 1000.)
        arg = np.sin(phase) + (np.pi - phase) * np.cos(phase)
        term3 = -2.5 * np.log10(arg)
        appMag = term1 + term2 + term3
        return appMag

    def setSatTableEntry(self, row, col, entry):
        """
        :param row:
        :param col:
        :param entry:
        :return:
        """
        self.ui.listSatelliteNames.setItem(row, col, entry)
        return True

    def updateTableEntries(self, row, satParam, isUp=None, isSunlit=None,
                           appMag=None, twilight=None):
        """
        :param row:
        :param satParam:
        :param isUp:
        :param isSunlit:
        :param appMag:
        :param twilight:
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

        if isUp is not None:
            if isUp[0]:
                t = self.convertTime(isUp[1][0], '%H:%M')
            else:
                t = ''

            entry = QTableWidgetItem(t)
            entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sigSetSatTableEntry.emit(row, 6, entry)

        if isSunlit is not None:
            if isSunlit:
                value = f'{appMag:1.1f}'
            else:
                value = ''

            entry = QCustomTableWidgetItem(value)
            entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sigSetSatTableEntry.emit(row, 7, entry)

        if twilight is not None:
            entry = QTableWidgetItem(f'{twilight:1.0f}')
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
        eph = self.app.ephemeris
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
            if not np.isnan(satParam[0]):
                isSunlit = self.findSunlit(sat, eph, timeNow)
                satRange = satParam[0]
                if isSunlit:
                    appMag = self.calcAppMag(sat, loc, eph, satRange, timeNow)
                else:
                    appMag = 99
            else:
                isSunlit = False
                appMag = 99
            self.updateTableEntries(row, satParam, isSunlit=isSunlit,
                                    appMag=appMag)
        return True

    @staticmethod
    def positionCursorInSatTable(satTab, satName):
        """
        :param satTab:
        :param satName:
        :return:
        """
        result = satTab.findItems(satName, Qt.MatchExactly)
        if len(result) == 0:
            return False
        item = result[0]
        index = satTab.row(item)
        satTab.selectRow(index)
        satTab.scrollToItem(item,
                            QAbstractItemView.PositionAtCenter
                            | QAbstractItemView.EnsureVisible)
        return True

    def filterSatelliteNamesList(self):
        """
        :return: true for test purpose
        """
        satTab = self.ui.listSatelliteNames
        filterStr = self.ui.filterSatellite.text().lower()
        satIsUp = self.ui.satIsUp
        satIsSunlit = self.ui.satIsSunlit

        checkIsUp = satIsUp.isChecked() and satIsUp.isEnabled()
        checkIsSunlit = satIsSunlit.isChecked() and satIsSunlit.isEnabled()
        checkRemoveSO = self.ui.satRemoveSO.isChecked()

        selectTwilight = self.ui.satTwilight.currentIndex()

        for row in range(satTab.model().rowCount()):
            name = satTab.model().index(row, 1).data().lower()
            number = satTab.model().index(row, 0).data().lower()
            show = filterStr in number + name
            if checkIsUp:
                show = show and satTab.model().index(row, 6).data() != ''
            if checkIsSunlit:
                show = show and satTab.model().index(row, 7).data() != ''
            if checkRemoveSO:
                show = show and 'starlink' not in name
                show = show and 'oneweb' not in name
                show = show and 'globalstar' not in name
                show = show and 'navstar' not in name
            if selectTwilight < 4:
                value = satTab.model().index(row, 8).data()
                actTwilight = int(value) if value is not None else 5
                show = show and actTwilight <= selectTwilight

            satTab.setRowHidden(row, not show)
        satName = self.ui.satelliteName.text()
        self.positionCursorInSatTable(satTab, satName)
        self.changeStyleDynamic(self.ui.satFilterGroup, 'running', False)
        return True

    def checkSatOk(self, sat, tEnd):
        """
        :param sat:
        :param tEnd:
        :return:
        """
        msg = sat.at(tEnd).message
        if msg:
            self.log.warning(f'{sat.name} caused SGP4: [{msg}]')
            return False
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
            if not self.checkSatOk(sat, timeNext):
                continue
            satParam = self.findRangeRate(sat, loc, timeNow)
            if not np.isnan(satParam).any():
                isSunlit = self.findSunlit(sat, eph, timeNow)
                isUp = self.findSatUp(sat, loc, timeNow, timeNext, altMin)
                fitTwilight = self.checkTwilight(eph, loc, isUp)
                satRange = satParam[0]
                if isSunlit:
                    appMag = self.calcAppMag(sat, loc, eph, satRange, timeNow)
                else:
                    appMag = 99
            else:
                fitTwilight = 4
                isSunlit = False
                isUp = False, []
                appMag = 99

            finished = (row + 1) / numSats * 100
            t = f'Filter - processed: {finished:3.0f}%'
            self.ui.satFilterGroup.setTitle(t)
            self.updateTableEntries(row, satParam, isUp, isSunlit, appMag,
                                    fitTwilight)
        else:
            self.satTableDynamicValid = True
            self.ui.satIsUp.setEnabled(True)
            self.ui.satIsSunlit.setEnabled(True)
            self.ui.satTwilight.setEnabled(True)
            t = 'Filter - processed: 100%'
            self.ui.satFilterGroup.setTitle(t)
            return True
        return False

    def satCalcTable(self):
        """
        :return:
        """
        if not self.satTableBaseValid:
            return False

        title = 'Setup ' + self.timeZoneString()
        self.ui.satSetupGroup.setTitle(title)
        self.satTableDynamicValid = False
        self.ui.satIsUp.setEnabled(False)
        self.ui.satIsSunlit.setEnabled(False)
        self.ui.satTwilight.setEnabled(False)
        worker = Worker(self.workerSatCalcTable)
        worker.signals.finished.connect(self.filterSatelliteNamesList)
        self.changeStyleDynamic(self.ui.satFilterGroup, 'running', True)
        self.threadPool.start(worker)
        return True

    def updateSatTable(self):
        """
        :return:
        """
        if not self.ui.satCyclicUpdates.isChecked():
            return False
        self.satCalcTable()
        return True

    def prepareSatTable(self):
        """
        :return:
        """
        satTab = self.ui.listSatelliteNames
        satTab.setRowCount(0)
        satTab.setColumnCount(9)
        hl = ['Num', 'Satellite Name', 'Dist\n[km]', 'Rad v\n[km/s]',
              'Lat v\n[deg/s]', 'Lon v\n[deg/s]',
              'Time\n[H:M]', 'Sat\n[mag]']
        satTab.setHorizontalHeaderLabels(hl)
        satTab.setColumnWidth(0, 50)
        satTab.setColumnWidth(1, 205)
        satTab.setColumnWidth(2, 50)
        satTab.setColumnWidth(3, 50)
        satTab.setColumnWidth(4, 45)
        satTab.setColumnWidth(5, 45)
        satTab.setColumnWidth(6, 50)
        satTab.setColumnWidth(7, 45)
        satTab.setColumnWidth(8, 0)
        satTab.verticalHeader().setDefaultSectionSize(16)
        return True

    def setupSatelliteNameList(self):
        """
        :return: success for test
        """
        if not self.satSourceValid:
            return False

        satTab = self.ui.listSatelliteNames
        self.prepareSatTable()

        for name in self.satellites:
            number = self.satellites[name].model.satnum
            row = satTab.rowCount()
            satTab.insertRow(row)
            entry = QTableWidgetItem(f'{number:5d}')
            entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            satTab.setItem(row, 0, entry)
            entry = QTableWidgetItem(name)
            entry.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            satTab.setItem(row, 1, entry)

        self.filterSatelliteNamesList()
        self.ui.satFilterGroup.setEnabled(True)
        self.ui.satProgDatabaseGroup.setEnabled(True)
        self.satTableBaseValid = True
        self.satCalcTable()
        return True

    def workerLoadDataFromSourceURLs(self, source='', isOnline=False):
        """
        :return: success
        """
        loader = self.app.mount.obsSite.loader
        fileName = os.path.basename(source)
        dirPath = self.app.mwGlob['dataDir']
        filePath = os.path.normpath(f'{dirPath}/{fileName}')
        if not isOnline:
            source = filePath
        satellites = loader.tle_file(source, reload=isOnline)
        self.satellites = {sat.name: sat for sat in satellites}
        if not os.path.isfile(filePath):
            return False

        daysOld = loader.days_old(filePath)
        self.ui.satSourceGroup.setTitle(f'Satellite data - age: {daysOld:2.1f}d')
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
        self.ui.listSatelliteNames.setRowCount(0)
        isOnline = self.ui.isOnline.isChecked()
        worker = Worker(self.workerLoadDataFromSourceURLs,
                        source=source,
                        isOnline=isOnline)
        worker.signals.finished.connect(self.setupSatelliteNameList)
        self.threadPool.start(worker)
        return True

    def progSatellites(self, satellites):
        """
        :param satellites:
        :return:
        """
        suc = self.databaseProcessing.writeSatelliteTLE(satellites, self.installPath)
        if not suc:
            self.msg.emit(2, 'TLE', 'Data error',
                          'Data could not be exported - stopping')
            return False

        self.msg.emit(0, 'TLE', 'Program', 'Uploading to mount')
        suc = self.app.automation.uploadTLEData()
        if not suc:
            self.msg.emit(2, 'TLE', 'Program error',
                          'Uploading error but files available')
        else:
            self.msg.emit(1, 'TLE', 'Program', 'Successful uploaded')
        return suc

    def satelliteFilter(self, satellitesRaw):
        """
        :param satellitesRaw:
        :return:
        """
        filterStr = self.ui.filterSatellite.text().lower()
        filtered = dict()
        for name, _ in satellitesRaw.items():
            if not isinstance(name, str):
                continue
            text = f'{name}'
            if filterStr.lower() not in text.lower():
                continue
            filtered[name] = satellitesRaw[name]
        return filtered

    def satelliteGUI(self):
        """
        :return:
        """
        suc = self.checkUpdaterOK()
        if not suc:
            return False

        source = self.ui.satelliteSource.currentText()
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

        self.msg.emit(1, 'TLE', 'Program', f'{source}')
        self.msg.emit(1, '', '', 'Exporting TLE data')
        return True

    def progSatellitesFiltered(self):
        """
        :return: success
        """
        suc = self.satelliteGUI()
        if not suc:
            return False

        filtered = self.satelliteFilter(self.satellites)
        self.progSatellites(filtered)
        return True

    def progSatellitesFull(self):
        """
        :return: success
        """
        suc = self.satelliteGUI()
        if not suc:
            return False

        self.progSatellites(self.satellites)
        return True
