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
import logging
import os
import json
import platform
# external packages
import PyQt5.QtCore
import skyfield
from mountcontrol import qtmount
from indibase import qtIndiBase
# local import
from mw4.gui import mainW
from mw4.gui import messageW
from mw4.gui import hemisphereW
from mw4.gui import measureW
from mw4.gui import imageW
from mw4.powerswitch import kmRelay
from mw4.modeldata import buildpoints
from mw4.modeldata import hipparcos
from mw4.environment import environ
from mw4.environment import skymeter
from mw4.environment import weather
from mw4.powerswitch import pegasusUPB
from mw4.base import measuredata
from mw4.remote import remote
from mw4.astrometry import astrometryKstars


class MountWizzard4(PyQt5.QtCore.QObject):
    """
    MountWizzard4 class is the main class for the application. it loads all windows and
    classes needed to fulfil the work of mountwizzard. any gui work should be handled
    through the window classes. main class is for setup, config, start, persist and
    shutdown the application.
    """

    __all__ = ['MountWizzard4',
               ]
    version = '0.6.dev2'
    logger = logging.getLogger(__name__)

    # central message and logging dispatching
    message = PyQt5.QtCore.pyqtSignal(str, int)
    redrawHemisphere = PyQt5.QtCore.pyqtSignal()
    remoteCommand = PyQt5.QtCore.pyqtSignal(str)
    update1s = PyQt5.QtCore.pyqtSignal()
    update3s = PyQt5.QtCore.pyqtSignal()
    update10s = PyQt5.QtCore.pyqtSignal()

    def __init__(self,
                 mwGlob=None,
                 ):
        super().__init__()

        # getting global app data
        self.expireData = False
        self.mwGlob = mwGlob
        self.timerCounter = 0
        self.threadPool = PyQt5.QtCore.QThreadPool()

        pathToData = self.mwGlob['dataDir']

        # persistence management through dict
        self.config = {}
        self.loadConfig()
        expireData, topo = self.initConfig()

        # initialize commands to mount
        self.mount = qtmount.Mount(host='192.168.2.15',
                                   MAC='00.c0.08.87.35.db',
                                   pathToData=pathToData,
                                   expire=expireData,
                                   verbose=None,
                                   )

        # setting location to last know config
        self.mount.obsSite.location = topo
        self.mount.signals.mountUp.connect(self.loadMountData)

        # get all planets for calculation
        load = skyfield.api.Loader(pathToData,
                                   expire=expireData,
                                   verbose=None,
                                   )
        self.planets = load('de421.bsp')

        # enabling message window first
        self.messageW = messageW.MessageWindow(self)

        # write basic data to message window
        verMC = self.mount.version
        verIB = qtIndiBase.Client.version
        profile = self.config.get('profileName', '-')
        self.message.emit('MountWizzard4 started', 1)
        self.message.emit('build version: [{0}]'.format(self.version), 1)
        self.message.emit('mountcontrol version: [{0}]'.format(verMC), 1)
        self.message.emit('indibase version: [{0}]'.format(verIB), 1)
        self.message.emit('Workdir is: [{0}]'.format(self.mwGlob['workDir']), 1)
        self.message.emit('Profile [{0}] loaded'.format(profile), 0)

        # loading other classes
        self.relay = kmRelay.KMRelay(host='192.168.2.15')
        self.environ = environ.Environ(host='localhost')
        self.skymeter = skymeter.Skymeter(host='localhost')
        self.weather = weather.Weather(host='localhost')
        self.power = pegasusUPB.PegasusUPB(host='localhost')
        self.data = buildpoints.DataPoint(self,
                                          mwGlob=self.mwGlob,
                                          )
        self.hipparcos = hipparcos.Hipparcos(self,
                                             mwGlob=self.mwGlob,
                                             )
        self.measure = measuredata.MeasureData(self)
        self.remote = remote.Remote(self)
        if platform.system() in ['Darwin', 'Linux']:
            self.astrometry = astrometryKstars.AstrometryKstars(mwGlob['tempDir'],
                                                                self.threadPool)
        else:
            self.astrometry = astrometryKstars.AstrometryKstars(mwGlob['tempDir'],
                                                                self.threadPool)
        # get the window widgets up
        self.mainW = mainW.MainWindow(self)
        self.hemisphereW = hemisphereW.HemisphereWindow(self)
        self.measureW = measureW.MeasureWindow(self)
        self.imageW = imageW.ImageWindow(self)

        # link cross widget gui signals as all ui widgets have to be present
        self.mainW.ui.openMessageW.clicked.connect(self.messageW.toggleWindow)
        self.mainW.ui.openHemisphereW.clicked.connect(self.hemisphereW.toggleWindow)
        self.mainW.ui.openImageW.clicked.connect(self.imageW.toggleWindow)

        # starting mount communication
        self.mount.startTimers()
        self.astrometry.checkAvailability()

        self.timer1s = PyQt5.QtCore.QTimer()
        self.timer1s.setSingleShot(False)
        self.timer1s.timeout.connect(self.sendUpdate)
        self.timer1s.start(500)

    def initConfig(self):
        """

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
        self.messageW.storeConfig()
        self.imageW.storeConfig()
        self.hemisphereW.storeConfig()
        self.measureW.storeConfig()
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
        return True

    def quit(self):
        """
        quit without saving persistence data

        :return:    True for test purpose
        """

        self.message.emit('MountWizzard4 manual stopped with quit', 1)
        self.timer1s.stop()
        self.mount.stopTimers()
        self.measure.timerTask.stop()
        self.relay.timerTask.stop()
        PyQt5.QtCore.QCoreApplication.quit()
        return True

    def quitSave(self):
        """
        quit with saving persistence data

        :return:    True for test purpose
        """

        self.message.emit('MountWizzard4 manual stopped with quit/save', 1)
        self.timer1s.stop()
        self.mount.stopTimers()
        self.measure.timerTask.stop()
        self.relay.timerTask.stop()
        self.storeConfig()
        self.saveConfig()
        PyQt5.QtCore.QCoreApplication.quit()
        return True

    @staticmethod
    def defaultConfig(config=None):
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
        if status:
            # self.mount.workaround()
            self.mount.getFW()
            self.mount.getLocation()
            self.mount.cycleSetting()
            self.mainW.refreshName()
            self.mainW.refreshModel()
            return True
        else:
            location = self.mount.obsSite.location
            self.mount.resetData()
            self.mount.obsSite.location = location
            return False
