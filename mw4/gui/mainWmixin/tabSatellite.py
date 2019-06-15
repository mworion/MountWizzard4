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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
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
        # self.ui.loadSatelliteSource.clicked.connect()
        self.ui.listSatelliteNames.itemPressed.connect(self.updateSatelliteData)

        self.setupSatelliteSourceGui()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
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
        setupSatelliteGui handles the dropdown list for the satellite data online
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
        setupSatelliteSourceGui handles the dropdown list for the satellite data online
        sources. therefore we add the necessary entries to populate the list.

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

    def loadSatelliteSource(self):

        key = self.ui.satelliteSource.currentText()
        source = self.satelliteSourceDropDown[key]
        reload = self.ui.checkReload.isChecked()
        self.satellites = self.app.loader.tle(source, reload=reload)

        self.setupSatelliteGui()

        return True

    def updateSatelliteData(self):

        key = self.ui.listSatelliteNames.currentItem().text()
        self.satellite = self.satellites[key]

        self.ui.satelliteName.setText(self.satellite.name)
        epochText = self.satellite.epoch.utc_strftime('%Y-%m-%d, %H:%M:%S')
        self.ui.satelliteEpoch.setText(epochText)

        now = self.app.mount.obsSite.ts.now()
        days = now - self.satellite.epoch
        self.ui.satelliteDataAge.setText(str(days))

        if self.app.satelliteW:
            self.app.satelliteW.signals.show.emit(self.satellite)
