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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
from pathlib import Path
# external packages
import PyQt5
from astropy.io import fits
# local import


class Satellite(object):
    """
    the Satellite window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self. satellites = list()
        self.satellite = None
        self.satelliteTLE = {}

        self.satelliteSourceDropDown = {
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

        self.ui.listSatelliteNames.itemPressed.connect(self.extractSatelliteData)
        self.ui.startSatelliteTracking.clicked.connect(self.startTrack)
        self.ui.stopSatelliteTracking.clicked.connect(self.stopTrack)
        self.ui.satelliteSource.currentIndexChanged.connect(self.loadSatelliteSource)

        self.app.mount.signals.calcTLEdone.connect(self.enableTrack)
        self.app.mount.signals.getTLEdone.connect(self.prepare)

        self.app.update3s.connect(self.updateSatelliteData)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        self.setupSatelliteSourceGui()
        self.loadSatelliteSource()

        config = self.app.config['mainW']
        self.ui.satExpiresYes.setChecked(config.get('satExpiresYes', False))
        self.ui.satExpiresNo.setChecked(config.get('satExpiresNo', True))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['satExpiresYes'] = self.ui.satExpiresYes.isChecked()
        config['satExpiresNo'] = self.ui.satExpiresNo.isChecked()
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """

        return True

    def setupSatelliteSourceGui(self):
        """
        setupSatelliteSourceGui handles the dropdown list for the satellite data online
        sources. therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        self.ui.satelliteSource.clear()
        self.ui.satelliteSource.setView(PyQt5.QtWidgets.QListView())
        for name, _ in self.satelliteSourceDropDown.items():
            self.ui.satelliteSource.addItem(name)

        return True

    def prepare(self, tleParams):
        """

        :param tleParams:
        :return: True for test purpose
        """

        self.extractSatelliteData(None, satName=tleParams.name)
        return True

    def setupSatelliteGui(self):
        """
        setupSatelliteGui clears the list view of satellite names deriving from the selected
        source file on disk. after that it populated the list with actual data.

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

    def loadTLEData(self, source=''):
        """
        loadTLEData load the two line elements from the source file and stores is separately
        in a dictionary, because we need that data later for transfer it to the mount
        computer. unfortunately the loader from skyfield does not store the original TLE
        data, but only parses it and throws the original away.

        :param source:
        :return: success
        """

        if not source:
            return False

        fileName = os.path.basename(source)
        dirPath = self.app.mwGlob['dataDir']
        filePath = f'{dirPath}/{fileName}'

        if not os.path.isfile(filePath):
            return False

        self.satelliteTLE = {}
        with open(filePath, mode='r') as tleFile:
            while True:
                l0 = tleFile.readline()
                l1 = tleFile.readline()
                l2 = tleFile.readline()

                if not l0:
                    break
                self.satelliteTLE[l0.strip()] = {'line0': l0.strip('\n'),
                                                 'line1': l1.strip('\n'),
                                                 'line2': l2.strip('\n'),
                                                 }
        return True

    def loadSatelliteSource(self):
        """
        loadSatelliteSource selects from a drop down list of possible satellite data sources
        on the web and once selected downloads the data. depending of the setting of reload
        is true setting, it takes an already loaded file from local disk.
        after loading or opening the source file, it updates the satellite list in the list
        view widget for the selection of satellites.

        :return: success
        """

        key = self.ui.satelliteSource.currentText()

        if key not in self.satelliteSourceDropDown:
            return False

        source = self.satelliteSourceDropDown[key]
        reload = self.ui.satExpiresYes.isChecked()
        self.satellites = self.app.loader.tle(source, reload=reload)

        suc = self.loadTLEData(source)
        if not suc:
            return False

        self.setupSatelliteGui()

        return True

    def updateSatelliteData(self):
        """
        updateSatelliteData calculates the actual satellite orbits, subpoint etc. and
        updates the data in the gui. in addition when satellite window is open it signals
        this update data as well for matplotlib drawings in satellite window.
        this method is called cyclic every 3 seconds for updates

        :return: success
        """

        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            return False

        # check if calculation is necessary to optimize cpu time
        # get index for satellite tab
        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Satellite')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)
        satTabVisible = self.ui.mainTabWidget.currentIndex() == tabIndex

        if not self.app.satelliteW and not satTabVisible:
            return False

        now = self.app.mount.obsSite.ts.now()
        observe = self.satellite.at(now)
        sett = self.app.mount.sett

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

        hasPressure = (sett.refractionPress is not None)
        hasTemperature = (sett.refractionTemp is not None)

        if hasPressure and hasTemperature:
            altaz = difference.at(now).altaz(temperature_C=sett.refractionPress,
                                             pressure_mbar=sett.refractionTemp)
        else:
            altaz = difference.at(now).altaz()

        alt, az, _ = altaz
        alt = alt.degrees
        az = az.degrees

        self.ui.satAltitude.setText(f'{alt:3.2f}')
        self.ui.satAzimuth.setText(f'{az:3.2f}')

        if not self.app.satelliteW:
            return

        self.app.satelliteW.signals.update.emit(observe, subpoint, altaz)
        return True

    def programTLEToMount(self):
        """
        programTLEToMount get the satellite data and programs this TLE data into the mount.
        after programming the parameters it forces the mount to calculate the satellite
        orbits immediately

        :return: success
        """

        if not self.app.mount.mountUp:
            self.app.message.emit('Mount is not online', 2)
            return False

        satellite = self.app.mount.satellite
        self.app.message.emit(f'Programming [{self.satellite.name}] to mount', 0)
        data = self.satelliteTLE[self.satellite.name]

        suc = satellite.setTLE(line0=data['line0'],
                               line1=data['line1'],
                               line2=data['line2'])
        if not suc:
            self.app.message.emit('Error program TLE', 2)
            return False

        return True

    def calcTLEParams(self):
        """
        calcTLEParams is called cyclic to update the orbit parameters in the mount computer

        :return: success
        """

        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            self.ui.stopSatelliteTracking.setEnabled(False)
            return False

        # starting thread for calculation of parameters
        self.app.mount.calcTLE()

        return True

    def extractSatelliteData(self, widget, satName=''):
        """
        extractSatelliteData is called when a satellite is selected via mouse click in the
        list menu. it collects the data and writes basic stuff to the gui.
        for speeding up, is calls updateSatelliteData immediately to get the actual data
        pushed to the gui and not waiting for the cyclic task.
        depending on the age of the satellite data is colors the frame

        :param widget:
        :param satName:
        :return: success
        """

        if not isinstance(satName, str):
            return False

        if not satName:
            satName = self.ui.listSatelliteNames.currentItem().text()[8:]

        if satName not in self.satellites:
            return False

        for index in range(self.ui.listSatelliteNames.model().rowCount()):
            if not self.ui.listSatelliteNames.item(index).text()[8:] == satName:
                continue
            item = self.ui.listSatelliteNames.item(index)
            item.setSelected(True)
            break

        position = PyQt5.QtWidgets.QAbstractItemView.EnsureVisible
        self.ui.listSatelliteNames.scrollToItem(item, position)
        self.satellite = self.satellites[satName]

        self.ui.satelliteName.setText(self.satellite.name)
        epochText = self.satellite.epoch.utc_strftime('%Y-%m-%d, %H:%M:%S')
        self.ui.satelliteEpoch.setText(epochText)

        now = self.app.mount.obsSite.ts.now()
        days = now - self.satellite.epoch
        self.ui.satelliteDataAge.setText(f'{days:2.2f}')

        if days > 10:
            self.changeStyleDynamic(self.ui.satelliteDataAge, 'color', 'red')
        elif 3 < days < 10:
            self.changeStyleDynamic(self.ui.satelliteDataAge, 'color', 'yellow')
        else:
            self.changeStyleDynamic(self.ui.satelliteDataAge, 'color', '')

        self.ui.satelliteNumber.setText(f'{self.satellite.model.satnum:5d}')

        self.ui.stopSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setEnabled(False)
        self.ui.satTransitStartUTC.setText('-')
        self.ui.satTransitEndUTC.setText('-')
        self.ui.satNeedFlip.setText('-')

        self.updateSatelliteData()
        self.programTLEToMount()
        self.calcTLEParams()

        if not self.app.satelliteW:
            return False

        self.app.satelliteW.signals.show.emit(self.satellite)
        return True

    def enableTrack(self, tleParams):
        """

        :return:
        """

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
            if not suc:
                self.app.message.emit('Cannot unpark mount', 2)
            else:
                self.app.message.emit('Mount unparked', 0)

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

        if not self.app.mount.mountUp:
            self.app.message.emit('Mount is not online', 2)
            return False

        suc = self.app.mount.obsSite.stopTracking()
        if not suc:
            self.app.message.emit('Cannot stop tracking', 2)
        else:
            self.app.message.emit('Stopped tracking', 0)
