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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
# external packages
import PyQt5
# local import
from mw4.base.tpool import Worker


class Satellite(object):
    """
    the Satellite window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

        self.satellites = dict()
        self.satellite = None
        self.satellitesRawTLE = {}

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

        self.ui.listSatelliteNames.itemPressed.connect(self.signalExtractSatelliteData)
        self.ui.startSatelliteTracking.clicked.connect(self.startTrack)
        self.ui.stopSatelliteTracking.clicked.connect(self.stopTrack)
        self.ui.satelliteSource.currentIndexChanged.connect(self.loadTLEDataFromSourceURLs)

        self.app.mount.signals.calcTLEdone.connect(self.updateSatelliteTrackGui)
        self.app.mount.signals.getTLEdone.connect(self.getSatelliteDataFromDatabase)
        self.ui.isOnline.stateChanged.connect(self.loadTLEDataFromSourceURLs)

        self.app.update3s.connect(self.updateOrbit)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        self.setupSatelliteSourceURLsDropDown()
        self.loadTLEDataFromSourceURLs()
        return True

    def setupSatelliteSourceURLsDropDown(self):
        """
        setupSatelliteSourceURLsDropDown handles the dropdown list for the satellite data
        online sources. therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        self.ui.satelliteSource.clear()
        self.ui.satelliteSource.setView(PyQt5.QtWidgets.QListView())
        for name in self.satelliteSourceURLs.keys():
            self.ui.satelliteSource.addItem(name)

        return True

    def setupSatelliteNameList(self):
        """
        setupSatelliteNameList clears the list view of satellite names deriving from the
        selected source file on disk. after that it populated the list with actual data.

        :return: success for test
        """

        self.ui.listSatelliteNames.clear()
        for name, _ in self.satellites.items():
            if not isinstance(name, str):
                continue
            entryName = f'{self.satellites[name].model.satnum:5d} - {name}'
            self.ui.listSatelliteNames.addItem(entryName)
        self.ui.listSatelliteNames.sortItems()
        self.ui.listSatelliteNames.update()

        return True

    @staticmethod
    def loadRawTLEData(filePath=''):
        """
        loadRawTLEData load the two line elements from the source file and stores is separately
        in a dictionary, because we need that data later for transfer it to the mount
        computer. unfortunately the loader from skyfield does not store the original TLE
        data, but only parses it and throws the original away.

        :param filePath:
        :return: satellitesRawTLE
        """

        data = dict()
        with open(filePath, mode='r') as tleFile:
            while True:
                l0 = tleFile.readline()
                l1 = tleFile.readline()
                l2 = tleFile.readline()

                if l0 == '':
                    break
                data[l0.strip()] = {'line0': l0.strip('\n'),
                                    'line1': l1.strip('\n'),
                                    'line2': l2.strip('\n'),
                                    }

        return data

    def loadTLEDataFromSourceURLsWorker(self, source='', reload=False):
        """
        loadTLEDataFromSourceURLsWorker selects from a drop down list of possible satellite
        data sources on the web and once selected downloads the data. depending of the
        setting of reload is true setting, it takes an already loaded file from local disk.
        after loading or opening the source file, it updates the satellite list in the list
        view widget for the selection of satellites.

        :return: success
        """

        if not source:
            return False

        satellites = self.app.mount.obsSite.loader.tle_file(source, reload=reload)
        self.satellites = {sat.name: sat for sat in satellites}

        fileName = os.path.basename(source)
        dirPath = self.app.mwGlob['dataDir']
        filePath = f'{dirPath}/{fileName}'

        if not os.path.isfile(filePath):
            return False

        self.satellitesRawTLE = self.loadRawTLEData(filePath=filePath)

        if len(self.satellites) != len(self.satellitesRawTLE):
            return False

        return True

    def loadTLEDataFromSourceURLs(self):
        """
        loadTLEDataFromSourceURLs selects from a drop down list of possible satellite
        data sources on the web and once selected downloads the data. depending of the
        setting of reload is true setting, it takes an already loaded file from local disk.
        after loading or opening the source file, it updates the satellite list in the list
        view widget for the selection of satellites.

        :return: success
        """

        key = self.ui.satelliteSource.currentText()

        if key not in self.satelliteSourceURLs:
            return False

        source = self.satelliteSourceURLs[key]
        reload = self.ui.isOnline.isChecked()

        worker = Worker(self.loadTLEDataFromSourceURLsWorker,
                        source=source,
                        reload=reload)
        worker.signals.result.connect(self.setupSatelliteNameList)
        self.threadPool.start(worker)

        return True

    def updateOrbit(self):
        """
        updateOrbit calculates the actual satellite orbits, sub point etc. and
        updates the data in the gui. in addition when satellite window is open it signals
        this update data as well for matplotlib drawings in satellite window.
        this method is called cyclic every 3 seconds for updates

        :return: success
        """

        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            return False

        # check if calculation is necessary to optimize cpu time
        # get index for satellite tab and check if it's visible. if not, no calculation
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

        # if the satellite window is not visible, there is no need for sending the data
        if not winObj.get('classObj'):
            return True

        winObj['classObj'].signals.update.emit(observe, subpoint, altaz)
        return True

    def programTLEDataToMount(self):
        """
        programTLEDataToMount get the satellite data and programs this TLE data into the mount.
        after programming the parameters it forces the mount to calculate the satellite
        orbits immediately

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
            data = self.satellitesRawTLE[self.satellite.name]
            suc = satellite.setTLE(line0=data['line0'],
                                   line1=data['line1'],
                                   line2=data['line2'])
            if not suc:
                self.app.message.emit('Error program TLE', 2)
                return False

        return True

    def calcOrbitFromTLEInMount(self):
        """
        calcOrbitFromTLEInMount is called cyclic to update the orbit parameters in the
        mount computer

        :return: success
        """

        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            self.ui.stopSatelliteTracking.setEnabled(False)
            return False

        # starting thread for calculation of parameters
        self.app.mount.calcTLE()

        return True

    def showRises(self):
        """
        showRises calculated the next three satellite passes for the presentation in the gui.
        the times shown might differ from the calculation of the mount as we dont know, how
        the mount calculates is timings.

        :return: True for test purpose
        """

        minAlt = 5

        loc = self.app.mount.obsSite.location
        obs = self.app.mount.obsSite
        t0 = obs.timeJD
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

        index = 0
        for ti, event in zip(t, events):
            if index > 2:
                break
            if event == 0:
                passUI[index]['rise'].setText(f'{ti.utc_strftime(fString)}')
            elif event == 1:
                continue
            elif event == 2:
                passUI[index]['settle'].setText(f'{ti.utc_strftime(fString)}')
                index += 1

        while index < 3:
            passUI[index]['rise'].setText('-')
            passUI[index]['settle'].setText('-')
            index += 1

        return True

    def extractSatelliteData(self, satName=''):
        """
        extractSatelliteData is called when a satellite is selected via mouse click in the
        list menu. it collects the data and writes basic stuff to the gui. depending on the
        age of the satellite data is colors the frame

        :param satName: additional parameter for calling this method
        :return: success
        """

        if satName not in self.satellites:
            return False

        # selecting the entry in the list box
        item = None
        for index in range(self.ui.listSatelliteNames.model().rowCount()):
            if not self.ui.listSatelliteNames.item(index).text()[8:] == satName:
                continue
            item = self.ui.listSatelliteNames.item(index)
            item.setSelected(True)
            break

        if not item:
            return False

        # making the entry visible (and scroll the list if necessary)
        position = PyQt5.QtWidgets.QAbstractItemView.EnsureVisible
        self.ui.listSatelliteNames.scrollToItem(item, position)
        self.satellite = self.satellites[satName]

        # now we prepare the selection of the data in the gui
        self.ui.satelliteName.setText(self.satellite.name)
        epochText = self.satellite.epoch.utc_strftime('%Y-%m-%d, %H:%M:%S')
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

        #
        self.updateOrbit()
        self.programTLEDataToMount()
        self.calcOrbitFromTLEInMount()
        self.showRises()

        winObj = self.app.uiWindows['showSatelliteW']

        if not winObj['classObj']:
            return False

        winObj['classObj'].signals.show.emit(self.satellite)
        return True

    def signalExtractSatelliteData(self, widget):
        """

        :param widget: widget from where the signal is send
        :return: True for test purpose
        """
        if not widget:
            return False

        if self.ui.listSatelliteNames.currentItem() is None:
            return False

        satName = self.ui.listSatelliteNames.currentItem().text()[8:]
        self.extractSatelliteData(satName=satName)

        return True

    def getSatelliteDataFromDatabase(self, tleParams=None):
        """
        getSatelliteDataFromDatabase get's called, when the TLE setup is read from the mount.
        we use the name to retrieve the data from the "active.txt" database to be able to
        work with external database. it calls extraction method for getting the specific
        satellite data read and stored.

        :param tleParams:
        :return: True for test purpose
        """

        if not tleParams:
            return False

        self.extractSatelliteData(satName=tleParams.name)
        return True

    def updateSatelliteTrackGui(self, tleParams=None):
        """
        updateSatelliteTrackGui is called, when the mount has finished its calculations
        based on programmed TLE data. It writes the data to the gui and enables the start
        track button.

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
        startTrack un parks the mount if the mount has this state, because tracking could not
        start with mount parked. if unparked, slewing is initiated.


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
        stopTrack just sends the command stop tracking. this is also valid for satellite
        tracking

        :return: success
        """

        # todo: what is the right stop command for satellite tracking as it fails sometimes

        if not self.app.mount.mountUp:
            self.app.message.emit('Mount is not online', 2)
            return False

        suc = self.app.mount.obsSite.stopTracking()
        if not suc:
            self.app.message.emit('Cannot stop tracking', 2)
        else:
            self.app.message.emit('Stopped tracking', 0)

        return suc
