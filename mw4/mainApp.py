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
import logging
import os
import json
import gc
# external packages
import PyQt5.QtCore
import skyfield
from mountcontrol import qtmount
# local import
from mw4.gui import mainW
from mw4.gui import messageW
from mw4.gui import hemisphereW
from mw4.gui import measureW
from mw4.gui import imageW
from mw4.gui import satelliteW
from mw4.powerswitch import kmRelay
from mw4.modeldata import buildpoints
from mw4.modeldata import hipparcos
from mw4.dome import dome
from mw4.imaging import camera
from mw4.environment import environ
from mw4.environment import skymeter
from mw4.environment import weather
from mw4.powerswitch import pegasusUPB
from mw4.base import measuredata
from mw4.remote import remote
from mw4.astrometry import astrometry


class MountWizzard4(PyQt5.QtCore.QObject):
    """
    MountWizzard4 class is the main class for the application. it loads all windows and
    classes needed to fulfil the work of mountwizzard. any gui work should be handled
    through the window classes. main class is for setup, config, start, persist and
    shutdown the application.
    """

    __all__ = ['MountWizzard4',
               ]
    version = '0.100'
    logger = logging.getLogger(__name__)

    # central message and logging dispatching
    message = PyQt5.QtCore.pyqtSignal(str, int)
    redrawHemisphere = PyQt5.QtCore.pyqtSignal()
    remoteCommand = PyQt5.QtCore.pyqtSignal(str)
    update1s = PyQt5.QtCore.pyqtSignal()
    update3s = PyQt5.QtCore.pyqtSignal()
    update10s = PyQt5.QtCore.pyqtSignal()
    update60s = PyQt5.QtCore.pyqtSignal()

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
        self.hemisphereW = None
        self.measureW = None
        self.imageW = None
        self.satelliteW = None
        self.threadPool = PyQt5.QtCore.QThreadPool()

        pathToData = self.mwGlob['dataDir']

        # persistence management through dict
        self.config = {}
        self.loadConfig()
        expireData, topo = self.initConfig()

        # initialize commands to mount
        self.mount = qtmount.Mount(host='192.168.2.15',
                                   MAC='00.c0.08.87.35.db',
                                   threadPool=self.threadPool,
                                   pathToData=pathToData,
                                   expire=expireData,
                                   verbose=False,
                                   )

        # setting location to last know config
        self.mount.obsSite.location = topo
        self.mount.signals.mountUp.connect(self.loadMountData)

        # get all planets for calculation
        self.loader = skyfield.api.Loader(pathToData,
                                          expire=expireData,
                                          verbose=False,
                                          )
        self.planets = self.loader('de421.bsp')
        self.relay = kmRelay.KMRelay(host='192.168.2.15')
        self.environ = environ.Environ(host='localhost')
        self.dome = dome.Dome(self, host='localhost')
        self.imaging = camera.Camera(self, host='localhost')
        self.skymeter = skymeter.Skymeter(host='localhost')
        self.weather = weather.Weather(host='localhost')
        self.power = pegasusUPB.PegasusUPB(host='localhost')
        self.data = buildpoints.DataPoint(self, mwGlob=self.mwGlob)
        self.hipparcos = hipparcos.Hipparcos(self, mwGlob=self.mwGlob)
        self.measure = measuredata.MeasureData(self)
        self.remote = remote.Remote(self)
        self.astrometry = astrometry.Astrometry(tempDir=mwGlob['tempDir'],
                                                threadPool=self.threadPool)

        # get the window widgets up
        self.mainW = mainW.MainWindow(self,
                                      threadPool=self.threadPool)
        self.showWindows()

        # link cross widget gui signals as all ui widgets have to be present
        self.mainW.ui.openMessageW.clicked.connect(self.toggleMessageWindow)
        self.mainW.ui.openHemisphereW.clicked.connect(self.toggleHemisphereWindow)
        self.mainW.ui.openImageW.clicked.connect(self.toggleImageWindow)
        self.mainW.ui.openMeasureW.clicked.connect(self.toggleMeasureWindow)
        self.mainW.ui.openSatelliteW.clicked.connect(self.toggleSatelliteWindow)

        # starting mount communication
        self.mount.startTimers()

        self.timer1s = PyQt5.QtCore.QTimer()
        self.timer1s.setSingleShot(False)
        self.timer1s.timeout.connect(self.sendUpdate)
        self.timer1s.start(500)

    def toggleHemisphereWindow(self):
        """

        :return:
        """
        if not self.hemisphereW:
            self.hemisphereW = hemisphereW.HemisphereWindow(self)
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
            self.messageW = messageW.MessageWindow(self)
            self.messageW.destroyed.connect(self.deleteMessageW)
        else:
            self.messageW.close()

    def deleteMessageW(self):
        """

        :return:
        """

        self.messageW = None
        gc.collect()

    def toggleImageWindow(self):
        """

        :return:
        """
        if not self.imageW:
            self.imageW = imageW.ImageWindow(self)
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
            self.measureW = measureW.MeasureWindow(self)
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
            self.satelliteW = satelliteW.SatelliteWindow(self,
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

        # check if data for skyfield expires or not and get the status for it
        if 'mainW' in self.config:
            expireData = self.config['mainW'].get('expiresYes', True)
        else:
            expireData = True
        # set observer position to last one first, to greenwich if not known
        lat = self.config.get('topoLat', 51.47)
        lon = self.config.get('topoLon', 0)
        elev = self.config.get('topoElev', 46)
        topo = skyfield.api.Topos(longitude_degrees=lon,
                                  latitude_degrees=lat,
                                  elevation_m=elev)

        return expireData, topo

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
        config['showHemisphereW'] = bool(self.hemisphereW)
        config['showImageW'] = bool(self.imageW)
        config['showMeasureW'] = bool(self.measureW)
        config['showSatelliteW'] = bool(self.satelliteW)
        if self.messageW:
            self.messageW.storeConfig()
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
