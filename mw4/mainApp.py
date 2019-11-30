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
import logging
import os
import sys
import json
import gc
# external packages
import PyQt5.QtCore
import skyfield
from mountcontrol import qtmount
from importlib_metadata import version
# local import
from mw4.gui.mainW import MainWindow
from mw4.gui.messageW import MessageWindow
from mw4.gui.keypadW import KeypadWindow
from mw4.gui.hemisphereW import HemisphereWindow
from mw4.gui.measureW import MeasureWindow
from mw4.gui.imageW import ImageWindow
from mw4.gui.satelliteW import SatelliteWindow
from mw4.powerswitch.kmRelay import KMRelay
from mw4.modeldata.buildpoints import DataPoint
from mw4.modeldata.hipparcos import Hipparcos
from mw4.dome.dome import Dome
from mw4.imaging.camera import Camera
from mw4.environment.sensorWeather import SensorWeather
from mw4.environment.skymeter import Skymeter
from mw4.environment.onlineWeather import OnlineWeather
from mw4.cover.flipflat import FlipFlat
from mw4.telescope.telescope import Telescope
from mw4.powerswitch.pegasusUPB import PegasusUPB
from mw4.base.measure import MeasureData
from mw4.remote.remote import Remote
from mw4.astrometry.astrometry import Astrometry


class MountWizzard4(PyQt5.QtCore.QObject):
    """
    MountWizzard4 class is the main class for the application. it loads all windows and
    classes needed to fulfil the work of mountwizzard. any gui work should be handled
    through the window classes. main class is for setup, config, start, persist and
    shutdown the application.
    """

    __all__ = ['MountWizzard4',
               ]
    __version__ = version('mountwizzard4')
    logger = logging.getLogger(__name__)

    # central message and logging dispatching
    message = PyQt5.QtCore.pyqtSignal(str, int)
    redrawHemisphere = PyQt5.QtCore.pyqtSignal()
    remoteCommand = PyQt5.QtCore.pyqtSignal(str)
    update1s = PyQt5.QtCore.pyqtSignal()
    update3s = PyQt5.QtCore.pyqtSignal()
    update10s = PyQt5.QtCore.pyqtSignal()
    update60s = PyQt5.QtCore.pyqtSignal()
    update3m = PyQt5.QtCore.pyqtSignal()
    update10m = PyQt5.QtCore.pyqtSignal()
    update30m = PyQt5.QtCore.pyqtSignal()
    update1h = PyQt5.QtCore.pyqtSignal()

    def __init__(self,
                 mwGlob=None,
                 ):
        super().__init__()
        # getting global app data
        self.expireData = False
        self.mountUp = False
        self.mwGlob = mwGlob
        self.timerCounter = 0
        self.mainW = None
        self.messageW = None
        self.keypadW = None
        self.hemisphereW = None
        self.measureW = None
        self.imageW = None
        self.satelliteW = None
        self.threadPool = PyQt5.QtCore.QThreadPool()
        self.threadPool.setMaxThreadCount(20)

        pathToData = self.mwGlob['dataDir']

        # persistence management through dict
        self.config = {}
        self.loadConfig()
        topo = self.initConfig()

        # initialize commands to mount
        self.mount = qtmount.Mount(host='192.168.2.15',
                                   MAC='00.c0.08.87.35.db',
                                   threadPool=self.threadPool,
                                   pathToData=pathToData,
                                   expire=False,
                                   verbose=False,
                                   )

        # setting location to last know config
        self.mount.obsSite.location = topo
        self.mount.signals.mountUp.connect(self.loadMountData)

        # get all planets for calculation
        try:
            self.planets = self.mount.obsSite.loader('de421_23.bsp')
        except Exception as e:
            self.logger.error(f'Failed planets: {e}')
            self.planets = None
        self.relay = KMRelay(host='192.168.2.15')
        self.sensorWeather = SensorWeather(self, host='localhost')
        self.onlineWeather = OnlineWeather(self,
                                           threadPool=self.threadPool)
        self.cover = FlipFlat(self, host='localhost')
        self.dome = Dome(self, host='localhost')
        self.imaging = Camera(self, host='localhost')
        self.telescope = Telescope(self, host='localhost')
        self.skymeter = Skymeter(self, host='localhost')
        self.power = PegasusUPB(self, host='localhost')
        self.data = DataPoint(self, mwGlob=self.mwGlob)
        self.hipparcos = Hipparcos(self, mwGlob=self.mwGlob)
        self.measure = MeasureData(self)
        self.remote = Remote(self)
        self.astrometry = Astrometry(self,
                                     tempDir=mwGlob['tempDir'],
                                     threadPool=self.threadPool)

        # get the window widgets up
        self.mainW = MainWindow(self,
                                threadPool=self.threadPool)
        self.showWindows()

        # link cross widget gui signals as all ui widgets have to be present
        self.mainW.ui.openMessageW.clicked.connect(self.toggleMessageWindow)
        self.mainW.ui.openHemisphereW.clicked.connect(self.toggleHemisphereWindow)
        self.mainW.ui.openImageW.clicked.connect(self.toggleImageWindow)
        self.mainW.ui.openMeasureW.clicked.connect(self.toggleMeasureWindow)
        self.mainW.ui.openSatelliteW.clicked.connect(self.toggleSatelliteWindow)
        self.mainW.ui.openKeypadW.clicked.connect(self.toggleKeypadWindow)

        # starting mount communication
        self.mount.startTimers()

        self.timer1s = PyQt5.QtCore.QTimer()
        self.timer1s.setSingleShot(False)
        self.timer1s.timeout.connect(self.sendUpdate)
        self.timer1s.start(500)

        # finishing for test: MW4 runs with keyword 'test' for 10 seconds an terminates
        if not hasattr(sys, 'argv'):
            return
        if not len(sys.argv) > 1:
            return
        if sys.argv[1] == 'test':
            self.update10s.connect(self.quitSave)

    def toggleHemisphereWindow(self):
        """

        :return:
        """
        if not self.hemisphereW:
            self.hemisphereW = HemisphereWindow(self)
            self.hemisphereW.destroyed.connect(self.deleteHemisphereW)
        else:
            self.hemisphereW.close()

    def deleteHemisphereW(self):
        """

        :return:
        """

        self.hemisphereW = None
        gc.collect()

    def toggleMessageWindow(self):
        """

        :return:
        """
        if not self.messageW:
            self.messageW = MessageWindow(self)
            self.messageW.destroyed.connect(self.deleteMessageW)
        else:
            self.messageW.close()

    def deleteMessageW(self):
        """

        :return:
        """

        self.messageW = None
        gc.collect()

    def toggleKeypadWindow(self):
        """

        :return:
        """
        if not self.keypadW:
            self.keypadW = KeypadWindow(self)
            self.keypadW.destroyed.connect(self.deleteKeypadW)
        else:
            self.keypadW.close()

    def deleteKeypadW(self):
        """

        :return:
        """

        self.keypadW = None
        gc.collect()

    def toggleImageWindow(self):
        """

        :return:
        """
        if not self.imageW:
            self.imageW = ImageWindow(self)
            self.imageW.destroyed.connect(self.deleteImageW)
        else:
            self.imageW.close()

    def deleteImageW(self):
        """

        :return:
        """

        self.imageW = None
        gc.collect()

    def toggleMeasureWindow(self):
        """

        :return:
        """
        if not self.measureW:
            self.measureW = MeasureWindow(self)
            self.measureW.destroyed.connect(self.deleteMeasureW)
        else:
            self.measureW.close()

    def deleteMeasureW(self):
        """

        :return:
        """
        self.measureW = None
        gc.collect()

    def toggleSatelliteWindow(self):
        """

        :return:
        """
        if not self.satelliteW:
            self.satelliteW = SatelliteWindow(self,
                                              threadPool=self.threadPool)
            self.satelliteW.destroyed.connect(self.deleteSatelliteW)
        else:
            self.satelliteW.close()

    def deleteSatelliteW(self):
        """

        :return:
        """
        self.satelliteW = None
        gc.collect()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return:
        """

        # set observer position to last one first, to greenwich if not known
        lat = self.config.get('topoLat', 51.47)
        lon = self.config.get('topoLon', 0)
        elev = self.config.get('topoElev', 46)
        topo = skyfield.api.Topos(longitude_degrees=lon,
                                  latitude_degrees=lat,
                                  elevation_m=elev)

        return topo

    def storeConfig(self):
        """
        storeConfig collects all persistent data from mainApp and it's submodules and stores
        it in the persistence dictionary for later saving

        :return: success for test purpose
        """

        config = self.config
        location = self.mount.obsSite.location
        if location is not None:
            config['topoLat'] = location.latitude.degrees
            config['topoLon'] = location.longitude.degrees
            config['topoElev'] = location.elevation.m
        self.mainW.storeConfig()

        config['showMessageW'] = bool(self.messageW)
        config['showKeypadW'] = bool(self.keypadW)
        config['showHemisphereW'] = bool(self.hemisphereW)
        config['showImageW'] = bool(self.imageW)
        config['showMeasureW'] = bool(self.measureW)
        config['showSatelliteW'] = bool(self.satelliteW)
        if self.messageW:
            self.messageW.storeConfig()
        if self.keypadW:
            self.keypadW.storeConfig()
        if self.imageW:
            self.imageW.storeConfig()
        if self.hemisphereW:
            self.hemisphereW.storeConfig()
        if self.measureW:
            self.measureW.storeConfig()
        if self.satelliteW:
            self.satelliteW.storeConfig()
        return True

    def showWindows(self):
        """

        :return: True for test purpose
        """

        if self.config.get('showMessageW', False):
            self.toggleMessageWindow()
        if self.config.get('showKeypadW', False):
            self.toggleKeypadWindow()
        if self.config.get('showHemisphereW', False):
            self.toggleHemisphereWindow()
        if self.config.get('showImageW', False):
            self.toggleImageWindow()
        if self.config.get('showMeasureW', False):
            self.toggleMeasureWindow()
        if self.config.get('showSatelliteW', False):
            self.toggleSatelliteWindow()

        return True

    def sendUpdate(self):
        """
        sendUpdate send regular signals in 1 and 10 seconds to enable regular tasks.
        it tries to avoid sending the signals at the same time.

        :return: true for test purpose
        """

        self.timerCounter += 0.5
        if (self.timerCounter + 0.5) % 1 == 0:
            self.update1s.emit()
        if (self.timerCounter + 1) % 3 == 0:
            self.update3s.emit()
        if (self.timerCounter + 2) % 10 == 0:
            self.update10s.emit()
        if (self.timerCounter + 2.5) % 60 == 0:
            self.update60s.emit()
        if (self.timerCounter + 1.5) % 180 == 0:
            self.update3m.emit()
        if (self.timerCounter + 1.5) % 600 == 0:
            self.update10m.emit()
        if (self.timerCounter + 1.5) % 1800 == 0:
            self.update30m.emit()
        if (self.timerCounter + 1.5) % 3600 == 0:
            self.update1h.emit()
        return True

    def quit(self):
        """
        quit without saving persistence data

        :return:    True for test purpose
        """

        self.mount.stopTimers()
        self.measure.timerTask.stop()
        self.relay.timerTask.stop()
        self.timer1s.stop()
        self.message.emit('MountWizzard4 manual stopped with quit', 1)
        PyQt5.QtCore.QCoreApplication.quit()
        return True

    def quitSave(self):
        """
        quit with saving persistence data

        :return:    True for test purpose
        """

        self.mount.stopTimers()
        self.measure.timerTask.stop()
        self.relay.timerTask.stop()
        self.storeConfig()
        self.saveConfig()
        self.timer1s.stop()
        self.message.emit('MountWizzard4 manual stopped with quit/save', 1)
        PyQt5.QtCore.QCoreApplication.quit()
        return True

    @staticmethod
    def defaultConfig(config=None):
        """

        :param config:
        :return:
        """

        if config is None:
            config = dict()
        config['profileName'] = 'config'
        config['version'] = '4.0'
        return config

    def loadConfig(self, name=None):
        """
        loadConfig loads a json file from disk and stores it to the config dicts for
        persistent data. if a file path is given, that's the relevant file, otherwise
        loadConfig loads from th default file, which is config.cfg

        :param      name:   name of the config file
        :return:    success if file could be loaded
        """

        configDir = self.mwGlob['configDir']
        # looking for file existence and creating new if necessary

        if name is None:
            name = 'config'
        fileName = configDir + '/' + name + '.cfg'

        if not os.path.isfile(fileName):
            self.config = self.defaultConfig()
            if name == 'config':
                self.logger.error('Config file {0} not existing'.format(fileName))
                return True
            else:
                return False

        # parsing the default file
        try:
            with open(fileName, 'r') as configFile:
                configData = json.load(configFile)
        except Exception as e:
            self.logger.error('Cannot parse: {0}, error: {1}'.format(fileName, e))
            self.config = self.defaultConfig()
            return False

        # check if reference ist still to default -> correcting
        if configData.get('reference', '') == 'config':
            del configData['reference']
        elif not configData.get('reference', ''):
            configData['profileName'] = 'config'

        # loading default and finishing up
        if configData['profileName'] == 'config':
            self.config = self.convertData(configData)
            return True

        # checking if reference to another file is available
        refName = configData.get('reference', 'config')
        if refName != name:
            suc = self.loadConfig(refName)
        else:
            self.config = configData
            return True
        return suc

    @staticmethod
    def convertData(data):
        """
        convertDate tries to convert data from an older or newer version of the config
        file to the actual needed one.

        :param      data:   config data as dict
        :return:    data:   config data as dict
        """

        return data

    def saveConfig(self, name=None):
        """
        saveConfig saves a json file to disk from the config dicts for
        persistent data.

        :param      name:   name of the config file
        :return:    success
        """

        configDir = self.mwGlob['configDir']

        if self.config.get('profileName', '') == 'config':
            if 'reference' in self.config:
                del self.config['reference']

        # default saving for reference
        if name is None:
            name = self.config.get('reference', 'config')

        fileName = configDir + '/' + name + '.cfg'
        with open(fileName, 'w') as outfile:
            json.dump(self.config,
                      outfile,
                      sort_keys=True,
                      indent=4)
        # if we save a reference first, we have to save the config as well
        if name != 'config':
            fileName = configDir + '/config.cfg'
            with open(fileName, 'w') as outfile:
                json.dump(self.config,
                          outfile,
                          sort_keys=True,
                          indent=4)
        return True

    def loadMountData(self, status):
        """
        loadMountData polls data from mount if connected otherwise clears all entries
        in attributes.

        :param      status: connection status to mount computer
        :return:    status how it was called
        """

        if status and not self.mountUp:
            self.mount.getFW()
            self.mount.getLocation()
            self.mount.cycleSetting()
            self.mainW.refreshName()
            self.mainW.refreshModel()
            self.mount.getTLE()
            self.mountUp = True
            return True
        elif not status and self.mountUp:
            location = self.mount.obsSite.location
            self.mount.resetData()
            self.mount.obsSite.location = location
            self.mountUp = False
            return False
        else:
            pass

        return status
