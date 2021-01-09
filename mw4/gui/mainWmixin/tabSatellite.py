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
import numpy as np
from sgp4.exporter import export_tle

# local import
from base.tpool import Worker
from logic.databaseProcessing.dataWriter import DataWriter


class Satellite(object):
    """
    """

    def __init__(self):
        self.satellites = dict()
        self.satellite = None
        self.satOrbits = None
        self.listSatelliteNamesProxy = None
        self.satellitesRawTLE = {}
        self.databaseProcessing = DataWriter(self.app)
        self.installPath = ''

        self.satelliteSourceURLs = {
            'Active': 'http://www.celestrak.com/NORAD/elements/active.txt',
            'Space Stations': 'http://www.celestrak.com/NORAD/elements/stations.txt',
            '100 brightest': 'http://www.celestrak.com/NORAD/elements/visual.txt',
            'NOAA': 'http://www.celestrak.com/NORAD/elements/noaa.txt',
            'GEOS': 'http://www.celestrak.com/NORAD/elements/goes.txt',
            'Weather': 'http://www.celestrak.com/NORAD/elements/weather.txt',
            'Earth Resources': 'http://celestrak.com/NORAD/elements/resource.txt',
            'TDRSS TRacking and Data Relay': 'http://celestrak.com/NORAD/elements/tdrss.txt',
            'ARGOS': 'http://celestrak.com/NORAD/elements/argos.txt',
            'Amateur Radio': 'http://www.celestrak.com/NORAD/elements/amateur.txt',
            'Space & Earth Science': 'http://celestrak.com/NORAD/elements/science.txt',
            'Engineering': 'http://celestrak.com/NORAD/elements/engineering.txt',
            'Last 30 days launch': 'http://www.celestrak.com/NORAD/elements/tle-new.txt',
        }

        self.ui.progSatellitesFull.clicked.connect(self.progSatellitesFull)
        self.ui.progSatellitesFiltered.clicked.connect(self.progSatellitesFiltered)
        self.ui.listSatelliteNames.doubleClicked.connect(self.signalExtractSatelliteData)
        self.ui.startSatelliteTracking.clicked.connect(self.startTrack)
        self.ui.stopSatelliteTracking.clicked.connect(self.stopTrack)
        self.ui.satelliteSource.currentIndexChanged.connect(self.loadTLEDataFromSourceURLs)
        self.ui.filterSatellite.textChanged.connect(self.filterSatelliteNamesList)

        self.app.sendSatelliteData.connect(self.sendSatelliteData)
        self.app.mount.signals.calcTLEdone.connect(self.updateSatelliteTrackGui)
        self.app.mount.signals.getTLEdone.connect(self.getSatelliteDataFromDatabase)
        self.ui.isOnline.stateChanged.connect(self.loadTLEDataFromSourceURLs)

        self.app.update3s.connect(self.updateOrbit)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        self.setupSatelliteSourceURLsDropDown()
        if not self.app.automation:
            self.installPath = self.app.mwGlob['dataDir']

        elif self.app.automation.installPath:
            self.installPath = self.app.automation.installPath

        else:
            self.installPath = self.app.mwGlob['dataDir']
        return True

    def setupSatelliteSourceURLsDropDown(self):
        """
        setupSatelliteSourceURLsDropDown handles the dropdown list for the
        satellite data online sources. therefore we add the necessary entries to
        populate the list.

        :return: success for test
        """
        self.ui.satelliteSource.clear()
        self.ui.satelliteSource.setView(PyQt5.QtWidgets.QListView())
        for name in self.satelliteSourceURLs.keys():
            self.ui.satelliteSource.addItem(name)
        return True

    def filterSatelliteNamesList(self):
        """
        :return: true for test purpose
        """
        listSat = self.ui.listSatelliteNames
        filterStr = self.ui.filterSatellite.text()

        for row in range(listSat.model().rowCount()):
            isFound = filterStr.lower() in listSat.model().index(row).data().lower()
            isVisible = isFound or not filterStr

            if isVisible:
                listSat.setRowHidden(row, False)

            else:
                listSat.setRowHidden(row, True)
        return True

    def setupSatelliteNameList(self):
        """
        setupSatelliteNameList clears the list view of satellite names deriving
        from the selected source file on disk. after that it populated the list
        with actual data.

        :return: success for test
        """
        self.ui.listSatelliteNames.clear()
        for name, _ in self.satellites.items():
            if not isinstance(name, str):
                continue
            entryName = f'{self.satellites[name].model.satnum:6d}: {name}'
            self.ui.listSatelliteNames.addItem(entryName)
        self.ui.listSatelliteNames.sortItems()
        self.ui.listSatelliteNames.update()
        self.filterSatelliteNamesList()
        return True

    def loadTLEDataFromSourceURLsWorker(self, source='', isOnline=False):
        """
        loadTLEDataFromSourceURLsWorker selects from a drop down list of
        possible satellite data sources on the web and once selected downloads
        the data. depending of the setting of reload is true setting, it takes an
        already loaded file from local disk. after loading or opening the source
        file, it updates the satellite list in the list view widget for the
        selection of satellites.

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
        return True

    def loadTLEDataFromSourceURLs(self):
        """
        loadTLEDataFromSourceURLs selects from a drop down list of possible
        satellite data sources on the web and once selected downloads the data.
        depending of the setting of reload is true setting, it takes an already
        loaded file from local disk. after loading or opening the source file,
        it updates the satellite list in the list view widget for the selection
        of satellites.

        :return: success
        """
        key = self.ui.satelliteSource.currentText()
        if key not in self.satelliteSourceURLs:
            return False

        source = self.satelliteSourceURLs[key]
        isOnline = self.ui.isOnline.isChecked()
        worker = Worker(self.loadTLEDataFromSourceURLsWorker,
                        source=source,
                        isOnline=isOnline)
        worker.signals.finished.connect(self.setupSatelliteNameList)
        self.threadPool.start(worker)

        return True

    def updateOrbit(self):
        """
        updateOrbit calculates the actual satellite orbits, sub point etc. and
        updates the data in the gui. in addition when satellite window is open
        it signals this update data as well for matplotlib drawings in satellite
        window. this method is called cyclic every 3 seconds for updates

        :return: success
        """
        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            return False

        # check if calculation is necessary to optimize cpu time
        # get index for satellite tab and check if it's visible. i
        # f not, no calculation
        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Satellite')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)
        satTabVisible = self.ui.mainTabWidget.currentIndex() == tabIndex

        winObj = self.app.uiWindows['showSatelliteW']

        if not winObj:
            return False

        # if nothing is visible, nothing to update !
        if not winObj.get('classObj') and not satTabVisible:
            return False

        # now calculating the satellite data
        now = self.app.mount.obsSite.ts.now()
        observe = self.satellite.at(now)

        subpoint = observe.subpoint()
        difference = self.satellite - self.app.mount.obsSite.location

        ra, dec, _ = difference.at(now).radec()
        ra = ra.hours
        dec = dec.degrees

        self.ui.satRa.setText(f'{ra:3.2f}')
        self.ui.satDec.setText(f'{dec:3.2f}')

        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        self.ui.satLatitude.setText(f'{lat:3.2f}')
        self.ui.satLongitude.setText(f'{lon:3.2f}')

        altaz = difference.at(now).altaz()

        alt, az, _ = altaz
        alt = alt.degrees
        az = az.degrees

        self.ui.satAltitude.setText(f'{alt:3.2f}')
        self.ui.satAzimuth.setText(f'{az:3.2f}')

        if not winObj.get('classObj'):
            return True

        winObj['classObj'].signals.update.emit(observe, subpoint, altaz)

        return True

    def programTLEDataToMount(self):
        """
        programTLEDataToMount get the satellite data and programs this TLE data
        into the mount. after programming the parameters it forces the mount to
        calculate the satellite orbits immediately

        :return: success
        """
        if not self.app.mount.mountUp:
            self.app.message.emit('Mount is not online', 2)
            return False

        satellite = self.app.mount.satellite
        if satellite.tleParams.name == self.satellite.name:
            self.app.message.emit(f'Actual satellite is  [{self.satellite.name}]', 0)

        else:
            self.app.message.emit(f'Programming [{self.satellite.name}] to mount', 0)
            line0 = self.satellite.name
            line1, line2 = export_tle(self.satellite.model)
            suc = satellite.setTLE(line0=line0,
                                   line1=line1,
                                   line2=line2)
            if not suc:
                self.app.message.emit('Error program TLE', 2)
                return False
        return True

    def calcOrbitFromTLEInMount(self):
        """
        :return: success
        """
        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            self.ui.stopSatelliteTracking.setEnabled(False)
            return False

        self.app.mount.calcTLE()
        return True

    def showRises(self):
        """
        showRises calculated the next three satellite passes for the
        presentation in the gui. the times shown might differ from the
        calculation of the mount as we dont know, how the mount calculates is
        timings.

        :return: True for test purpose
        """
        minAlt = self.app.mount.setting.horizonLimitLow
        if minAlt is None:
            minAlt = 0

        loc = self.app.mount.obsSite.location
        obs = self.app.mount.obsSite

        orbitCycleTime = np.pi / self.satellite.model.no_kozai / 12 / 60

        t0 = obs.ts.tt_jd(obs.timeJD.tt - orbitCycleTime)
        t1 = obs.ts.tt_jd(obs.timeJD.tt + 3)

        t, events = self.satellite.find_events(loc, t0, t1, altitude_degrees=minAlt)

        passUI = {
            0:
                {'rise': self.ui.satTransitStartUTC_1,
                 'settle': self.ui.satTransitEndUTC_1,
                 },
            1:
                {'rise': self.ui.satTransitStartUTC_2,
                 'settle': self.ui.satTransitEndUTC_2,
                 },
            2:
                {'rise': self.ui.satTransitStartUTC_3,
                 'settle': self.ui.satTransitEndUTC_3,
                 },
        }

        fString = "%Y-%m-%d  %H:%M"

        # collecting the events
        index = 0
        satOrbits = dict()
        for ti, event in zip(t, events):
            if event == 0:
                satOrbits[index] = {'rise': ti}

            elif event == 1:
                continue

            elif event == 2:
                if index not in satOrbits:
                    continue

                satOrbits[index]['settle'] = ti

                if ti.tt < obs.timeJD.tt:
                    continue

                index += 1

        for satOrbit in satOrbits:
            if satOrbit > 2:
                break
            timeRise = satOrbits[satOrbit]['rise'].utc_strftime(fString)
            timeSettle = satOrbits[satOrbit]['settle'].utc_strftime(fString)
            passUI[satOrbit]['rise'].setText(f'{timeRise}')
            passUI[satOrbit]['settle'].setText(f'{timeSettle}')

        while index < 3:
            passUI[index]['rise'].setText('-')
            passUI[index]['settle'].setText('-')
            index += 1

        return satOrbits

    def extractSatelliteData(self, satName=''):
        """
        extractSatelliteData is called when a satellite is selected via mouse
        click in the list menu. it collects the data and writes basic stuff to
        the gui. depending on the age of the satellite data is colors the frame

        :param satName: additional parameter for calling this method
        :return: success
        """
        if satName not in self.satellites:
            return False

        index = self.findIndexValue(self.ui.listSatelliteNames, satName,
                                    relaxed=True)
        item = self.ui.listSatelliteNames.item(index)

        if item is None:
            return False

        item.setSelected(True)

        # making the entry visible (and scroll the list if necessary)
        position = PyQt5.QtWidgets.QAbstractItemView.EnsureVisible
        self.ui.listSatelliteNames.scrollToItem(item, position)
        self.satellite = self.satellites[satName]

        # now we prepare the selection of the data in the gui
        self.ui.satelliteName.setText(self.satellite.name)
        epochText = self.satellite.epoch.utc_strftime('%Y-%m-%d, %H:%M')
        self.ui.satelliteEpoch.setText(epochText)

        # the epoch should be not too old
        now = self.app.mount.obsSite.ts.now()
        days = now - self.satellite.epoch
        self.ui.satelliteDataAge.setText(f'{days:2.2f}')

        if days > 10:
            self.changeStyleDynamic(self.ui.satelliteDataAge, 'color', 'red')

        elif 3 < days < 10:
            self.changeStyleDynamic(self.ui.satelliteDataAge, 'color', 'yellow')

        else:
            self.changeStyleDynamic(self.ui.satelliteDataAge, 'color', '')

        # filling up the satellite data
        self.ui.satelliteNumber.setText(f'{self.satellite.model.satnum:5d}')
        self.ui.stopSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setEnabled(False)
        self.ui.satTransitStartUTC.setText('-')
        self.ui.satTransitEndUTC.setText('-')
        self.ui.satNeedFlip.setText('-')

        self.updateOrbit()
        self.programTLEDataToMount()
        self.calcOrbitFromTLEInMount()
        self.satOrbits = self.showRises()

        winObj = self.app.uiWindows['showSatelliteW']

        if not winObj['classObj']:
            return False

        winObj['classObj'].signals.show.emit(self.satellite, self.satOrbits)
        return True

    def sendSatelliteData(self):
        """
        :return:
        """
        if not self.satellite or not self.satOrbits:
            return False

        winObj = self.app.uiWindows['showSatelliteW']

        if not winObj['classObj']:
            return False

        winObj['classObj'].signals.show.emit(self.satellite, self.satOrbits)
        return True

    def signalExtractSatelliteData(self):
        """
        :return: True for test purpose
        """
        satName = self.ui.listSatelliteNames.currentItem().text()[8:]
        self.extractSatelliteData(satName=satName)
        return True

    def getSatelliteDataFromDatabase(self, tleParams=None):
        """
        getSatelliteDataFromDatabase gets called, when the TLE setup is read
        from the mount. we use the name to retrieve the data from the
        "active.txt" database to be able to work with external database. it calls
        extraction method for getting the specific satellite data read and stored.

        :param tleParams:
        :return: True for test purpose
        """
        if not tleParams:
            return False

        self.extractSatelliteData(satName=tleParams.name)
        return True

    def updateSatelliteTrackGui(self, tleParams=None):
        """
        updateSatelliteTrackGui is called, when the mount has finished its
        calculations based on programmed TLE data. It writes the data to the gui
        and enables the start track button.

        :return: success for test purpose
        """
        if not tleParams:
            return False

        if tleParams.jdStart is not None:
            time = self.app.mount.obsSite.ts.tt_jd(tleParams.jdStart)
            self.ui.satTransitStartUTC.setText(time.utc_strftime('%Y-%m-%d  %H:%M:%S'))

        else:
            self.ui.satTransitStartUTC.setText('No transit')

        if tleParams.jdEnd is not None:
            time = self.app.mount.obsSite.ts.tt_jd(tleParams.jdEnd)
            self.ui.satTransitEndUTC.setText(time.utc_strftime('%Y-%m-%d  %H:%M:%S'))

        else:
            self.ui.satTransitEndUTC.setText('No transit')

        if tleParams.flip:
            self.ui.satNeedFlip.setText('YES')

        else:
            self.ui.satNeedFlip.setText('NO')

        if tleParams.message is not None:
            self.app.message.emit(tleParams.message, 0)

        if tleParams.altitude is not None:
            self.ui.stopSatelliteTracking.setEnabled(True)
            self.ui.startSatelliteTracking.setEnabled(True)
        else:
            self.ui.stopSatelliteTracking.setEnabled(False)
            self.ui.startSatelliteTracking.setEnabled(False)

        return True

    def startTrack(self):
        """
        :return: success
        """
        if not self.app.mount.mountUp:
            self.app.message.emit('Mount is not online', 2)
            return False

        # if mount is currently parked, we unpark it
        if self.app.mount.obsSite.status == 5:
            suc = self.app.mount.obsSite.unpark()
            if suc:
                self.app.message.emit('Mount unparked', 0)

            else:
                self.app.message.emit('Cannot unpark mount', 2)

        suc, message = self.app.mount.satellite.slewTLE()
        if not suc:
            self.app.message.emit(message, 2)
            return False

        self.app.message.emit(message, 0)
        return True

    def stopTrack(self):
        """
        :return: success
        """
        if not self.app.mount.mountUp:
            self.app.message.emit('Mount is not online', 2)
            return False

        suc = self.app.mount.obsSite.stopTracking()
        if not suc:
            self.app.message.emit('Cannot stop tracking', 2)
        else:
            self.app.message.emit('Stopped tracking', 0)
        return suc

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
        self.app.message.emit('Exporting MPC data', 0)

        filterStr = self.ui.filterSatellite.text().lower()

        filtered = dict()
        for name, _ in self.satellites.items():
            if not isinstance(name, str):
                continue

            text = f'{self.satellites[name].model.satnum:6d}: {name}'
            if filterStr.lower() not in text.lower():
                continue

            filtered[name] = self.satellites[name]

        suc = self.databaseProcessing.writeSatelliteTLE(filtered,
                                                        self.installPath)

        if not suc:
            self.app.message.emit('Data could not be exported - stopping', 2)
            return False

        if not self.app.automation:
            self.app.message.emit('Not running windows, no updater available', 2)
            return False

        self.app.message.emit('Uploading TLE data to mount', 0)
        suc = self.app.automation.uploadTLEData()

        if not suc:
            self.app.message.emit('Uploading error', 2)

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
            self.app.message.emit('Not running windows, no updater available', 2)
            return False

        self.app.message.emit('Uploading TLE data to mount', 0)
        suc = self.app.automation.uploadTLEData()

        if not suc:
            self.app.message.emit('Uploading error', 2)

        self.app.message.emit('Programming success', 1)
        return suc
