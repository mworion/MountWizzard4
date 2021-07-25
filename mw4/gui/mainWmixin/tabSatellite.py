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
from skyfield import almanac

# local import
from base.tpool import Worker
from logic.databaseProcessing.dataWriter import DataWriter


class Satellite(object):
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

    def __init__(self):
        self.satellites = dict()
        self.satellite = None
        self.satOrbits = None
        self.listSatelliteNamesProxy = None
        self.satellitesRawTLE = {}
        self.databaseProcessing = DataWriter(self.app)
        self.installPath = ''
        self.nextSatPass = [None, None, None]
        self.lastMeridianLimit = None

        baseUrl = 'http://www.celestrak.com/NORAD/elements/'
        self.satelliteSourceURLs = {
            'Active': baseUrl + 'active.txt',
            'Space Stations': baseUrl + 'stations.txt',
            '100 brightest': baseUrl + 'visual.txt',
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
        msig.calcTLEdone.connect(self.updateSatelliteTrackGui)
        msig.calcTrajectoryDone.connect(self.updateSatelliteTrackGui)
        msig.getTLEdone.connect(self.getSatelliteDataFromDatabase)
        msig.firmwareDone.connect(self.enableGuiFunctions)
        msig.trajectoryProgress.connect(self.trajectoryProgress)
        msig.pointDone.connect(self.followMount)
        msig.settingDone.connect(self.updatePasses)

        self.ui.progSatellitesFull.clicked.connect(self.progSatellitesFull)
        self.ui.progSatellitesFiltered.clicked.connect(self.progSatellitesFiltered)
        self.ui.listSatelliteNames.doubleClicked.connect(self.chooseSatellite)
        self.ui.startSatelliteTracking.clicked.connect(self.startTrack)
        self.ui.stopSatelliteTracking.clicked.connect(self.stopTrack)
        self.ui.satelliteSource.currentIndexChanged.connect(self.loadDataFromSourceURLs)
        self.ui.isOnline.stateChanged.connect(self.loadDataFromSourceURLs)
        self.ui.filterSatellite.textChanged.connect(self.filterSatelliteNamesList)
        self.app.sendSatelliteData.connect(self.sendSatelliteData)
        self.ui.satAfterFlip.clicked.connect(self.showSatPasses)
        self.ui.satBeforeFlip.clicked.connect(self.showSatPasses)
        self.ui.avoidHorizon.clicked.connect(self.showSatPasses)
        self.ui.useInternalSatCalc.clicked.connect(self.showSatPasses)
        self.ui.useInternalSatCalc.clicked.connect(self.enableGuiFunctions)
        self.ui.progTrajectory.clicked.connect(self.startProg)
        self.app.update1s.connect(self.updateOrbit)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']

        self.ui.satelliteSource.clear()
        self.ui.satelliteSource.setView(PyQt5.QtWidgets.QListView())
        for name in self.satelliteSourceURLs.keys():
            self.ui.satelliteSource.addItem(name)

        self.ui.filterSatellite.setText(config.get('filterSatellite'))
        self.ui.domeAutoFollowSat.setChecked(config.get('domeAutoFollowSat', False))
        self.ui.useInternalSatCalc.setChecked(config.get('useInternalSatCalc',
                                                         False))
        self.ui.satBeforeFlip.setChecked(config.get('satBeforeFlip', True))
        self.ui.satAfterFlip.setChecked(config.get('satAfterFlip', True))
        self.ui.avoidHorizon.setChecked(config.get('avoidHorizon', False))
        self.ui.trackingSim.setChecked(config.get('trackingSim', False))

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
        config['filterSatellite'] = self.ui.filterSatellite.text()
        config['domeAutoFollowSat'] = self.ui.domeAutoFollowSat.isChecked()
        config['useInternalSatCalc'] = self.ui.useInternalSatCalc.isChecked()
        config['satBeforeFlip'] = self.ui.satBeforeFlip.isChecked()
        config['satAfterFlip'] = self.ui.satAfterFlip.isChecked()
        config['avoidHorizon'] = self.ui.avoidHorizon.isChecked()
        config['trackingSim'] = self.ui.trackingSim.isChecked()
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

    def calcPassEvents(self, obsSite):
        """
        :return:
        """
        minAlt = self.app.mount.setting.horizonLimitLow
        if minAlt is None:
            minAlt = 5
        if minAlt < 5:
            minAlt = 5

        loc = obsSite.location
        orbitCycleTime = np.pi / self.satellite.model.no_kozai / 12 / 60

        t0 = obsSite.ts.tt_jd(obsSite.timeJD.tt - orbitCycleTime)
        t1 = obsSite.ts.tt_jd(obsSite.timeJD.tt + 5)
        times, events = self.satellite.find_events(loc, t0, t1,
                                                   altitude_degrees=minAlt)
        return times, events

    def extractOrbits(self, timeNow, times, events):
        """
        :param timeNow:
        :param times:
        :param events:
        :return:
        """
        counter = 0
        self.satOrbits = []

        for ti, event in zip(times, events):
            if event == 0:
                self.satOrbits.append({'rise': ti})

            elif event == 1:
                if counter >= len(self.satOrbits):
                    continue
                self.satOrbits[counter]['culminate'] = ti

            elif event == 2:
                if counter >= len(self.satOrbits):
                    continue
                self.satOrbits[counter]['settle'] = ti

                if ti.tt < timeNow.tt:
                    del self.satOrbits[counter]
                    continue
                counter += 1

            if counter > 2:
                break

        if not self.satOrbits:
            return False
        if 'settle' not in self.satOrbits[-1]:
            del self.satOrbits[counter]
            return False

        return True

    @staticmethod
    def calcSatelliteMeridianTransit(satellite, location, tolerance):
        """
        :param satellite:
        :param location:
        :param tolerance:
        :return:
        """
        difference = satellite - location

        def west_of_meridian_at(t):
            alt, az, _ = difference.at(t).altaz()
            delta = (az.degrees + tolerance + 360) % 360 - 180
            return delta < 0

        west_of_meridian_at.step_days = 0.4
        return west_of_meridian_at

    @staticmethod
    def sortFlipEvents(satOrbit, t0, t1, t2):
        """
        :param satOrbit:
        :param t0:
        :param t1:
        :param t2:
        :return:
        """
        settle = satOrbit['settle']
        rise = satOrbit['rise']
        if t0:
            satOrbit['flip'] = t0[0]
        if t1 and t2:
            if t1[0].tt > t2[0].tt:
                satOrbit['flipEarly'] = t2[0]
                satOrbit['flipLate'] = t1[0]
            else:
                satOrbit['flipEarly'] = t1[0]
                satOrbit['flipLate'] = t2[0]
        if t1 and not t2:
            if abs(rise.tt - t1[0].tt) > abs(settle.tt - t1[0].tt):
                satOrbit['flipLate'] = t1[0]
            else:
                satOrbit['flipEarly'] = t1[0]
        if not t1 and t2:
            if abs(rise.tt - t2[0].tt) > abs(settle.tt - t2[0].tt):
                satOrbit['flipLate'] = t2[0]
            else:
                satOrbit['flipEarly'] = t2[0]

        return True

    def addMeridianTransit(self, location):
        """
        :param location:
        :return:
        """
        limit = self.app.mount.setting.meridianLimitTrack
        if limit is None:
            limit = 0
        limit = limit * 0.95

        f0 = self.calcSatelliteMeridianTransit(self.satellite, location, 0)
        f1 = self.calcSatelliteMeridianTransit(self.satellite, location, limit)
        f2 = self.calcSatelliteMeridianTransit(self.satellite, location, -limit)
        for satOrbit in self.satOrbits:
            t0, y0 = almanac.find_discrete(satOrbit['rise'],
                                           satOrbit['settle'], f0)
            t1, y1 = almanac.find_discrete(satOrbit['rise'],
                                           satOrbit['settle'], f1)
            t2, y2 = almanac.find_discrete(satOrbit['rise'],
                                           satOrbit['settle'], f2)

            self.sortFlipEvents(satOrbit, t0, t1, t2)
        return True

    def sendSatelliteData(self, alt=[], az=[], isSunlit=[]):
        """
        :param alt:
        :param az:
        :param isSunlit:
        :return:
        """
        if not self.satellite:
            return False

        winObj = self.app.uiWindows['showSatelliteW']
        if not winObj['classObj']:
            return False

        winObj['classObj'].signals.show.emit(self.satellite,
                                             self.satOrbits,
                                             alt,
                                             az,
                                             isSunlit)
        return True

    def clearTrackingParameters(self):
        """
        :return:
        """
        self.ui.satTrajectoryStart.setText('-')
        self.ui.satTrajectoryEnd.setText('-')
        self.ui.satTrajectoryFlip.setText('-')
        self.ui.trajectoryProgress.setValue(0)
        self.ui.stopSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setText('Start satellite tracking')
        self.changeStyleDynamic(self.ui.startSatelliteTracking, 'running', 'false')
        return True

    def updatePasses(self):
        """
        :return:
        """
        actMeridianLimit = self.app.mount.setting.meridianLimitTrack
        if actMeridianLimit is None:
            return False

        if actMeridianLimit != self.lastMeridianLimit:
            self.showSatPasses()
            self.lastMeridianLimit = actMeridianLimit
        return True

    def showSatPasses(self):
        """
        :return: True for test purpose
        """
        if not self.satellite:
            return False
        self.clearTrackingParameters()
        obsSite = self.app.mount.obsSite
        times, events = self.calcPassEvents(obsSite)

        timeNow = obsSite.timeJD
        self.extractOrbits(timeNow, times, events)
        self.addMeridianTransit(obsSite.location)

        for i in range(0, 3):
            self.passUI[i]['rise'].setText('-')
            self.passUI[i]['culminate'].setText('-')
            self.passUI[i]['settle'].setText('-')
            self.passUI[i]['flip'].setText('-')
            self.passUI[i]['date'].setText('-')

        fString = "%H:%M:%S"
        fStringDate = "%d %b"
        for i, satOrbit in enumerate(self.satOrbits):
            riseT = satOrbit.get('rise', None)
            if riseT is not None:
                riseStr = riseT.utc_strftime(fString)
                dateStr = riseT.utc_strftime(fStringDate)
            else:
                riseStr = 'unknown'
                dateStr = '---'
            culminateT = satOrbit.get('culminate', None)
            if culminateT is not None:
                culminateStr = culminateT.utc_strftime(fString)
            else:
                culminateStr = 'unknown'
            settleT = satOrbit.get('settle', None)
            if settleT is not None:
                settleStr = settleT.utc_strftime(fString)
            else:
                settleStr = 'unknown'
            flipT = satOrbit.get('flip', None)
            if flipT is not None:
                flipStr = flipT.utc_strftime(fString)
            else:
                flipStr = 'no flip'

            self.passUI[i]['rise'].setText(riseStr)
            self.passUI[i]['culminate'].setText(culminateStr)
            self.passUI[i]['settle'].setText(settleStr)
            self.passUI[i]['flip'].setText(flipStr)
            self.passUI[i]['date'].setText(dateStr)

        self.progTrajectoryToMount()
        return True

    def extractSatelliteData(self, satName=''):
        """
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
        position = PyQt5.QtWidgets.QAbstractItemView.EnsureVisible
        self.ui.listSatelliteNames.scrollToItem(item, position)
        self.satellite = self.satellites[satName]
        self.ui.satelliteName.setText(self.satellite.name)
        epochText = self.satellite.epoch.utc_strftime('%Y-%m-%d, %H:%M')
        self.ui.satelliteEpoch.setText(epochText)

        now = self.app.mount.obsSite.ts.now()
        days = now - self.satellite.epoch
        self.ui.satelliteDataAge.setText(f'{days:2.2f}')
        self.app.message.emit(f'Actually using satellite data for: [{satName}]', 0)

        if days > 10:
            self.changeStyleDynamic(self.ui.satelliteDataAge, 'color', 'red')
        elif 3 < days < 10:
            self.changeStyleDynamic(self.ui.satelliteDataAge, 'color', 'yellow')
        else:
            self.changeStyleDynamic(self.ui.satelliteDataAge, 'color', '')

        self.ui.satelliteNumber.setText(f'{self.satellite.model.satnum:5d}')
        return True

    def programDataToMount(self, satName=''):
        """
        :return: success
        """
        if not satName:
            return False
        if satName not in self.satellites:
            return False

        satellite = self.app.mount.satellite
        self.app.message.emit(f'Programming [{satName}] to mount', 0)
        line1, line2 = export_tle(self.satellites[satName].model)
        suc = satellite.setTLE(line0=satName,
                               line1=line1,
                               line2=line2)
        if not suc:
            self.app.message.emit('Error program TLE', 2)
            return False
        self.app.mount.getTLE()
        return True

    def chooseSatellite(self):
        """
        :return: True for test purpose
        """
        satName = self.ui.listSatelliteNames.currentItem().text()[8:]
        if self.app.deviceStat['mount']:
            self.programDataToMount(satName=satName)
        else:
            self.extractSatelliteData(satName=satName)
            self.showSatPasses()
        return True

    def getSatelliteDataFromDatabase(self, tleParams=None):
        """
        :param tleParams:
        :return: True for test purpose
        """
        if tleParams is None:
            return False

        self.extractSatelliteData(satName=tleParams.name)
        self.showSatPasses()
        return True

    def filterSatelliteNamesList(self):
        """
        :return: true for test purpose
        """
        listSat = self.ui.listSatelliteNames
        filterStr = self.ui.filterSatellite.text()

        for row in range(listSat.model().rowCount()):
            isFound = filterStr.lower() in listSat.model().index(row).data().lower()
            listSat.setRowHidden(row, not isFound)

        return True

    def setupSatelliteNameList(self):
        """
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

    def loadDataFromSourceURLsWorker(self, source='', isOnline=False):
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
        return True

    def loadDataFromSourceURLs(self):
        """
        :return: success
        """
        key = self.ui.satelliteSource.currentText()
        if key not in self.satelliteSourceURLs:
            return False

        source = self.satelliteSourceURLs[key]
        isOnline = self.ui.isOnline.isChecked()
        worker = Worker(self.loadDataFromSourceURLsWorker,
                        source=source,
                        isOnline=isOnline)
        worker.signals.finished.connect(self.setupSatelliteNameList)
        self.threadPool.start(worker)
        return True

    def updateOrbit(self):
        """
        :return: success
        """
        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            self.ui.stopSatelliteTracking.setEnabled(False)
            self.changeStyleDynamic(self.ui.startSatelliteTracking, 'running', 'false')
            return False

        now = self.app.mount.obsSite.ts.now()
        winObj = self.app.uiWindows['showSatelliteW']
        if not winObj.get('classObj'):
            return False

        location = self.app.mount.obsSite.location
        winObj['classObj'].signals.update.emit(now, location)
        return True

    def calcTrajectoryData(self, start, end):
        """
        :param start:
        :param end:
        :return:
        """
        duration = min(end - start, 900 / 86400)
        if duration < 1 / 86400:
            return [], [], []

        m = self.app.mount
        temp = m.setting.refractionTemp
        press = m.setting.refractionPress
        timeSeries = start + np.arange(0, duration, 1 / 86400)
        timeVec = m.obsSite.ts.tt_jd(timeSeries)

        earth = self.app.ephemeris['earth']
        ssb_sat = earth + self.satellite
        ssb_loc = earth + m.obsSite.location
        topocentric = ssb_loc.at(timeVec).observe(ssb_sat).apparent()
        alt, az, _ = topocentric.altaz(pressure_mbar=press, temperature_C=temp)
        isSunlit = self.satellite.at(timeVec).is_sunlit(self.app.ephemeris)
        return alt.degrees, az.degrees, isSunlit

    def filterHorizon(self, start, end, alt, az):
        """
        Filter horizon runs from starts on both sides of the track and tries to
        determine, when a track is hidden behind horizon line. As a satellite
        track has to be in one piece, the resulting vectors might have a shorter
        length and a different start and end time.

        :param start:
        :param end:
        :param alt:
        :param az:
        :return:
        """
        useHorizon = self.ui.avoidHorizon.isChecked()
        if not useHorizon:
            return start, end, alt, az

        timeDelayStart = 0
        for altitude, azimuth in list(zip(alt, az)):
            if self.app.data.isAboveHorizon((altitude, azimuth)):
                break
            timeDelayStart += 1
            alt = np.delete(alt, 0)
            az = np.delete(az, 0)

        timeDelayEnd = 0
        for altitude, azimuth in reversed(list(zip(alt, az))):
            if self.app.data.isAboveHorizon((altitude, azimuth)):
                break
            timeDelayEnd += 1
            alt = np.delete(alt, -1)
            az = np.delete(az, -1)

        start += timeDelayStart / 86400
        end -= timeDelayEnd / 86400

        return start, end, alt, az

    def selectStartEnd(self):
        """
        :return:
        """
        if not self.satOrbits:
            return 0, 0
        if 'rise' not in self.satOrbits[0]:
            return 0, 0
        if 'settle' not in self.satOrbits[0]:
            return 0, 0

        isBefore = self.ui.satBeforeFlip.isChecked()
        isAfter = self.ui.satAfterFlip.isChecked()
        start = self.satOrbits[0]['rise'].tt
        end = self.satOrbits[0]['settle'].tt

        if isBefore and isAfter:
            pass
        elif isBefore and not isAfter:
            if 'flipLate' in self.satOrbits[0]:
                end = self.satOrbits[0]['flipLate'].tt
        elif not isBefore and isAfter:
            if 'flipEarly' in self.satOrbits[0]:
                start = self.satOrbits[0]['flipEarly'].tt
        else:
            return 0, 0

        return start, end

    def progTrajectoryToMount(self):
        """
        :return:
        """
        start, end = self.selectStartEnd()
        if not start or not end:
            return False

        useInternal = self.ui.useInternalSatCalc.isChecked()
        if useInternal:
            alt, az, isSunlit = self.calcTrajectoryData(start, end)
            start, end, alt, az = self.filterHorizon(start, end, alt, az)
        else:
            alt = []
            az = []
            isSunlit = []
        self.sendSatelliteData(alt=alt, az=az, isSunlit=isSunlit)
        if self.app.deviceStat['mount'] and not useInternal:
            self.app.mount.calcTLE(start)

        return True

    def startProg(self):
        """
        :return:
        """
        self.clearTrackingParameters()
        isSim = self.ui.trackingSim.isChecked()
        t = ('for simulation' if isSim else '')
        self.app.message.emit('Programming satellite track data ' + t, 0)
        start, end = self.selectStartEnd()
        if not start or not end:
            return False
        alt, az, isSunlit = self.calcTrajectoryData(start, end)
        start, end, alt, az = self.filterHorizon(start, end, alt, az)
        self.changeStyleDynamic(self.ui.progTrajectory, 'running', True)
        self.app.mount.progTrajectory(start, alt=alt, az=az, sim=isSim)
        return True

    def trajectoryProgress(self, value):
        """
        :param value:
        :return:
        """
        self.ui.trajectoryProgress.setValue(value)
        if value == 100:
            self.changeStyleDynamic(self.ui.progTrajectory, 'running', False)
        return True

    def updateSatelliteTrackGui(self, params=None):
        """
        :return: success for test purpose
        """
        if params is None:
            return False
        self.ui.trajectoryProgress.setValue(0)

        if params.jdStart is not None and self.satOrbits:
            t = params.jdStart.utc_strftime('%d %b  %H:%M:%S')
            self.ui.satTrajectoryStart.setText(t)
        else:
            self.ui.satTrajectoryStart.setText('No transit')

        if params.jdEnd is not None and self.satOrbits:
            t = params.jdEnd.utc_strftime('%d %b  %H:%M:%S')
            self.ui.satTrajectoryEnd.setText(t)
        else:
            self.ui.satTrajectoryEnd.setText('No transit')

        if params.flip and self.satOrbits:
            self.ui.satTrajectoryFlip.setText('YES')
        else:
            self.ui.satTrajectoryFlip.setText('NO')

        if params.message is not None:
            self.app.message.emit(params.message, 0)

        if params.jdStart is not None and self.satOrbits:
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
        if not self.app.deviceStat['mount']:
            self.app.message.emit('Mount is not online', 2)
            return False

        if self.app.mount.obsSite.status == 5:
            suc = self.app.mount.obsSite.unpark()
            if suc:
                self.app.message.emit('Mount unparked', 0)
            else:
                self.app.message.emit('Cannot unpark mount', 2)

        self.app.dome.avoidFirstOvershoot()
        suc, message = self.app.mount.satellite.slewTLE()
        if not suc:
            self.app.message.emit(message, 2)
            return False

        self.changeStyleDynamic(self.ui.startSatelliteTracking, 'running', True)
        self.app.message.emit(message, 0)
        return True

    def stopTrack(self):
        """
        :return: success
        """
        if not self.app.deviceStat['mount']:
            self.app.message.emit('Mount is not online', 2)
            return False

        suc = self.app.mount.obsSite.startTracking()
        if not suc:
            self.app.message.emit('Cannot stop tracking', 2)
            return False

        self.ui.startSatelliteTracking.setText('Start satellite tracking')
        self.changeStyleDynamic(self.ui.startSatelliteTracking, 'running', 'false')
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
        self.app.message.emit('Exporting TLE data', 0)

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

    def followMount(self, obs):
        """
        :return:
        """
        TLESCK = {
            'V': 'is slewing to transit start',
            'P': 'is waiting for satellite',
            'S': 'is catching satellite',
            'T': 'is tracking satellite',
        }

        status = obs.status
        if status != 10:
            return False
        if not self.ui.domeAutoFollowSat.isChecked():
            return False
        if not self.app.deviceStat['dome']:
            return False

        stat = obs.statusSat
        statText = (TLESCK[stat] if stat in TLESCK else '')
        self.ui.startSatelliteTracking.setText(statText)

        azimuth = obs.Az.degrees
        altitude = obs.Alt.degrees
        self.app.dome.slewDome(altitude=altitude, azimuth=azimuth, follow=True)
        return True
