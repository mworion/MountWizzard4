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

        self.ui.satelliteSource.currentIndexChanged.connect(self.loadSatelliteSource)
        self.ui.listSatelliteNames.itemPressed.connect(self.extractSatelliteData)
        self.ui.programSatelliteDataMount.clicked.connect(self.programTLEToMount)

        self.app.update3s.connect(self.updateSatelliteData)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        self.setupSatelliteSourceGui()

        config = self.app.config['mainW']
        self.ui.checkReload.setChecked(config.get('checkReloadSatellites', False))
        self.ui.satelliteSource.setCurrentIndex(config.get('satelliteSource', 0))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['checkReloadSatellites'] = self.ui.checkReload.isChecked()
        config['satelliteSource'] = self.ui.satelliteSource.currentIndex()
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
            self.ui.listSatelliteNames.addItem(name)
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
        reload = self.ui.checkReload.isChecked()
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
            return False

        now = self.app.mount.obsSite.ts.now()
        observe = self.satellite.at(now)

        subpoint = observe.subpoint()
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        self.ui.satLatitude.setText(f'{lat:3.2f}')
        self.ui.satLongitude.setText(f'{lon:3.2f}')

        difference = self.satellite - self.app.mount.obsSite.location
        altaz = difference.at(now).altaz()
        alt, az, _ = altaz
        alt = alt.degrees
        az = az.degrees
        self.ui.satAltitude.setText(f'{alt:3.2f}')
        self.ui.satAzimuth.setText(f'{az:3.2f}')

        if not self.app.satelliteW:
            return False

        self.app.satelliteW.signals.update.emit(observe, subpoint, altaz)
        return True

    def extractSatelliteData(self):
        """
        extractSatelliteData is called when a satellite is selected via mouse click in the
        list menu. it collects the data and writes basic stuff to the gui.
        for speeding up, is calls updateSatelliteData immediately to get the actual data
        pushed to the gui and not waiting for the cyclic task.
        depending on the age of the satellite data is colors the frame

        :return: success
        """

        key = self.ui.listSatelliteNames.currentItem().text()
        self.satellite = self.satellites[key]

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

        self.updateSatelliteData()

        if not self.app.satelliteW:
            return False

        self.app.satelliteW.signals.show.emit(self.satellite)
        return True

    def showTLEStatus(self):
        """

        :return: success
        """

        if self.ui.satNameMount.text() == '-':
            return False

        suc, response = obsSite.calcTLE(julianDate=obsSite.timeJD.tt,
                                        duration=720,
                                        )
        if not suc:
            self.app.message.emit('Error calculate TLE', 2)
            return False

        alt, az = response[0].split(',')
        ra, dec = response[1].split(',')
        start, end, flip = response[2].split(',')
        startUTC = obsSite.ts.tt_jd(float(start)).utc_strftime('%Y-%m-%d  %H:%M:%S')
        endUTC = obsSite.ts.tt_jd(float(end)).utc_strftime('%Y-%m-%d  %H:%M:%S')

        self.ui.satAltitudeMount.setText(alt)
        self.ui.satAzimuthMount.setText(az)
        self.ui.satRaMount.setText(ra)
        self.ui.satDecMount.setText(dec)
        self.ui.satTransitStartUTC.setText(startUTC)
        self.ui.satTransitEndUTC.setText(endUTC)
        self.ui.satNameMount.setText(self.satellite.name)

        if flip == 'F':
            self.ui.satNeedFlip.setText('YES')
        else:
            self.ui.satNeedFlip.setText('NO')

        suc, message = obsSite.getTLEStat()
        if not suc:
            self.app.message.emit('Error status TLE', 2)
            return False

        self.ui.satelliteStatus.setText(message)

        return True

    def programTLEToMount(self):
        """

        :return: success
        """

        obsSite = self.app.mount.obsSite
        data = self.satelliteTLE[self.satellite.name]

        suc = obsSite.setTLE(line0=data['line0'],
                             line1=data['line1'],
                             line2=data['line2'])
        if not suc:
            self.app.message.emit('Error program TLE', 2)
            return False

        self.showTLEStatus()
        return True

    def clearTLEToMount(self):
        """

        :return: True for test purpose
        """

        self.ui.satAltitudeMount.setText('-')
        self.ui.satRaMount.setText('-')
        self.ui.satDecMount.setText('-')
        self.ui.satTransitStartUTC.setText('-')
        self.ui.satTransitEndUTC.setText('-')
        self.ui.satNameMount.setText('-')
        self.ui.satelliteStatus.setText('-')

        return True

    def startTrack(self):
        """

        :return: success
        """

        suc = self.app.mount.obsSite.slewTLE()
        if not suc:
            self.app.message.emit(message, 2)
            return False

        self.ui.satelliteStatus.setText(message)

        return True
